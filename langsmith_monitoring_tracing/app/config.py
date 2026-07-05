import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # ── LLM Configuration ──────────────────────────────────────────
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = ""
    MODEL_NAME: str = "deepseek-chat"  # deepseek-chat (V3) or deepseek-reasoner (R1)

    # ── LangSmith Tracing ──────────────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = ""
    LANGCHAIN_ENDPOINT: str = "

    # ── Application ────────────────────────────────────────────────
    APP_NAME: str = "AI Career Mentor"
    APP_HOST: str = ""
    APP_PORT: int = 
    MAX_CONVERSATION_HISTORY: int = 20  # Max messages to keep per session
    SESSION_TIMEOUT_MINUTES: int = 60   # Auto-expire inactive sessions

    # ── Cost Tracking (per 1M tokens) ─────────────────────────────
    # DeepSeek V3 pricing (cache miss) — update if pricing changes
    COST_PER_1M_INPUT_TOKENS: float = 0.27
    COST_PER_1M_OUTPUT_TOKENS: float = 1.10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def configure_langsmith_env(self) -> None:
        """Set LangSmith environment variables for automatic tracing."""
        os.environ["LANGCHAIN_TRACING_V2"] = str(self.LANGCHAIN_TRACING_V2).lower()
        os.environ["LANGCHAIN_API_KEY"] = self.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = self.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = self.LANGCHAIN_ENDPOINT


settings = Settings()
