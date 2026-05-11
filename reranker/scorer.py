from collections import Counter
from config import SEMANTIC_WEIGHT, PERSONALIZATION_WEIGHT


def _get_dominant_category(user_profile: dict) -> str | None:
    clicks = user_profile.get("category_clicks", {})
    if not clicks:
        return None
    return max(clicks, key=clicks.get)


def rerank(results: list, user_profile: dict) -> list:
    dominant = _get_dominant_category(user_profile)

    if dominant is None:
        for r in results:
            r["personalization_score"] = r["semantic_score"]
            r["personalization_boost"] = 0.0
        return results

    clicked_ids = set(user_profile.get("clicked_ids", []))

    ranked = []
    for item in results:
        boost = 0.0
        if item["category"] == dominant:
            boost += 0.8
        if item["id"] in clicked_ids:
            boost += 0.2

        boost = min(boost, 1.0)
        final_score = SEMANTIC_WEIGHT * item["semantic_score"] + PERSONALIZATION_WEIGHT * boost

        item = item.copy()
        item["personalization_boost"] = round(boost, 4)
        item["personalization_score"] = round(final_score, 4)
        ranked.append(item)

    ranked.sort(key=lambda x: x["personalization_score"], reverse=True)
    return ranked