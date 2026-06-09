# Financial Research Agent 📈

An Agentic RAG system that analyzes stocks and produces investment reports
using LangGraph, Groq, Tavily search, and yfinance.

## Tech Stack
- **LLM:** Llama 3.3 70B via Groq (free)
- **Embeddings:** all-MiniLM-L6-v2 (local)
- **Vector DB:** ChromaDB (in-memory)
- **Agent framework:** LangGraph (ReAct loop)
- **News search:** Tavily API
- **Financial data:** yfinance
- **Deployment:** FastAPI on Render

## Setup
1. Clone the repo
2. Install: `pip install -r requirements.txt`
3. Add keys to `.env`: `GROQ_API_KEY` and `TAVILY_API_KEY`
4. Run locally: `uvicorn app:app --reload`
5. POST to `/analyze` with `{"query": "Analyze NVIDIA", "ticker": "NVDA"}`

## Deploy on Render
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`