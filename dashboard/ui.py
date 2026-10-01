# -*- coding: utf-8 -*-
"""
Dashboard UI Design System
===========================
Reusable CSS, components, and formatting helpers.
"""

# -- CSS Variables & Theme --
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@300;400;500&family=Playfair+Display:wght@500;600;700&display=swap');

:root {
    /* -- Fonts -- */
    --font-body: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-display: 'Playfair Display', Georgia, serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', 'Cascadia Code', monospace;

    /* -- Colors -- */
    --bg: #0f1114;
    --bg-elevated: #151719;
    --surface: rgba(255,255,255,0.03);
    --surface-hover: rgba(255,255,255,0.052);
    --surface-active: rgba(255,255,255,0.07);
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.11);
    --border-subtle: rgba(255,255,255,0.035);
    --text: #ece8e1;
    --text-secondary: #a09a90;
    --text-muted: #625d55;
    --text-dim: #403c36;
    --accent: #d4af61;
    --accent-soft: rgba(212,175,97,0.12);
    --danger: #d4736a;
    --danger-soft: rgba(212,115,106,0.10);
    --warning: #d4a84e;
    --warning-soft: rgba(212,168,78,0.10);
    --success: #62b87a;
    --success-soft: rgba(98,184,122,0.10);

    /* -- Surfaces -- */
    --radius: 10px;
    --radius-sm: 6px;
    --glass-blur: 20px;
    --glass-bg: rgba(255,255,255,0.022);
    --glass-border: rgba(255,255,255,0.05);
    --glass-shadow: 0 2px 16px rgba(0,0,0,0.18);
    --transition: 180ms ease;
}

/* ================================================================
   1. BASE & BACKGROUND
   ================================================================ */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.stApp {
    background: var(--bg) !important;
    background-image: none !important;
    color: var(--text);
}
.stApp [data-testid="stHeader"] { background: var(--bg) !important; }
[data-testid="stAppViewContainer"] { background: var(--bg) !important; }
[data-testid="stBottomBlockContainer"] { background: var(--bg) !important; }
.main .block-container { background: var(--bg) !important; }

/* ================================================================
   2. TYPOGRAPHY
   ================================================================ */
.stMarkdown p, .stMarkdown li {
    font-family: var(--font-body) !important;
    font-size: 0.88rem;
    line-height: 1.6;
    color: var(--text-secondary);
}
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-display) !important;
    color: var(--text) !important;
}

/* ================================================================
   3. SIDEBAR
   ================================================================ */
section[data-testid="stSidebar"] {
    background: rgba(15,17,20,0.94) !important;
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border-right: 1px solid var(--border-subtle) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 24px;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    font-family: var(--font-body) !important;
}

/* ================================================================
   4. METRICS (KPI cards)
   ================================================================ */
div[data-testid="metric-container"] {
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 18px 22px;
    box-shadow: var(--glass-shadow);
    transition: border-color var(--transition), background var(--transition);
}
div[data-testid="metric-container"]:hover {
    border-color: var(--border-hover);
    background: var(--surface-hover);
}
[data-testid="stMetricLabel"] {
    font-family: var(--font-body) !important;
    font-size: 0.68rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--font-body) !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: -0.03em !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
}

/* ================================================================
   5. TABS (Navigation)
   ================================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-body) !important;
    background: transparent;
    border-radius: 0;
    padding: 11px 22px;
    color: var(--text-muted);
    font-size: 0.82rem;
    font-weight: 500;
    border: none;
    border-bottom: 2px solid transparent;
    transition: color var(--transition), border-color var(--transition);
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary);
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    background: transparent !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600;
}

/* ================================================================
   6. DATAFRAMES & TABLES
   ================================================================ */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}

/* ================================================================
   7. BUTTONS
   ================================================================ */
.stButton > button {
    font-family: var(--font-body) !important;
    background: var(--glass-bg) !important;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    padding: 9px 18px !important;
    transition: all var(--transition) !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--surface-hover) !important;
    border-color: var(--border-hover) !important;
    color: var(--text) !important;
}
.stButton > button:active {
    background: var(--surface-active) !important;
}
.stDownloadButton > button {
    font-family: var(--font-body) !important;
    background: var(--accent-soft) !important;
    border: 1px solid rgba(212,175,97,0.2) !important;
    color: var(--accent) !important;
    font-weight: 500 !important;
}
.stDownloadButton > button:hover {
    background: rgba(212,175,97,0.18) !important;
    color: var(--accent) !important;
}

