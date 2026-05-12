import pytest
from httpx import AsyncClient, ASGITransport
from api.routes import app

@pytest.mark.anyio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

@pytest.mark.anyio
async def test_search_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/search", params={"q": "football"})
    assert r.status_code == 200
    data = r.json()
    assert "results" in data
    assert len(data["results"]) == 10

@pytest.mark.anyio
async def test_rerank_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.post("/rerank", json={
            "query": "space exploration",
            "user_profile": {"category_clicks": {"Sci/Tech": 3}, "clicked_ids": []}
        })
    assert r.status_code == 200
    assert "results" in r.json()