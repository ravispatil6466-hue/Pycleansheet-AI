"""
state.py
--------
Central session-state bootstrap for the whole app: dataset, undo/redo
history stack, cleaning log, dashboard layout, filters, and theme.
"""

import streamlit as st
import pandas as pd


def init_state():
    defaults = {
        "theme_mode": "dark",
        "df": None,                 # current working dataframe
        "df_original": None,        # untouched original upload
        "history": [],              # undo stack of dataframes
        "future": [],                # redo stack of dataframes
        "cleaning_log": [],         # human-readable list of cleaning actions
        "dashboard_charts": [],     # list of chart config dicts
        "active_filters": {},       # column -> filter value
        "dataset_name": None,
        "api_key": "",
        "api_provider": "None (built-in insights)",
        "chat_history": [],
        "python_editor_code": "df.head()",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def set_dataframe(df: pd.DataFrame, name: str = None, push_history: bool = True):
    """Set a brand new working dataframe (e.g. after upload)."""
    st.session_state.df = df.copy()
    st.session_state.df_original = df.copy()
    st.session_state.history = []
    st.session_state.future = []
    st.session_state.cleaning_log = []
    if name:
        st.session_state.dataset_name = name


def push_undo_snapshot(action_label: str):
    """Call BEFORE mutating st.session_state.df to record the previous state."""
    if st.session_state.df is not None:
        st.session_state.history.append(st.session_state.df.copy())
        st.session_state.future = []  # any new action clears redo stack
        st.session_state.cleaning_log.append(action_label)


def undo():
    if st.session_state.history:
        st.session_state.future.append(st.session_state.df.copy())
        st.session_state.df = st.session_state.history.pop()
        if st.session_state.cleaning_log:
            st.session_state.cleaning_log.pop()


def redo():
    if st.session_state.future:
        st.session_state.history.append(st.session_state.df.copy())
        st.session_state.df = st.session_state.future.pop()


def reset_dataset():
    if st.session_state.df_original is not None:
        st.session_state.df = st.session_state.df_original.copy()
        st.session_state.history = []
        st.session_state.future = []
        st.session_state.cleaning_log = []
