"""
python_editor.py
-----------------
Embedded Python code editor. Users write code against `df` (the current
working dataframe) and `pd`/`np`/`px` are available in scope. The result
of the last expression (or an explicit `result = ...` assignment) is
displayed, and if the code reassigns `df`, the session's working
dataframe is updated immediately.

Execution is sandboxed to a restricted set of builtins to reduce risk,
but this remains a power-user feature: only run trusted code.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import contextlib

from src import state as S

SAFE_BUILTINS = {
    "len": len, "range": range, "sum": sum, "min": min, "max": max,
    "sorted": sorted, "list": list, "dict": dict, "set": set, "tuple": tuple,
    "enumerate": enumerate, "zip": zip, "abs": abs, "round": round,
    "str": str, "int": int, "float": float, "bool": bool, "print": print,
}


def render(df: pd.DataFrame):
    st.markdown('<div class="pcs-title">🐍 Python Editor</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Execute Python directly on your dataframe. `df`, `pd`, `np`, and `px` are available.</div>', unsafe_allow_html=True)

    st.session_state.python_editor_code = st.text_area(
        "Code",
        value=st.session_state.python_editor_code,
        height=220,
        label_visibility="collapsed",
    )

    c1, c2 = st.columns([1, 1])
    with c1:
        run = st.button("▶️ Run Code", use_container_width=True)
    with c2:
        commit = st.checkbox("Update working dataset if `df` is reassigned", value=True)

    if run:
        local_scope = {"df": df.copy(), "pd": pd, "np": np, "px": px}
        stdout_buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_buffer):
                exec(
                    compile(st.session_state.python_editor_code, "<pycleansheet_editor>", "exec"),
                    {"__builtins__": SAFE_BUILTINS},
                    local_scope,
                )
            output_text = stdout_buffer.getvalue()
            if output_text.strip():
                st.code(output_text)

            if "result" in local_scope:
                result = local_scope["result"]
                if isinstance(result, pd.DataFrame):
                    st.dataframe(result, use_container_width=True)
                elif hasattr(result, "to_html"):  # plotly figure
                    st.plotly_chart(result, use_container_width=True)
                else:
                    st.write(result)

            new_df = local_scope.get("df")
            if commit and isinstance(new_df, pd.DataFrame) and not new_df.equals(df):
                S.push_undo_snapshot("Python Editor: dataframe updated")
                st.session_state.df = new_df
                st.success("Working dataset updated from Python Editor.")
                st.dataframe(new_df.head(50), use_container_width=True)
        except Exception as e:
            st.error(f"Execution error: {e}")

    with st.expander("💡 Example snippets"):
        st.code(
            "# Filter rows\n"
            "result = df[df.iloc[:, 0].notna()]\n\n"
            "# Create a new column\n"
            "df['new_col'] = df.select_dtypes('number').sum(axis=1)\n\n"
            "# Quick chart\n"
            "result = px.histogram(df, x=df.columns[0])",
            language="python",
        )
