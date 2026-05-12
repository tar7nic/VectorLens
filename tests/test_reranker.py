from reranker.scorer import rerank

MOCK_RESULTS = [
    {"id": 1, "title": "NBA Finals", "category": "Sports", "semantic_score": 0.9, "text": ""},
    {"id": 2, "title": "Stock crash", "category": "Business", "semantic_score": 0.8, "text": ""},
    {"id": 3, "title": "SpaceX launch", "category": "Sci/Tech", "semantic_score": 0.7, "text": ""},
]

def test_cold_start_no_boost():
    profile = {"category_clicks": {}, "clicked_ids": []}
    results = rerank(MOCK_RESULTS, profile)
    for r in results:
        assert r["personalization_boost"] == 0

def test_dominant_category_boosted():
    profile = {"category_clicks": {"Sports": 5}, "clicked_ids": []}
    results = rerank(MOCK_RESULTS, profile)
    sports = next(r for r in results if r["category"] == "Sports")
    others = [r for r in results if r["category"] != "Sports"]
    assert sports["personalization_boost"] > 0
    assert all(r["personalization_boost"] == 0 for r in others)

def test_clicked_id_boosted():
    profile = {"category_clicks": {}, "clicked_ids": [2]}
    results = rerank(MOCK_RESULTS, profile)
    clicked = next(r for r in results if r["id"] == 2)
    assert clicked["personalization_boost"] > 0