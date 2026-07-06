"""
In-memory metrics store and analytics engine.

Replaces Prometheus — tracks all the same metrics but stores them
in Python data structures for the built-in dashboard.

Tracks:
    - Request counts (success/error)
    - Latency (with percentile calculations)
    - Token usage (prompt/completion)
    - Cost accumulation
    - Active sessions
    - Per-request log (last 100 requests)
"""

import time
import threading
import json
import os
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
from typing import Optional


@dataclass
class RequestLog:
    """A single request's observability data."""
    timestamp: datetime
    session_id: str
    message_preview: str
    latency_seconds: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    status: str  # "success" or "error"
    error_type: Optional[str] = None


class MetricsStore:
    """Thread-safe in-memory metrics store.

    Provides the same observability as Prometheus but without
    any external dependencies. Data lives in memory and resets
    on app restart (which is fine for learning).
    """

    def __init__(self, max_log_size: int = 100) -> None:
        self._lock = threading.Lock()

        # ── Counters ────────────────────────────────────────────
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        self.error_counts: dict[str, int] = {}  # error_type → count

        # ── Token & Cost ────────────────────────────────────────
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.total_cost_usd: float = 0.0

        # ── Latency Tracking ────────────────────────────────────
        self._latencies: list[float] = []  # all latencies for percentile calc

        # ── Session Tracking ────────────────────────────────────
        self.active_sessions: int = 0

        # ── Request Log (rolling window) ────────────────────────
        self.request_log: deque[RequestLog] = deque(maxlen=max_log_size)

        # ── Timeline (per-minute aggregates) ────────────────────
        self._minute_buckets: dict[str, dict] = {}  # "HH:MM" → {requests, errors, tokens, cost, latencies}

        # ── Start Time ──────────────────────────────────────────
        self.start_time: datetime = datetime.now()

        # ── Persistence ─────────────────────────────────────────
        self.data_dir = "data"
        self.metrics_file = os.path.join(self.data_dir, "metrics.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self.load_from_disk()

    # ── Recording Methods ───────────────────────────────────────

    def record_success(
        self,
        session_id: str,
        message: str,
        latency: float,
        prompt_tokens: int,
        completion_tokens: int,
        cost: float,
    ) -> None:
        """Record a successful request with all its metrics."""
        with self._lock:
            self.total_requests += 1
            self.successful_requests += 1
            self.total_prompt_tokens += prompt_tokens
            self.total_completion_tokens += completion_tokens
            self.total_cost_usd += cost
            self._latencies.append(latency)

            log = RequestLog(
                timestamp=datetime.now(),
                session_id=session_id,
                message_preview=message[:80] + ("..." if len(message) > 80 else ""),
                latency_seconds=round(latency, 3),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                cost_usd=round(cost, 8),
                status="success",
            )
            self.request_log.append(log)
            self._record_minute_bucket(log)
            self.save_to_disk()

    def record_error(self, session_id: str, message: str, error_type: str) -> None:
        """Record a failed request."""
        with self._lock:
            self.total_requests += 1
            self.failed_requests += 1
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

            log = RequestLog(
                timestamp=datetime.now(),
                session_id=session_id,
                message_preview=message[:80] + ("..." if len(message) > 80 else ""),
                latency_seconds=0,
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                cost_usd=0,
                status="error",
                error_type=error_type,
            )
            self.request_log.append(log)
            self._record_minute_bucket(log)
            self.save_to_disk()

    def set_active_sessions(self, count: int) -> None:
        """Update the active session count."""
        with self._lock:
            self.active_sessions = count

    # ── Query Methods ───────────────────────────────────────────

    def get_dashboard_data(self) -> dict:
        """Get all metrics formatted for the dashboard.

        Returns a single dict with everything the dashboard needs.
        """
        with self._lock:
            latencies = sorted(self._latencies) if self._latencies else []

            return {
                # Overview
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "start_time": self.start_time.isoformat(),

                # Request counts
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "error_rate_pct": round(
                    (self.failed_requests / self.total_requests * 100)
                    if self.total_requests > 0 else 0, 2
                ),
                "error_counts": dict(self.error_counts),

                # Latency
                "avg_latency": round(
                    sum(latencies) / len(latencies) if latencies else 0, 3
                ),
                "p50_latency": self._percentile(latencies, 50),
                "p95_latency": self._percentile(latencies, 95),
                "p99_latency": self._percentile(latencies, 99),
                "min_latency": round(latencies[0], 3) if latencies else 0,
                "max_latency": round(latencies[-1], 3) if latencies else 0,

                # Tokens
                "total_prompt_tokens": self.total_prompt_tokens,
                "total_completion_tokens": self.total_completion_tokens,
                "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
                "avg_tokens_per_request": round(
                    (self.total_prompt_tokens + self.total_completion_tokens) / self.successful_requests
                    if self.successful_requests > 0 else 0
                ),

                # Cost
                "total_cost_usd": round(self.total_cost_usd, 6),
                "avg_cost_per_request": round(
                    self.total_cost_usd / self.successful_requests
                    if self.successful_requests > 0 else 0, 6
                ),

                # Sessions
                "active_sessions": self.active_sessions,

                # Recent requests (newest first)
                "recent_requests": [
                    {
                        "timestamp": r.timestamp.strftime("%H:%M:%S"),
                        "session_id": r.session_id[:8] + "...",
                        "message": r.message_preview,
                        "latency": r.latency_seconds,
                        "tokens": r.total_tokens,
                        "cost": f"${r.cost_usd:.6f}",
                        "status": r.status,
                        "error_type": r.error_type,
                    }
                    for r in reversed(self.request_log)
                ],

                # Timeline data (for charts)
                "timeline": self._get_timeline_data(),
            }

    # ── Internal Helpers ────────────────────────────────────────

    @staticmethod
    def _percentile(sorted_data: list[float], pct: int) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0
        idx = int(len(sorted_data) * pct / 100)
        idx = min(idx, len(sorted_data) - 1)
        return round(sorted_data[idx], 3)

    def _record_minute_bucket(self, log: RequestLog) -> None:
        """Aggregate request data into per-minute buckets for timeline charts."""
        key = log.timestamp.strftime("%H:%M")
        if key not in self._minute_buckets:
            self._minute_buckets[key] = {
                "time": key,
                "requests": 0,
                "errors": 0,
                "tokens": 0,
                "cost": 0.0,
                "latencies": [],
            }
        bucket = self._minute_buckets[key]
        bucket["requests"] += 1
        if log.status == "error":
            bucket["errors"] += 1
        bucket["tokens"] += log.total_tokens
        bucket["cost"] += log.cost_usd
        if log.latency_seconds > 0:
            bucket["latencies"].append(log.latency_seconds)

    def _get_timeline_data(self) -> list[dict]:
        """Get per-minute aggregated data for timeline charts."""
        timeline = []
        for key in sorted(self._minute_buckets.keys())[-30:]:  # Last 30 minutes
            bucket = self._minute_buckets[key]
            lats = bucket["latencies"]
            timeline.append({
                "time": bucket["time"],
                "requests": bucket["requests"],
                "errors": bucket["errors"],
                "tokens": bucket["tokens"],
                "cost": round(bucket["cost"], 6),
                "avg_latency": round(sum(lats) / len(lats), 3) if lats else 0,
            })
        return timeline

    # ── Persistence Helpers ─────────────────────────────────────

    def save_to_disk(self) -> None:
        """Save current metrics to a JSON file."""
        data = {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "error_counts": self.error_counts,
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_cost_usd": self.total_cost_usd,
            "_latencies": self._latencies,
            "_minute_buckets": self._minute_buckets,
            "request_log": [
                {**dataclasses.asdict(log), "timestamp": log.timestamp.isoformat()}
                for log in self.request_log
            ],
        }
        try:
            with open(self.metrics_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save metrics: {e}")

    def load_from_disk(self) -> None:
        """Load metrics from a JSON file if it exists."""
        if not os.path.exists(self.metrics_file):
            return
            
        try:
            with open(self.metrics_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self.total_requests = data.get("total_requests", 0)
            self.successful_requests = data.get("successful_requests", 0)
            self.failed_requests = data.get("failed_requests", 0)
            self.error_counts = data.get("error_counts", {})
            self.total_prompt_tokens = data.get("total_prompt_tokens", 0)
            self.total_completion_tokens = data.get("total_completion_tokens", 0)
            self.total_cost_usd = data.get("total_cost_usd", 0.0)
            self._latencies = data.get("_latencies", [])
            self._minute_buckets = data.get("_minute_buckets", {})
            
            # Reconstruct RequestLog objects
            self.request_log.clear()
            for log_data in data.get("request_log", []):
                log_data["timestamp"] = datetime.fromisoformat(log_data["timestamp"])
                self.request_log.append(RequestLog(**log_data))
                
        except Exception as e:
            print(f"Failed to load metrics: {e}")



# Singleton instance
metrics_store = MetricsStore()