/* ================================================================
   8. INPUTS & SELECTS
   ================================================================ */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="popover"] > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
}
div[data-baseweb="select"] > div:hover,
div[data-baseweb="input"] > div:hover {
    border-color: var(--border-hover) !important;
}
.stDateInput > div > div > div {
    background: var(--surface) !important;
}
.stMultiSelect > div > div {
    background: var(--surface) !important;
}
.stSelectbox label, .stMultiSelect label, .stDateInput label {
    font-family: var(--font-body) !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: var(--text-muted) !important;
}
.stTextInput label {
    font-family: var(--font-body) !important;
    color: var(--text-muted) !important;
}

/* ================================================================
   9. EXPANDERS
   ================================================================ */
.streamlit-expanderHeader {
    font-family: var(--font-body) !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
}

/* ================================================================
   10. SCROLLBAR
   ================================================================ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.07); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.13); }

/* ================================================================
   11. CUSTOM COMPONENTS
   ================================================================ */
/* -- App header -- */
.app-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 0 0 20px 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 28px;
}
.app-brand { display: flex; flex-direction: column; gap: 3px; }
.app-brand-name {
    font-family: var(--font-display);
    font-size: 1.35rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.01em;
}
.app-brand-sub {
    font-family: var(--font-body);
    font-size: 0.74rem;
    color: var(--text-muted);
    font-weight: 400;
    letter-spacing: 0.01em;
}
.app-status {
    display: flex;
    align-items: center;
    gap: 16px;
    font-family: var(--font-body);
    font-size: 0.72rem;
    color: var(--text-secondary);
}

/* -- Status dot -- */
.status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.status-dot-healthy { background: var(--success); box-shadow: 0 0 8px rgba(98,184,122,0.35); }
.status-dot-stale { background: var(--warning); box-shadow: 0 0 8px rgba(212,168,78,0.35); }
.status-dot-offline { background: var(--danger); box-shadow: 0 0 8px rgba(212,115,106,0.35); }

/* -- Section headers -- */
.section-label {
    font-family: var(--font-body);
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-dim);
    margin-bottom: 12px;
    margin-top: 28px;
}
.section-title {
    font-family: var(--font-display);
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 4px;
}
.section-caption {
    font-family: var(--font-body);
    font-size: 0.74rem;
    color: var(--text-muted);
    margin-bottom: 16px;
    line-height: 1.5;
}

/* -- Glass panel -- */
.glass-panel {
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 20px;
    box-shadow: var(--glass-shadow);
    margin-bottom: 16px;
}

/* -- Sidebar elements -- */
.sidebar-brand {
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: 0.02em;
    margin-bottom: 2px;
}
.sidebar-sub {
    font-family: var(--font-body);
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-subtle);
    letter-spacing: 0.01em;
}
.sidebar-label {
    font-family: var(--font-body);
    font-size: 0.62rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-dim);
    margin-top: 20px;
    margin-bottom: 10px;
}

/* -- Pipeline info -- */
.pipeline-info {
    background: var(--surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 14px;
    margin-top: 20px;
}
.pipeline-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.72rem;
    padding: 4px 0;
}
.pipeline-key {
    font-family: var(--font-body);
    color: var(--text-muted);
    font-size: 0.7rem;
}
.pipeline-val {
    font-family: var(--font-mono);
    color: var(--text-secondary);
    font-size: 0.68rem;
}

/* -- KPI blocks -- */
.kpi-label {
    font-family: var(--font-body);
    font-size: 0.64rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted);
    margin-bottom: 4px;
}
.kpi-value {
    font-family: var(--font-body);
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.035em;
    line-height: 1.1;
}
.kpi-secondary-value {
    font-family: var(--font-body);
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.02em;
    line-height: 1.1;
}
.kpi-context {
    font-family: var(--font-mono);
    font-size: 0.66rem;
    font-weight: 300;
    color: var(--text-dim);
    margin-top: 6px;
}

/* -- Divider -- */
.divider { height: 1px; background: var(--border-subtle); margin: 28px 0; }

