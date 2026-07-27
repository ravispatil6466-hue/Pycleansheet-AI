"""
cleaning.py
-----------
Data Cleaning page: missing values, duplicates, outliers, whitespace,
renaming, dtype conversion, standardization, undo/redo, cleaning history.
"""

import streamlit as st
import pandas as pd
import numpy as np

from src import state as S


def render(df: pd.DataFrame):
    st.markdown('<div class="pcs-title">🧹 Data Cleaning Studio</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Clean, transform and standardize your dataset with full undo/redo history.</div>', unsafe_allow_html=True)

    top = st.columns([1, 1, 1, 3])
    with top[0]:
        if st.button("↩️ Undo", use_container_width=True, disabled=not st.session_state.history):
            S.undo()
            st.rerun()
    with top[1]:
        if st.button("↪️ Redo", use_container_width=True, disabled=not st.session_state.future):
            S.redo()
            st.rerun()
    with top[2]:
        if st.button("🔄 Reset Dataset", use_container_width=True):
            S.reset_dataset()
            st.rerun()

    st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)

    tabs = st.tabs([
        "Missing Values", "Duplicates", "Outliers", "Text & Whitespace",
        "Rename & Types", "Preprocessing", "Cleaning History",
    ])

    # ---------------- Missing values ----------------
    with tabs[0]:
        st.subheader("Missing Values")
        na_summary = df.isna().sum()
        na_summary = na_summary[na_summary > 0]
        if na_summary.empty:
            st.success("No missing values detected. 🎉")
        else:
            st.dataframe(na_summary.rename("Missing Count").to_frame(), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ Remove Rows with Missing Values", use_container_width=True):
                S.push_undo_snapshot("Removed rows with missing values")
                st.session_state.df = st.session_state.df.dropna()
                st.rerun()
        with c2:
            method = st.selectbox("Fill method", ["Mean", "Median", "Mode", "Zero", "Custom Value", "Forward Fill", "Backward Fill"])
            custom_val = None
            if method == "Custom Value":
                custom_val = st.text_input("Custom fill value", "0")
            if st.button("🧴 Fill Missing Values", use_container_width=True):
                S.push_undo_snapshot(f"Filled missing values ({method})")
                new_df = st.session_state.df.copy()
                for col in new_df.columns:
                    if new_df[col].isna().sum() == 0:
                        continue
                    if method == "Mean" and pd.api.types.is_numeric_dtype(new_df[col]):
                        new_df[col] = new_df[col].fillna(new_df[col].mean())
                    elif method == "Median" and pd.api.types.is_numeric_dtype(new_df[col]):
                        new_df[col] = new_df[col].fillna(new_df[col].median())
                    elif method == "Mode":
                        m = new_df[col].mode()
                        if not m.empty:
                            new_df[col] = new_df[col].fillna(m.iloc[0])
                    elif method == "Zero":
                        new_df[col] = new_df[col].fillna(0)
                    elif method == "Custom Value":
                        new_df[col] = new_df[col].fillna(custom_val)
                    elif method == "Forward Fill":
                        new_df[col] = new_df[col].ffill()
                    elif method == "Backward Fill":
                        new_df[col] = new_df[col].bfill()
                st.session_state.df = new_df
                st.rerun()

    # ---------------- Duplicates ----------------
    with tabs[1]:
        st.subheader("Duplicate Records")
        dup_count = df.duplicated().sum()
        st.metric("Duplicate Rows", int(dup_count))
        if dup_count > 0:
            st.dataframe(df[df.duplicated(keep=False)].head(50), use_container_width=True)
        if st.button("🗑️ Remove Duplicate Rows", use_container_width=True, disabled=dup_count == 0):
            S.push_undo_snapshot("Removed duplicate rows")
            st.session_state.df = st.session_state.df.drop_duplicates()
            st.rerun()

    # ---------------- Outliers ----------------
    with tabs[2]:
        st.subheader("Outlier Detection & Handling (IQR method)")
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        if not num_cols:
            st.info("No numeric columns available.")
        else:
            col = st.selectbox("Select numeric column", num_cols)
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outliers = df[(df[col] < lower) | (df[col] > upper)]
            st.write(f"Bounds: **{lower:.2f}** to **{upper:.2f}** — {len(outliers)} outliers found")
            st.dataframe(outliers.head(50), use_container_width=True)

            action = st.radio("Action", ["Remove Outliers", "Cap Outliers (Winsorize)"], horizontal=True)
            if st.button("⚙️ Apply Outlier Handling", use_container_width=True):
                S.push_undo_snapshot(f"Handled outliers in {col} ({action})")
                new_df = st.session_state.df.copy()
                if action == "Remove Outliers":
                    new_df = new_df[(new_df[col] >= lower) & (new_df[col] <= upper)]
                else:
                    new_df[col] = new_df[col].clip(lower=lower, upper=upper)
                st.session_state.df = new_df
                st.rerun()

    # ---------------- Text / whitespace ----------------
    with tabs[3]:
        st.subheader("Text Cleanup")
        text_cols = df.select_dtypes(include="object").columns.tolist()
        if not text_cols:
            st.info("No text columns available.")
        else:
            sel_cols = st.multiselect("Columns to clean", text_cols, default=text_cols)
            c1, c2, c3 = st.columns(3)
            with c1:
                trim = st.checkbox("Trim whitespace", True)
            with c2:
                case_opt = st.selectbox("Case", ["No change", "lower", "UPPER", "Title Case"])
            with c3:
                dedupe_space = st.checkbox("Collapse multiple spaces", True)
            if st.button("✨ Apply Text Cleaning", use_container_width=True):
                S.push_undo_snapshot("Cleaned text columns")
                new_df = st.session_state.df.copy()
                for col in sel_cols:
                    s = new_df[col].astype(str)
                    if trim:
                        s = s.str.strip()
                    if dedupe_space:
                        s = s.str.replace(r"\s+", " ", regex=True)
                    if case_opt == "lower":
                        s = s.str.lower()
                    elif case_opt == "UPPER":
                        s = s.str.upper()
                    elif case_opt == "Title Case":
                        s = s.str.title()
                    new_df[col] = s
                st.session_state.df = new_df
                st.rerun()

    # ---------------- Rename & dtype ----------------
    with tabs[4]:
        st.subheader("Rename Columns & Convert Data Types")
        c1, c2 = st.columns(2)
        with c1:
            old_name = st.selectbox("Column to rename", df.columns.tolist())
            new_name = st.text_input("New name", old_name)
            if st.button("✏️ Rename Column", use_container_width=True):
                S.push_undo_snapshot(f"Renamed '{old_name}' → '{new_name}'")
                st.session_state.df = st.session_state.df.rename(columns={old_name: new_name})
                st.rerun()
            if st.button("🔠 Standardize All Column Names (snake_case)", use_container_width=True):
                S.push_undo_snapshot("Standardized column names")
                new_df = st.session_state.df.copy()
                new_df.columns = [c.strip().lower().replace(" ", "_") for c in new_df.columns]
                st.session_state.df = new_df
                st.rerun()
        with c2:
            type_col = st.selectbox("Column to convert", df.columns.tolist(), key="typecol")
            new_type = st.selectbox("Convert to", ["int", "float", "str", "category", "datetime", "bool"])
            if st.button("🔁 Convert Data Type", use_container_width=True):
                S.push_undo_snapshot(f"Converted '{type_col}' to {new_type}")
                new_df = st.session_state.df.copy()
                try:
                    if new_type == "datetime":
                        new_df[type_col] = pd.to_datetime(new_df[type_col], errors="coerce")
                    elif new_type == "int":
                        new_df[type_col] = pd.to_numeric(new_df[type_col], errors="coerce").astype("Int64")
                    elif new_type == "float":
                        new_df[type_col] = pd.to_numeric(new_df[type_col], errors="coerce")
                    else:
                        new_df[type_col] = new_df[type_col].astype(new_type)
                    st.session_state.df = new_df
                    st.rerun()
                except Exception as e:
                    st.error(f"Conversion failed: {e}")

    # ---------------- Preprocessing ----------------
    with tabs[5]:
        st.subheader("Feature Preprocessing")
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        cat_cols = df.select_dtypes(include="object").columns.tolist()

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Scaling (numeric columns)**")
            scale_cols = st.multiselect("Columns", num_cols, key="scale_cols")
            scale_method = st.radio("Method", ["Normalization (Min-Max)", "Standardization (Z-score)"], key="scale_method")
            if st.button("📐 Apply Scaling", use_container_width=True):
                S.push_undo_snapshot(f"Applied {scale_method} to {scale_cols}")
                new_df = st.session_state.df.copy()
                for col in scale_cols:
                    if scale_method.startswith("Normalization"):
                        mn, mx = new_df[col].min(), new_df[col].max()
                        new_df[col] = (new_df[col] - mn) / (mx - mn) if mx != mn else 0.0
                    else:
                        mu, sigma = new_df[col].mean(), new_df[col].std()
                        new_df[col] = (new_df[col] - mu) / sigma if sigma else 0.0
                st.session_state.df = new_df
                st.rerun()
        with c2:
            st.markdown("**Encoding (categorical columns)**")
            enc_cols = st.multiselect("Columns", cat_cols, key="enc_cols")
            enc_method = st.radio("Method", ["Label Encoding", "One-Hot Encoding"], key="enc_method")
            if st.button("🔢 Apply Encoding", use_container_width=True):
                S.push_undo_snapshot(f"Applied {enc_method} to {enc_cols}")
                new_df = st.session_state.df.copy()
                if enc_method == "Label Encoding":
                    for col in enc_cols:
                        new_df[col] = new_df[col].astype("category").cat.codes
                else:
                    new_df = pd.get_dummies(new_df, columns=enc_cols)
                st.session_state.df = new_df
                st.rerun()

    # ---------------- History ----------------
    with tabs[6]:
        st.subheader("Cleaning History")
        if not st.session_state.cleaning_log:
            st.info("No cleaning actions performed yet.")
        else:
            for i, action in enumerate(st.session_state.cleaning_log, 1):
                st.markdown(f"**{i}.** {action}")

    st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)
    st.subheader("Live Preview")
    st.dataframe(st.session_state.df.head(100), use_container_width=True)
