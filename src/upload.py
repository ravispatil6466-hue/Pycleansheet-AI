"""
upload.py
---------
Dataset upload page: CSV / Excel / JSON ingestion, quick preview, and
KPI overview immediately after upload.
"""

import streamlit as st
import pandas as pd

from src import state as S
from src.components import render_kpi_row


def _read_file(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    if name.endswith(".json"):
        return pd.read_json(uploaded_file)
    raise ValueError("Unsupported file type. Please upload CSV, Excel, or JSON.")


def render():
    st.markdown('<div class="pcs-title">📁 Upload Dataset</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Upload CSV, Excel, or JSON to begin cleaning, analyzing and visualizing.</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drag & drop or browse", type=["csv", "xlsx", "xls", "json"])
    sample = st.checkbox("Or load a bundled sample dataset instead")
    st.markdown('</div>', unsafe_allow_html=True)

    if sample:
        import numpy as np
        rng = np.random.default_rng(42)
        n = 500
        df = pd.DataFrame({
            "order_id": range(1, n + 1),
            "order_date": rng.choice(pd.date_range("2024-01-01", periods=365, freq="D"), n),
            "city": rng.choice(["Bengaluru", "Mumbai", "Delhi", "Chennai", "Pune", "Hyderabad"], n),
            "category": rng.choice(["Electronics", "Apparel", "Home", "Grocery", "Beauty"], n),
            "units_sold": rng.integers(1, 50, n),
            "unit_price": rng.uniform(50, 2500, n).round(2),
            "customer_age": rng.integers(18, 70, n),
            "rating": rng.uniform(1, 5, n).round(1),
        })
        df["revenue"] = (df["units_sold"] * df["unit_price"]).round(2)
        # inject some missing values and duplicates for realism
        df.loc[rng.choice(n, 15, replace=False), "rating"] = None
        df = pd.concat([df, df.sample(5, random_state=1)], ignore_index=True)
        S.set_dataframe(df, name="sample_retail_sales.csv")
        st.success("Sample dataset loaded: sample_retail_sales.csv")

    elif uploaded_file is not None:
        try:
            df = _read_file(uploaded_file)
            S.set_dataframe(df, name=uploaded_file.name)
            st.success(f"Loaded **{uploaded_file.name}** — {df.shape[0]:,} rows × {df.shape[1]} columns")
        except Exception as e:
            st.error(f"Could not read file: {e}")

    if st.session_state.df is not None:
        st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)
        render_kpi_row(st.session_state.df)
        st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)
        st.subheader("Preview")
        st.dataframe(st.session_state.df.head(50), use_container_width=True)
