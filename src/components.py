"""
components.py
-------------
Reusable, styled UI building blocks: animated KPI cards, the Power-BI-style
filter panel (slicers), and the format panel used by the dashboard builder.
"""

import streamlit as st
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------------------------
def render_kpi_row(df: pd.DataFrame):
    if df is None:
        st.info("Upload a dataset to see KPI cards.")
        return

    total_rows = len(df)
    total_cols = df.shape[1]
    missing = int(df.isna().sum().sum())
    missing_pct = round((missing / (total_rows * total_cols) * 100), 2) if total_rows and total_cols else 0
    duplicates = int(df.duplicated().sum())
    mem_mb = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2)
    dtypes_count = df.dtypes.nunique()
    quality_score = max(0, round(100 - missing_pct - (duplicates / max(total_rows, 1) * 100), 1))

    kpis = [
        ("📊", "Total Rows", f"{total_rows:,}"),
        ("🧮", "Total Columns", f"{total_cols:,}"),
        ("❓", "Missing Values", f"{missing:,}"),
        ("📉", "Null %", f"{missing_pct}%"),
        ("🧬", "Duplicate Records", f"{duplicates:,}"),
        ("✅", "Data Quality Score", f"{quality_score}/100"),
        ("💾", "Memory Usage", f"{mem_mb} MB"),
        ("🗂️", "Distinct Data Types", f"{dtypes_count}"),
    ]

    cols = st.columns(4)
    for i, (icon, label, value) in enumerate(kpis):
        with cols[i % 4]:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-icon">{icon}</div>
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# FILTER PANEL (Slicers)
# ---------------------------------------------------------------------------
def render_filter_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Renders a Power-BI style slicer panel in an expander and returns the
    filtered dataframe. Filters are stored in session_state so they persist
    across pages."""
    if df is None:
        return df

    with st.expander("🧊 Filter Panel / Slicers", expanded=False):
        st.caption("Column filters, dropdowns, multi-select, range sliders and search — applied live.")
        search_term = st.text_input("🔎 Global search", value=st.session_state.active_filters.get("__search__", ""))
        st.session_state.active_filters["__search__"] = search_term

        filter_cols = st.multiselect(
            "Choose columns to add slicers for",
            options=list(df.columns),
            default=st.session_state.active_filters.get("__cols__", [])[:3],
        )
        st.session_state.active_filters["__cols__"] = filter_cols

        filtered = df.copy()

        if search_term:
            mask = filtered.astype(str).apply(lambda row: row.str.contains(search_term, case=False, na=False)).any(axis=1)
            filtered = filtered[mask]

        for col in filter_cols:
            series = df[col]
            if pd.api.types.is_numeric_dtype(series):
                min_v, max_v = float(series.min()), float(series.max())
                if min_v == max_v:
                    continue
                sel = st.slider(f"Range: {col}", min_value=min_v, max_value=max_v, value=(min_v, max_v))
                filtered = filtered[(filtered[col] >= sel[0]) & (filtered[col] <= sel[1])]
            elif pd.api.types.is_datetime64_any_dtype(series):
                min_d, max_d = series.min(), series.max()
                sel = st.date_input(f"Date range: {col}", value=(min_d, max_d))
                if isinstance(sel, tuple) and len(sel) == 2:
                    filtered = filtered[(filtered[col] >= pd.to_datetime(sel[0])) & (filtered[col] <= pd.to_datetime(sel[1]))]
            else:
                options = sorted(series.dropna().astype(str).unique().tolist())
                sel = st.multiselect(f"Slicer: {col}", options=options, default=options)
                filtered = filtered[filtered[col].astype(str).isin(sel)]

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Apply Filters", use_container_width=True):
                st.session_state["__filtered_snapshot__"] = filtered
        with c2:
            if st.button("🧹 Clear Filters", use_container_width=True):
                st.session_state.active_filters = {}
                st.rerun()

    return filtered


# ---------------------------------------------------------------------------
# FORMAT PANEL (used by dashboard builder for per-chart styling)
# ---------------------------------------------------------------------------
DEFAULT_FORMAT = {
    "bg_color": "#111827",
    "title_color": "#F3F4F6",
    "chart_theme": "plotly_dark",
    "palette": "Vivid",
    "font_family": "Inter, sans-serif",
    "font_size": 13,
    "bold": False,
    "italic": False,
    "underline": False,
    "text_align": "left",
    "border_radius": 16,
    "opacity": 1.0,
    "width": 2,       # in grid units (1-3 columns)
    "height": 380,    # px
    "show_legend": True,
    "show_grid": True,
    "show_tooltips": True,
}

PALETTES = {
    "Vivid": ["#7C6CFF", "#22D3EE", "#F472B6", "#34D399", "#FBBF24", "#F87171", "#60A5FA", "#A78BFA"],
    "Corporate": ["#1F3B73", "#2D6CA2", "#57A6DC", "#7FC8F8", "#B9E3FF", "#E5E9F0", "#4B5563", "#9CA3AF"],
    "Sunset": ["#FF6B6B", "#FFA36B", "#FFD56B", "#8CFF6B", "#6BFFD5", "#6BA3FF", "#B96BFF", "#FF6BE0"],
    "Mono Blue": ["#0B3C5D", "#1D5B8C", "#328CC1", "#73C2FB", "#A9E5FF", "#D6F3FF", "#083049", "#062436"],
}


def render_format_panel(chart_id: str, current: dict) -> dict:
    """Renders the format panel controls for one chart and returns the
    updated format dict."""
    fmt = {**DEFAULT_FORMAT, **current}
    with st.expander(f"🎨 Format Panel — {chart_id}", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            fmt["bg_color"] = st.color_picker("Background Color", fmt["bg_color"], key=f"bg_{chart_id}")
            fmt["title_color"] = st.color_picker("Title Color", fmt["title_color"], key=f"tc_{chart_id}")
            fmt["chart_theme"] = st.selectbox(
                "Chart Theme", ["plotly_dark", "plotly_white", "ggplot2", "seaborn", "simple_white"],
                index=["plotly_dark", "plotly_white", "ggplot2", "seaborn", "simple_white"].index(fmt["chart_theme"]),
                key=f"theme_{chart_id}",
            )
            fmt["palette"] = st.selectbox("Color Palette", list(PALETTES.keys()),
                                           index=list(PALETTES.keys()).index(fmt["palette"]), key=f"pal_{chart_id}")
        with c2:
            fmt["font_family"] = st.selectbox(
                "Font Family", ["Inter, sans-serif", "Poppins, sans-serif", "Georgia, serif", "Courier New, monospace"],
                index=0 if fmt["font_family"].startswith("Inter") else 0, key=f"font_{chart_id}",
            )
            fmt["font_size"] = st.slider("Font Size", 8, 28, fmt["font_size"], key=f"fs_{chart_id}")
            fmt["bold"] = st.checkbox("Bold", fmt["bold"], key=f"bold_{chart_id}")
            fmt["italic"] = st.checkbox("Italic", fmt["italic"], key=f"ital_{chart_id}")
            fmt["underline"] = st.checkbox("Underline", fmt["underline"], key=f"und_{chart_id}")
        with c3:
            fmt["text_align"] = st.selectbox("Text Alignment", ["left", "center", "right"],
                                              index=["left", "center", "right"].index(fmt["text_align"]), key=f"ta_{chart_id}")
            fmt["border_radius"] = st.slider("Border Radius", 0, 40, fmt["border_radius"], key=f"br_{chart_id}")
            fmt["opacity"] = st.slider("Opacity", 0.2, 1.0, fmt["opacity"], key=f"op_{chart_id}")
            fmt["width"] = st.select_slider("Chart Width (grid units)", options=[1, 2, 3], value=fmt["width"], key=f"w_{chart_id}")
            fmt["height"] = st.slider("Chart Height (px)", 220, 700, fmt["height"], key=f"h_{chart_id}")

        c4, c5, c6 = st.columns(3)
        with c4:
            fmt["show_legend"] = st.checkbox("Show Legend", fmt["show_legend"], key=f"leg_{chart_id}")
        with c5:
            fmt["show_grid"] = st.checkbox("Show Grid", fmt["show_grid"], key=f"grid_{chart_id}")
        with c6:
            fmt["show_tooltips"] = st.checkbox("Show Tooltips", fmt["show_tooltips"], key=f"tip_{chart_id}")

    return fmt


def format_to_css(fmt: dict) -> str:
    weight = "700" if fmt.get("bold") else "500"
    style = "italic" if fmt.get("italic") else "normal"
    decoration = "underline" if fmt.get("underline") else "none"
    return (
        f"background:{fmt['bg_color']}; color:{fmt['title_color']}; "
        f"font-family:{fmt['font_family']}; font-size:{fmt['font_size']}px; "
        f"font-weight:{weight}; font-style:{style}; text-decoration:{decoration}; "
        f"text-align:{fmt['text_align']}; border-radius:{fmt['border_radius']}px; "
        f"opacity:{fmt['opacity']}; padding:10px 14px;"
    )
