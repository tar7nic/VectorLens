# Semantic Search Engine with Personalization

A full-stack semantic search system combining dense vector retrieval with
session-based personalized re-ranking.

## Architecture
┌─────────────────────────────────────────────────────┐
│                   Streamlit UI                       │
│  app.py · pages/Analytics · pages/API Explorer      │
└────────────────────┬────────────────────────────────┘
│ HTTP (httpx)
▼
┌─────────────────────────────────────────────────────┐
│               FastAPI Backend (:8000)                │
│  GET /health · GET /search · POST /rerank            │
└──────┬────────────────────────────┬─────────────────┘
│                            │
▼                            ▼
┌─────────────┐            ┌────────────────┐
│ Sentence-   │            │  Re-ranker     │
│ BERT Encoder│            │  scorer.py     │
│ MiniLM-L6   │            │  0.7s + 0.3p   │
└──────┬──────┘            └───────┬────────┘
│ query vector              │ boosted scores
▼                           │
┌─────────────┐                    │
│ FAISS Index │────top-10─────────►│
│ IndexFlatL2 │                    │
│ 5000 docs   │                    │
└─────────────┘                    │
▼
┌────────────────┐
│  User Profile  │
│ session state  │
│ category_clicks│
└────────────────┘

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt

python build_index.py          # One-time index build (~5 min)

# Terminal 1
uvicorn api.routes:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2
streamlit run app.py
```

## Project Structure
semantic-search-personalization/
├── data/
│   ├── init.py
│   └── loader.py          # HuggingFace AG News loader
├── embeddings/
│   ├── init.py
│   ├── indexer.py         # FAISS index build + load
│   └── searcher.py        # Query encoding + FAISS search
├── reranker/
│   ├── init.py
│   └── scorer.py          # Personalization scoring
├── api/
│   ├── init.py
│   └── routes.py          # FastAPI endpoints
├── pages/
│   ├── 1_Analytics.py     # Session analytics dashboard
│   └── 2_API_Explorer.py  # Live API testing UI
├── app.py                 # Main Streamlit frontend
├── build_index.py         # One-time index builder
├── config.py              # All constants
├── requirements.txt
├── .gitignore
└── README.md

## How Personalization Works

| Phase        | Score Formula                          |
|--------------|----------------------------------------|
| Cold start   | `final = semantic_score`               |
| After clicks | `final = 0.7 × sem + 0.3 × boost`     |
| Boost value  | `+0.8` if category matches dominant    |
|              | `+0.2` if article ID already clicked   |

## Sample Queries

- `SpaceX rocket launch` → Sci/Tech results
- `NBA playoffs championship` → Sports results  
- `Federal Reserve interest rates` → Business results
- `UN Security Council meeting` → World results

Click Sports results → re-search `championship` → Sports articles jump to #1.