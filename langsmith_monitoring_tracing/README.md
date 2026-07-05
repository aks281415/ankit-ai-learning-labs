# 🤖 AI Conversational Chatbot — Observability Platform

A simplified, production-oriented **AI Career Mentor** chatbot featuring a **built-in real-time monitoring dashboard** and **LangSmith LLM tracing**.

---

## 🌟 Key Features

1. **Real-Time Chat Interface (`/`)**: A sleek UI with Server-Sent Events (SSE) streaming for character-by-character responses.
2. **Monitoring Dashboard (`/dashboard`)**: Built-in HTML/JS dashboard tracking latency, tokens, costs, and request volume. Survives server restarts via `data/metrics.json`.
3. **LangSmith Integration**: Full prompt tracing, token analytics, and cost tracking. Chat turns are properly grouped into Threads via Session IDs.
4. **All-in-One Architecture**: Runs entirely from a single FastAPI server. No external databases, Prometheus, or Grafana required.

---

## 🚀 Setup Guide

### 1. Prerequisites
- Python 3.10+
- [DeepSeek API Key](https://platform.deepseek.com/)
- [LangSmith API Key](https://smith.langchain.com/) (Free)

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
*(Note: LangSmith tracing can be disabled by setting `LANGCHAIN_TRACING_V2=false` if you just want to run the bot locally.)*

---

## ▶️ Running the Application

Run the server with a single command:
```bash
uvicorn app.main:app --reload --port 8000
```

### Available Endpoints
| Feature | URL |
|---------|-----|
| 💬 **Chatbot UI** | [http://localhost:8000/](http://localhost:8000/) |
| 📊 **Dashboard** | [http://localhost:8000/dashboard](http://localhost:8000/dashboard) |
| 📝 **Swagger API** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| 📈 **Raw Metrics** | [http://localhost:8000/api/metrics](http://localhost:8000/api/metrics) |

---

## 🛠 Tech Stack

- **Backend:** FastAPI, Python, Uvicorn
- **AI/LLM:** LangChain, DeepSeek API
- **Observability:** LangSmith (Tracing), Custom Built-in UI (Metrics)
