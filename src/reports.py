"""
reports.py
----------
Report Generator: builds a polished, self-contained HTML report covering
dataset summary, cleaning history, EDA highlights, dashboard chart list,
and AI insights / business summary — no external PDF library required.

The HTML report opens in any browser and can be turned into a PDF via
the browser's built-in "Print → Save as PDF" option, so there's no need
for reportlab, wkhtmltopdf, or any other heavyweight/native dependency.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from html import escape

from src.chatbot import generate_ai_summary


def _kpi_block(df: pd.DataFrame) -> str:
    total_rows = len(df)
    total_cols = df.shape[1]
    missing = int(df.isna().sum().sum())
    dup = int(df.duplicated().sum())
    mem_mb = round(df.memory_usage(deep=True).sum() / (1024 ** 2), 2)
    missing_pct = round((missing / (total_rows * total_cols) * 100), 2) if total_rows and total_cols else 0

    cards = [
        ("Total Rows", f"{total_rows:,}"),
        ("Total Columns", f"{total_cols:,}"),
        ("Missing Values", f"{missing:,}"),
        ("Null %", f"{missing_pct}%"),
        ("Duplicate Rows", f"{dup:,}"),
        ("Memory Usage", f"{mem_mb} MB"),
    ]
    html = '<div class="kpi-grid">'
    for label, value in cards:
        html += f'<div class="kpi"><div class="kpi-label">{escape(label)}</div><div class="kpi-value">{escape(value)}</div></div>'
    html += "</div>"
    return html


def _df_to_html_table(df: pd.DataFrame, max_rows: int = 15) -> str:
    if df is None or df.empty:
        return "<p><em>No data available.</em></p>"
    return df.head(max_rows).to_html(classes="pcs-table", border=0, index=True, escape=True)


def _strongest_correlation_pair(df: pd.DataFrame, num_cols: list):
    if len(num_cols) < 2:
        return None
    corr = df[num_cols].corr(numeric_only=True).abs()
    arr = corr.to_numpy(copy=True)
    if arr.size == 0:
        return None
    np.fill_diagonal(arr, 0)
    idx = np.unravel_index(np.argmax(arr), arr.shape)
    value = arr[idx]
    if not np.isfinite(value):
        return None
    return corr.index[idx[0]], corr.columns[idx[1]], float(value)


def build_html_report(df: pd.DataFrame, sections: list) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    dataset_name = escape(str(st.session_state.get("dataset_name") or "Uploaded dataset"))
    body = ""

    if "Dataset Summary" in sections:
        body += "<h2>📊 Dataset Summary</h2>"
        body += _kpi_block(df)
        body += "<h3>Data Types</h3>"
        dtypes_df = df.dtypes.astype(str).rename("dtype").to_frame()
        body += _df_to_html_table(dtypes_df, max_rows=len(dtypes_df))

    if "Cleaning Report" in sections:
        body += "<h2>🧹 Cleaning History</h2>"
        log = st.session_state.get("cleaning_log", [])
        if log:
            body += "<ol>" + "".join(f"<li>{escape(a)}</li>" for a in log) + "</ol>"
        else:
            body += "<p><em>No cleaning actions were performed.</em></p>"

    if "EDA Report" in sections:
        body += "<h2>🔬 EDA Highlights</h2>"
        num_cols = df.select_dtypes(include=np.number).columns.tolist()
        pair = _strongest_correlation_pair(df, num_cols)
        if pair:
            body += f"<p><strong>Strongest correlation:</strong> {escape(str(pair[0]))} ↔ {escape(str(pair[1]))} ({pair[2]:.2f})</p>"
        desc = df.describe(include=[np.number]).transpose().round(2)
        if not desc.empty:
            body += "<h3>Summary Statistics (numeric columns)</h3>"
            body += _df_to_html_table(desc, max_rows=len(desc))

    if "Dashboard Report" in sections:
        body += "<h2>🧩 Dashboard Charts</h2>"
        charts = st.session_state.get("dashboard_charts", [])
        if charts:
            body += "<ul>" + "".join(
                f"<li>{escape(c.get('title','Untitled'))} — {escape(c.get('type','Chart'))}</li>" for c in charts
            ) + "</ul>"
        else:
            body += "<p><em>No dashboard charts have been created yet.</em></p>"

    if "AI Insights" in sections or "Business Summary" in sections:
        body += "<h2>🤖 AI Insights & Business Summary</h2>"
        summary = generate_ai_summary(df)
        summary_html = (
            summary.replace("### ", "<h3>").replace("\n\n", "</p><p>")
        )
        # Lightweight markdown-ish cleanup: bold and simple line breaks
        import re
        summary_html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", summary_html)
        summary_html = summary_html.replace("\n- ", "<br>• ").replace("\n", "<br>")
        body += f"<div class='ai-summary'>{summary_html}</div>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Pycleansheet AI Report — {dataset_name}</title>
<style>
    body {{
        font-family: 'Segoe UI', Inter, Arial, sans-serif;
        background: #0b0f19;
        color: #1f2937;
        margin: 0;
        padding: 0;
    }}
    .page {{
        max-width: 900px;
        margin: 0 auto;
        background: #ffffff;
        padding: 40px 48px;
    }}
    .header {{
        background: linear-gradient(90deg, #6D5AF7, #0891B2);
        color: white;
        padding: 28px 40px;
        border-radius: 0 0 16px 16px;
    }}
    .header h1 {{ margin: 0; font-size: 1.7rem; }}
    .header p {{ margin: 4px 0 0; opacity: 0.9; font-size: 0.9rem; }}
    h2 {{ color: #6D5AF7; border-bottom: 2px solid #eef1fb; padding-bottom: 6px; margin-top: 2.2rem; }}
    h3 {{ color: #111827; margin-top: 1.4rem; }}
    .kpi-grid {{ display: flex; flex-wrap: wrap; gap: 14px; margin: 16px 0; }}
    .kpi {{
        background: #f5f7fb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px 18px;
        min-width: 140px;
    }}
    .kpi-label {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; font-weight: 600; }}
    .kpi-value {{ font-size: 1.35rem; font-weight: 800; color: #111827; margin-top: 2px; }}
    table.pcs-table {{ border-collapse: collapse; width: 100%; font-size: 0.82rem; margin: 10px 0 20px; }}
    table.pcs-table th, table.pcs-table td {{ border: 1px solid #e5e7eb; padding: 6px 10px; text-align: left; }}
    table.pcs-table th {{ background: #111827; color: white; }}
    table.pcs-table tr:nth-child(even) {{ background: #f9fafb; }}
    .ai-summary {{ background: #f5f7fb; border-radius: 12px; padding: 16px 20px; line-height: 1.6; }}
    .footer {{ margin-top: 3rem; text-align: center; color: #9ca3af; font-size: 0.78rem; }}
    @media print {{
        body {{ background: white; }}
        .page {{ box-shadow: none; }}
    }}
</style>
</head>
<body>
<div class="header">
    <h1>🧠 Pycleansheet AI — Analytics Report</h1>
    <p>Generated: {generated} &nbsp;·&nbsp; Dataset: {dataset_name}</p>
</div>
<div class="page">
    {body}
    <div class="footer">Pycleansheet AI · Built with Streamlit &amp; Plotly</div>
</div>
</body>
</html>"""
    return html


def render(df: pd.DataFrame):
    st.markdown('<div class="pcs-title">📑 Report Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Generate a professional HTML report covering any combination of sections. Open it in a browser, or use Print → Save as PDF for a PDF copy.</div>', unsafe_allow_html=True)

    sections = st.multiselect(
        "Sections to include",
        ["Dataset Summary", "Cleaning Report", "EDA Report", "Dashboard Report", "AI Insights", "Business Summary"],
        default=["Dataset Summary", "Cleaning Report", "EDA Report", "AI Insights"],
    )

    if st.button("📄 Generate Report", use_container_width=True):
        with st.spinner("Building report..."):
            html_report = build_html_report(df, sections)
        st.success("Report generated.")
        st.download_button(
            "⬇️ Download HTML Report",
            data=html_report,
            file_name=f"pycleansheet_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True,
        )
        st.caption("Tip: open the downloaded file in your browser, then use **Ctrl+P → Save as PDF** if you need a PDF copy.")
        with st.expander("Preview report"):
            st.components.v1.html(html_report, height=600, scrolling=True)
