import streamlit as st
import pandas as pd

st.set_page_config(page_title="Analytics", page_icon="📊", layout="wide")

st.markdown("# 📊 Session Analytics")
st.divider()

if "user_profile" not in st.session_state or not st.session_state.user_profile["history"]:
    st.info("No session data yet. Go to the main page, search, and click some results first.")
    st.stop()

profile  = st.session_state.user_profile
history  = profile["history"]
clicks   = profile["category_clicks"]
times    = st.session_state.get("query_times", [])

CATEGORY_COLORS = {
    "World":   "#3B82F6",
    "Sports":  "#10B981",
    "Business":"#F59E0B",
    "Sci/Tech":"#8B5CF6",
}

# ── Top metrics ───────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Clicks",     sum(clicks.values()))
c2.metric("Unique Articles",  len(profile["clicked_ids"]))
c3.metric("Total Searches",   st.session_state.get("search_count", 0))
c4.metric("Avg Query Time",
          f"{round(sum(times)/len(times),1)} ms" if times else "—")

st.divider()

col_left, col_right = st.columns(2)

# ── Click distribution ────────────────────────────────────────────────────────
with col_left:
    st.markdown("### Category Click Distribution")
    if clicks:
        df_clicks = pd.DataFrame(
            list(clicks.items()), columns=["Category", "Clicks"]
        ).sort_values("Clicks", ascending=False)
        st.bar_chart(df_clicks.set_index("Category"))
    else:
        st.caption("No clicks yet.")

# ── Query time trend ──────────────────────────────────────────────────────────
with col_right:
    st.markdown("### Query Response Time Trend (ms)")
    if times:
        df_times = pd.DataFrame({"Query #": range(1, len(times)+1), "Response Time (ms)": times})
        st.line_chart(df_times.set_index("Query #"))
    else:
        st.caption("No queries yet.")

st.divider()

# ── Click history table ───────────────────────────────────────────────────────
st.markdown("### Full Click History")
if history:
    df_hist = pd.DataFrame(history)
    df_hist.index += 1
    df_hist.columns = ["Article Title", "Category"]
    st.dataframe(df_hist, use_container_width=True)
else:
    st.caption("No history yet.")

# ── Personalization insight ───────────────────────────────────────────────────
st.divider()
st.markdown("### Personalization Insight")
if clicks:
    dom = max(clicks, key=clicks.get)
    total = sum(clicks.values())
    pct = round(clicks[dom] / total * 100)
    color = CATEGORY_COLORS.get(dom, "#6B7280")
    st.markdown(
        f"The re-ranker is currently boosting **{dom}** articles "
        f"(representing **{pct}%** of your clicks). "
        f"Articles in this category receive a **+0.8 personalization boost**, "
        f"shifting their final score from pure semantic similarity "
        f"toward your demonstrated interests.",
    )
    st.progress(pct / 100)