import streamlit as st
import httpx
import json
from config import API_BASE_URL

st.set_page_config(page_title="API Explorer", page_icon="⚡", layout="wide")

st.markdown("# ⚡ API Explorer")
st.markdown("Test the FastAPI backend endpoints directly from the browser.")
st.divider()

tab1, tab2, tab3 = st.tabs(["GET /health", "GET /search", "POST /rerank"])

with tab1:
    st.markdown("### Health Check")
    st.code(f"GET {API_BASE_URL}/health", language="bash")
    if st.button("Run", key="health"):
        try:
            r = httpx.get(f"{API_BASE_URL}/health", timeout=10)
            st.json(r.json())
        except Exception as e:
            st.error(str(e))

with tab2:
    st.markdown("### Semantic Search")
    q = st.text_input("Query", value="SpaceX rocket launch", key="search_q")
    st.code(f"GET {API_BASE_URL}/search?q={q}", language="bash")
    if st.button("Run", key="search_run"):
        try:
            r = httpx.get(f"{API_BASE_URL}/search", params={"q": q}, timeout=30)
            data = r.json()
            st.markdown(f"**Response time:** {data.get('response_time_ms')} ms · "
                        f"**Results:** {len(data.get('results', []))}")
            st.json(data)
        except Exception as e:
            st.error(str(e))

with tab3:
    st.markdown("### Re-rank with User Profile")
    q2 = st.text_input("Query", value="championship game", key="rerank_q")
    profile_json = st.text_area(
        "User Profile (JSON)",
        value='{"category_clicks": {"Sports": 5, "World": 1}, "clicked_ids": []}',
        height=100,
    )
    if st.button("Run", key="rerank_run"):
        try:
            profile = json.loads(profile_json)
            r = httpx.post(
                f"{API_BASE_URL}/rerank",
                json={"query": q2, "user_profile": profile},
                timeout=30,
            )
            data = r.json()
            st.markdown(f"**Response time:** {data.get('response_time_ms')} ms")
            st.json(data)
        except Exception as e:
            st.error(str(e))