"""
Retail ELT Platform — Executive Analytics Dashboard
=====================================================
A modern, minimal, professional analytics interface connected
directly to the PostgreSQL Gold layer dimensional warehouse.
"""

import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import streamlit as st
import json

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
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', -apple-system, sans-serif; }
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    div[data-testid="metric-container"] {
        background-color: #111827; border: 1px solid #1f2937; border-radius: 8px;
        padding: 14px 18px; transition: border-color 0.2s ease;
    }
    div[data-testid="metric-container"]:hover { border-color: #374151; }
    [data-testid="stMetricLabel"] { font-size: 0.725rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.05em !important; color: #94a3b8 !important; }
    [data-testid="stMetricValue"] { font-size: 1.65rem !important; font-weight: 700 !important; color: #f8fafc !important; letter-spacing: -0.02em !important; }
    [data-testid="stMetricDelta"] { font-size: 0.775rem !important; font-weight: 500 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid #1e293b; padding-bottom: 0px; }
    .stTabs [data-baseweb="tab"] { background-color: transparent; border-radius: 6px 6px 0 0; padding: 8px 18px; color: #94a3b8; font-weight: 500; border: 1px solid transparent; border-bottom: none; }
    .stTabs [aria-selected="true"] { background-color: #111827; color: #f8fafc; border-color: #1e293b; }
    div[data-testid="stDataFrame"] { border: 1px solid #1e293b; border-radius: 6px; overflow: hidden; }
    .card-title { font-size: 0.95rem; font-weight: 600; color: #f8fafc; margin-bottom: 2px; }
    .card-caption { font-size: 0.75rem; color: #94a3b8; margin-bottom: 12px; line-height: 1.4; }
    .status-badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 99px; font-size: 0.725rem; font-weight: 600; }
    .badge-healthy { background-color: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
    .badge-stale { background-color: rgba(245, 158, 11, 0.1); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); }
    .badge-offline { background-color: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }
    .badge-dot { width: 6px; height: 6px; border-radius: 50%; margin-right: 6px; }
    .dot-healthy { background-color: #10b981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.5); }
    .dot-stale { background-color: #f59e0b; box-shadow: 0 0 8px rgba(245, 158, 11, 0.5); }
    .dot-offline { background-color: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.5); }
    .sidebar-section-title { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #475569; margin-top: 24px; margin-bottom: 8px; }
    .telemetry-row { display: flex; justify-content: space-between; font-size: 0.75rem; color: #94a3b8; padding: 4px 0; border-bottom: 1px solid #1e293b; }
    .telemetry-val { color: #e2e8f0; font-family: monospace; }
</style>
    """,
    unsafe_allow_html=True,
)

PALETTE = {
    "primary": "#3b82f6", "emerald": "#10b981", "amber": "#f59e0b", "rose": "#ef4444", "slate": "#64748b",
    "sequence": ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ec4899", "#14b8a6", "#ef4444"],
}

def apply_chart_theme(fig, height=350, showlegend=True, legend=None, margin=None):
    fig.update_layout(
        height=height, margin=margin or dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#94a3b8", size=11), showlegend=showlegend,
        hoverlabel=dict(bgcolor="#1e293b", font_size=12, font_family="Inter", bordercolor="#334155")
    )
    if legend: fig.update_layout(legend=legend)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="#1e293b", zeroline=False, showline=True, linecolor="#1e293b")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#1e293b", zeroline=False, showline=False)
    return fig

# ============================================================
# 3. Connection & Data Load
# ============================================================
@st.cache_resource
def get_engine():
    user = os.getenv("POSTGRES_USER", "retail_user")
    password = os.getenv("POSTGRES_PASSWORD", "retail_pass_change_me")
    host = os.getenv("POSTGRES_HOST", "postgres")
    db = os.getenv("POSTGRES_DB", "retail_warehouse")
    try: return create_engine(f"postgresql://{user}:{password}@{host}:5432/{db}")
    except: return None

@st.cache_data(ttl=300)
def load_mart(table_name):
    engine = get_engine()
    if not engine: return None
    try: return pd.read_sql(f"SELECT * FROM gold.{table_name}", engine)
    except: return None

def get_pipeline_freshness(df):
    if df is not None and not df.empty and "dbt_updated_at" in df.columns:
        last_load = pd.to_datetime(df["dbt_updated_at"].max()).tz_localize(None)
        hours_ago = (datetime.utcnow() - last_load).total_seconds() / 3600
        return last_load, round(hours_ago, 1)
    return None, None

# Load global tables
fct_orders = load_mart("fct_orders")
if fct_orders is None or fct_orders.empty:
    st.error("Warehouse Connection Required or no data found in fct_orders.")
    st.stop()

# Ensure dates are datetime
if "order_date" in fct_orders.columns:
    fct_orders["order_date"] = pd.to_datetime(fct_orders["order_date"])

last_load, hours_ago = get_pipeline_freshness(fct_orders)

# Load other marts
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
promo_perf = load_mart("promotion_performance")
supplier_perf = load_mart("supplier_performance")
delivery_perf = load_mart("delivery_performance")

# ============================================================
# 4. Global Filters & Sidebar
# ============================================================
with st.sidebar:
    st.markdown('<div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-bottom: 2px;">Bombay Bazaar</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.775rem; color: #64748b; margin-bottom: 16px; border-bottom: 1px solid #1e293b; padding-bottom: 12px;">Retail ELT Platform · Medallion Gold</div>', unsafe_allow_html=True)

    if hours_ago is not None:
        if hours_ago <= 6:
            badge_class, dot_class, status_label = "badge-healthy", "dot-healthy", "Pipeline Active"
        elif hours_ago <= 24:
            badge_class, dot_class, status_label = "badge-stale", "dot-stale", "Data Stale"
        else:
            badge_class, dot_class, status_label = "badge-offline", "dot-offline", "SLA Breach"
    else:
        badge_class, dot_class, status_label = "badge-offline", "dot-offline", "Unknown Status"

    st.markdown(f'<div class="status-badge {badge_class}" style="width: 100%; justify-content: center; margin-bottom: 16px;"><span class="badge-dot {dot_class}"></span><span>{status_label}</span></div>', unsafe_allow_html=True)

    if st.button("↻ Refresh Warehouse Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div class="sidebar-section-title">Global Filters</div>', unsafe_allow_html=True)
    
    min_date = fct_orders["order_date"].min().date() if not fct_orders.empty else datetime.utcnow().date() - timedelta(days=90)
    max_date = fct_orders["order_date"].max().date() if not fct_orders.empty else datetime.utcnow().date()
    
    selected_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    
    comparison_period = st.selectbox("Comparison Period", options=["None", "Previous Period", "Previous Year"])
    
    available_regions = fct_orders["region"].dropna().unique().tolist() if "region" in fct_orders.columns else []
    selected_regions = st.multiselect("Region", options=available_regions, default=available_regions)
    
    status_options = ["All"] + fct_orders["order_status"].dropna().unique().tolist() if "order_status" in fct_orders.columns else ["All"]
    selected_status = st.selectbox("Order Status", options=status_options, index=0)

    if st.button("Reset Filters", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown('<div style="height: 16px;"></div>', unsafe_allow_html=True)
    if st.button("👁️ View Raw Data Explorer", use_container_width=True, type="secondary"):
        st.session_state.show_raw_data = not st.session_state.get("show_raw_data", False)

# Filter fct_orders based on selections
filtered_orders = fct_orders.copy()
if len(selected_dates) == 2:
    start_dt, end_dt = selected_dates
    filtered_orders = filtered_orders[(filtered_orders["order_date"].dt.date >= start_dt) & (filtered_orders["order_date"].dt.date <= end_dt)]

if selected_regions:
    filtered_orders = filtered_orders[filtered_orders["region"].isin(selected_regions)]

if selected_status != "All":
    filtered_orders = filtered_orders[filtered_orders["order_status"] == selected_status]

# ============================================================
# 5. Header Area
# ============================================================
col_head_left, col_head_right = st.columns([3, 1])
with col_head_left:
    st.markdown('<div style="margin-bottom: 18px;"><div style="font-size: 1.6rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.02em;">Executive Analytics</div><div style="font-size: 0.875rem; color: #94a3b8; margin-top: 2px;">Comprehensive insights and metrics for retail operations.</div></div>', unsafe_allow_html=True)

# ============================================================
# 6. Executive Overview (KPIs)
# ============================================================
completed_orders = filtered_orders[filtered_orders["order_status"] == "completed"] if "order_status" in filtered_orders.columns else filtered_orders
total_gross_rev = completed_orders["line_total_gross"].sum() if "line_total_gross" in completed_orders.columns else 0.0
total_net_rev = completed_orders["line_total_net"].sum() if "line_total_net" in completed_orders.columns else 0.0
total_orders = completed_orders["order_id"].nunique() if "order_id" in completed_orders.columns else 0
total_customers = completed_orders["customer_id"].nunique() if "customer_id" in completed_orders.columns else 0
aov = total_net_rev / max(total_orders, 1)
gross_profit = completed_orders["gross_profit"].sum() if "gross_profit" in completed_orders.columns else 0.0
gross_margin_val = (gross_profit / max(total_net_rev, 1)) * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Gross Revenue", f"₹{total_gross_rev:,.0f}")
k2.metric("Net Revenue", f"₹{total_net_rev:,.0f}")
k3.metric("Total Orders", f"{total_orders:,}")
k4.metric("Unique Customers", f"{total_customers:,}")

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
k5, k6, k7, k8 = st.columns(4)
k5.metric("Avg Order Value (AOV)", f"₹{aov:,.0f}")
k6.metric("Gross Profit", f"₹{gross_profit:,.0f}")
k7.metric("Gross Margin", f"{gross_margin_val:.1f}%")
refund_rate = refund_data["overall_return_rate_pct"].iloc[0] if refund_data is not None and not refund_data.empty and "overall_return_rate_pct" in refund_data.columns else 0
k8.metric("Return Rate", f"{refund_rate:.1f}%")

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# ============================================================
# 7. Tabs
# ============================================================
t_sales, t_cust, t_prod, t_inv, t_fin, t_promo, t_supply, t_about = st.tabs([
    "Sales", "Customers", "Products", "Inventory", "Financials", "Promotions", "Supply Chain", "About"
])

# ------------- 7.1 SALES -------------
with t_sales:
    s1, s2 = st.columns([3, 2])
    with s1:
        st.markdown('<div class="card-title">Revenue Trend</div><div class="card-caption">Daily net revenue over time.</div>', unsafe_allow_html=True)
        if daily_sales is not None and not daily_sales.empty:
            fig = px.line(daily_sales, x="sale_date", y="net_revenue", color_discrete_sequence=[PALETTE["primary"]])
            fig.update_traces(fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.08)")
            st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
        else: st.info("No data")
    with s2:
        st.markdown('<div class="card-title">Revenue by Region</div><div class="card-caption">Contribution of each region.</div>', unsafe_allow_html=True)
        if region_rev is not None and not region_rev.empty:
            fig = px.pie(region_rev, names="region", values="net_revenue", hole=0.5, color_discrete_sequence=PALETTE["sequence"])
            st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
        else: st.info("No data")

    st.markdown('<div class="card-title">Sales Drill-down</div>', unsafe_allow_html=True)
    if not filtered_orders.empty:
        agg = filtered_orders.groupby(["region", "product_name"]).agg(
            Orders=("order_id", "nunique"), Revenue=("line_total_net", "sum"), Profit=("gross_profit", "sum")
        ).reset_index().sort_values("Revenue", ascending=False).head(20)
        st.dataframe(agg, use_container_width=True, hide_index=True)

    st.markdown('<div class="card-title">Regional Sales Sunburst</div>', unsafe_allow_html=True)
    if not filtered_orders.empty:
        sun_df = filtered_orders.groupby(['region', 'store_name']).agg({'line_total_net': 'sum'}).reset_index()
        fig_sun = px.sunburst(sun_df, path=['region', 'store_name'], values='line_total_net',
                              color='line_total_net', color_continuous_scale='Blues')
        st.plotly_chart(apply_chart_theme(fig_sun, height=400), use_container_width=True)


# ------------- 7.2 CUSTOMERS -------------
with t_cust:
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown('<div class="card-title">Customer Segments (RFM)</div>', unsafe_allow_html=True)
        if clv is not None and not clv.empty:
            seg = clv["customer_segment"].value_counts().reset_index()
            seg.columns = ["Segment", "Count"]
            fig = px.pie(seg, names="Segment", values="Count", hole=0.5, color_discrete_sequence=PALETTE["sequence"])
            st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
        else: st.info("No data")
    with c2:
        st.markdown('<div class="card-title">Customer Lifetime Value Distribution</div>', unsafe_allow_html=True)
        if clv is not None and not clv.empty and "estimated_clv" in clv.columns:
            fig = px.histogram(clv, x="estimated_clv", nbins=30, color_discrete_sequence=[PALETTE["emerald"]])
            st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
        else: st.info("No data")
    
    st.markdown('<div class="card-title">At-Risk Customers (Win-back Priority)</div>', unsafe_allow_html=True)
    if churn is not None and not churn.empty:
        st.dataframe(churn[churn["churn_status"].isin(["at_risk", "churned"])].head(15), use_container_width=True, hide_index=True)

# ------------- 7.3 PRODUCTS -------------
with t_prod:
    p1, p2 = st.columns(2)
    with p1:
        st.markdown('<div class="card-title">Top 10 Products by Revenue</div>', unsafe_allow_html=True)
        if top_prods is not None and not top_prods.empty:
            st.dataframe(top_prods.sort_values("total_revenue", ascending=False).head(10), use_container_width=True, hide_index=True)
    with p2:
        st.markdown('<div class="card-title">Product Profitability Matrix</div>', unsafe_allow_html=True)
        if gross_margin is not None and not gross_margin.empty:
            st.dataframe(gross_margin.sort_values("gross_margin_pct", ascending=False).head(10), use_container_width=True, hide_index=True)

# ------------- 7.4 INVENTORY -------------
with t_inv:
    i1, i2 = st.columns(2)
    with i1:
        st.markdown('<div class="card-title">Stock Alerts</div>', unsafe_allow_html=True)
        if stock_alerts is not None and not stock_alerts.empty:
            fig = px.bar(stock_alerts["alert_severity"].value_counts().reset_index(), x="alert_severity", y="count", color_discrete_sequence=[PALETTE["rose"]])
            st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
    with i2:
        st.markdown('<div class="card-title">Inventory Turnover Category</div>', unsafe_allow_html=True)
        if inv_turnover is not None and not inv_turnover.empty:
            turn_col = "turnover_category" if "turnover_category" in inv_turnover.columns else "movement_category"
            if turn_col in inv_turnover.columns:
                fig = px.pie(inv_turnover[turn_col].value_counts().reset_index(), names=turn_col, values="count", color_discrete_sequence=PALETTE["sequence"])
                st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)

    st.markdown('<div class="card-title">Replenishment Priority Queue</div>', unsafe_allow_html=True)
    if stock_alerts is not None and not stock_alerts.empty:
        st.dataframe(stock_alerts.head(15), use_container_width=True, hide_index=True)

# ------------- 7.5 FINANCIALS -------------
with t_fin:

    st.markdown('<div class="card-title">Revenue to Profit Waterfall</div>', unsafe_allow_html=True)
    if not filtered_orders.empty:
        gross_rev = filtered_orders['line_total_gross'].sum() if 'line_total_gross' in filtered_orders.columns else 0
        discounts = -filtered_orders['discount_amount'].sum() if 'discount_amount' in filtered_orders.columns else 0
        net_rev = gross_rev + discounts
        cogs = -filtered_orders['line_cost'].sum() if 'line_cost' in filtered_orders.columns else 0
        profit = net_rev + cogs
        
        fig_wf = go.Figure(go.Waterfall(
            name="20", orientation="v",
            measure=["absolute", "relative", "total", "relative", "total"],
            x=["Gross Revenue", "Discounts", "Net Revenue", "COGS", "Gross Profit"],
            textposition="outside",
            text=[f"₹{x/1000:,.0f}k" for x in [gross_rev, discounts, net_rev, cogs, profit]],
            y=[gross_rev, discounts, net_rev, cogs, profit],
            connector={"line":{"color":"#334155"}},
            decreasing={"marker":{"color": PALETTE["rose"]}},
            increasing={"marker":{"color": PALETTE["emerald"]}},
            totals={"marker":{"color": PALETTE["primary"]}}
        ))
        st.plotly_chart(apply_chart_theme(fig_wf, height=400), use_container_width=True)

with t_fin:
    f1, f2 = st.columns(2)
    with f1:
        st.markdown('<div class="card-title">Refund Analysis</div>', unsafe_allow_html=True)
        if refund_data is not None and not refund_data.empty:
            cat_col = "return_category" if "return_category" in refund_data.columns else refund_data.columns[0]
            cnt_col = "return_count" if "return_count" in refund_data.columns else refund_data.columns[1]
            fig = px.pie(refund_data, names=cat_col, values=cnt_col, hole=0.5, color_discrete_sequence=PALETTE["sequence"])
            st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
    with f2:
        st.markdown('<div class="card-title">Payment Method Reliability</div>', unsafe_allow_html=True)
        if payment_rates is not None and not payment_rates.empty:
            st.dataframe(payment_rates, use_container_width=True, hide_index=True)

# ------------- 7.6 PROMOTIONS -------------
with t_promo:
    st.markdown('<div class="card-title">Promotion Effectiveness</div>', unsafe_allow_html=True)
    if promo_perf is not None and not promo_perf.empty:
        st.dataframe(promo_perf, use_container_width=True, hide_index=True)
        fig = px.bar(promo_perf, x="promotion_name", y="net_revenue", color="is_currently_active", color_discrete_sequence=[PALETTE["primary"], PALETTE["slate"]])
        st.plotly_chart(apply_chart_theme(fig, height=400), use_container_width=True)
    else:
        st.info("No promotion data available.")

# ------------- 7.7 SUPPLY CHAIN -------------
with t_supply:
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown('<div class="card-title">Delivery Performance Trend</div>', unsafe_allow_html=True)
        if delivery_perf is not None and not delivery_perf.empty:
            fig = px.line(delivery_perf, x="shipping_month", y="on_time_pct", title="On-Time Delivery %", color_discrete_sequence=[PALETTE["emerald"]])
            st.plotly_chart(apply_chart_theme(fig, height=300), use_container_width=True)
        else: st.info("No delivery data available.")
    with sc2:
        st.markdown('<div class="card-title">Supplier Performance</div>', unsafe_allow_html=True)
        if supplier_perf is not None and not supplier_perf.empty:
            st.dataframe(supplier_perf.sort_values("total_units_in_stock", ascending=False).head(15), use_container_width=True, hide_index=True)
        else: st.info("No supplier data available.")

# ------------- 7.8 ABOUT -------------
with t_about:
    st.markdown('<div class="card-title" style="font-size: 1.25rem;">Executive Summary & Key Insights</div>', unsafe_allow_html=True)
    
    # Extract insights
    top_region = region_rev.sort_values("net_revenue", ascending=False).iloc[0]["region"] if (region_rev is not None and not region_rev.empty) else "N/A"
    top_region_rev = region_rev.sort_values("net_revenue", ascending=False).iloc[0]["net_revenue"] if (region_rev is not None and not region_rev.empty) else 0
    top_product = top_prods.sort_values("total_revenue", ascending=False).iloc[0]["product_name"] if (top_prods is not None and not top_prods.empty) else "N/A"
    avg_clv = clv["estimated_clv"].mean() if (clv is not None and not clv.empty and "estimated_clv" in clv.columns) else 0
    
    st.markdown(f"""
    <div style="font-size: 1rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 24px;">
    <strong>Overall Performance:</strong><br>
    • <strong>Total Net Revenue:</strong> ₹{total_net_rev:,.0f} across {total_orders:,} total orders.<br>
    • <strong>Gross Margin Health:</strong> Maintained an average gross margin of {gross_margin_val:.1f}%, indicating strong operational profitability.<br>
    • <strong>Average Order Value (AOV):</strong> ₹{aov:,.0f} per transaction.
    <br><br>
    <strong>Market & Product Insights:</strong><br>
    • <strong>Top Region:</strong> The <strong>{top_region}</strong> region is the highest performer, driving ₹{top_region_rev:,.0f} in net revenue.<br>
    • <strong>Hero Product:</strong> <strong>{top_product}</strong> is the best-selling product overall.<br>
    • <strong>Customer Value:</strong> The estimated average Customer Lifetime Value (CLV) is strong at ₹{avg_clv:,.0f}.
    <br><br>
    <strong>Operational Health:</strong><br>
    • <strong>Refunds & Returns:</strong> Sitting at a {refund_rate:.1f}% return rate.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        """
        ---
        ### Analytics Catalog
        - **Net Revenue**: Gross Revenue minus Discounts.
        - **Gross Profit**: Net Revenue minus COGS (Cost of Goods Sold).
        - **AOV (Average Order Value)**: Total Net Revenue divided by number of completed orders.
        - **Return Rate**: Percentage of processed refunds vs total transactions.
        - **On-Time Delivery %**: Shipments delivered before or on estimated delivery date.
        """
    )

# ============================================================
# 8. Raw Data Explorer (Toggleable)
# ============================================================
if st.session_state.get("show_raw_data", False):
    st.markdown('<div style="height: 32px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 1.4rem; font-weight: 700; color: #f8fafc; border-top: 1px solid #1e293b; padding-top: 16px;">Raw Data Explorer (fct_orders)</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 16px;">Explore the fully enriched, Gold-layer transactional dataset.</div>', unsafe_allow_html=True)
    st.dataframe(fct_orders, use_container_width=True)

