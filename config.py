from pathlib import Path

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
EMBEDDINGS_DIR = BASE_DIR / "embeddings"

DATASET_NAME = "ag_news"
DATASET_SPLIT = "train"
DATASET_SIZE = 5000

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

FAISS_INDEX_PATH = EMBEDDINGS_DIR / "faiss.index"
METADATA_PATH = EMBEDDINGS_DIR / "metadata.pkl"

TOP_K = 10
SEMANTIC_WEIGHT = 0.7
PERSONALIZATION_WEIGHT = 0.3

CATEGORY_MAP = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}

API_HOST = "127.0.0.1"
API_PORT = 8000
API_BASE_URL = "http://127.0.0.1:8000"