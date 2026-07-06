# 🤖 AI Conversational Chatbot — Observability Platform

A production-oriented **AI Career Mentor** chatbot built to demonstrate how to monitor, debug, and operate LLM applications in production. The focus is not on building the smartest chatbot — it is on understanding what happens *after* you deploy one.

> **Core idea:** Anyone can call an LLM API. The hard part is knowing when it's slow, why it's giving bad answers, and how much it's costing you.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User / Browser                        │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP / SSE
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Application (Port 8000)             │
│                                                             │
│   GET  /              → Chat UI (HTML)                      │
│   POST /chat/stream   → SSE Streaming Chat Endpoint         │
│   GET  /dashboard     → Monitoring Dashboard (HTML)         │
│   GET  /api/metrics   → Raw Metrics JSON                    │
│   GET  /health        → Health Check                        │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐      ┌───────────────────────────────┐
│  ConversationManager │      │         MetricsStore          │
│  (In-Memory)         │      │  (In-Memory + metrics.json)   │
│                      │      │                               │
│  • session_id → msgs │      │  • Latency (P50/P95/P99)      │
│  • history trim      │      │  • Token usage & cost         │
│  • active count      │      │  • Error counts by type       │
└──────────┬───────────┘      │  • Per-minute timeline        │
           │                  │  • Rolling request log        │
           ▼                  └───────────────────────────────┘
┌──────────────────────┐
│  LangChain           │      ┌───────────────────────────────┐
│  ChatOpenAI          │─────▶│         LangSmith             │
│  (DeepSeek API)      │      │  (Cloud Tracing - Automatic)  │
│  astream() / SSE     │      │                               │
└──────────────────────┘      │  • Full prompt per call       │
                              │  • Exact response & tokens    │
                              │  • Latency per call           │
                              │  • Grouped by session Thread  │
                              └───────────────────────────────┘
```

**Key design decisions:**
- **Single process:** Everything runs inside one FastAPI server — no Docker, no external services, no Prometheus agents.
- **Two observability layers:** The built-in dashboard answers "is my system healthy?" (aggregate). LangSmith answers "what exactly did the LLM do on this specific request?" (per-call trace).
- **SSE Streaming:** Responses are streamed token-by-token so the user sees text as it's generated, not after a 10-second wait.
- **Metrics persist across restarts:** The metrics store saves to `data/metrics.json` on every request, so the dashboard retains history even after restarting the server.

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| 💬 **Streaming Chat UI** | Real-time SSE-based chat where tokens appear character-by-character as the LLM generates them |
| 📊 **Monitoring Dashboard** | Built-in live dashboard tracking latency percentiles, token usage, cost, and error rates at the **application level** (sessions, uptime, request log) |
| 🔍 **LangSmith Tracing & Monitoring** | Every LLM call is traced with full prompt, response, token usage, and latency. LangSmith also has its own **Monitoring tab** with aggregate charts — complementing the custom dashboard rather than replacing it |
| 💾 **Metrics Persistence** | Metrics survive server restarts via `data/metrics.json` — the dashboard doesn't reset to zero on every deploy |
| 🔒 **Thread-Safe Metrics** | `threading.Lock()` ensures concurrent requests don't corrupt shared metric counters |

---

## 🚀 Setup Guide

### 1. Prerequisites
- Python 3.10+
- [DeepSeek API Key](https://platform.deepseek.com/) — the LLM provider
- [LangSmith API Key](https://smith.langchain.com/) — free, for prompt tracing

### 2. Installation
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Environment Setup
Copy `.env.example` to `.env` and fill in your keys:
```env
DEEPSEEK_API_KEY=sk-your-deepseek-key
LANGCHAIN_API_KEY=lsv2_pt_your-langsmith-key
```
> LangSmith is optional. Set `LANGCHAIN_TRACING_V2=false` to disable tracing if you just want to run the chatbot locally.

---

## ▶️ Running

```bash
uvicorn app.main:app --reload --port 8000
```

| Endpoint | What it does |
|---|---|
| 💬 [localhost:8000/](http://localhost:8000/) | Chat UI — send messages, see streaming responses |
| 📊 [localhost:8000/dashboard](http://localhost:8000/dashboard) | Live monitoring dashboard |
| 📝 [localhost:8000/docs](http://localhost:8000/docs) | Swagger UI for testing the API directly |
| 📈 [localhost:8000/api/metrics](http://localhost:8000/api/metrics) | Raw JSON metrics consumed by the dashboard |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI + Uvicorn (async Python) |
| **LLM Framework** | LangChain (ChatOpenAI interface) |
| **LLM Provider** | DeepSeek V3 (OpenAI-compatible API) |
| **LLM Tracing** | LangSmith (automatic, cloud-based) |
| **Metrics & Dashboard** | Custom in-memory store + HTML/JS/CSS |
| **Streaming** | Server-Sent Events (SSE) via FastAPI StreamingResponse |

---

## 📁 Project Structure

```
LANGSMITH_MONITORING_TRACEABILITY/
├── app/
│   ├── main.py          # All FastAPI routes
│   ├── chain.py         # LangChain + DeepSeek + streaming logic
│   ├── metrics.py       # In-memory metrics store (replaces Prometheus)
│   ├── conversation.py  # Session & chat history manager
│   ├── dashboard.py     # Monitoring dashboard HTML
│   ├── chat_ui.py       # Chat interface HTML
│   ├── config.py        # Settings from .env (Pydantic)
│   └── schemas.py       # Request/response models
├── docs/
│   └── learning.md      # Deep-dive concepts and metrics reference
├── data/
│   └── metrics.json     # Persisted metrics (auto-generated)
├── .env.example         # Environment variable template
└── requirements.txt     # Python dependencies
```

> 📖 **Learning Notes:** All key concepts behind this project — LLM observability, streaming, metrics design, cost tracking, and architecture decisions — are documented in [`docs/learning.md`](./docs/learning.md).
