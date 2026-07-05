import time
import logging
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.config import settings
from app.schemas import TokenUsage, ResponseMetadata

logger = logging.getLogger(__name__)


# ── System Prompt ───────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert AI Career Mentor with deep knowledge of the technology industry, \
career development, and professional growth strategies.

Your role:
- Provide personalized career guidance based on the user's background, skills, and goals.
- Remember and reference details the user has shared earlier in the conversation.
- Suggest specific technologies, learning paths, certifications, and career moves.
- Give actionable, practical advice — not generic platitudes.
- Be encouraging but realistic about career expectations.

Guidelines:
- Always acknowledge what the user has told you before (their experience, skills, role, etc.).
- Tailor every recommendation to their specific situation.
- When suggesting technologies, explain WHY they're relevant to the user's profile.
- Keep responses focused and well-structured (use bullet points when listing recommendations).
- If the user hasn't shared enough context, ask clarifying questions before giving advice.
"""


# ── LLM Initialization ─────────────────────────────────────────────

def create_llm() -> ChatOpenAI:
    """Create and return a configured DeepSeek LLM instance.

    Uses ChatOpenAI with DeepSeek's OpenAI-compatible endpoint.
    """
    return ChatOpenAI(
        model=settings.MODEL_NAME,
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        temperature=0.7,
        max_tokens=1024,
    )


# Global LLM instance (created once, reused across requests)
llm: Optional[ChatOpenAI] = None


def get_llm() -> ChatOpenAI:
    """Get or create the LLM singleton."""
    global llm
    if llm is None:
        llm = create_llm()
    return llm


# ── Message Building ───────────────────────────────────────────────

def build_messages(
    user_message: str,
    history: list[dict[str, str]],
) -> list:
    """Build the message list for the LLM call.

    Args:
        user_message: The current user message.
        history: Previous conversation messages [{"role": "user"|"assistant", "content": str}].

    Returns:
        List of LangChain message objects.
    """
    messages = [SystemMessage(content=SYSTEM_PROMPT)]

    # Add conversation history
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    # Add the current user message
    messages.append(HumanMessage(content=user_message))

    return messages


# ── Cost Calculation ────────────────────────────────────────────────

def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
    """Calculate estimated cost based on DeepSeek pricing.

    Args:
        prompt_tokens: Number of input tokens.
        completion_tokens: Number of output tokens.

    Returns:
        Estimated cost in USD.
    """
    input_cost = (prompt_tokens / 1_000_000) * settings.COST_PER_1M_INPUT_TOKENS
    output_cost = (completion_tokens / 1_000_000) * settings.COST_PER_1M_OUTPUT_TOKENS
    return round(input_cost + output_cost, 8)


# ── Main Chat Function ─────────────────────────────────────────────

async def get_chat_response(
    user_message: str,
    history: list[dict[str, str]],
    session_id: str = None,
) -> tuple[str, ResponseMetadata]:
    """Generate a chat response using the DeepSeek LLM.

    This function:
    1. Builds the message list from history + current message
    2. Invokes the LLM (LangSmith traces this automatically)
    3. Extracts token usage and calculates cost
    4. Returns the response text and metadata

    Args:
        user_message: The user's current message.
        history: Conversation history for context.

    Returns:
        Tuple of (response_text, response_metadata)

    Raises:
        Exception: If the LLM call fails.
    """
    model = get_llm()
    messages = build_messages(user_message, history)
    config = {"configurable": {"session_id": session_id}} if session_id else {}

    # Time the LLM call
    start_time = time.time()
    response = await model.ainvoke(messages, config=config)
    latency = time.time() - start_time

    # Extract token usage from response
    token_usage = TokenUsage()
    if response.usage_metadata:
        token_usage = TokenUsage(
            prompt_tokens=response.usage_metadata.get("input_tokens", 0),
            completion_tokens=response.usage_metadata.get("output_tokens", 0),
            total_tokens=response.usage_metadata.get("total_tokens", 0),
        )

    # Calculate cost
    cost = calculate_cost(token_usage.prompt_tokens, token_usage.completion_tokens)

    metadata = ResponseMetadata(
        model=settings.MODEL_NAME,
        latency_seconds=round(latency, 4),
        token_usage=token_usage,
        estimated_cost_usd=cost,
    )

    logger.info(
        "LLM response generated | model=%s | latency=%.2fs | tokens=%d | cost=$%.6f",
        settings.MODEL_NAME,
        latency,
        token_usage.total_tokens,
        cost,
    )

    return response.content, metadata


async def get_chat_response_stream(
    user_message: str,
    history: list[dict[str, str]],
    session_id: str = None,
):
    """Generate a streaming chat response using the DeepSeek LLM.
    
    Yields chunks of text as they arrive, and finally yields the full
    metadata and accumulated text for the caller to record metrics.
    """
    import json
    model = get_llm()
    messages = build_messages(user_message, history)

    start_time = time.time()
    full_text = ""
    token_usage = TokenUsage()
    config = {"configurable": {"session_id": session_id}} if session_id else {}

    # We pass stream_options={"include_usage": True} so the final chunk 
    # contains the token counts (supported by DeepSeek/OpenAI APIs)
    async for chunk in model.astream(messages, stream_options={"include_usage": True}, config=config):
        if chunk.content:
            # chunk.content might be a string or a list (for multimodal), usually string here
            text = chunk.content if isinstance(chunk.content, str) else str(chunk.content)
            full_text += text
            yield {"type": "chunk", "text": text}

        # Check for usage metadata in the final chunk
        if hasattr(chunk, "usage_metadata") and chunk.usage_metadata:
            token_usage = TokenUsage(
                prompt_tokens=chunk.usage_metadata.get("input_tokens", 0),
                completion_tokens=chunk.usage_metadata.get("output_tokens", 0),
                total_tokens=chunk.usage_metadata.get("total_tokens", 0),
            )

    latency = time.time() - start_time
    
    # Fallback: if include_usage didn't work, estimate tokens (1 token ~ 4 chars)
    if token_usage.total_tokens == 0:
        est_prompt = sum(len(m.content) for m in messages) // 4
        est_completion = len(full_text) // 4
        token_usage = TokenUsage(
            prompt_tokens=est_prompt,
            completion_tokens=est_completion,
            total_tokens=est_prompt + est_completion
        )

    cost = calculate_cost(token_usage.prompt_tokens, token_usage.completion_tokens)

    metadata = ResponseMetadata(
        model=settings.MODEL_NAME,
        latency_seconds=round(latency, 4),
        token_usage=token_usage,
        estimated_cost_usd=cost,
    )

    logger.info(
        "LLM stream finished | latency=%.2fs | tokens=%d",
        latency, token_usage.total_tokens
    )

    yield {"type": "metadata", "metadata": metadata.model_dump(), "full_text": full_text}
