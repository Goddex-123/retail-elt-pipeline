# -*- coding: utf-8 -*-
"""
Dashboard UI Design System
===========================
Reusable CSS, components, and formatting helpers.
"""

# -- CSS Variables & Theme --
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #111316;
    --bg-warm: #14161a;
    --surface: rgba(255,255,255,0.028);
    --surface-hover: rgba(255,255,255,0.048);
    --surface-active: rgba(255,255,255,0.065);
    --border: rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.10);
    --border-subtle: rgba(255,255,255,0.035);
    --text: #e8e4df;
    --text-secondary: #9a9489;
    --text-muted: #5c5850;
    --text-dim: #3d3a35;
    --accent: #c9a96e;
    --accent-muted: rgba(201,169,110,0.15);
    --danger: #c9655a;
    --warning: #c9a355;
    --success: #5aad72;
    --radius: 8px;
    --radius-sm: 5px;
    --glass-blur: 18px;
    --glass-bg: rgba(255,255,255,0.025);
    --glass-border: rgba(255,255,255,0.055);
    --glass-shadow: 0 4px 24px rgba(0,0,0,0.2);
    --transition: 160ms ease;
}

/* -- Base -- */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 80% 60% at 20% 40%, rgba(201,169,110,0.018) 0%, transparent 70%),
        radial-gradient(ellipse 60% 50% at 80% 20%, rgba(140,160,180,0.012) 0%, transparent 70%);
    color: var(--text);
}

/* -- Sidebar -- */
section[data-testid="stSidebar"] {
    background: rgba(17,19,22,0.92) !important;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border-right: 1px solid var(--border-subtle) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 20px;
}

/* -- Metric containers -- */
div[data-testid="metric-container"] {
    background: var(--glass-bg);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius);
    padding: 16px 20px;
    box-shadow: var(--glass-shadow);
    transition: border-color var(--transition), background var(--transition);
}
div[data-testid="metric-container"]:hover {
    border-color: var(--border-hover);
    background: var(--surface-hover);
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--text-secondary) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    letter-spacing: -0.025em !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.7rem !important;
    font-weight: 500 !important;
}

/* -- Tabs -- */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
    padding-bottom: 0;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 0;
    padding: 10px 20px;
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 500;
    border: none;
    border-bottom: 2px solid transparent;
    transition: color var(--transition), border-color var(--transition);
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text);
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    background: transparent !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600;
}

/* -- DataFrames -- */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
}

/* -- Buttons -- */
.stButton > button {
    background: var(--glass-bg) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
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

/* -- Inputs / Selects -- */
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="popover"] > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
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
    font-size: 0.7rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    color: var(--text-muted) !important;
}

/* -- Expanders -- */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-size: 0.85rem !important;
}

/* -- Scrollbar -- */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.14); }

/* -- Custom components -- */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 0 20px 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 24px;
}
.app-brand { display: flex; flex-direction: column; gap: 2px; }
.app-brand-name { font-size: 1.15rem; font-weight: 600; color: var(--text); letter-spacing: -0.01em; }
.app-brand-sub { font-size: 0.72rem; color: var(--text-muted); font-weight: 400; }
.app-status { display: flex; align-items: center; gap: 16px; font-size: 0.72rem; color: var(--text-secondary); }
.status-dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; margin-right: 5px; }
.status-dot-healthy { background: var(--success); box-shadow: 0 0 6px rgba(90,173,114,0.4); }
.status-dot-stale { background: var(--warning); box-shadow: 0 0 6px rgba(201,163,85,0.4); }
.status-dot-offline { background: var(--danger); box-shadow: 0 0 6px rgba(201,101,90,0.4); }

.section-label { font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; color: var(--text-muted); margin-bottom: 12px; margin-top: 24px; }
.section-title { font-size: 0.92rem; font-weight: 600; color: var(--text); margin-bottom: 4px; }
.section-caption { font-size: 0.72rem; color: var(--text-secondary); margin-bottom: 16px; line-height: 1.4; }

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

