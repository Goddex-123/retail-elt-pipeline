# -*- coding: utf-8 -*-
"""
Dashboard UI Design System
===========================
Premium dark analytical workspace design system with multi-font typography,
balanced color science, zero-white scrollbars, and refined micro-interactions.
"""

# -- CSS Variables & Global Stylesheet --
THEME_CSS = """
<style>
/* ================================================================
   0. MULTI-FONT TYPOGRAPHY SYSTEM
   - Plus Jakarta Sans: UI, body, buttons, tables, filters
   - Playfair Display: Luxury brand identity & narrative titles
   - Space Grotesk: Section labels, category kickers, KPI subheaders
   - JetBrains Mono: Tabular figures, metrics, currency, codes, timestamps
   ================================================================ */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,400&family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    /* Color scheme hints for browser engine (prevents native white scrollbars) */
    color-scheme: dark !important;

    /* -- Font Families -- */
    --font-body: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-display: 'Playfair Display', Georgia, serif;
    --font-heading: 'Plus Jakarta Sans', sans-serif;
    --font-kicker: 'Space Grotesk', sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', monospace;

    /* -- Canvas & Elevation (Balanced Dark Slate) -- */
    --bg-base: #0b0d10;
    --bg-surface: #11141a;
    --bg-surface-elevated: #161a22;
    --bg-surface-card: rgba(255, 255, 255, 0.028);
    --bg-surface-hover: rgba(255, 255, 255, 0.055);
    --bg-surface-active: rgba(255, 255, 255, 0.08);

    /* -- Borders & Dividers -- */
    --border-subtle: rgba(255, 255, 255, 0.05);
    --border-base: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(255, 255, 255, 0.15);
    --border-accent: rgba(223, 177, 91, 0.35);

    /* -- Typography Colors (WCAG AAA/AA Compliant) -- */
    --text-primary: #f4f5f7;       /* 96% luminance */
    --text-secondary: #a2aab8;     /* 68% luminance */
    --text-muted: #6b7385;         /* 45% luminance */
    --text-dim: #484f5e;           /* 32% luminance */

    /* -- Accent & Semantic Palette (Harmonized Saturation) -- */
    --accent: #dfb15b;             /* Champagne Gold */
    --accent-glow: rgba(223, 177, 91, 0.14);
    --accent-hover: #e8c274;

    --success: #4ade80;            /* Emerald */
    --success-soft: rgba(74, 222, 128, 0.12);

    --warning: #fbbf24;            /* Amber */
    --warning-soft: rgba(251, 191, 36, 0.12);

    --danger: #f87171;             /* Coral Red */
    --danger-soft: rgba(248, 113, 113, 0.12);

    --info: #5eb1d6;               /* Sky Cyan */
    --info-soft: rgba(94, 177, 214, 0.12);

    --purple: #a78bfa;             /* Lavender */
    --purple-soft: rgba(167, 139, 250, 0.12);

    /* -- Geometry & Shadows -- */
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --glass-blur: 20px;
    --card-shadow: 0 4px 24px -2px rgba(0, 0, 0, 0.35);
    --transition: all 180ms cubic-bezier(0.16, 1, 0.3, 1);
}

/* ================================================================
   1. GLOBAL SCROLLBARS — ZERO WHITE SCROLLBARS
   Styles native Chromium, Firefox, WebKit, and Streamlit inner scrollbars
   ================================================================ */
html, body, :root {
    color-scheme: dark !important;
}

* {
    scrollbar-width: thin !important;
    scrollbar-color: rgba(255, 255, 255, 0.16) transparent !important;
}

*::-webkit-scrollbar {
    width: 6px !important;
    height: 6px !important;
    background-color: transparent !important;
}

*::-webkit-scrollbar-track {
    background-color: transparent !important;
}

*::-webkit-scrollbar-thumb {
    background-color: rgba(255, 255, 255, 0.14) !important;
    border-radius: 10px !important;
}

*::-webkit-scrollbar-thumb:hover {
    background-color: rgba(255, 255, 255, 0.26) !important;
}

*::-webkit-scrollbar-corner {
    background-color: transparent !important;
}

/* ================================================================
   2. STREAMLIT ROOT & CANVAS OVERRIDES
   ================================================================ */
html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    background-color: var(--bg-base) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.stApp {
    background-color: var(--bg-base) !important;
    background-image: none !important;
    color: var(--text-primary);
}

.stApp [data-testid="stHeader"] {
    background: var(--bg-base) !important;
    border-bottom: 1px solid var(--border-subtle);
}

[data-testid="stAppViewContainer"] {
    background-color: var(--bg-base) !important;
}

[data-testid="stBottomBlockContainer"] {
    background-color: var(--bg-base) !important;
}

.main .block-container {
    background-color: var(--bg-base) !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px;
}

/* Remove default Streamlit top decoration line */
div[data-testid="stDecoration"],
header[data-testid="stHeader"]::before {
    display: none !important;
}

/* ================================================================
   3. SIDEBAR NAVIGATION & CONTROLS
   ================================================================ */
section[data-testid="stSidebar"] {
    background-color: #0d1015 !important;
    border-right: 1px solid var(--border-subtle) !important;
}

section[data-testid="stSidebar"] > div:first-child {
    padding-top: 22px;
}

section[data-testid="stSidebar"] * {
    scrollbar-width: thin !important;
    scrollbar-color: rgba(255, 255, 255, 0.14) transparent !important;
}

/* Sidebar Labels */
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stDateInput label {
    font-family: var(--font-kicker) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--text-muted) !important;
    margin-bottom: 6px !important;
}

/* ================================================================
   4. INPUTS, SELECTS, DATE PICKER & CHIPS (FIX WHITE BOXES & RED CHIPS)
   ================================================================ */
/* All Inputs (Text, Date, Number) */
div[data-baseweb="input"],
div[data-baseweb="input"] > div,
div[data-baseweb="input"] input,
.stDateInput input,
.stTextInput input,
.stNumberInput input {
    background-color: #14171d !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-base) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
}

div[data-baseweb="input"] input:focus,
.stDateInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent-glow) !important;
}

/* Selectbox Dropdowns */
div[data-baseweb="select"] > div {
    background-color: #14171d !important;
    border: 1px solid var(--border-base) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    font-size: 0.82rem !important;
    color: var(--text-primary) !important;
}

div[data-baseweb="select"] > div:hover {
    border-color: var(--border-hover) !important;
}

/* Popovers / Calendar Datepicker Menu */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="calendar"],
div[data-baseweb="calendar"] * {
    background-color: #14171d !important;
    color: var(--text-primary) !important;
    border-color: var(--border-base) !important;
}

/* Multi-select Region Chips — Transform tomato red into refined champagne gold */
span[data-baseweb="tag"],
div[data-baseweb="tag"] {
    background: rgba(223, 177, 91, 0.12) !important;
    border: 1px solid rgba(223, 177, 91, 0.28) !important;
    border-radius: 4px !important;
    padding: 3px 9px !important;
    transition: var(--transition) !important;
}

span[data-baseweb="tag"] span,
span[data-baseweb="tag"] div,
div[data-baseweb="tag"] span {
    color: #e5be6c !important;
    font-family: var(--font-body) !important;
    font-size: 0.74rem !important;
    font-weight: 500 !important;
}

span[data-baseweb="tag"] svg,
div[data-baseweb="tag"] svg {
    fill: #e5be6c !important;
}

span[data-baseweb="tag"]:hover {
    background: rgba(223, 177, 91, 0.22) !important;
    border-color: rgba(223, 177, 91, 0.45) !important;
}

/* ================================================================
   5. NAVIGATION TABS
   ================================================================ */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 0;
    background: transparent;
}

.stTabs [data-baseweb="tab"] {
    font-family: var(--font-heading) !important;
    background: transparent !important;
    border-radius: 0;
    padding: 11px 20px;
    color: var(--text-muted);
    font-size: 0.84rem;
    font-weight: 500;
    border: none;
    border-bottom: 2px solid transparent;
    transition: var(--transition);
}

.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-secondary) !important;
}

.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600 !important;
}

/* BaseWeb Tab Highlight underline */
div[data-baseweb="tab-highlight"] {
    background-color: var(--accent) !important;
    height: 2px !important;
}

div[data-baseweb="tab-border"] {
    background-color: var(--border-subtle) !important;
}

/* ================================================================
   6. METRIC (KPI) CARDS & KPI RAIL
   ================================================================ */
div[data-testid="metric-container"] {
    background: var(--bg-surface-card);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    box-shadow: var(--card-shadow);
    transition: var(--transition);
}

div[data-testid="metric-container"]:hover {
    border-color: var(--border-hover);
    background: var(--bg-surface-hover);
    transform: translateY(-1px);
}

[data-testid="stMetricLabel"] {
    font-family: var(--font-kicker) !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    color: var(--text-muted) !important;
}

[data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    font-variant-numeric: tabular-nums;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em !important;
}

/* Custom KPI HTML block */
.kpi-card {
    background: var(--bg-surface-card);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    box-shadow: var(--card-shadow);
    transition: var(--transition);
}

.kpi-card:hover {
    border-color: var(--border-hover);
    background: var(--bg-surface-hover);
}

.kpi-label {
    font-family: var(--font-kicker);
    font-size: 0.66rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.kpi-value {
    font-family: var(--font-mono);
    font-size: 1.75rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    color: var(--text-primary);
    letter-spacing: -0.03em;
    line-height: 1.1;
}

.kpi-secondary-value {
    font-family: var(--font-mono);
    font-size: 1.25rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.1;
}

.kpi-context {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 400;
    color: var(--text-secondary);
    margin-top: 7px;
    opacity: 0.85;
}

/* ================================================================
   7. DATAFRAMES & TABLES
   ================================================================ */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
}

div[data-testid="stDataFrame"] * {
    scrollbar-width: thin !important;
    scrollbar-color: rgba(255, 255, 255, 0.16) transparent !important;
}

/* ================================================================
   8. BUTTONS
   ================================================================ */
.stButton > button {
    font-family: var(--font-heading) !important;
    background: var(--bg-surface-card) !important;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid var(--border-base) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 8px 16px !important;
    transition: var(--transition) !important;
    box-shadow: none !important;
}

.stButton > button:hover {
    background: var(--bg-surface-hover) !important;
    border-color: var(--border-hover) !important;
    color: var(--text-primary) !important;
    transform: translateY(-1px);
}

.stButton > button:active {
    background: var(--bg-surface-active) !important;
    transform: translateY(0);
}

.stDownloadButton > button {
    font-family: var(--font-heading) !important;
    background: var(--accent-glow) !important;
    border: 1px solid var(--border-accent) !important;
    color: var(--accent) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    border-radius: var(--radius-sm) !important;
    transition: var(--transition) !important;
}

.stDownloadButton > button:hover {
    background: rgba(223, 177, 91, 0.22) !important;
    border-color: var(--accent) !important;
    color: #f7d88e !important;
}

/* ================================================================
   9. CUSTOM BRAND & SECTION HEADINGS
   ================================================================ */
.app-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    padding: 0 0 18px 0;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 24px;
}

.app-brand {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.app-brand-name {
    font-family: var(--font-display);
    font-size: 1.55rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.015em;
    line-height: 1.2;
}

.app-brand-sub {
    font-family: var(--font-body);
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 400;
    letter-spacing: 0.01em;
}

.app-status {
    display: flex;
    align-items: center;
    gap: 14px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-secondary);
}

.status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

.status-dot-healthy {
    background: var(--success);
    box-shadow: 0 0 8px rgba(74, 222, 128, 0.5);
}

.status-dot-stale {
    background: var(--warning);
    box-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
}

.status-dot-offline {
    background: var(--danger);
    box-shadow: 0 0 8px rgba(248, 113, 113, 0.5);
}

/* Section Headings */
.section-title {
    font-family: var(--font-heading);
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    margin-bottom: 3px;
    margin-top: 14px;
}

.section-caption {
    font-family: var(--font-body);
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-bottom: 14px;
    line-height: 1.5;
}

/* Sidebar Branding */
.sidebar-brand {
    font-family: var(--font-display);
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text-primary);
    letter-spacing: 0.01em;
    margin-bottom: 2px;
}

.sidebar-sub {
    font-family: var(--font-body);
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-bottom: 18px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border-subtle);
}

.sidebar-label {
    font-family: var(--font-kicker);
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-dim);
    margin-top: 18px;
    margin-bottom: 8px;
}

/* Pipeline Metadata Card in Sidebar */
.pipeline-info {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    margin-top: 16px;
}

.pipeline-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
}

.pipeline-key {
    font-family: var(--font-body);
    color: var(--text-muted);
    font-size: 0.72rem;
}

.pipeline-val {
    font-family: var(--font-mono);
    color: var(--text-secondary);
    font-size: 0.7rem;
    font-weight: 500;
}

/* Divider */
.divider {
    height: 1px;
    background: var(--border-subtle);
    margin: 24px 0;
}

/* Data Explorer Header */
.data-explorer-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin-bottom: 18px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border-subtle);
}

.data-explorer-title {
    font-family: var(--font-heading);
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
}

.data-explorer-sub {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--accent);
    margin-top: 3px;
}

.data-explorer-meta {
    display: flex;
    gap: 20px;
    font-family: var(--font-body);
    font-size: 0.74rem;
    color: var(--text-muted);
}

.data-explorer-meta span {
    font-family: var(--font-mono);
    color: var(--text-primary);
    font-weight: 600;
}

/* About / Insights Section Card */
.about-section {
    background: var(--bg-surface-card);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 22px 26px;
    margin-bottom: 14px;
}

.about-section-title {
    font-family: var(--font-heading);
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.about-section-body {
    font-family: var(--font-body);
    font-size: 0.82rem;
    color: var(--text-secondary);
    line-height: 1.75;
}

.about-section-body strong {
    color: var(--text-primary);
    font-weight: 600;
}

/* Status Tags */
.status-tag {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.68rem;
    font-weight: 600;
    font-family: var(--font-mono);
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.status-tag-risk {
    background: var(--warning-soft);
    color: var(--warning);
    border: 1px solid rgba(251, 191, 36, 0.25);
}

.status-tag-churned {
    background: var(--danger-soft);
    color: var(--danger);
    border: 1px solid rgba(248, 113, 113, 0.25);
}

.status-tag-active {
    background: var(--success-soft);
    color: var(--success);
    border: 1px solid rgba(74, 222, 128, 0.25);
}

/* ================================================================
   10. CHROME CLEANUP
   ================================================================ */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: var(--bg-base) !important; }
</style>
"""

