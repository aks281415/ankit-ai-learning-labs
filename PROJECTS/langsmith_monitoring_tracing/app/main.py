"""
FastAPI application — routes, middleware, and startup configuration.

Endpoints:
    GET  /                  — Chat UI (talk to the bot)
    POST /chat              — Chat API endpoint
    GET  /dashboard         — Built-in monitoring dashboard
    GET  /api/metrics       — JSON metrics for the dashboard
    GET  /sessions          — List active sessions
    GET  /sessions/{id}     — Get session details & history
    DELETE /sessions/{id}   — Delete a session
    GET  /health            — Health check
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import json

from app.config import settings
from app.schemas import (
    ChatRequest,
    ChatResponse,
    SessionInfo,
    HealthResponse,
)
from app.conversation import conversation_manager
from app.chain import get_chat_response, get_chat_response_stream
from app.metrics import metrics_store
from app.dashboard import DASHBOARD_HTML
from app.chat_ui import CHAT_HTML

# ── Logging Setup ───────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("chatbot")


# ── Application Lifespan ───────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    settings.configure_langsmith_env()
    logger.info("=" * 60)
    logger.info("🚀  %s is starting up", settings.APP_NAME)
    logger.info("   Model       : %s", settings.MODEL_NAME)
    logger.info("   DeepSeek URL: %s", settings.DEEPSEEK_BASE_URL)
    logger.info("   LangSmith   : %s", "enabled" if settings.LANGCHAIN_TRACING_V2 else "disabled")
    logger.info("   Project     : %s", settings.LANGCHAIN_PROJECT)
    logger.info("   Chat UI     : http://localhost:%s/", settings.APP_PORT)
    logger.info("   Dashboard   : http://localhost:%s/dashboard", settings.APP_PORT)
    logger.info("=" * 60)
    yield
    # Shutdown
    logger.info("👋  %s is shutting down", settings.APP_NAME)


# ── FastAPI App ─────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    description="AI Career Mentor with built-in observability dashboard + LangSmith tracing",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════
#  ROUTES
# ═══════════════════════════════════════════════════════════════════


# ── Chat UI (Homepage) ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def chat_ui():
    """Serve the chat interface at the homepage.

    Users can have multi-turn conversations with the AI Career Mentor
    directly from their browser — no curl or Swagger needed.
    """
    return HTMLResponse(content=CHAT_HTML)


# ── Chat API (Streaming) ────────────────────────────────────────────

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Process a chat message and stream the response back using SSE."""
    session_id = conversation_manager.get_or_create_session(request.session_id)
    metrics_store.set_active_sessions(conversation_manager.active_count)
    history = conversation_manager.get_history(session_id)

    async def event_generator():
        try:
            async for item in get_chat_response_stream(request.message, history, session_id=session_id):
                if item["type"] == "chunk":
                    yield f"data: {json.dumps({'type': 'chunk', 'text': item['text']})}\n\n"
                
                elif item["type"] == "metadata":
                    full_text = item["full_text"]
                    metadata_dict = item["metadata"]
                    
                    conversation_manager.add_message(session_id, "user", request.message)
                    conversation_manager.add_message(session_id, "assistant", full_text)
                    
                    metrics_store.record_success(
                        session_id=session_id,
                        message=request.message,
                        latency=metadata_dict["latency_seconds"],
                        prompt_tokens=metadata_dict["token_usage"]["prompt_tokens"],
                        completion_tokens=metadata_dict["token_usage"]["completion_tokens"],
                        cost=metadata_dict["estimated_cost_usd"],
                    )
                    metrics_store.set_active_sessions(conversation_manager.active_count)
                    
                    yield f"data: {json.dumps({'type': 'metadata', 'session_id': session_id, 'metadata': metadata_dict})}\n\n"
        
        except Exception as e:
            error_type = "unknown"
            if "timeout" in str(e).lower(): error_type = "timeout"
            elif "api" in str(e).lower() or "auth" in str(e).lower(): error_type = "llm_error"
            
            metrics_store.record_error(session_id, request.message, error_type)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Chat API (Blocking) ─────────────────────────────────────────────

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return an AI response.

    Flow:
        1. Get or create a conversation session
        2. Retrieve conversation history
        3. Call the LLM via LangChain (traced by LangSmith)
        4. Store the exchange in session history
        5. Record metrics in the built-in metrics store
        6. Return the response with metadata
    """
    session_id = None
    try:
        # 1. Session management
        session_id = conversation_manager.get_or_create_session(request.session_id)
        metrics_store.set_active_sessions(conversation_manager.active_count)

        # 2. Get history for context
        history = conversation_manager.get_history(session_id)

        # 3. Call LLM
        response_text, metadata = await get_chat_response(request.message, history, session_id=session_id)

        # 4. Store messages in session
        conversation_manager.add_message(session_id, "user", request.message)
        conversation_manager.add_message(session_id, "assistant", response_text)

        # 5. Record metrics
        metrics_store.record_success(
            session_id=session_id,
            message=request.message,
            latency=metadata.latency_seconds,
            prompt_tokens=metadata.token_usage.prompt_tokens,
            completion_tokens=metadata.token_usage.completion_tokens,
            cost=metadata.estimated_cost_usd,
        )
        metrics_store.set_active_sessions(conversation_manager.active_count)

        logger.info(
            "Chat | session=%s | latency=%.2fs | tokens=%d | cost=$%.6f",
            session_id[:8],
            metadata.latency_seconds,
            metadata.token_usage.total_tokens,
            metadata.estimated_cost_usd,
        )

        # 6. Return response
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            metadata=metadata,
        )

    except Exception as e:
        # Determine error type for metrics
        error_type = "unknown"
        if "timeout" in str(e).lower():
            error_type = "timeout"
        elif "api" in str(e).lower() or "auth" in str(e).lower():
            error_type = "llm_error"
        elif "validation" in str(e).lower():
            error_type = "validation_error"

        metrics_store.record_error(
            session_id=session_id or "unknown",
            message=request.message,
            error_type=error_type,
        )
        logger.error("Chat error | type=%s | error=%s", error_type, str(e))
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ── Dashboard ───────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    """Serve the built-in real-time monitoring dashboard.

    Auto-refreshes every 3 seconds by fetching /api/metrics.
    No Grafana or external tools needed.
    """
    return HTMLResponse(content=DASHBOARD_HTML)


@app.get("/api/metrics")
async def api_metrics():
    """JSON metrics endpoint consumed by the dashboard.

    Returns all metrics in a single JSON response for the
    dashboard to render charts, stats, and the request log.
    """
    return JSONResponse(content=metrics_store.get_dashboard_data())


# ── Sessions ────────────────────────────────────────────────────────

@app.get("/sessions", response_model=list[SessionInfo])
async def list_sessions():
    """List all active conversation sessions."""
    sessions = conversation_manager.list_sessions()
    return [SessionInfo(**s) for s in sessions]


@app.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get detailed information and history for a specific session."""
    info = conversation_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(status_code=404, detail="Session not found")
    return info


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a conversation session."""
    deleted = conversation_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    metrics_store.set_active_sessions(conversation_manager.active_count)
    return {"message": f"Session {session_id} deleted", "status": "ok"}


# ── Health ──────────────────────────────────────────────────────────

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.APP_NAME,
        model=settings.MODEL_NAME,
        langsmith_enabled=settings.LANGCHAIN_TRACING_V2,
        active_sessions=conversation_manager.active_count,
    )


# ── Cleanup (manual trigger) ───────────────────────────────────────

@app.post("/admin/cleanup")
async def cleanup_sessions():
    """Remove expired sessions (inactive > SESSION_TIMEOUT_MINUTES)."""
    removed = conversation_manager.cleanup_expired_sessions()
    metrics_store.set_active_sessions(conversation_manager.active_count)
    return {
        "message": f"Removed {removed} expired sessions",
        "active_sessions": conversation_manager.active_count,
    }
