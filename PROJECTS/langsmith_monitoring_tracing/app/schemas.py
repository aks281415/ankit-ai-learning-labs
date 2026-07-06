"""
Pydantic models for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Request Models ──────────────────────────────────────────────────

class ChatRequest(BaseModel):
    """Incoming chat message from the user."""
    session_id: Optional[str] = Field(
        None,
        description="Session ID for multi-turn conversation. Auto-generated if not provided."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="The user's message to the chatbot."
    )


# ── Response Models ─────────────────────────────────────────────────

class TokenUsage(BaseModel):
    """Token usage breakdown for a single request."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ResponseMetadata(BaseModel):
    """Metadata about the LLM response for observability."""
    model: str = ""
    latency_seconds: float = 0.0
    token_usage: TokenUsage = TokenUsage()
    estimated_cost_usd: float = 0.0


class ChatResponse(BaseModel):
    """Response returned to the user after a chat request."""
    session_id: str
    response: str
    metadata: ResponseMetadata


class SessionInfo(BaseModel):
    """Summary information about a conversation session."""
    session_id: str
    message_count: int
    created_at: datetime
    last_active: datetime


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    app_name: str
    model: str
    langsmith_enabled: bool
    active_sessions: int
