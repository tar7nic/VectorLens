import requests
from eval.metrics import evaluate_results

SAMPLE_QUERIES = [
    {"query": "football world cup results", "relevant_category": "Sports"},
    {"query": "stock market crash economy", "relevant_category": "Business"},
    {"query": "nasa space mission launch", "relevant_category": "Sci/Tech"},
    {"query": "election president government", "relevant_category": "World"},
    {"query": "NBA basketball championship", "relevant_category": "Sports"},
]

CATEGORY_MAP = {0: "World", 1: "Sports", 2: "Business", 3: "Sci/Tech"}


def run_evaluation(api_base="http://localhost:8000"):
    eval_results = []

    for item in SAMPLE_QUERIES:
        query = item["query"]
        relevant_category = item["relevant_category"]

        resp = requests.get(f"{api_base}/search", params={"q": query})
        if resp.status_code != 200:
            continue

        raw = resp.json().get("results", [])
        for r in raw:
            r["category"] = CATEGORY_MAP.get(r.get("category"), str(r.get("category")))

        semantic_metrics = evaluate_results(raw, relevant_category)

        rerank_resp = requests.post(f"{api_base}/rerank", json={
            "query": query,
            "user_profile": {
                "clicked_categories": {relevant_category: 5},
                "clicked_ids": []
            }
        })

        reranked = []
        if rerank_resp.status_code == 200:
            reranked = rerank_resp.json().get("results", [])
            for r in reranked:
                r["category"] = CATEGORY_MAP.get(r.get("category"), str(r.get("category")))

        personalized_metrics = evaluate_results(reranked, relevant_category) if reranked else semantic_metrics

        eval_results.append({
            "query": query,
            "relevant_category": relevant_category,
            "semantic": semantic_metrics,
            "personalized": personalized_metrics,
        })

    return eval_results