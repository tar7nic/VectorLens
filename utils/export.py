import csv
import json
import io


def results_to_csv(results: list[dict]) -> str:
    if not results:
        return ""
    output = io.StringIO()
    fields = ["rank", "title", "category", "semantic_score", "final_score"]
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    for i, r in enumerate(results, 1):
        writer.writerow({**r, "rank": i})
    return output.getvalue()


def profile_to_json(user_profile: dict) -> str:
    return json.dumps(user_profile, indent=2)


def json_to_profile(json_str: str) -> dict:
    return json.loads(json_str)