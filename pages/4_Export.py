import streamlit as st
import json
import pandas as pd
from utils.export import results_to_csv, profile_to_json, json_to_profile
from utils.query_log import get_recent_logs, init_db

st.set_page_config(page_title="Export & Persistence", page_icon="💾", layout="wide")
st.title("💾 Export & Persistence")

init_db()

tab1, tab2, tab3 = st.tabs(["📁 Search Results Export", "👤 Profile Save / Load", "🗃️ Query Log"])

with tab1:
    st.subheader("Export Last Search Results to CSV")
    results = st.session_state.get("last_results", [])
    if results:
        csv_data = results_to_csv(results)
        st.download_button(
            label="⬇ Download Results as CSV",
            data=csv_data,
            file_name="search_results.csv",
            mime="text/csv",
        )
        df = pd.DataFrame(results)
        display_cols = [c for c in ["title", "category", "semantic_score", "final_score"] if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)
    else:
        st.info("No search results in session yet. Run a search on the main page first.")

with tab2:
    st.subheader("Save Current Profile")
    profile = st.session_state.get("user_profile", {})
    if profile:
        json_str = profile_to_json(profile)
        st.download_button(
            label="⬇ Download Profile as JSON",
            data=json_str,
            file_name="user_profile.json",
            mime="application/json",
        )
        st.code(json_str, language="json")
    else:
        st.info("No profile data yet. Interact with search results first.")

    st.divider()
    st.subheader("Import Profile")
    uploaded = st.file_uploader("Upload a previously saved profile JSON", type=["json"])
    if uploaded:
        try:
            loaded_profile = json_to_profile(uploaded.read().decode("utf-8"))
            st.session_state["user_profile"] = loaded_profile
            st.success("Profile loaded into session!")
            st.json(loaded_profile)
        except Exception as e:
            st.error(f"Invalid JSON: {e}")

with tab3:
    st.subheader("Persistent Query Log (SQLite)")
    logs = get_recent_logs(50)
    if logs:
        df_log = pd.DataFrame(logs)
        df_log["timestamp"] = pd.to_datetime(df_log["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
        df_log["response_time_ms"] = df_log["response_time_ms"].round(2)
        st.dataframe(df_log, use_container_width=True)

        csv_log = df_log.to_csv(index=False)
        st.download_button(
            label="⬇ Download Query Log as CSV",
            data=csv_log,
            file_name="query_log.csv",
            mime="text/csv",
        )
    else:
        st.info("No queries logged yet. Run searches via the API to populate this log.")