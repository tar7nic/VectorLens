import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from config import MODEL_NAME, TOP_K


_model = None


def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def search(query: str, index, metadata: list, embeddings: np.ndarray, top_k: int = TOP_K):
    model = _get_model()
    query_vec = model.encode([query], normalize_embeddings=True).astype("float32")

    _, indices = index.search(query_vec, top_k)

    results = []
    for rank, idx in enumerate(indices[0]):
        item = metadata[idx].copy()
        doc_vec = embeddings[idx].reshape(1, -1)
        score = float(cosine_similarity(query_vec, doc_vec)[0][0])
        item["semantic_score"] = round(score, 4)
        item["rank"] = rank + 1
        results.append(item)

    return results