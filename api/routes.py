import time
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.query_log import init_db, log_query
from embeddings import load_index, search
from reranker import rerank
from data import load_dataset_records
from embeddings.indexer import build_index
from config import FAISS_INDEX_PATH, METADATA_PATH

app = FastAPI(title="Semantic Search API", version="1.0.0")
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_index = None
_metadata = None
_embeddings = None


def _get_resources():
    global _index, _metadata, _embeddings
    if _index is None:
        if FAISS_INDEX_PATH.exists() and METADATA_PATH.exists():
            _index, _metadata, _embeddings = load_index()
        else:
            df = load_dataset_records()
            _index, _metadata, _embeddings = build_index(df)
    return _index, _metadata, _embeddings


class RerankRequest(BaseModel):
    query: str
    user_profile: dict


@app.get("/health")
def health():
    idx, meta, _ = _get_resources()
    return {"status": "ok", "indexed_docs": idx.ntotal}


@app.get("/search")
def search_endpoint(q: str = Query(..., min_length=1)):
    start = time.time()
    idx, meta, emb = _get_resources()
    results = search(q, idx, meta, emb)
    elapsed_ms = round((time.time() - start) * 1000, 2)
    top_category = results[0]["category"] if results else "unknown"
    log_query(q, str(top_category), elapsed_ms)
    return {
        "query": q,
        "results": results,
        "response_time_ms": elapsed_ms,
        "total_indexed": idx.ntotal,
    }

@app.post("/rerank")
def rerank_endpoint(body: RerankRequest):
    start = time.time()
    idx, meta, emb = _get_resources()
    raw_results = search(body.query, idx, meta, emb)
    reranked = rerank(raw_results, body.user_profile)
    elapsed_ms = round((time.time() - start) * 1000, 2)
    top_category = reranked[0]["category"] if reranked else "unknown"
    log_query(body.query, str(top_category), elapsed_ms)
    return {
        "query": body.query,
        "results": reranked,
        "response_time_ms": elapsed_ms,
    }