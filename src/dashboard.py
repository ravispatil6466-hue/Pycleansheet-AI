"""
dashboard.py
------------
Power-BI-style Dashboard Builder. Native Streamlit has no real mouse
drag/resize API, so this module implements the practical equivalent:
add / duplicate / delete / reorder ("move up/down" = drag equivalent) /
resize (grid-unit width + px height) / lock charts, snap-to-grid via a
fixed 3-column grid, zoom, and save/load/reset layout (persisted in
session_state so it survives page switches; can be exported/imported
as JSON for real persistence across sessions).
"""

import streamlit as st
import pandas as pd
import json
import uuid

from src.charts import CHART_TYPES, build_chart
from src.components import render_format_panel, DEFAULT_FORMAT


def _new_chart(df: pd.DataFrame) -> dict:
    return {
        "id": str(uuid.uuid4())[:8],
        "title": "New Chart",
        "type": "Bar Chart",
        "mapping": {},
        "format": {**DEFAULT_FORMAT},
        "locked": False,
    }


def _mapping_editor(chart: dict, df: pd.DataFrame):
    fields = CHART_TYPES[chart["type"]]["fields"]
    cols = list(df.columns)
    mapping = chart["mapping"]
    ui_cols = st.columns(max(len(fields), 1)) if fields else [st]
    for i, field in enumerate(fields):
        target = ui_cols[i] if fields else st
        with target:
            if field in ("path", "dimensions"):
                mapping[field] = st.multiselect(field.title(), cols, default=mapping.get(field, []), key=f"{chart['id']}_{field}")
            elif field == "color":
                options = ["(none)"] + cols
                cur = mapping.get(field) or "(none)"
                choice = st.selectbox("Color", options, index=options.index(cur) if cur in options else 0, key=f"{chart['id']}_{field}")
                mapping[field] = None if choice == "(none)" else choice
            else:
                options = cols
                cur = mapping.get(field, cols[0] if cols else None)
                idx = options.index(cur) if cur in options else 0
                mapping[field] = st.selectbox(field.title(), options, index=idx, key=f"{chart['id']}_{field}") if options else None
    chart["mapping"] = mapping


def render(df: pd.DataFrame):
    st.markdown('<div class="pcs-title">🧩 Dashboard Builder</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Add, arrange, resize and style charts — Power BI style. Snap-to-grid with 3 columns.</div>', unsafe_allow_html=True)

    top = st.columns([1, 1, 1, 1, 1, 2])
    with top[0]:
        if st.button("➕ Add Chart", use_container_width=True):
            st.session_state.dashboard_charts.append(_new_chart(df))
            st.rerun()
    with top[1]:
        zoom = st.select_slider("🔍 Zoom", options=[75, 90, 100, 110, 125, 150], value=st.session_state.get("dash_zoom", 100))
        st.session_state["dash_zoom"] = zoom
    with top[2]:
        if st.button("💾 Save Layout", use_container_width=True):
            st.session_state["saved_layout"] = json.dumps(st.session_state.dashboard_charts)
            st.toast("Layout saved to session.", icon="💾")
    with top[3]:
        if st.button("📂 Load Layout", use_container_width=True, disabled="saved_layout" not in st.session_state):
            st.session_state.dashboard_charts = json.loads(st.session_state["saved_layout"])
            st.rerun()
    with top[4]:
        if st.button("🧨 Reset Dashboard", use_container_width=True):
            st.session_state.dashboard_charts = []
            st.rerun()
    with top[5]:
        uploaded = st.file_uploader("Import layout JSON", type=["json"], label_visibility="collapsed")
        if uploaded is not None:
            try:
                st.session_state.dashboard_charts = json.load(uploaded)
                st.success("Layout imported.")
            except Exception as e:
                st.error(f"Invalid layout file: {e}")

    layout_json = json.dumps(st.session_state.dashboard_charts, indent=2)
    st.download_button("⬇️ Export Layout JSON", data=layout_json, file_name="pycleansheet_dashboard_layout.json",
                        mime="application/json", use_container_width=False)

    st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)

    if not st.session_state.dashboard_charts:
        st.info("No charts yet. Click **➕ Add Chart** to start building your dashboard.")
        return

    st.markdown(f"<div style='zoom:{zoom}%'>", unsafe_allow_html=True)

    charts = st.session_state.dashboard_charts
    for c in charts:
        c.setdefault("format", {**DEFAULT_FORMAT})
        c.setdefault("mapping", {})
        c.setdefault("locked", False)
        c.setdefault("title", "Untitled Chart")
        c.setdefault("type", "Bar Chart")
        c.setdefault("id", str(uuid.uuid4())[:8])

    i = 0
    while i < len(charts):
        # Determine how many charts fit in this visual "row" based on width (grid units out of 3)
        row_charts = []
        used = 0
        j = i
        while j < len(charts) and used < 3:
            w = charts[j]["format"].get("width", 1)
            if used + w > 3 and used > 0:
                break
            row_charts.append(charts[j])
            used += w
            j += 1
        cols = st.columns([c["format"].get("width", 1) for c in row_charts])
        for col, chart in zip(cols, row_charts):
            with col:
                _render_chart_tile(chart, df, charts)
        i = j

    st.markdown("</div>", unsafe_allow_html=True)