.sidebar-brand { font-size: 0.82rem; font-weight: 600; color: var(--text); letter-spacing: 0.04em; margin-bottom: 1px; }
.sidebar-sub { font-size: 0.68rem; color: var(--text-muted); margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--border-subtle); }
.sidebar-label { font-size: 0.62rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-top: 20px; margin-bottom: 8px; }

.pipeline-info { background: var(--surface); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 12px; margin-top: 16px; }
.pipeline-row { display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; padding: 3px 0; }
.pipeline-key { color: var(--text-muted); }
.pipeline-val { color: var(--text-secondary); font-family: 'SF Mono', 'Cascadia Code', monospace; font-size: 0.68rem; }

.kpi-label { font-size: 0.62rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-secondary); margin-bottom: 2px; }
.kpi-value { font-size: 1.6rem; font-weight: 600; color: var(--text); letter-spacing: -0.03em; line-height: 1.1; }
.kpi-secondary-value { font-size: 1.15rem; font-weight: 600; color: var(--text); letter-spacing: -0.02em; line-height: 1.1; }
.kpi-context { font-size: 0.68rem; color: var(--text-muted); margin-top: 4px; }
.divider { height: 1px; background: var(--border-subtle); margin: 24px 0; }

.data-explorer-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.data-explorer-title { font-size: 1.05rem; font-weight: 600; color: var(--text); }
.data-explorer-meta { display: flex; gap: 20px; font-size: 0.7rem; color: var(--text-secondary); }
.data-explorer-meta span { font-family: 'SF Mono', 'Cascadia Code', monospace; color: var(--text); font-size: 0.68rem; }

.about-section { background: var(--surface); border: 1px solid var(--border-subtle); border-radius: var(--radius); padding: 20px 24px; margin-bottom: 12px; }
.about-section-title { font-size: 0.78rem; font-weight: 600; color: var(--text); margin-bottom: 8px; }
.about-section-body { font-size: 0.78rem; color: var(--text-secondary); line-height: 1.65; }
.about-section-body strong { color: var(--text); font-weight: 500; }

.status-tag { display: inline-block; padding: 2px 8px; border-radius: 3px; font-size: 0.65rem; font-weight: 500; }
.status-tag-risk { background: rgba(201,163,85,0.12); color: var(--warning); }
.status-tag-churned { background: rgba(201,101,90,0.12); color: var(--danger); }
.status-tag-active { background: rgba(90,173,114,0.12); color: var(--success); }

/* -- Hide Streamlit branding -- */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
</style>
"""

# -- Chart palette (restrained) --
PALETTE = {
    "primary": "#c9a96e",
    "secondary": "#7a9bb5",
    "tertiary": "#8a7eb5",
    "muted": "#5c5850",
    "success": "#5aad72",
    "danger": "#c9655a",
    "warning": "#c9a355",
    "sequence": ["#c9a96e", "#7a9bb5", "#8a7eb5", "#6aaa8a", "#b57a7a", "#7ab5a5", "#b5a37a"],
}


def apply_chart_theme(fig, height=320, showlegend=True, legend=None, margin=None):
    """Apply consistent dark glass theme to all Plotly figures."""
    fig.update_layout(
        height=height,
        margin=margin or dict(l=0, r=0, t=8, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#9a9489", size=11),
        showlegend=showlegend,
        hoverlabel=dict(
            bgcolor="rgba(20,22,26,0.95)",
            font_size=12,
            font_family="Inter",
            font_color="#e8e4df",
            bordercolor="rgba(255,255,255,0.08)",
        ),
    )
    if legend:
        fig.update_layout(legend=legend)
    fig.update_xaxes(
        showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.04)",
        zeroline=False, showline=True, linecolor="rgba(255,255,255,0.06)",
        tickfont=dict(size=10),
    )
    fig.update_yaxes(
        showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.04)",
        zeroline=False, showline=False,
        tickfont=dict(size=10),
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
