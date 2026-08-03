"""
theme.py
--------
Central place for all visual styling: dark/light mode, glassmorphism cards,
gradients, animated KPI cards, sidebar/topbar styling, fonts, and hover
effects. Keeping every CSS rule in one module makes the "premium SaaS" look
consistent across every page of Pycleansheet AI.
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Color tokens for the two themes
# ---------------------------------------------------------------------------
THEMES = {
    "dark": {
        "bg_gradient": "linear-gradient(135deg,#0b0f19 0%,#111827 45%,#0b1220 100%)",
        "surface": "rgba(255,255,255,0.06)",
        "surface_border": "rgba(255,255,255,0.12)",
        "text": "#F3F4F6",
        "text_muted": "#9CA3AF",
        "accent": "#7C6CFF",
        "accent2": "#22D3EE",
        "accent3": "#F472B6",
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "sidebar_bg": "linear-gradient(180deg,#0f1425 0%,#0a0e19 100%)",
    },
    "light": {
        "bg_gradient": "linear-gradient(135deg,#f5f7fb 0%,#eef1fb 45%,#eef7fb 100%)",
        "surface": "rgba(255,255,255,0.65)",
        "surface_border": "rgba(15,23,42,0.08)",
        "text": "#111827",
        "text_muted": "#4B5563",
        "accent": "#6D5AF7",
        "accent2": "#0891B2",
        "accent3": "#DB2777",
        "success": "#059669",
        "warning": "#D97706",
        "danger": "#DC2626",
        "sidebar_bg": "linear-gradient(180deg,#ffffff 0%,#f3f4fb 100%)",
    },
}


def get_palette():
    mode = st.session_state.get("theme_mode", "dark")
    return THEMES[mode]


def inject_css():
    """Injects the full glassmorphism / premium SaaS stylesheet."""
    p = get_palette()
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {p['bg_gradient']};
        color: {p['text']};
    }}

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {{
        background: {p['sidebar_bg']};
        border-right: 1px solid {p['surface_border']};
    }}
    section[data-testid="stSidebar"] * {{ color: {p['text']} !important; }}

    /* ---------- Headings ---------- */
    h1, h2, h3 {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}

    .pcs-title {{
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        font-size: 2.1rem;
        background: linear-gradient(90deg, {p['accent']}, {p['accent2']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.1rem;
    }}
    .pcs-subtitle {{
        color: {p['text_muted']};
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }}

    /* ---------- Glass card ---------- */
    .glass-card {{
        background: {p['surface']};
        border: 1px solid {p['surface_border']};
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border-radius: 18px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        margin-bottom: 1rem;
    }}
    .glass-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 14px 40px rgba(0,0,0,0.28);
    }}

    /* ---------- KPI cards ---------- */
    .kpi-card {{
        background: {p['surface']};
        border: 1px solid {p['surface_border']};
        border-radius: 16px;
        padding: 1rem 1.1rem;
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: pcsFadeUp 0.5s ease both;
    }}
    .kpi-card:hover {{
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 12px 30px rgba(124,108,255,0.25);
    }}
    .kpi-card::before {{
        content:"";
        position:absolute; top:-40%; right:-20%;
        width:120px; height:120px; border-radius:50%;
        background: radial-gradient(circle, {p['accent']}55, transparent 70%);
    }}
    .kpi-label {{
        color: {p['text_muted']};
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }}
    .kpi-value {{
        font-family: 'Poppins', sans-serif;
        font-size: 1.7rem;
        font-weight: 800;
        margin-top: 2px;
        background: linear-gradient(90deg, {p['accent']}, {p['accent3']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .kpi-icon {{ font-size: 1.4rem; }}

    @keyframes pcsFadeUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ---------- Buttons ---------- */
    .stButton>button, .stDownloadButton>button {{
        background: linear-gradient(90deg, {p['accent']}, {p['accent2']});
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.1rem;
        font-weight: 600;
        transition: all 0.18s ease;
        box-shadow: 0 4px 14px rgba(124,108,255,0.35);
    }}
    .stButton>button:hover, .stDownloadButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(124,108,255,0.45);
        filter: brightness(1.08);
    }}

    /* ---------- Badges / chips ---------- */
    .pcs-chip {{
        display:inline-block; padding:3px 10px; border-radius:999px;
        background:{p['accent']}22; color:{p['accent']};
        font-size:0.75rem; font-weight:600; margin-right:6px;
        border:1px solid {p['accent']}44;
    }}

    /* ---------- Top nav bar ---------- */
    .pcs-topbar {{
        display:flex; align-items:center; justify-content:space-between;
        padding: 0.6rem 1rem; border-radius: 16px;
        background: {p['surface']}; border: 1px solid {p['surface_border']};
        backdrop-filter: blur(12px); margin-bottom: 1.1rem;
    }}

    /* ---------- Dashboard chart tile ---------- */
    .chart-tile {{
        background: {p['surface']};
        border: 1px solid {p['surface_border']};
        border-radius: 16px;
        padding: 0.7rem 0.9rem 0.3rem 0.9rem;
        margin-bottom: 0.9rem;
        transition: box-shadow 0.2s ease;
    }}
    .chart-tile:hover {{ box-shadow: 0 10px 26px rgba(0,0,0,0.22); }}
    .chart-tile-title {{
        font-weight:700; font-size:0.95rem; margin-bottom:0.2rem;
    }}

    /* ---------- Divider ---------- */
    .pcs-divider {{
        height:1px; background: {p['surface_border']}; margin: 0.9rem 0;
    }}

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: {p['accent']}66; border-radius: 8px; }}

    /* ---------- Loading pulse ---------- */
    .pcs-pulse {{
        display:inline-block; width:10px; height:10px; border-radius:50%;
        background:{p['accent']}; margin-right:6px;
        animation: pcsPulse 1.1s infinite ease-in-out;
    }}
    @keyframes pcsPulse {{
        0%,100% {{ transform: scale(0.7); opacity:0.6; }}
        50% {{ transform: scale(1.2); opacity:1; }}
    }}

    /* dataframe rounding */
    [data-testid="stDataFrame"] {{ border-radius: 14px; overflow:hidden; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def loading_screen(message="Loading Pycleansheet AI..."):
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:center;height:40vh;flex-direction:column;">
            <div style="font-size:2rem;">⚡</div>
            <div style="margin-top:0.6rem;"><span class="pcs-pulse"></span>{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
