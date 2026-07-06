"""
In-memory conversation state manager.

Stores conversation history per session, tracks session lifecycle,
and maintains the active_conversations gauge for Prometheus.
"""

import uuid
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from typing import Optional

from app.config import settings


class ConversationStateManager:
    """Manages multi-turn conversation state in memory.

    Each session stores:
        - messages: list of {"role": "user"|"assistant", "content": str}
        - created_at: session creation timestamp
        - last_active: last interaction timestamp
        - message_count: total messages exchanged
    """

    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    # ── Session Lifecycle ───────────────────────────────────────────

    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """Get an existing session or create a new one.

        Args:
            session_id: Optional existing session ID. If None, creates new.

        Returns:
            The session ID (existing or newly generated).
        """
        if session_id and session_id in self._sessions:
            return session_id

        new_id = session_id or str(uuid.uuid4())
        self._sessions[new_id] = {
            "messages": [],
            "created_at": datetime.now(),
            "last_active": datetime.now(),
            "message_count": 0,
        }
        return new_id

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and its history.

        Returns:
            True if session existed and was deleted, False otherwise.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    # ── Message Management ──────────────────────────────────────────

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add a message to the session history.

        Args:
            session_id: The session to add the message to.
            role: Either "user" or "assistant".
            content: The message content.
        """
        if session_id not in self._sessions:
            self.get_or_create_session(session_id)

        session = self._sessions[session_id]
        session["messages"].append({"role": role, "content": content})
        session["last_active"] = datetime.now()
        session["message_count"] += 1

        # Trim history to prevent unbounded memory growth
        max_messages = settings.MAX_CONVERSATION_HISTORY
        if len(session["messages"]) > max_messages:
            session["messages"] = session["messages"][-max_messages:]

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        """Get the conversation history for a session.

        Returns:
            List of message dicts with 'role' and 'content' keys.
            Returns empty list if session doesn't exist.
        """
        if session_id not in self._sessions:
            return []
        return list(self._sessions[session_id]["messages"])

    def get_message_count(self, session_id: str) -> int:
        """Get the total message count for a session."""
        if session_id not in self._sessions:
            return 0
        return self._sessions[session_id]["message_count"]

    # ── Session Queries ─────────────────────────────────────────────

    def list_sessions(self) -> list[dict]:
        """List all active sessions with summary info.

        Returns:
            List of dicts with session_id, message_count, created_at, last_active.
        """
        return [
            {
                "session_id": sid,
                "message_count": data["message_count"],
                "created_at": data["created_at"],
                "last_active": data["last_active"],
            }
            for sid, data in self._sessions.items()
        ]

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get detailed info for a specific session."""
        if session_id not in self._sessions:
            return None
        data = self._sessions[session_id]
        return {
            "session_id": session_id,
            "message_count": data["message_count"],
            "created_at": data["created_at"],
            "last_active": data["last_active"],
            "messages": list(data["messages"]),
        }

    @property
    def active_count(self) -> int:
        """Number of currently active sessions."""
        return len(self._sessions)

    # ── Cleanup ─────────────────────────────────────────────────────

    def cleanup_expired_sessions(self) -> int:
        """Remove sessions that have been inactive longer than the timeout.

        Returns:
            Number of sessions removed.
        """
        timeout = timedelta(minutes=settings.SESSION_TIMEOUT_MINUTES)
        now = datetime.now()
        expired = [
            sid
            for sid, data in self._sessions.items()
            if now - data["last_active"] > timeout
        ]
        for sid in expired:
            del self._sessions[sid]

        return len(expired)



# Singleton instance used across the application
conversation_manager = ConversationStateManager()
