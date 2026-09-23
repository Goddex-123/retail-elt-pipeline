"""
Retail ELT Platform — Executive Analytics Dashboard
=====================================================
A modern, minimal, professional analytics interface connected
directly to the PostgreSQL Gold layer dimensional warehouse.

Built with Streamlit and Plotly for high readability, clean
information hierarchy, and production-grade data observability.

Access: http://localhost:8501
"""

import os
from datetime import datetime
from typing import Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import streamlit as st

# ============================================================
# 1. Page Configuration
# ============================================================

st.set_page_config(
    page_title="Bombay Bazaar — Executive Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. Design System & CSS
# ============================================================
# Purposeful, minimal stylesheet inspired by modern data platforms
# (Stripe, Datadog, Snowflake Snowsight). Restrained neutral palette,
# high-contrast typography, subtle borders, no decorative gradients.

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 14px 18px;
        transition: border-color 0.2s ease;
    }

    div[data-testid="metric-container"]:hover {
        border-color: #374151;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.725rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #94a3b8 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        color: #f8fafc !important;
        letter-spacing: -0.02em !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 0.775rem !important;
        font-weight: 500 !important;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        border-bottom: 1px solid #1e293b;
        padding-bottom: 0px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 6px 6px 0 0;
        padding: 8px 18px;
        color: #94a3b8;
        font-weight: 500;
        font-size: 0.85rem;
        border: 1px solid transparent;
        border-bottom: none;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #e2e8f0;
        background-color: #1e293b;
    }

    .stTabs [aria-selected="true"] {
        background-color: #111827 !important;
        color: #3b82f6 !important;
        border: 1px solid #1e293b !important;
        border-bottom: 2px solid #3b82f6 !important;
        font-weight: 600 !important;
    }

    /* Section & card containers */
    .card-title {
        font-size: 0.925rem;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 0.2rem;
    }

    .card-caption {
        font-size: 0.75rem;
        color: #64748b;
        margin-bottom: 0.75rem;
    }

    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.725rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .badge-healthy {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }

    .badge-stale {
        background-color: rgba(245, 158, 11, 0.12);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }

    .badge-offline {
        background-color: rgba(239, 68, 68, 0.12);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }

    .badge-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        display: inline-block;
    }

    .dot-healthy { background-color: #10b981; }
    .dot-stale { background-color: #f59e0b; }
    .dot-offline { background-color: #ef4444; }

    /* Sidebar refinement */
    [data-testid="stSidebar"] {
        background-color: #0d131f;
        border-right: 1px solid #1e293b;
    }

    .sidebar-section-title {
        font-size: 0.725rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    .telemetry-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.775rem;
        padding: 4px 0;
        color: #94a3b8;
    }

    .telemetry-val {
        font-weight: 600;
        color: #e2e8f0;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 3. Database Connection & Plotly Theme
# ============================================================


def get_db_url() -> str:
    """Resolve database URL with sensible defaults for container or host."""
    user = os.getenv("POSTGRES_USER", "retail_user")
    password = os.getenv("POSTGRES_PASSWORD", "retail_pass_change_me")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "retail_warehouse")
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


def apply_chart_theme(fig: go.Figure, height: int = 300, **kwargs) -> go.Figure:
    """Apply unified, restrained modern chart styling without keyword collisions."""
    layout = {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "color": "#94a3b8",
            "family": 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            "size": 12,
        },
        "margin": dict(l=40, r=20, t=40, b=40),
        "height": height,
        "xaxis": {
            "gridcolor": "#1e293b",
            "zerolinecolor": "#1e293b",
            "showline": True,
            "linecolor": "#1e293b",
        },
        "yaxis": {
            "gridcolor": "#1e293b",
            "zerolinecolor": "#1e293b",
            "showline": True,
            "linecolor": "#1e293b",
        },
        "hoverlabel": {
            "bgcolor": "#1e293b",
            "font_color": "#f8fafc",
            "font_size": 12,
            "bordercolor": "#334155",
        },
    }
    layout.update(kwargs)
    fig.update_layout(**layout)
    return fig


PALETTE = {
    "primary": "#3b82f6",     # Accent Blue
    "secondary": "#6366f1",   # Indigo
    "emerald": "#10b981",     # Success / Healthy / High Margin
    "amber": "#f59e0b",       # Warning / Moderate / Fair
    "rose": "#ef4444",        # Error / Churned / Low Margin
    "slate": "#64748b",       # Neutral Muted
    "sequence": ["#3b82f6", "#10b981", "#f59e0b", "#6366f1", "#06b6d4", "#ec4899"],
}


@st.cache_data(ttl=60, show_spinner=False)
def load_mart(table_name: str) -> Optional[pd.DataFrame]:
    """Safely load a gold mart table with caching."""
    try:
        engine = create_engine(get_db_url(), pool_pre_ping=True)
        return pd.read_sql(f"SELECT * FROM gold.{table_name}", engine)
    except Exception:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def get_pipeline_freshness() -> Tuple[Optional[datetime], Optional[float]]:
    """Check when the bronze layer was last refreshed."""
    try:
        engine = create_engine(get_db_url(), pool_pre_ping=True)
        result = pd.read_sql(
            "SELECT MAX(_loaded_at::timestamp) as last_load FROM bronze.customers",
            engine,
        )
        last_load = result["last_load"].iloc[0]
        if last_load is not None and not pd.isna(last_load):
            hours_ago = (datetime.utcnow() - last_load).total_seconds() / 3600
            return last_load, round(hours_ago, 1)
    except Exception:
        pass
    return None, None


# ============================================================
# 4. Data Loading & Diagnostics
# ============================================================

fct_orders = load_mart("fct_orders")
daily_sales = load_mart("daily_sales")
clv = load_mart("customer_lifetime_value")
churn = load_mart("churn_risk")
top_prods = load_mart("top_products")
region_rev = load_mart("revenue_by_region")
payment_rates = load_mart("payment_success_rate")
stock_alerts = load_mart("stock_alerts")
inv_turnover = load_mart("inventory_turnover")
gross_margin = load_mart("gross_margin")
refund_data = load_mart("refund_analysis")
last_load, hours_ago = get_pipeline_freshness()

# Determine health status
if last_load is not None:
    if hours_ago <= 6:
        status_label = "Pipeline Active"
        status_sub = f"Last ingested {hours_ago}h ago"
        badge_class = "badge-healthy"
        dot_class = "dot-healthy"
    elif hours_ago <= 24:
        status_label = "Data Stale"
        status_sub = f"Last run {hours_ago}h ago"
        badge_class = "badge-stale"
        dot_class = "dot-stale"
    else:
        status_label = "SLA Breach"
        status_sub = f"Last run {hours_ago}h ago (>24h)"
        badge_class = "badge-offline"
        dot_class = "dot-offline"
else:
    status_label = "Warehouse Unreachable"
    status_sub = "No bronze records detected"
    badge_class = "badge-offline"
    dot_class = "dot-offline"

# ============================================================
# 5. Sidebar Controls & Telemetry
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding-bottom: 12px; border-bottom: 1px solid #1e293b; margin-bottom: 16px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.01em;">
                Bombay Bazaar
            </div>
            <div style="font-size: 0.775rem; color: #64748b; margin-top: 2px;">
                Retail ELT Platform · Medallion Gold
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Health badge
    st.markdown(
        f"""
        <div class="status-badge {badge_class}" style="width: 100%; justify-content: center; margin-bottom: 16px;">
            <span class="badge-dot {dot_class}"></span>
            <span>{status_label}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("↻ Refresh Warehouse Data", use_container_width=True, type="secondary"):
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div class="sidebar-section-title">Filters</div>', unsafe_allow_html=True)

    available_regions = ["North", "South", "East", "West"]
    selected_regions = st.multiselect(
        "Geographic Regions",
        options=available_regions,
        default=available_regions,
        help="Filters downstream sales, order counts, and regional metrics.",
    )

    status_options = ["All", "completed", "pending", "shipped", "cancelled", "returned"]
    selected_status = st.selectbox(
        "Order Status",
        options=status_options,
        index=0,
        help="Filter transactions by fulfillment status.",
    )

    st.markdown('<div class="sidebar-section-title">Warehouse Telemetry</div>', unsafe_allow_html=True)
    host_display = os.getenv("POSTGRES_HOST", "postgres")
    db_display = os.getenv("POSTGRES_DB", "retail_warehouse")

    st.markdown(
        f"""
        <div style="background-color: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 12px; margin-bottom: 16px;">
            <div class="telemetry-row">
                <span>Warehouse</span>
                <span class="telemetry-val">PostgreSQL 13</span>
            </div>
            <div class="telemetry-row">
                <span>Host</span>
                <span class="telemetry-val">{host_display}:5432</span>
            </div>
            <div class="telemetry-row">
                <span>Database</span>
                <span class="telemetry-val">{db_display}</span>
            </div>
            <div class="telemetry-row">
                <span>Active Layer</span>
                <span class="telemetry-val">gold (dbt marts)</span>
            </div>
            <div class="telemetry-row">
                <span>Cadence</span>
                <span class="telemetry-val">Daily 02:00 UTC</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="font-size: 0.725rem; color: #475569; text-align: center; margin-top: 24px;">
            Retail ELT Platform v2.0<br>
            dbt Core · Airflow · PostgreSQL
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 6. Header Area
# ============================================================

col_head_left, col_head_right = st.columns([3, 1])

with col_head_left:
    st.markdown(
        """
        <div style="margin-bottom: 18px;">
            <div style="font-size: 1.6rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">Executive Analytics</div>
            <div style="font-size: 0.875rem; color: #94a3b8; margin-top: 2px;">
                Omnichannel retail performance, customer retention cohorts, and inventory intelligence from Gold marts.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_head_right:
    st.markdown(
        f"""
        <div style="text-align: right; margin-top: 4px;">
            <span class="status-badge {badge_class}">
                <span class="badge-dot {dot_class}"></span>
                {status_sub}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 7. Render Function
# ============================================================


def render_dashboard():
    # Apply region filter to fct_orders
    filtered_orders = fct_orders.copy()
    if "region" in filtered_orders.columns and selected_regions:
        filtered_orders = filtered_orders[filtered_orders["region"].isin(selected_regions)]

    # Apply status filter
    if "order_status" in filtered_orders.columns and selected_status != "All":
        filtered_orders = filtered_orders[filtered_orders["order_status"] == selected_status]

    # Calculate completed orders for financial metrics
    if "order_status" in filtered_orders.columns:
        completed_orders = filtered_orders[filtered_orders["order_status"] == "completed"]
    else:
        completed_orders = filtered_orders

    if filtered_orders.empty:
        st.info("No records match the selected region and status filters. Please adjust your filter selections in the sidebar.")
        return

    # Executive KPIs
    total_net_rev = completed_orders["line_total_net"].sum() if "line_total_net" in completed_orders.columns else 0.0
    total_discount = completed_orders["discount_amount"].sum() if "discount_amount" in completed_orders.columns else 0.0
    order_count = completed_orders["order_id"].nunique() if "order_id" in completed_orders.columns else 0
    customer_count = completed_orders["customer_id"].nunique() if "customer_id" in completed_orders.columns else 0
    avg_order_val = total_net_rev / max(order_count, 1)
    total_profit = completed_orders["gross_profit"].sum() if "gross_profit" in completed_orders.columns else 0.0
    margin_percentage = (total_profit / max(total_net_rev, 1)) * 100

    # KPI Metrics Row
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric(
            label="Net Revenue",
            value=f"₹{total_net_rev:,.0f}",
            delta=f"-₹{total_discount:,.0f} disc" if total_discount > 0 else None,
            delta_color="off",
        )
    with kpi2:
        st.metric(
            label="Completed Orders",
            value=f"{order_count:,}",
            delta=f"{len(completed_orders):,} items",
            delta_color="off",
        )
    with kpi3:
        st.metric(
            label="Unique Buyers",
            value=f"{customer_count:,}",
            delta=f"₹{(total_net_rev / max(customer_count, 1)):,.0f}/cust",
            delta_color="off",
        )
    with kpi4:
        st.metric(
            label="Avg Order Value",
            value=f"₹{avg_order_val:,.0f}",
            delta="Per checkout",
            delta_color="off",
        )
    with kpi5:
        st.metric(
            label="Gross Margin",
            value=f"{margin_percentage:.1f}%",
            delta=f"₹{total_profit:,.0f} profit",
            delta_color="normal",
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Tabs
    tab_sales, tab_cust, tab_inv, tab_fin, tab_qual = st.tabs(
        ["Sales Analytics", "Customer Intelligence", "Inventory & Supply", "Financial Health", "Pipeline Health & Quality"]
    )

    # ---------------- TAB 1: Sales ----------------
    with tab_sales:
        col_s1, col_s2 = st.columns([3, 2])
        with col_s1:
            st.markdown('<div class="card-title">Net Revenue Trend (Daily)</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Daily sales volume with 7-day moving average smoothing.</div>', unsafe_allow_html=True)

            if daily_sales is not None and not daily_sales.empty and "sale_date" in daily_sales.columns:
                fig_daily = go.Figure()
                fig_daily.add_trace(
                    go.Scatter(
                        x=daily_sales["sale_date"],
                        y=daily_sales["net_revenue"],
                        mode="lines",
                        name="Daily Revenue",
                        line=dict(color=PALETTE["primary"], width=2),
                        fill="tozeroy",
                        fillcolor="rgba(59, 130, 246, 0.08)",
                        hovertemplate="%{x|%b %d}: ₹%{y:,.0f}<extra></extra>",
                    )
                )
                if "revenue_7d_ma" in daily_sales.columns:
                    fig_daily.add_trace(
                        go.Scatter(
                            x=daily_sales["sale_date"],
                            y=daily_sales["revenue_7d_ma"],
                            mode="lines",
                            name="7-Day Moving Avg",
                            line=dict(color=PALETTE["amber"], width=2, dash="dot"),
                            hovertemplate="7D MA: ₹%{y:,.0f}<extra></extra>",
                        )
                    )
                apply_chart_theme(
                    fig_daily,
                    height=320,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_daily, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Daily sales time-series is currently empty.")

        with col_s2:
            st.markdown('<div class="card-title">Revenue by Geographic Region</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Regional sales contribution across retail locations.</div>', unsafe_allow_html=True)

            if region_rev is not None and not region_rev.empty:
                fig_region = px.bar(
                    region_rev,
                    x="region",
                    y="net_revenue",
                    color="region",
                    color_discrete_sequence=PALETTE["sequence"],
                    labels={"region": "Region", "net_revenue": "Net Sales (INR)"},
                )
                apply_chart_theme(
                    fig_region,
                    height=320,
                    showlegend=False,
                )
                fig_region.update_traces(
                    hovertemplate="<b>%{x}</b>: ₹%{y:,.0f}<extra></extra>",
                    marker=dict(line=dict(width=0)),
                )
                st.plotly_chart(fig_region, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Regional revenue breakdown not available.")

        col_p1, col_p2 = st.columns([3, 2])
        with col_p1:
            st.markdown('<div class="card-title">Top Products by Net Revenue (Pareto Analysis)</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Leading product lines sorted by total revenue contribution.</div>', unsafe_allow_html=True)

            if top_prods is not None and not top_prods.empty:
                top_display = top_prods.head(10).sort_values("total_revenue", ascending=True)
                fig_prod = px.bar(
                    top_display,
                    x="total_revenue",
                    y="product_name",
                    orientation="h",
                    color_discrete_sequence=[PALETTE["primary"]],
                    labels={"total_revenue": "Revenue (INR)", "product_name": "Product"},
                )
                apply_chart_theme(
                    fig_prod,
                    height=340,
                    margin=dict(l=140, r=20, t=20, b=40),
                )
                fig_prod.update_traces(
                    hovertemplate="<b>%{y}</b>: ₹%{x:,.0f}<extra></extra>",
                )
                st.plotly_chart(fig_prod, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Top products summary not available.")

        with col_p2:
            st.markdown('<div class="card-title">Regional Performance Summary</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Store density, orders, and sales share per region.</div>', unsafe_allow_html=True)

            if region_rev is not None and not region_rev.empty:
                display_region_cols = ["region", "store_count", "total_orders", "net_revenue", "revenue_share_pct"]
                valid_cols = [c for c in display_region_cols if c in region_rev.columns]
                reg_table = region_rev[valid_cols].copy()

                st.dataframe(
                    reg_table,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "region": st.column_config.TextColumn("Region"),
                        "store_count": st.column_config.NumberColumn("Stores", format="%d"),
                        "total_orders": st.column_config.NumberColumn("Orders", format="%d"),
                        "net_revenue": st.column_config.NumberColumn("Net Sales", format="₹%d"),
                        "revenue_share_pct": st.column_config.ProgressColumn(
                            "Contribution",
                            format="%.1f%%",
                            min_value=0,
                            max_value=100,
                        ),
                    },
                )
            else:
                st.info("Regional table not available.")

    # ---------------- TAB 2: Customers ----------------
    with tab_cust:
        if clv is not None and not clv.empty:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Total Profiled Customers", f"{len(clv):,}")
            with c2:
                avg_clv_val = clv["estimated_clv"].mean() if "estimated_clv" in clv.columns else 0.0
                st.metric("Mean Estimated CLV", f"₹{avg_clv_val:,.0f}")
            with c3:
                at_risk_count = len(clv[clv["customer_segment"] == "At Risk"]) if "customer_segment" in clv.columns else 0
                st.metric("At-Risk Segment", f"{at_risk_count:,}", delta="Requires Win-back", delta_color="inverse")
            with c4:
                champ_count = len(clv[clv["customer_segment"] == "Champions"]) if "customer_segment" in clv.columns else 0
                st.metric("Champions Segment", f"{champ_count:,}", delta="High LTV Tier", delta_color="normal")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown('<div class="card-title">Customer Segmentation (RFM Model)</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Recency, Frequency, and Monetary cohort categorization.</div>', unsafe_allow_html=True)

            if clv is not None and not clv.empty and "customer_segment" in clv.columns:
                seg_counts = clv["customer_segment"].value_counts().reset_index()
                seg_counts.columns = ["Segment", "Count"]

                fig_seg = px.pie(
                    seg_counts,
                    values="Count",
                    names="Segment",
                    hole=0.55,
                    color="Segment",
                    color_discrete_sequence=PALETTE["sequence"],
                )
                apply_chart_theme(
                    fig_seg,
                    height=290,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                )
                fig_seg.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b>: %{value:,} customers (%{percent})<extra></extra>",
                )
                st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Segmentation cohort data not available.")

        with col_c2:
            st.markdown('<div class="card-title">Customer Churn Risk Distribution</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Risk classification based on days elapsed since last purchase.</div>', unsafe_allow_html=True)

            if churn is not None and not churn.empty and "churn_status" in churn.columns:
                churn_order = ["active", "warm", "cooling", "at_risk", "churned"]
                churn_counts = churn["churn_status"].value_counts().reindex(churn_order).fillna(0).reset_index()
                churn_counts.columns = ["Status", "Count"]

                fig_churn = px.bar(
                    churn_counts,
                    x="Status",
                    y="Count",
                    color="Status",
                    color_discrete_map={
                        "active": PALETTE["emerald"],
                        "warm": PALETTE["primary"],
                        "cooling": PALETTE["amber"],
                        "at_risk": "#f97316",
                        "churned": PALETTE["rose"],
                    },
                    labels={"Status": "Churn Tier", "Count": "Customers"},
                )
                apply_chart_theme(
                    fig_churn,
                    height=290,
                    showlegend=False,
                )
                fig_churn.update_traces(
                    hovertemplate="<b>%{x}</b>: %{y:,} customers<extra></extra>",
                )
                st.plotly_chart(fig_churn, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Churn risk distribution not available.")

        if churn is not None and not churn.empty and "winback_priority" in churn.columns:
            st.markdown('<div class="card-title">High-Priority Win-back Targets</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">High lifetime spend customers with inactive recency window.</div>', unsafe_allow_html=True)

            targets = churn[churn["winback_priority"] == "high_priority"].copy()
            if targets.empty:
                targets = churn.head(15).copy()

            view_cols = ["customer_id", "customer_name", "customer_city", "loyalty_tier", "total_orders", "total_revenue", "days_since_last_order", "churn_status"]
            valid_view_cols = [c for c in view_cols if c in targets.columns]

            st.dataframe(
                targets[valid_view_cols].head(15),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "customer_id": st.column_config.NumberColumn("ID", format="%d"),
                    "customer_name": st.column_config.TextColumn("Customer"),
                    "customer_city": st.column_config.TextColumn("City"),
                    "loyalty_tier": st.column_config.TextColumn("Tier"),
                    "total_orders": st.column_config.NumberColumn("Orders", format="%d"),
                    "total_revenue": st.column_config.NumberColumn("Lifetime Spend", format="₹%d"),
                    "days_since_last_order": st.column_config.NumberColumn("Days Inactive", format="%d d"),
                    "churn_status": st.column_config.TextColumn("Status"),
                },
            )

    # ---------------- TAB 3: Inventory ----------------
    with tab_inv:
        col_i1, col_i2 = st.columns(2)
        with col_i1:
            st.markdown('<div class="card-title">Stockout & Reorder Alert Severity</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Inventory SKU counts grouped by replenishment urgency.</div>', unsafe_allow_html=True)

            if stock_alerts is not None and not stock_alerts.empty and "alert_severity" in stock_alerts.columns:
                sev_order = ["critical", "high", "medium", "low"]
                sev_counts = stock_alerts["alert_severity"].value_counts().reindex(sev_order).dropna().reset_index()
                sev_counts.columns = ["Severity", "Count"]

                fig_sev = px.bar(
                    sev_counts,
                    x="Severity",
                    y="Count",
                    color="Severity",
                    color_discrete_map={
                        "critical": PALETTE["rose"],
                        "high": "#f97316",
                        "medium": PALETTE["amber"],
                        "low": PALETTE["emerald"],
                    },
                    labels={"Severity": "Severity Tier", "Count": "SKUs"},
                )
                apply_chart_theme(
                    fig_sev,
                    height=290,
                    showlegend=False,
                )
                fig_sev.update_traces(
                    hovertemplate="<b>%{x}</b>: %{y:,} items<extra></extra>",
                )
                st.plotly_chart(fig_sev, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No active stock alerts detected. All warehouse SKUs within safety bounds.")

        with col_i2:
            st.markdown('<div class="card-title">Inventory Velocity Classification</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Ratio of units sold against average warehouse stock on hand.</div>', unsafe_allow_html=True)

            cat_col = "turnover_category" if (inv_turnover is not None and "turnover_category" in inv_turnover.columns) else "movement_category"

            if inv_turnover is not None and not inv_turnover.empty and cat_col in inv_turnover.columns:
                turn_counts = inv_turnover[cat_col].value_counts().reset_index()
                turn_counts.columns = ["Category", "Count"]

                fig_turn = px.pie(
                    turn_counts,
                    values="Count",
                    names="Category",
                    hole=0.55,
                    color="Category",
                    color_discrete_sequence=PALETTE["sequence"],
                )
                apply_chart_theme(
                    fig_turn,
                    height=290,
                    legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
                )
                fig_turn.update_traces(
                    textposition="inside",
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b>: %{value:,} products (%{percent})<extra></extra>",
                )
                st.plotly_chart(fig_turn, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Inventory turnover classification data not available.")

        if stock_alerts is not None and not stock_alerts.empty:
            st.markdown('<div class="card-title">Replenishment Priority Queue</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Specific store locations requiring procurement action.</div>', unsafe_allow_html=True)

            stock_cols = ["store_name", "product_name", "region", "quantity_on_hand", "reorder_level", "suggested_reorder_qty", "alert_severity"]
            valid_stock_cols = [c for c in stock_cols if c in stock_alerts.columns]

            st.dataframe(
                stock_alerts[valid_stock_cols].head(20),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "store_name": st.column_config.TextColumn("Store Location"),
                    "product_name": st.column_config.TextColumn("Product Name"),
                    "region": st.column_config.TextColumn("Region"),
                    "quantity_on_hand": st.column_config.NumberColumn("Current Stock", format="%d"),
                    "reorder_level": st.column_config.NumberColumn("Min Threshold", format="%d"),
                    "suggested_reorder_qty": st.column_config.NumberColumn("Reorder Qty", format="%d"),
                    "alert_severity": st.column_config.TextColumn("Severity"),
                },
            )

    # ---------------- TAB 4: Finance ----------------
    with tab_fin:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown('<div class="card-title">Payment Method Success Rates</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Transaction reliability across gateway payment rails.</div>', unsafe_allow_html=True)

            if payment_rates is not None and not payment_rates.empty and "payment_method" in payment_rates.columns:
                fig_pay = px.bar(
                    payment_rates,
                    x="payment_method",
                    y="success_rate_pct",
                    color="reliability_tier" if "reliability_tier" in payment_rates.columns else None,
                    color_discrete_map={
                        "excellent": PALETTE["emerald"],
                        "good": PALETTE["primary"],
                        "fair": PALETTE["amber"],
                        "poor": PALETTE["rose"],
                    },
                    labels={"payment_method": "Payment Method", "success_rate_pct": "Success Rate (%)"},
                )
                apply_chart_theme(
                    fig_pay,
                    height=290,
                    showlegend=False,
                    yaxis_range=[70, 100],
                )
                fig_pay.update_traces(
                    hovertemplate="<b>%{x}</b>: %{y:.1f}% success<extra></extra>",
                )
                st.plotly_chart(fig_pay, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Payment gateway reliability data not available.")

        with col_f2:
            st.markdown('<div class="card-title">Product Gross Margin Leaders</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Top margin percentage products contributing to gross profit.</div>', unsafe_allow_html=True)

            if gross_margin is not None and not gross_margin.empty and "gross_margin_pct" in gross_margin.columns:
                top_margins = gross_margin.head(10).sort_values("gross_margin_pct", ascending=True)
                fig_margin = px.bar(
                    top_margins,
                    x="gross_margin_pct",
                    y="product_name",
                    orientation="h",
                    color_discrete_sequence=[PALETTE["emerald"]],
                    labels={"gross_margin_pct": "Gross Margin (%)", "product_name": "Product"},
                )
                apply_chart_theme(
                    fig_margin,
                    height=290,
                    margin=dict(l=140, r=20, t=20, b=40),
                )
                fig_margin.update_traces(
                    hovertemplate="<b>%{y}</b>: %{x:.1f}% margin<extra></extra>",
                )
                st.plotly_chart(fig_margin, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("Gross margin analysis not available.")

        if refund_data is not None and not refund_data.empty:
            col_r1, col_r2 = st.columns([1, 1])
            cat_col = "return_category" if "return_category" in refund_data.columns else refund_data.columns[0]
            cnt_col = "return_count" if "return_count" in refund_data.columns else refund_data.columns[1]

            with col_r1:
                st.markdown('<div class="card-title">Returns by Reason Category</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-caption">Primary drivers of customer returns and refund processing.</div>', unsafe_allow_html=True)

                fig_ret = px.pie(
                    refund_data,
                    values=cnt_col,
                    names=cat_col,
                    hole=0.55,
                    color_discrete_sequence=PALETTE["sequence"],
                )
                apply_chart_theme(
                    fig_ret,
                    height=260,
                )
                fig_ret.update_traces(
                    hovertemplate="<b>%{label}</b>: %{value:,} returns (%{percent})<extra></extra>",
                )
                st.plotly_chart(fig_ret, use_container_width=True, config={"displayModeBar": False})

            with col_r2:
                st.markdown('<div class="card-title">Payment Method Performance Matrix</div>', unsafe_allow_html=True)
                st.markdown('<div class="card-caption">Transaction volumes and reliability rankings.</div>', unsafe_allow_html=True)

                if payment_rates is not None and not payment_rates.empty:
                    pay_cols = ["payment_method", "total_transactions", "successful_transactions", "success_rate_pct", "reliability_tier"]
                    valid_pay = [c for c in pay_cols if c in payment_rates.columns]
                    st.dataframe(
                        payment_rates[valid_pay],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "payment_method": st.column_config.TextColumn("Gateway / Method"),
                            "total_transactions": st.column_config.NumberColumn("Volume", format="%d"),
                            "successful_transactions": st.column_config.NumberColumn("Successes", format="%d"),
                            "success_rate_pct": st.column_config.ProgressColumn("Success %", format="%.1f%%", min_value=0, max_value=100),
                            "reliability_tier": st.column_config.TextColumn("Tier"),
                        },
                    )

    # ---------------- TAB 5: Pipeline Health & Quality ----------------
    with tab_qual:
        q1, q2, q3 = st.columns(3)
        with q1:
            st.metric(
                label="Last Ingestion Timestamp",
                value=last_load.strftime("%H:%M UTC") if last_load else "N/A",
                delta=f"{hours_ago} hours ago" if hours_ago is not None else None,
                delta_color="off",
            )
        with q2:
            st.metric(
                label="SLA Compliance",
                value="Target Met (<4h)" if (hours_ago is not None and hours_ago <= 4) else "Within Window",
                delta="Daily Schedule: 02:00 UTC",
                delta_color="normal",
            )
        with q3:
            st.metric(
                label="Architecture Hierarchy",
                value="Bronze → Silver → Gold",
                delta="dbt Medallion Pattern",
                delta_color="off",
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        col_q1, col_q2 = st.columns([1, 1])
        with col_q1:
            st.markdown('<div class="card-title">Gold Layer Warehouse Inventory</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Live record counts across active business marts.</div>', unsafe_allow_html=True)

            marts_inventory = [
                ("fct_orders", fct_orders, "Order line item fact table"),
                ("daily_sales", daily_sales, "Daily aggregated revenue time-series"),
                ("customer_lifetime_value", clv, "RFM segment scores & predicted CLV"),
                ("churn_risk", churn, "Recency attrition scoring & win-back priority"),
                ("top_products", top_prods, "Product performance & Pareto contribution"),
                ("revenue_by_region", region_rev, "Geographic revenue & store density"),
                ("stock_alerts", stock_alerts, "Store-level inventory safety thresholds"),
                ("inventory_turnover", inv_turnover, "Product turnover ratios & velocity"),
                ("gross_margin", gross_margin, "Product gross margins & profitability"),
                ("payment_success_rate", payment_rates, "Payment gateway reliability metrics"),
                ("refund_analysis", refund_data, "Customer return reasons & refund totals"),
            ]

            table_rows = []
            for name, df_obj, desc in marts_inventory:
                count_val = len(df_obj) if df_obj is not None else 0
                table_rows.append({"Mart Table": f"gold.{name}", "Records": count_val, "Description": desc})

            df_inventory = pd.DataFrame(table_rows)
            st.dataframe(
                df_inventory,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Mart Table": st.column_config.TextColumn("Table Identifier"),
                    "Records": st.column_config.NumberColumn("Row Count", format="%d"),
                    "Description": st.column_config.TextColumn("Granularity / Purpose"),
                },
            )

        with col_q2:
            st.markdown('<div class="card-title">Data Quality Assertions & Gates</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-caption">Automated dbt and Python validations enforced in pipeline.</div>', unsafe_allow_html=True)

            st.markdown(
                """
                <div style="background-color: #111827; border: 1px solid #1f2937; border-radius: 6px; padding: 16px;">
                    <div style="margin-bottom: 12px;">
                        <div style="font-weight: 600; color: #f8fafc; font-size: 0.85rem;">1. Entity Uniqueness & Nullability</div>
                        <div style="font-size: 0.775rem; color: #94a3b8;">
                            Enforced via dbt schema tests on all surrogate keys (<code>unique</code>, <code>not_null</code>).
                            SCD2 customer dimensions validate version uniqueness on <code>dbt_scd_id</code>.
                        </div>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <div style="font-weight: 600; color: #f8fafc; font-size: 0.85rem;">2. Referential Integrity</div>
                        <div style="font-size: 0.775rem; color: #94a3b8;">
                            Foreign key relationship assertions ensure every order maps to a validated customer, store, and product.
                        </div>
                    </div>
                    <div style="margin-bottom: 12px;">
                        <div style="font-weight: 600; color: #f8fafc; font-size: 0.85rem;">3. Custom Domain Rules (<code>positive_value</code>)</div>
                        <div style="font-size: 0.775rem; color: #94a3b8;">
                            Custom SQL macros guarantee non-negative line prices and quantities, quarantining corrupted POS records in staging.
                        </div>
                    </div>
                    <div>
                        <div style="font-weight: 600; color: #f8fafc; font-size: 0.85rem;">4. High-Water Mark CDC Tracking</div>
                        <div style="font-size: 0.775rem; color: #94a3b8;">
                            Incremental ingestion tracks <code>MAX(order_date)</code> with parameterized bind parameters to prevent duplicate writes and injection.
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# 8. Execution Flow & Diagnostics
# ============================================================

if fct_orders is None or (hasattr(fct_orders, "empty") and fct_orders.empty):
    st.markdown(
        """
        <div style="background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 28px; margin-top: 16px;">
            <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-bottom: 8px;">
                Warehouse Connection Required
            </div>
            <div style="font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 18px;">
                The dashboard connects directly to PostgreSQL <code>gold</code> marts. The database is currently
                unreachable or gold marts have not been generated yet.
            </div>
            <div style="background-color: #0b0f19; border: 1px solid #1e293b; border-radius: 6px; padding: 14px; margin-bottom: 18px; font-family: monospace; font-size: 0.8rem; color: #cbd5e1;">
                # 1. Start database and orchestration stack<br>
                docker compose up -d<br><br>
                # 2. Trigger the automated daily pipeline<br>
                docker compose exec airflow-webserver airflow dags trigger retail_daily_pipeline<br><br>
                # 3. Or run the automated demo bootstrap script<br>
                ./scripts/init_demo.sh
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Retry Connection", type="primary"):
        st.cache_data.clear()
        st.rerun()

    st.stop()
else:
    render_dashboard()

# ============================================================
# 9. Minimal Footer
# ============================================================

st.markdown(
    """
    <div style="border-top: 1px solid #1e293b; padding-top: 16px; margin-top: 36px; text-align: center; color: #475569; font-size: 0.775rem;">
        Retail ELT Platform · Medallion Architecture (PostgreSQL & dbt Core) · Apache Airflow 2.7.1
    </div>
    """,
    unsafe_allow_html=True,
)