# -- Balanced Chart Palette (Equal Perceptual Luminance) --
PALETTE = {
    "primary": "#dfb15b",       # Champagne Gold
    "secondary": "#5eb1d6",     # Sky Blue
    "tertiary": "#a78bfa",      # Lavender
    "success": "#4ade80",       # Emerald Green
    "warning": "#fbbf24",       # Warm Amber
    "danger": "#f87171",        # Coral Red
    "muted": "#525968",         # Slate Neutral
    "sequence": [
        "#dfb15b",  # Gold
        "#5eb1d6",  # Sky Blue
        "#a78bfa",  # Lavender
        "#4ade80",  # Emerald
        "#f87171",  # Coral
        "#e5be6c",  # Light Amber
        "#38bdf8",  # Cyan
    ],
}


def apply_chart_theme(fig, height=320, showlegend=True, legend=None, margin=None):
    """
    Apply a consistent high-end dark glass theme to Plotly figures.
    Uses Plus Jakarta Sans for UI labels, JetBrains Mono for axes numbers,
    and ample right margin to ensure horizontal bar text is never clipped.
    """
    default_margin = dict(l=0, r=48, t=12, b=0)
    fig.update_layout(
        height=height,
        margin=margin or default_margin,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Plus Jakarta Sans, sans-serif",
            color="#a2aab8",
            size=11,
        ),
        showlegend=showlegend,
        hoverlabel=dict(
            bgcolor="#14171d",
            font_size=11.5,
            font_family="Plus Jakarta Sans",
            font_color="#f4f5f7",
            bordercolor="rgba(255, 255, 255, 0.12)",
        ),
    )
    if legend:
        fig.update_layout(legend=legend)
    else:
        fig.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=10.5, family="Plus Jakarta Sans"),
            )
        )

    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255, 255, 255, 0.04)",
        zeroline=False,
        showline=True,
        linecolor="rgba(255, 255, 255, 0.06)",
        tickfont=dict(size=10, family="JetBrains Mono, monospace", color="#838c9d"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255, 255, 255, 0.04)",
        zeroline=False,
        showline=False,
        tickfont=dict(size=10, family="Plus Jakarta Sans, sans-serif", color="#838c9d"),
    )
    return fig


# -- Number Formatting with Tabular Alignment --
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
    """Format integer with standard thousands separator."""
    if val is None:
        return "---"
    return f"{int(val):,}"


def fmt_pct(val):
    """Format percentage to one decimal place."""
    if val is None:
        return "---"
    return f"{val:.1f}%"


# -- Reusable HTML Helpers --
def section_header(title, caption=None):
    """Render a crisp section title with optional caption."""
    html = f'<div class="section-title">{title}</div>'
    if caption:
        html += f'<div class="section-caption">{caption}</div>'
    return html


def kpi_block(label, value, context=None, primary=True):
    """Render a KPI block using glass card styling and monospace numbers."""
    val_cls = "kpi-value" if primary else "kpi-secondary-value"
    html = f'''
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="{val_cls}">{value}</div>
    '''
    if context:
        html += f'<div class="kpi-context">{context}</div>'
    html += '</div>'
    return html
