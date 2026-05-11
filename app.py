import time
import streamlit as st
import httpx
from config import API_BASE_URL, CATEGORY_MAP

st.set_page_config(
    page_title="Semantic Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .result-card {
        padding: 16px 20px;
        border: 1px solid #2d2d2d;
        border-radius: 12px;
        margin-bottom: 12px;
        background: #1a1a1a;
        transition: border-color 0.2s;
    }
    .result-card:hover { border-color: #555; }
    .category-badge {
        display: inline-block;
        padding: 2px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }
    .score-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 12px;
        background: #2a2a2a;
        color: #aaa;
        margin-right: 8px;
    }
    .boost-pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 8px;
        font-size: 12px;
        background: #1a3a1a;
        color: #4ade80;
        margin-right: 8px;
    }
    .rank-num {
        font-size: 28px;
        font-weight: 800;
        color: #333;
        line-height: 1;
    }
    .article-title {
        font-size: 15px;
        font-weight: 600;
        color: #f0f0f0;
        margin: 6px 0;
        line-height: 1.4;
    }
    .article-snippet {
        font-size: 12px;
        color: #888;
        margin-top: 4px;
        line-height: 1.5;
    }
    .metric-box {
        background: #1a1a1a;
        border: 1px solid #2d2d2d;
        border-radius: 10px;
        padding: 14px 18px;
        text-align: center;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #fff;
    }
    .metric-label {
        font-size: 11px;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 2px;
    }
    .sidebar-history-item {
        font-size: 12px;
        padding: 5px 10px;
        margin: 3px 0;
        border-radius: 6px;
        background: #1a1a1a;
        border-left: 3px solid;
        color: #ccc;
    }
    .filter-bar {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
        flex-wrap: wrap;
    }
    div[data-testid="stButton"] button {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

CATEGORY_COLORS = {
    "World":   "#3B82F6",
    "Sports":  "#10B981",
    "Business":"#F59E0B",
    "Sci/Tech":"#8B5CF6",
}

# ── Session State Init ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "user_profile": {"category_clicks": {}, "clicked_ids": [], "history": []},
        "results": [],
        "last_query": "",
        "response_time": None,
        "total_indexed": None,
        "active_filter": "All",
        "search_count": 0,
        "query_times": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_reranked(query, user_profile):
    try:
        r = httpx.post(
            f"{API_BASE_URL}/rerank",
            json={"query": query, "user_profile": user_profile},
            timeout=30,
        )
        data = r.json()
        return data.get("results", []), data.get("response_time_ms"), data.get("total_indexed")
    except Exception as e:
        st.error(f"API error: {e}")
        return [], None, None


def record_click(item):
    profile = st.session_state.user_profile
    cat = item["category"]
    profile["category_clicks"][cat] = profile["category_clicks"].get(cat, 0) + 1
    if item["id"] not in profile["clicked_ids"]:
        profile["clicked_ids"].append(item["id"])
    profile["history"].append({"title": item["title"], "category": cat})


def dominant_category():
    clicks = st.session_state.user_profile.get("category_clicks", {})
    return max(clicks, key=clicks.get) if clicks else None


def avg_query_time():
    times = st.session_state.query_times
    return round(sum(times) / len(times), 1) if times else None


def get_filtered_results():
    results = st.session_state.results
    f = st.session_state.active_filter
    if f == "All":
        return results
    return [r for r in results if r["category"] == f]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👤 Your Profile")
    st.divider()

    dom = dominant_category()
    if dom:
        color = CATEGORY_COLORS.get(dom, "#6B7280")
        st.markdown(
            f"**Dominant Interest**<br>"
            f"<span style='background:{color};color:white;padding:3px 14px;"
            f"border-radius:20px;font-size:13px;font-weight:700'>{dom}</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("**Dominant Interest**")
        st.caption("🧊 Cold start — click results to build your profile")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**Category Breakdown**")
    clicks = st.session_state.user_profile["category_clicks"]
    total_clicks = sum(clicks.values()) or 1
    for cat, cnt in sorted(clicks.items(), key=lambda x: -x[1]):
        color = CATEGORY_COLORS.get(cat, "#6B7280")
        pct = int(cnt / total_clicks * 100)
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"margin:5px 0'>"
            f"<span style='background:{color};color:white;padding:1px 10px;"
            f"border-radius:12px;font-size:12px'>{cat}</span>"
            f"<span style='color:#aaa;font-size:12px'>{cnt} clicks · {pct}%</span>"
            f"</div>"
            f"<div style='background:#2d2d2d;border-radius:4px;height:4px;margin-bottom:6px'>"
            f"<div style='background:{color};width:{pct}%;height:4px;border-radius:4px'></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    if not clicks:
        st.caption("No clicks recorded yet.")

    st.divider()
    st.markdown("**Recent Clicks**")
    history = st.session_state.user_profile["history"][-10:][::-1]
    if history:
        for h in history:
            color = CATEGORY_COLORS.get(h["category"], "#6B7280")
            st.markdown(
                f"<div class='sidebar-history-item' style='border-left-color:{color}'>"
                f"{h['title'][:55]}{'...' if len(h['title'])>55 else ''}"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.caption("Nothing yet.")

    st.divider()
    st.markdown("**Session Stats**")
    st.markdown(
        f"<div style='font-size:13px;color:#aaa'>"
        f"🔍 Searches: <strong style='color:#fff'>{st.session_state.search_count}</strong><br>"
        f"👆 Total Clicks: <strong style='color:#fff'>{sum(clicks.values())}</strong><br>"
        f"⚡ Avg Query Time: <strong style='color:#fff'>"
        f"{'—' if not st.session_state.query_times else str(avg_query_time()) + ' ms'}"
        f"</strong></div>",
        unsafe_allow_html=True,
    )

    st.divider()
    if st.button("🗑 Reset Session", use_container_width=True):
        for k in ["user_profile", "results", "last_query", "response_time",
                  "total_indexed", "active_filter", "search_count", "query_times"]:
            del st.session_state[k]
        st.rerun()


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🔍 Semantic Search Engine")
st.markdown("*Powered by sentence-transformers · FAISS · Personalized Re-ranking*")
st.divider()

# ── Metrics Row ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
metrics = [
    ("📚", "Docs Indexed", str(st.session_state.total_indexed or "—")),
    ("⚡", "Last Query", f"{st.session_state.response_time} ms" if st.session_state.response_time else "—"),
    ("📊", "Avg Query Time", f"{avg_query_time()} ms" if st.session_state.query_times else "—"),
    ("🏷", "Top Category", dominant_category() or "None yet"),
]
for col, (icon, label, val) in zip([c1, c2, c3, c4], metrics):
    with col:
        st.markdown(
            f"<div class='metric-box'>"
            f"<div style='font-size:20px'>{icon}</div>"
            f"<div class='metric-value'>{val}</div>"
            f"<div class='metric-label'>{label}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Search Bar ────────────────────────────────────────────────────────────────
col_input, col_btn = st.columns([5, 1])
with col_input:
    query = st.text_input(
        "",
        placeholder="e.g. SpaceX rocket launch, stock market crash, NBA playoffs...",
        label_visibility="collapsed",
        key="search_input",
    )
with col_btn:
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    search_clicked = st.button("Search →", type="primary", use_container_width=True)

if search_clicked and query.strip():
    with st.spinner("Encoding query and searching..."):
        results, rt, total = fetch_reranked(query.strip(), st.session_state.user_profile)
        st.session_state.results = results
        st.session_state.last_query = query.strip()
        st.session_state.response_time = rt
        st.session_state.active_filter = "All"
        st.session_state.search_count += 1
        if rt:
            st.session_state.query_times.append(rt)
        if total:
            st.session_state.total_indexed = total

# ── Filter Bar ────────────────────────────────────────────────────────────────
if st.session_state.results:
    st.markdown("<br>", unsafe_allow_html=True)
    present_cats = list(dict.fromkeys(r["category"] for r in st.session_state.results))
    filter_options = ["All"] + present_cats

    st.markdown("**Filter by category:**")
    filter_cols = st.columns(len(filter_options))
    for i, opt in enumerate(filter_options):
        with filter_cols[i]:
            active = st.session_state.active_filter == opt
            color = CATEGORY_COLORS.get(opt, "#555")
            btn_style = f"background:{color}" if active else ""
            if st.button(
                f"{'✓ ' if active else ''}{opt}",
                key=f"filter_{opt}",
                use_container_width=True,
            ):
                st.session_state.active_filter = opt
                st.rerun()

# ── Results ───────────────────────────────────────────────────────────────────
filtered = get_filtered_results()

if filtered:
    has_boost = any(r.get("personalization_boost", 0) > 0 for r in filtered)
    mode = "🎯 Personalized re-ranking active" if has_boost else "🧊 Cold start — semantic only"
    st.markdown(f"<br>**{len(filtered)} results** for `{st.session_state.last_query}` &nbsp;·&nbsp; {mode}", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    for i, item in enumerate(filtered):
        cat = item["category"]
        color = CATEGORY_COLORS.get(cat, "#6B7280")
        sem   = item.get("semantic_score", 0)
        pers  = item.get("personalization_score", sem)
        boost = item.get("personalization_boost", 0)
        snippet = item.get("text", "")[:160] + "..."

        col_rank, col_content, col_action = st.columns([1, 10, 2])

        with col_rank:
            st.markdown(
                f"<div style='text-align:center;padding-top:16px'>"
                f"<span class='rank-num'>#{i+1}</span></div>",
                unsafe_allow_html=True,
            )

        with col_content:
            boost_html = (
                f"<span class='boost-pill'>🚀 +{boost:.2f} boost</span>"
                if boost > 0 else ""
            )
            st.markdown(
                f"<div class='result-card'>"
                f"<div style='margin-bottom:8px'>"
                f"<span class='category-badge' style='background:{color};color:white'>{cat}</span>"
                f"</div>"
                f"<div class='article-title'>{item['title']}</div>"
                f"<div class='article-snippet'>{snippet}</div>"
                f"<div style='margin-top:10px'>"
                f"<span class='score-pill'>🎯 Semantic {sem:.3f}</span>"
                f"<span class='score-pill'>⭐ Final {pers:.3f}</span>"
                f"{boost_html}"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

        with col_action:
            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
            already = item["id"] in st.session_state.user_profile["clicked_ids"]
            btn_label = "✓ Clicked" if already else "👆 Click"
            if st.button(btn_label, key=f"click_{i}_{item['id']}", use_container_width=True, disabled=already):
                record_click(item)
                results_fresh, rt, _ = fetch_reranked(
                    st.session_state.last_query,
                    st.session_state.user_profile,
                )
                st.session_state.results = results_fresh
                if rt:
                    st.session_state.response_time = rt
                    st.session_state.query_times.append(rt)
                st.rerun()

elif st.session_state.last_query:
    st.warning("No results found for this filter. Try 'All'.")
else:
    st.markdown(
        "<div style='text-align:center;padding:80px 0;color:#444'>"
        "<div style='font-size:48px'>🔍</div>"
        "<div style='font-size:16px;margin-top:12px'>Enter a query above to search 5,000 news articles</div>"
        "<div style='font-size:13px;margin-top:6px;color:#333'>Try: SpaceX · NBA Finals · Apple earnings · Climate change</div>"
        "</div>",
        unsafe_allow_html=True,
    )