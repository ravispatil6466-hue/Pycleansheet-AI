"""
eda.py
------
Exploratory Data Analysis page: summary stats, correlation, outlier
report, missing value report, categorical / numerical analysis, and
a lightweight feature-importance view.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff

from src.chatbot import generate_ai_summary


def render(df: pd.DataFrame):
    st.markdown('<div class="pcs-title">🔬 Exploratory Data Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Summary statistics, correlation, distributions, and AI-generated insights.</div>', unsafe_allow_html=True)

    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    tabs = st.tabs([
        "Summary Statistics", "Correlation", "Missing Value Report",
        "Outlier Report", "Categorical Analysis", "Numerical Analysis",
        "Feature Importance", "AI Summary",
    ])

    with tabs[0]:
        st.subheader("Summary Statistics")
        st.dataframe(df.describe(include="all").transpose(), use_container_width=True)
        st.markdown("**Data Types**")
        st.dataframe(df.dtypes.astype(str).rename("dtype").to_frame(), use_container_width=True)

    with tabs[1]:
        st.subheader("Correlation Matrix")
        if len(num_cols) < 2:
            st.info("Need at least two numeric columns for correlation analysis.")
        else:
            corr = df[num_cols].corr(numeric_only=True)
            fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", aspect="auto",
                             title="Correlation Heatmap")
            fig.update_layout(template="plotly_dark", height=520)
            st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.subheader("Missing Value Report")
        na = df.isna().sum()
        na_pct = (na / len(df) * 100).round(2)
        report = pd.DataFrame({"missing_count": na, "missing_pct": na_pct}).sort_values("missing_count", ascending=False)
        st.dataframe(report, use_container_width=True)
        if report["missing_count"].sum() > 0:
            fig = px.bar(report[report.missing_count > 0].reset_index(), x="index", y="missing_pct",
                         title="Missing Value % by Column", labels={"index": "Column"})
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No missing values in this dataset.")

    with tabs[3]:
        st.subheader("Outlier Report (IQR method)")
        if not num_cols:
            st.info("No numeric columns available.")
        else:
            rows = []
            for col in num_cols:
                q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                iqr = q3 - q1
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                n_out = int(((df[col] < lower) | (df[col] > upper)).sum())
                rows.append({"column": col, "lower_bound": lower, "upper_bound": upper, "outlier_count": n_out})
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

    with tabs[4]:
        st.subheader("Categorical Analysis")
        if not cat_cols:
            st.info("No categorical columns available.")
        else:
            col = st.selectbox("Select categorical column", cat_cols)
            vc = df[col].value_counts().head(20).reset_index()
            vc.columns = [col, "count"]
            fig = px.bar(vc, x=col, y="count", title=f"Top values in {col}", color="count", color_continuous_scale="Purples")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(vc, use_container_width=True)

    with tabs[5]:
        st.subheader("Numerical Analysis")
        if not num_cols:
            st.info("No numeric columns available.")
        else:
            col = st.selectbox("Select numeric column", num_cols, key="num_analysis_col")
            fig = px.histogram(df, x=col, marginal="box", title=f"Distribution of {col}", nbins=40)
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            st.write(df[col].describe().to_frame().T)

    with tabs[6]:
        st.subheader("Feature Importance (variance-based proxy)")
        if len(num_cols) < 2:
            st.info("Need at least two numeric columns.")
        else:
            variances = df[num_cols].var(numeric_only=True).sort_values(ascending=False)
            fig = px.bar(variances.reset_index(), x="index", y=0 if 0 in variances.reset_index().columns else variances.name,
                         title="Relative Feature Variance (proxy for importance without a target)")
            st.caption("For true model-based importance, select a target column in the Python Editor and train a model (e.g. RandomForestRegressor/Classifier).")
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    with tabs[7]:
        st.subheader("AI-Generated Dataset Summary")
        if st.button("🤖 Generate AI Summary", use_container_width=True):
            with st.spinner("Analyzing dataset..."):
                summary = generate_ai_summary(df)
            st.markdown(summary)
