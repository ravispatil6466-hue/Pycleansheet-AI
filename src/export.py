"""
export.py
---------
Export Center: cleaned dataset (CSV / Excel / JSON), dashboard export
(PDF snapshot via reports module / static HTML), and individual chart
export (PNG / SVG / HTML — PNG/SVG require the optional `kaleido`
package; if unavailable we gracefully fall back to interactive HTML).
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

from src.charts import build_chart, CHART_TYPES


def render(df: pd.DataFrame):
    st.markdown('<div class="pcs-title">📤 Export Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Export your cleaned dataset and dashboard charts in multiple formats.</div>', unsafe_allow_html=True)

    tabs = st.tabs(["Dataset Export", "Dashboard Charts Export"])

    with tabs[0]:
        st.subheader("Export Cleaned Dataset")
        c1, c2, c3 = st.columns(3)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        with c1:
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", data=csv_bytes, file_name=f"pycleansheet_data_{ts}.csv",
                                mime="text/csv", use_container_width=True)
        with c2:
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Data")
            st.download_button("⬇️ Download Excel", data=excel_buf.getvalue(), file_name=f"pycleansheet_data_{ts}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with c3:
            json_bytes = df.to_json(orient="records", indent=2).encode("utf-8")
            st.download_button("⬇️ Download JSON", data=json_bytes, file_name=f"pycleansheet_data_{ts}.json",
                                mime="application/json", use_container_width=True)

    with tabs[1]:
        st.subheader("Export Individual Charts")
        charts = st.session_state.get("dashboard_charts", [])
        if not charts:
            st.info("Build charts in the Dashboard Builder first.")
        else:
            chart_titles = [f"{c['title']} ({c['type']})" for c in charts]
            selection = st.selectbox("Select chart", chart_titles)
            chart = charts[chart_titles.index(selection)]
            try:
                fig = build_chart(chart["type"], df, chart["mapping"], chart["format"])
                fig.update_layout(title=chart["title"])
                st.plotly_chart(fig, use_container_width=True)

                c1, c2, c3 = st.columns(3)
                with c1:
                    html_str = fig.to_html(include_plotlyjs="cdn")
                    st.download_button("⬇️ Export HTML (interactive)", data=html_str,
                                        file_name=f"{chart['title']}.html", mime="text/html", use_container_width=True)
                with c2:
                    try:
                        png_bytes = fig.to_image(format="png", scale=2)
                        st.download_button("⬇️ Export PNG", data=png_bytes, file_name=f"{chart['title']}.png",
                                            mime="image/png", use_container_width=True)
                    except Exception:
                        st.caption("PNG export needs the optional `kaleido` package (`pip install kaleido`).")
                with c3:
                    try:
                        svg_bytes = fig.to_image(format="svg")
                        st.download_button("⬇️ Export SVG", data=svg_bytes, file_name=f"{chart['title']}.svg",
                                            mime="image/svg+xml", use_container_width=True)
                    except Exception:
                        st.caption("SVG export needs the optional `kaleido` package (`pip install kaleido`).")
            except Exception as e:
                st.warning(f"This chart isn't fully configured yet: {e}")