/* -- Data explorer -- */
.data-explorer-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-subtle);
}
.data-explorer-title {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text);
}
.data-explorer-sub {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-top: 3px;
}
.data-explorer-meta {
    display: flex;
    gap: 24px;
    font-family: var(--font-body);
    font-size: 0.72rem;
    color: var(--text-muted);
}
.data-explorer-meta span {
    font-family: var(--font-mono);
    color: var(--text-secondary);
    font-size: 0.7rem;
    font-weight: 400;
}

/* -- About sections -- */
.about-section {
    background: var(--surface);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius);
    padding: 22px 26px;
    margin-bottom: 14px;
}
.about-section-title {
    font-family: var(--font-display);
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 10px;
}
.about-section-body {
    font-family: var(--font-body);
    font-size: 0.8rem;
    color: var(--text-secondary);
    line-height: 1.75;
}
.about-section-body strong {
    color: var(--text);
    font-weight: 600;
}

/* -- Status tags -- */
.status-tag { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.66rem; font-weight: 500; font-family: var(--font-body); }
.status-tag-risk { background: var(--warning-soft); color: var(--warning); }
.status-tag-churned { background: var(--danger-soft); color: var(--danger); }
.status-tag-active { background: var(--success-soft); color: var(--success); }

/* ================================================================
   12. HIDE STREAMLIT CHROME
   ================================================================ */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: var(--bg) !important; }
</style>
"""

# -- Chart palette --
PALETTE = {
    "primary": "#d4af61",
    "secondary": "#7a9eb8",
    "tertiary": "#9484b8",
    "muted": "#5c5850",
    "success": "#62b87a",
    "danger": "#d4736a",
    "warning": "#d4a84e",
    "sequence": ["#d4af61", "#7a9eb8", "#9484b8", "#62b87a", "#d4736a", "#6ab8a0", "#b8a06a"],
}


def apply_chart_theme(fig, height=320, showlegend=True, legend=None, margin=None):
    """Apply consistent dark glass theme to all Plotly figures."""
    fig.update_layout(
        height=height,
        margin=margin or dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, Inter, sans-serif", color="#a09a90", size=11),
        showlegend=showlegend,
        hoverlabel=dict(
            bgcolor="rgba(15,17,20,0.96)",
            font_size=12,
            font_family="DM Sans",
            font_color="#ece8e1",
            bordercolor="rgba(255,255,255,0.07)",
        ),
    )
    if legend:
        fig.update_layout(legend=legend)
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.035)",
        zeroline=False, showline=True, linecolor="rgba(255,255,255,0.05)",
        tickfont=dict(size=10, family="DM Sans"),
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.035)",
        zeroline=False, showline=False,
        tickfont=dict(size=10, family="DM Sans"),
    )
    return fig


# -- Number formatting --
def fmt_currency(val):
    """Format currency with Indian Rupee symbol, adaptive magnitude."""
    if val is None:
        return "---"
    av = abs(val)
    if av >= 1_00_00_000:
        return f"{'−' if val < 0 else ''}₹{av/1_00_00_000:,.2f}Cr"
    if av >= 1_00_000:
        return f"{'−' if val < 0 else ''}₹{av/1_00_000:,.1f}L"
    if av >= 1_000:
        return f"{'−' if val < 0 else ''}₹{av/1_000:,.1f}K"
    return f"{'−' if val < 0 else ''}₹{av:,.0f}"


def fmt_number(val):
    """Format integer with commas."""
    if val is None:
        return "---"
    return f"{int(val):,}"


def fmt_pct(val):
    """Format percentage."""
    if val is None:
        return "---"
    return f"{val:.1f}%"


# -- Reusable HTML helpers --
def section_header(title, caption=None):
    """Render a section title with optional caption."""
    html = f'<div class="section-title">{title}</div>'
    if caption:
        html += f'<div class="section-caption">{caption}</div>'
    return html


def kpi_block(label, value, context=None, primary=True):
    """Render a KPI block as HTML."""
    cls = "kpi-value" if primary else "kpi-secondary-value"
    html = f'<div class="kpi-label">{label}</div><div class="{cls}">{value}</div>'
    if context:
        html += f'<div class="kpi-context">{context}</div>'
    return html
