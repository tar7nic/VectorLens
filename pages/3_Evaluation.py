import streamlit as st
import pandas as pd
from eval.evaluator import run_evaluation

st.set_page_config(page_title="Evaluation", page_icon="📊", layout="wide")
st.title("📊 Evaluation — Precision & NDCG")

st.markdown("Runs 5 sample queries against the live API and computes IR metrics.")

if st.button("▶ Run Evaluation", type="primary"):
    with st.spinner("Running evaluation against localhost:8000 ..."):
        try:
            results = run_evaluation()
            st.success(f"Evaluated {len(results)} queries")

            rows = []
            for r in results:
                rows.append({
                    "Query": r["query"],
                    "Category": r["relevant_category"],
                    "Semantic P@5": round(r["semantic"]["precision_at_5"], 3),
                    "Personalized P@5": round(r["personalized"]["precision_at_5"], 3),
                    "Semantic P@10": round(r["semantic"]["precision_at_10"], 3),
                    "Personalized P@10": round(r["personalized"]["precision_at_10"], 3),
                    "Semantic NDCG@10": round(r["semantic"]["ndcg_at_10"], 3),
                    "Personalized NDCG@10": round(r["personalized"]["ndcg_at_10"], 3),
                })

            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True)

            st.subheader("Average Scores")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("Semantic P@5", round(df["Semantic P@5"].mean(), 3))
            col2.metric("Personalized P@5", round(df["Personalized P@5"].mean(), 3),
                        delta=round(df["Personalized P@5"].mean() - df["Semantic P@5"].mean(), 3))
            col3.metric("Semantic P@10", round(df["Semantic P@10"].mean(), 3))
            col4.metric("Personalized P@10", round(df["Personalized P@10"].mean(), 3),
                        delta=round(df["Personalized P@10"].mean() - df["Semantic P@10"].mean(), 3))
            col5.metric("Semantic NDCG@10", round(df["Semantic NDCG@10"].mean(), 3))
            col6.metric("Personalized NDCG@10", round(df["Personalized NDCG@10"].mean(), 3),
                        delta=round(df["Personalized NDCG@10"].mean() - df["Semantic NDCG@10"].mean(), 3))

            st.subheader("Before vs After Personalization")
            chart_df = pd.DataFrame({
                "Semantic": [r["semantic"]["ndcg_at_10"] for r in results],
                "Personalized": [r["personalized"]["ndcg_at_10"] for r in results],
            }, index=[r["query"][:30] + "..." for r in results])
            st.bar_chart(chart_df)

        except Exception as e:
            st.error(f"Error: {e}. Make sure FastAPI is running on localhost:8000.")
else:
    st.info("Click **Run Evaluation** to start. FastAPI must be running on localhost:8000.")