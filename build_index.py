from data.loader import load_dataset_records
from embeddings.indexer import build_index

if __name__ == "__main__":
    print("Loading dataset...")
    df = load_dataset_records()
    print(f"Loaded {len(df)} records.")
    print("Building FAISS index...")
    index, metadata, embeddings = build_index(df)
    print(f"Done. Indexed {index.ntotal} documents.")