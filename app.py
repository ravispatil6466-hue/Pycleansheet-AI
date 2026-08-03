"""
Pycleansheet AI — Intelligent Data Cleaning, Analytics & Dashboard Platform
============================================================================
Main application entry point. Handles global page config, theme, sidebar
navigation, and routes to each feature module.

Run with:
    streamlit run app.py
"""

import streamlit as st

from src import state as S
from src.theme import inject_css, get_palette
from src.components import render_kpi_row, render_filter_panel
from src import upload, cleaning, eda, dashboard, python_editor, reports, export
from src.chatbot import answer_question, nl_to_chart

st.set_page_config(
    page_title="Pycleansheet AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

S.init_state()
inject_css()

# ---------------------------------------------------------------------------
# SIDEBAR — branding, theme toggle, navigation, AI settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:0.4rem;">
            <div style="font-size:1.8rem;">🧠</div>
            <div>
                <div style="font-family:Poppins,sans-serif;font-weight:800;font-size:1.15rem;line-height:1.1;">Pycleansheet AI</div>
                <div style="font-size:0.72rem;opacity:0.7;">Data Cleaning · Analytics · Dashboards</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)

    theme_choice = st.radio("Theme", ["Dark", "Light"], horizontal=True,
                             index=0 if st.session_state.theme_mode == "dark" else 1)
    st.session_state.theme_mode = "dark" if theme_choice == "Dark" else "light"

    st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)

    PAGES = [
        "📁 Upload Data",
        "🧹 Data Cleaning",
        "🔬 EDA",
        "🧩 Dashboard Builder",
        "🐍 Python Editor",
        "🤖 AI Chatbot",
        "💬 Natural Language Analytics",
        "📑 Report Generator",
        "📤 Export Center",
    ]
    page = st.radio("Navigate", PAGES, label_visibility="collapsed")

    st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)
    with st.expander("⚙️ AI Settings"):
        st.session_state.api_provider = st.selectbox(
            "AI Provider",
            ["None (built-in insights)", "Anthropic (Claude)", "OpenAI (GPT)"],
            index=["None (built-in insights)", "Anthropic (Claude)", "OpenAI (GPT)"].index(st.session_state.api_provider),
        )
        if st.session_state.api_provider != "None (built-in insights)":
            st.session_state.api_key = st.text_input("API Key", type="password", value=st.session_state.api_key)
            st.caption("Your key stays in this session only and is never stored server-side.")

    if st.session_state.dataset_name:
        st.markdown('<div class="pcs-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<span class="pcs-chip">📄 {st.session_state.dataset_name}</span>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# MAIN AREA
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="pcs-topbar">
        <div style="font-weight:700;">🧠 Pycleansheet AI</div>
        <div style="opacity:0.75;font-size:0.85rem;">Intelligent Data Cleaning · Analytics · Power BI-style Dashboards</div>
    </div>
    """,
    unsafe_allow_html=True,
)

df = st.session_state.df

if page == "📁 Upload Data":
    upload.render()

elif page == "🧹 Data Cleaning":
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        cleaning.render(df)

elif page == "🔬 EDA":
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        render_kpi_row(df)
        filtered = render_filter_panel(df)
        eda.render(filtered if filtered is not None else df)

elif page == "🧩 Dashboard Builder":
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        filtered = render_filter_panel(df)
        dashboard.render(filtered if filtered is not None else df)

elif page == "🐍 Python Editor":
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        python_editor.render(df)

elif page == "🤖 AI Chatbot":
    st.markdown('<div class="pcs-title">🤖 AI Chatbot</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Ask about your dataset: summaries, correlations, trends, recommendations.</div>', unsafe_allow_html=True)
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        prompt = st.chat_input("Ask about your dataset...")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    reply = answer_question(df, prompt)
                st.markdown(reply)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})

elif page == "💬 Natural Language Analytics":
    st.markdown('<div class="pcs-title">💬 Natural Language Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="pcs-subtitle">Type a request like "show revenue by city" or "top 5 category" to auto-generate a chart.</div>', unsafe_allow_html=True)
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        query = st.text_input("Describe the chart you want", placeholder="e.g. show sales by month, compare revenue by city, top 5 products")
        if query:
            fig = nl_to_chart(df, query)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                if st.button("➕ Add to Dashboard"):
                    import uuid
                    from src.components import DEFAULT_FORMAT
                    st.session_state.dashboard_charts.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": query.title(),
                        "type": "Bar Chart",
                        "mapping": {},
                        "format": {**DEFAULT_FORMAT},
                        "locked": False,
                    })
                    st.success("Added a starter chart to the Dashboard Builder — refine its fields there.")
            else:
                st.info("Couldn't confidently parse that request. Try patterns like 'show <metric> by <column>', 'compare <metric> by <column>', 'distribution of <column>', or 'top 5 <column>'.")

elif page == "📑 Report Generator":
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        reports.render(df)

elif page == "📤 Export Center":
    if df is None:
        st.warning("Please upload a dataset first from **📁 Upload Data**.")
    else:
        export.render(df)

st.markdown(
    """
    <div style="text-align:center;opacity:0.5;font-size:0.75rem;margin-top:2rem;">
        Pycleansheet AI · Built with Streamlit, Plotly & ❤️ — Portfolio-ready Data Analytics Platform
    </div>
    """,
    unsafe_allow_html=True,
)