def _render_chart_tile(chart: dict, df: pd.DataFrame, charts: list):
    idx = charts.index(chart)
    with st.container():
        st.markdown('<div class="chart-tile">', unsafe_allow_html=True)
        head = st.columns([3, 1])
        with head[0]:
            chart["title"] = st.text_input("Title", chart["title"], key=f"title_{chart['id']}", label_visibility="collapsed")
        with head[1]:
            chart["type"] = st.selectbox("Type", list(CHART_TYPES.keys()),
                                          index=list(CHART_TYPES.keys()).index(chart["type"]),
                                          key=f"type_{chart['id']}", label_visibility="collapsed")

        disabled = chart.get("locked", False)
        if not disabled:
            _mapping_editor(chart, df)

        try:
            fig = build_chart(chart["type"], df, chart["mapping"], chart["format"])
            fig.update_layout(title=chart["title"])
            st.plotly_chart(fig, use_container_width=True, key=f"plot_{chart['id']}")
        except Exception as e:
            st.warning(f"Configure fields above to render this chart. ({e})")

        chart["format"] = render_format_panel(chart["id"], chart["format"])

        controls = st.columns(6)
        with controls[0]:
            if st.button("⬆️", key=f"up_{chart['id']}", help="Move earlier (drag equivalent)", disabled=idx == 0):
                charts[idx - 1], charts[idx] = charts[idx], charts[idx - 1]
                st.rerun()
        with controls[1]:
            if st.button("⬇️", key=f"down_{chart['id']}", help="Move later (drag equivalent)", disabled=idx == len(charts) - 1):
                charts[idx + 1], charts[idx] = charts[idx], charts[idx + 1]
                st.rerun()
        with controls[2]:
            if st.button("📄", key=f"dup_{chart['id']}", help="Duplicate"):
                new_chart = json.loads(json.dumps(chart))
                new_chart["id"] = str(uuid.uuid4())[:8]
                new_chart["title"] = chart["title"] + " (copy)"
                charts.insert(idx + 1, new_chart)
                st.rerun()
        with controls[3]:
            if st.button("🗑️", key=f"del_{chart['id']}", help="Delete"):
                charts.pop(idx)
                st.rerun()
        with controls[4]:
            lock_label = "🔓" if chart.get("locked") else "🔒"
            if st.button(lock_label, key=f"lock_{chart['id']}", help="Lock/Unlock visual"):
                chart["locked"] = not chart.get("locked", False)
                st.rerun()
        with controls[5]:
            layer_label = "⬆️ Front"
            if st.button(layer_label, key=f"front_{chart['id']}", help="Bring to front (reorder to top)"):
                charts.insert(0, charts.pop(idx))
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
