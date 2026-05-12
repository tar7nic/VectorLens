import pytest
from embeddings.indexer import load_index
from embeddings.searcher import search
from config import FAISS_INDEX_PATH, METADATA_PATH
import pickle

@pytest.fixture
def resources():
    idx = load_index(FAISS_INDEX_PATH)
    with open(METADATA_PATH, "rb") as f:
        meta = pickle.load(f)
    from sentence_transformers import SentenceTransformer
    from config import MODEL_NAME
    emb = SentenceTransformer(MODEL_NAME)
    return idx, meta, emb

def test_search_returns_10_results(resources):
    idx, meta, emb = resources
    results = search("technology news", idx, meta, emb)
    assert len(results) == 10

def test_search_result_keys(resources):
    idx, meta, emb = resources
    results = search("sports championship", idx, meta, emb)
    for r in results:
        assert "title" in r
        assert "category" in r
        assert "semantic_score" in r