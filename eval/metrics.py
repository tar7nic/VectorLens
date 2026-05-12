import numpy as np

def precision_at_k(results, relevant_category, k):
    top_k = results[:k]
    hits = sum(1 for r in top_k if r["category"] == relevant_category)
    return hits / k


def dcg_at_k(results, relevant_category, k):
    top_k = results[:k]
    dcg = 0.0
    for i, r in enumerate(top_k):
        rel = 1 if r["category"] == relevant_category else 0
        dcg += rel / np.log2(i + 2)
    return dcg


def ndcg_at_k(results, relevant_category, k):
    actual_dcg = dcg_at_k(results, relevant_category, k)
    ideal_hits = min(k, sum(1 for r in results if r["category"] == relevant_category))
    ideal_dcg = sum(1 / np.log2(i + 2) for i in range(ideal_hits))
    if ideal_dcg == 0:
        return 0.0
    return actual_dcg / ideal_dcg


def evaluate_results(results, relevant_category):
    return {
        "precision_at_5": precision_at_k(results, relevant_category, 5),
        "precision_at_10": precision_at_k(results, relevant_category, 10),
        "ndcg_at_10": ndcg_at_k(results, relevant_category, 10),
    }