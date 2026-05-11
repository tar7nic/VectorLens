import pickle
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from config import MODEL_NAME, EMBEDDING_DIM, FAISS_INDEX_PATH, METADATA_PATH


def build_index(df):
    model = SentenceTransformer(MODEL_NAME)
    texts = df["text"].tolist()

    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(embeddings)

    FAISS_INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(FAISS_INDEX_PATH))

    metadata = df[["id", "title", "category", "category_id", "text"]].to_dict(orient="records")
    with open(METADATA_PATH, "wb") as f:
        pickle.dump({"metadata": metadata, "embeddings": embeddings}, f)

    return index, metadata, embeddings


def load_index():
    index = faiss.read_index(str(FAISS_INDEX_PATH))
    with open(METADATA_PATH, "rb") as f:
        stored = pickle.load(f)
    return index, stored["metadata"], stored["embeddings"]