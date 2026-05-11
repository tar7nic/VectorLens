import pandas as pd
from datasets import load_dataset
from config import DATASET_NAME, DATASET_SPLIT, DATASET_SIZE, CATEGORY_MAP


def load_dataset_records() -> pd.DataFrame:
    raw = load_dataset(DATASET_NAME, split=DATASET_SPLIT)
    subset = raw.select(range(DATASET_SIZE))

    records = []
    for idx, item in enumerate(subset):
        records.append({
            "id": idx,
            "title": item["text"].split(".")[0][:120],
            "text": item["text"],
            "category_id": item["label"],
            "category": CATEGORY_MAP[item["label"]],
        })

    return pd.DataFrame(records)