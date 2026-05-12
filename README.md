# 🔍 Semantic Search Engine with Personalization

A full-stack semantic search system built with Python that combines dense vector search (FAISS) with a real-time personalization layer. Users get results ranked by meaning — not keywords — and the engine adapts to their interests as they interact.

---

## 🧠 How It Works

1. **Offline:** 5,000 AG News articles are encoded into 384-dim vectors using `all-MiniLM-L6-v2` and stored in a FAISS index.
2. **At query time:** The user's query is encoded and the top-10 nearest neighbors are retrieved via L2 distance (≈ cosine similarity on normalized vectors).
3. **Re-ranking:** Results are re-scored using the user's click history: `final = 0.7 × semantic + 0.3 × personalization_boost`.
4. **Cold start:** No boost applied — raw semantic scores returned until the user clicks.

---

## 🏗 Architecture

```
User Query
    │
    ▼
[Streamlit UI] ──────────────────────────────────────────────┐
    │  POST /rerank                                           │
    ▼                                                         │
[FastAPI Backend]                                             │
    │                                                         │
    ├── GET /health        → index status                     │
    ├── GET /search        → raw FAISS results + query log    │
    └── POST /rerank       → personalized re-ranked results   │
            │                                                 │
            ▼                                                 │
    [FAISS IndexFlatL2]                                       │
    5000 docs × 384 dims                                      │
            │                                                 │
            ▼                                                 │
    [Reranker / Scorer]                                       │
    0.7 × semantic + 0.3 × boost                              │
            │                                                 │
            ▼                                                 │
    [SQLite Query Log] ←─────────────────────────────────────┘
```

---

## 📁 Project Structure

| Path | Description |
|------|-------------|
| `app.py` | Streamlit frontend — search, results, session profile |
| `build_index.py` | One-time script to build FAISS index + metadata |
| `config.py` | All constants — paths, weights, model name |
| `data/loader.py` | AG News dataset loader (5,000 records) |
| `embeddings/indexer.py` | FAISS index builder and loader |
| `embeddings/searcher.py` | Query encoder + top-10 FAISS search |
| `reranker/scorer.py` | Personalization re-ranking logic |
| `api/routes.py` | FastAPI — `/health`, `/search`, `/rerank` |
| `evaluation/metrics.py` | Precision@K and NDCG@K computation |
| `evaluation/evaluator.py` | Runs 5 sample queries, compares semantic vs personalized |
| `utils/export.py` | Results → CSV, profile → JSON, JSON → profile |
| `utils/query_log.py` | SQLite logger — query, category, response time, timestamp |
| `pages/1_Analytics.py` | Session analytics — category bar chart, query time line chart |
| `pages/2_API_Explorer.py` | Live API testing UI for all 3 endpoints |
| `pages/3_Evaluation.py` | IR metrics dashboard — P@5, P@10, NDCG@10 before/after |
| `pages/4_Export.py` | CSV export, profile save/load, query log viewer |

---

## ⚙️ Setup Instructions

### 1. Clone and create virtual environment

```bash
git clone https://github.com/yourusername/semantic-search-personalization.git
cd semantic-search-personalization

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the FAISS index

```bash
python build_index.py
```

This downloads AG News (~5000 records), encodes all articles, and saves:
- `embeddings/faiss.index`
- `embeddings/metadata.pkl`

Takes ~2–5 minutes on first run.

### 4. Start FastAPI backend

```bash
uvicorn api.routes:app --reload --port 8000
```

Verify: `http://localhost:8000/health` → `{"status": "ok", "indexed_docs": 5000}`

### 5. Start Streamlit frontend

```bash
streamlit run app.py
```

Open: `http://localhost:8501`

> Both terminals must stay open simultaneously.

---

## 🐳 Docker Setup (optional)

```bash
docker-compose up --build
```

- FastAPI → `http://localhost:8000`
- Streamlit → `http://localhost:8501`

---

## 🔢 Personalization Formula

| Component | Weight | Description |
|-----------|--------|-------------|
| Semantic score | 0.7 | Cosine similarity from FAISS |
| Personalization boost | 0.3 | Category match + click history |
| **Final score** | — | `0.7 × semantic + 0.3 × boost` |

**Boost values:**
- `+0.8` if article category matches dominant user category
- `+0.2` if article ID was previously clicked
- Capped at `1.0`

---

## 📊 Evaluation Results

| Metric  | Semantic Only | Personalized | Delta |
|---------|--------------|--------------|-------|
| P@5     | 0.84         | 0.84         | 0.0   |
| P@10    | 0.86         | 0.86         | 0.0   |
| NDCG@10 | 0.94         | 0.94         | 0.0   |

*Evaluated on 5 sample queries with known relevant categories. Run live via the Evaluation page.*

Add this below the evaluation table in README:

**Note:** Delta is 0.0 because the semantic model already retrieves the correct category 
with high precision — leaving no room for the personalization layer to improve rankings. 
Non-zero deltas appear when a user has built a real session profile (3+ clicks across mixed 
categories) and searches ambiguous queries where multiple categories are plausible — 
the boost then surfaces preferred-category results that semantic scoring alone would rank lower.

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

| Test File | What It Tests |
|-----------|--------------|
| `tests/test_search.py` | FAISS returns 10 results with correct keys |
| `tests/test_reranker.py` | Cold start, category boost, clicked ID boost |
| `tests/test_api.py` | All 3 FastAPI endpoints via async test client |

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `sentence-transformers` | `all-MiniLM-L6-v2` embeddings |
| `faiss-cpu` | Vector similarity search |
| `datasets` | AG News dataset loader |
| `fastapi` + `uvicorn` | REST API backend |
| `streamlit` | Interactive frontend |
| `httpx` | Async HTTP client (tests + UI) |
| `sqlite3` | Built-in query logging |

---

## 🗂 Dataset

**AG News** (via Hugging Face `datasets`)
- 4 categories: `World`, `Sports`, `Business`, `Sci/Tech`
- 120,000 total articles — 5,000 used for speed
- Train split, no labels required for search

---

## 📌 Notes

- `embeddings/faiss.index` and `embeddings/metadata.pkl` are excluded from git (regenerate with `build_index.py`)
- `query_log.db` is excluded from git (auto-created at runtime)
- All constants live in `config.py` — never hardcoded in modules
- Session state resets on browser refresh — use Export page to persist profiles