# -*- coding: utf-8 -*-
"""
Bombay Bazaar - Retail Intelligence
=====================================
Gold-layer analytical workspace.
PostgreSQL / dbt / Airflow / Streamlit
"""

import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import streamlit as st
from ui import THEME_CSS, PALETTE, apply_chart_theme, fmt_currency, fmt_number, fmt_pct, section_header, kpi_block

# ============================================================
# 1. Page config
# ============================================================
st.set_page_config(
    page_title="Bombay Bazaar - Retail Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(THEME_CSS, unsafe_allow_html=True)

# ============================================================
# 2. Data layer
# ============================================================
@st.cache_resource
def get_engine():
    user = os.getenv("POSTGRES_USER", "retail_user")
    password = os.getenv("POSTGRES_PASSWORD", "retail_pass_change_me")
    host = os.getenv("POSTGRES_HOST", "postgres")
    db = os.getenv("POSTGRES_DB", "retail_warehouse")
    try:
        return create_engine(f"postgresql://{user}:{password}@{host}:5432/{db}")
    except Exception:
        return None

@st.cache_data(ttl=300)
def load_mart(table_name):
    engine = get_engine()
    if not engine:
        return None
    try:
        return pd.read_sql(f"SELECT * FROM gold.{table_name}", engine)
    except Exception:
        return None

def get_pipeline_freshness(df):
    if df is not None and not df.empty and "dbt_updated_at" in df.columns:
        last_load = pd.to_datetime(df["dbt_updated_at"].max()).tz_localize(None)
        hours_ago = (datetime.utcnow() - last_load).total_seconds() / 3600
        return last_load, round(hours_ago, 1)
    return None, None

# Load all marts
fct_orders = load_mart("fct_orders")
if fct_orders is None or fct_orders.empty:
    st.error("Warehouse connection required. No data found in fct_orders.")
    st.stop()

if "order_date" in fct_orders.columns:
    fct_orders["order_date"] = pd.to_datetime(fct_orders["order_date"])

last_load, hours_ago = get_pipeline_freshness(fct_orders)

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
# 3. Sidebar
# ============================================================
with st.sidebar:
    st.markdown('<div class="sidebar-brand">BOMBAY BAZAAR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-sub">Retail Intelligence</div>', unsafe_allow_html=True)

    # Pipeline status
    if hours_ago is not None:
        if hours_ago <= 6:
            dot_cls, status_txt = "status-dot-healthy", "Pipeline healthy"
        elif hours_ago <= 24:
            dot_cls, status_txt = "status-dot-stale", "Data stale"
        else:
            dot_cls, status_txt = "status-dot-offline", "SLA breach"
    else:
        dot_cls, status_txt = "status-dot-offline", "Unknown"

    freshness_str = ""
    if hours_ago is not None:
        if hours_ago < 1:
            freshness_str = f"{int(hours_ago * 60)}m ago"
        elif hours_ago < 24:
            freshness_str = f"{hours_ago:.0f}h ago"
        else:
            freshness_str = f"{hours_ago / 24:.0f}d ago"

    st.markdown(f'''
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
        <span class="status-dot {dot_cls}"></span>
        <span style="font-size:0.72rem;color:var(--text-secondary);">{status_txt}</span>
    </div>
    <div style="font-size:0.65rem;color:var(--text-muted);margin-bottom:16px;">Updated {freshness_str}</div>
    ''', unsafe_allow_html=True)

    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Filters
    st.markdown('<div class="sidebar-label">Data Controls</div>', unsafe_allow_html=True)

    min_date = fct_orders["order_date"].min().date() if not fct_orders.empty else datetime.utcnow().date() - timedelta(days=90)
    max_date = fct_orders["order_date"].max().date() if not fct_orders.empty else datetime.utcnow().date()
    selected_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

    available_regions = fct_orders["region"].dropna().unique().tolist() if "region" in fct_orders.columns else []
    selected_regions = st.multiselect("Region", options=available_regions, default=available_regions)

    status_options = ["All"] + fct_orders["order_status"].dropna().unique().tolist() if "order_status" in fct_orders.columns else ["All"]
    selected_status = st.selectbox("Order Status", options=status_options, index=0)

    comparison_period = st.selectbox("Comparison", options=["None", "Previous Period", "Previous Year"])

    if st.button("Reset filters", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Pipeline info
    st.markdown(f'''
    <div class="pipeline-info">
        <div class="pipeline-row"><span class="pipeline-key">Database</span><span class="pipeline-val">PostgreSQL</span></div>
        <div class="pipeline-row"><span class="pipeline-key">Schema</span><span class="pipeline-val">gold</span></div>
        <div class="pipeline-row"><span class="pipeline-key">Orchestrator</span><span class="pipeline-val">Airflow</span></div>
        <div class="pipeline-row"><span class="pipeline-key">Transform</span><span class="pipeline-val">dbt</span></div>
        <div class="pipeline-row"><span class="pipeline-key">Records</span><span class="pipeline-val">{fmt_number(len(fct_orders))}</span></div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)
    if st.button("Data Explorer", use_container_width=True):
        st.session_state.show_raw_data = not st.session_state.get("show_raw_data", False)

# ============================================================
# 4. Filter logic
# ============================================================
filtered_orders = fct_orders.copy()
if len(selected_dates) == 2:
    start_dt, end_dt = selected_dates
    filtered_orders = filtered_orders[
        (filtered_orders["order_date"].dt.date >= start_dt) &
        (filtered_orders["order_date"].dt.date <= end_dt)
    ]
if selected_regions:
    filtered_orders = filtered_orders[filtered_orders["region"].isin(selected_regions)]
if selected_status != "All":
    filtered_orders = filtered_orders[filtered_orders["order_status"] == selected_status]

# ============================================================
# 5. Data Explorer (full-page mode)
# ============================================================
if st.session_state.get("show_raw_data", False):
    if st.button("Back to dashboard"):
        st.session_state.show_raw_data = False
        st.rerun()

    row_count = len(fct_orders)
    col_count = len(fct_orders.columns)
    date_min = fct_orders["order_date"].min().strftime("%Y-%m-%d") if not fct_orders.empty else "N/A"
    date_max = fct_orders["order_date"].max().strftime("%Y-%m-%d") if not fct_orders.empty else "N/A"

    st.markdown(f'''
    <div class="data-explorer-header">
        <div>
            <div class="data-explorer-title">Data Explorer</div>
            <div style="font-size:0.72rem;color:var(--text-muted);margin-top:2px;">gold.fct_orders</div>
        </div>
        <div class="data-explorer-meta">
            <div>Rows <span>{fmt_number(row_count)}</span></div>
            <div>Columns <span>{col_count}</span></div>
            <div>Range <span>{date_min} to {date_max}</span></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    search_term = st.text_input("Search", placeholder="Filter rows by any column value...", label_visibility="collapsed")

    display_df = fct_orders.copy()
    if search_term:
        mask = display_df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)
        display_df = display_df[mask]

    st.dataframe(display_df, use_container_width=True, height=600)

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "fct_orders_export.csv", "text/csv", use_container_width=True)
    st.stop()

# ============================================================
# 6. KPIs
# ============================================================
active = filtered_orders
total_net_rev = active["line_total_net"].sum() if "line_total_net" in active.columns else 0.0
total_gross_rev = active["line_total_gross"].sum() if "line_total_gross" in active.columns else 0.0
total_orders = active["order_id"].nunique() if "order_id" in active.columns else 0
total_customers = active["customer_id"].nunique() if "customer_id" in active.columns else 0
aov = total_net_rev / max(total_orders, 1)
gross_profit = active["gross_profit"].sum() if "gross_profit" in active.columns else 0.0
gross_margin_val = (gross_profit / max(total_net_rev, 1)) * 100
refund_rate = refund_data["overall_return_rate_pct"].iloc[0] if refund_data is not None and not refund_data.empty and "overall_return_rate_pct" in refund_data.columns else 0

# Header
st.markdown(f'''
<div class="app-header">
    <div class="app-brand">
        <div class="app-brand-name">Retail Intelligence</div>
        <div class="app-brand-sub">Gold-layer operational analytics</div>
    </div>
    <div class="app-status">
        <span><span class="status-dot {dot_cls}"></span>{status_txt}</span>
        <span style="color:var(--text-muted);">{freshness_str}</span>
    </div>
</div>
''', unsafe_allow_html=True)

# KPI rail
k1, k2, k3, k4, k5 = st.columns(5)
k1.markdown(kpi_block("Net Revenue", fmt_currency(total_net_rev), f"Gross {fmt_currency(total_gross_rev)}"), unsafe_allow_html=True)
k2.markdown(kpi_block("Orders", fmt_number(total_orders), f"{fmt_number(total_customers)} customers"), unsafe_allow_html=True)
k3.markdown(kpi_block("AOV", fmt_currency(aov)), unsafe_allow_html=True)
k4.markdown(kpi_block("Gross Margin", fmt_pct(gross_margin_val), f"Profit {fmt_currency(gross_profit)}"), unsafe_allow_html=True)
k5.markdown(kpi_block("Return Rate", fmt_pct(refund_rate)), unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ============================================================
# 7. Tabs
# ============================================================
t_overview, t_cust, t_prod, t_inv, t_fin, t_promo, t_supply, t_about = st.tabs([
    "Overview", "Customers", "Products", "Inventory", "Finance", "Promotions", "Supply Chain", "About"
])

# ── OVERVIEW ──────────────────────────────────────────────────
with t_overview:
    # Revenue trend + Regional
    ov1, ov2 = st.columns([3, 2])
    with ov1:
        st.markdown(section_header("Revenue Trend", "Daily net revenue over the selected period."), unsafe_allow_html=True)
        if daily_sales is not None and not daily_sales.empty:
            fig = px.area(daily_sales, x="sale_date", y="net_revenue", color_discrete_sequence=[PALETTE["primary"]])
            fig.update_traces(line=dict(width=1.5), fillcolor="rgba(201,169,110,0.06)")
            st.plotly_chart(apply_chart_theme(fig, height=300, showlegend=False), use_container_width=True)
        else:
            st.info("No daily sales data available.")

    with ov2:
        st.markdown(section_header("Regional Performance", "Net revenue by region."), unsafe_allow_html=True)
        if region_rev is not None and not region_rev.empty:
            rr = region_rev.sort_values("net_revenue", ascending=True)
            fig = px.bar(rr, y="region", x="net_revenue", orientation="h",
                         color_discrete_sequence=[PALETTE["primary"]],
                         text=rr["net_revenue"].apply(lambda x: fmt_currency(x)))
            fig.update_traces(textposition="outside", textfont_size=10, cliponaxis=False)
            st.plotly_chart(apply_chart_theme(fig, height=300, showlegend=False), use_container_width=True)
        else:
            st.info("No regional data available.")

    # Sales performance table
    st.markdown(section_header("Sales Performance", "Top product-region combinations by revenue."), unsafe_allow_html=True)
    if not filtered_orders.empty:
        agg = filtered_orders.groupby(["region", "product_name"]).agg(
            Orders=("order_id", "nunique"),
            Revenue=("line_total_net", "sum"),
            Profit=("gross_profit", "sum"),
        ).reset_index()
        agg["Margin"] = (agg["Profit"] / agg["Revenue"].replace(0, 1) * 100).round(1)
        agg = agg.sort_values("Revenue", ascending=False).head(15)
        agg["Revenue"] = agg["Revenue"].apply(lambda x: f"{x:,.0f}")
        agg["Profit"] = agg["Profit"].apply(lambda x: f"{x:,.0f}")
        agg["Margin"] = agg["Margin"].apply(lambda x: f"{x:.1f}%")
        agg.columns = ["Region", "Product", "Orders", "Revenue", "Profit", "Margin"]
        st.dataframe(agg, use_container_width=True, hide_index=True)

    # Order status distribution
    ov3, ov4 = st.columns(2)
    with ov3:
        st.markdown(section_header("Order Status Mix", "Distribution of order statuses."), unsafe_allow_html=True)
        if "order_status" in filtered_orders.columns:
            status_df = filtered_orders["order_status"].value_counts().reset_index()
            status_df.columns = ["Status", "Count"]
            fig = px.bar(status_df, x="Status", y="Count", color_discrete_sequence=[PALETTE["secondary"]])
            st.plotly_chart(apply_chart_theme(fig, height=260, showlegend=False), use_container_width=True)

    with ov4:
        st.markdown(section_header("Revenue by Region", "Proportional share."), unsafe_allow_html=True)
        if region_rev is not None and not region_rev.empty:
            fig = px.pie(region_rev, names="region", values="net_revenue", hole=0.55,
                         color_discrete_sequence=PALETTE["sequence"])
            fig.update_traces(textposition="inside", textinfo="percent", textfont_size=11)
            st.plotly_chart(apply_chart_theme(fig, height=260), use_container_width=True)

# ── CUSTOMERS ─────────────────────────────────────────────────
with t_cust:
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown(section_header("Customer Segments", "RFM-based segmentation."), unsafe_allow_html=True)
        if clv is not None and not clv.empty and "customer_segment" in clv.columns:
            seg = clv["customer_segment"].value_counts().reset_index()
            seg.columns = ["Segment", "Count"]
            fig = px.pie(seg, names="Segment", values="Count", hole=0.5,
                         color_discrete_sequence=PALETTE["sequence"])
            fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10)
            st.plotly_chart(apply_chart_theme(fig, height=280), use_container_width=True)
        else:
            st.info("No segment data.")
    with c2:
        st.markdown(section_header("CLV Distribution", "Estimated customer lifetime value spread."), unsafe_allow_html=True)
        if clv is not None and not clv.empty and "estimated_clv" in clv.columns:
            fig = px.histogram(clv, x="estimated_clv", nbins=30,
                               color_discrete_sequence=[PALETTE["secondary"]])
            st.plotly_chart(apply_chart_theme(fig, height=280, showlegend=False), use_container_width=True)
        else:
            st.info("No CLV data.")

    st.markdown(section_header("At-Risk Customers", "Customers requiring win-back attention."), unsafe_allow_html=True)
    if churn is not None and not churn.empty:
        at_risk = churn[churn["churn_status"].isin(["at_risk", "churned"])].head(15).copy()
        if not at_risk.empty:
            display_cols = ["customer_name", "customer_city", "loyalty_tier", "total_orders", "total_revenue", "days_since_last_order", "churn_status", "winback_priority"]
            available_cols = [c for c in display_cols if c in at_risk.columns]
            show_df = at_risk[available_cols].copy()
            if "total_revenue" in show_df.columns:
                show_df["total_revenue"] = show_df["total_revenue"].apply(lambda x: f"{x:,.0f}")
            st.dataframe(show_df, use_container_width=True, hide_index=True)
        else:
            st.info("No at-risk customers detected.")

# ── PRODUCTS ──────────────────────────────────────────────────
with t_prod:
    st.markdown(section_header("Top Products by Revenue", "Best performing products across all stores."), unsafe_allow_html=True)
    if top_prods is not None and not top_prods.empty:
        tp = top_prods.sort_values("total_revenue", ascending=False).head(10).copy()
        fig = px.bar(tp, x="total_revenue", y="product_name", orientation="h",
                     color_discrete_sequence=[PALETTE["primary"]],
                     text=tp["total_revenue"].apply(lambda x: fmt_currency(x)))
        fig.update_traces(textposition="outside", textfont_size=10, cliponaxis=False)
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(apply_chart_theme(fig, height=360, showlegend=False), use_container_width=True)

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(section_header("Product Profitability", "Margin analysis by product."), unsafe_allow_html=True)
        if gross_margin is not None and not gross_margin.empty:
            gm = gross_margin.sort_values("gross_margin_pct", ascending=False).head(10).copy()
            display_cols = ["product_name", "total_revenue", "gross_profit", "gross_margin_pct", "margin_tier"]
            available_cols = [c for c in display_cols if c in gm.columns]
            show_gm = gm[available_cols].copy()
            if "total_revenue" in show_gm.columns:
                show_gm["total_revenue"] = show_gm["total_revenue"].apply(lambda x: f"{x:,.0f}")
            if "gross_profit" in show_gm.columns:
                show_gm["gross_profit"] = show_gm["gross_profit"].apply(lambda x: f"{x:,.0f}")
            if "gross_margin_pct" in show_gm.columns:
                show_gm["gross_margin_pct"] = show_gm["gross_margin_pct"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(show_gm, use_container_width=True, hide_index=True)

    with p2:
        st.markdown(section_header("Revenue Contribution", "Cumulative contribution of top products."), unsafe_allow_html=True)
        if top_prods is not None and not top_prods.empty and "cumulative_contribution_pct" in top_prods.columns:
            tp_chart = top_prods.sort_values("product_rank").head(15)
            fig = px.line(tp_chart, x="product_rank", y="cumulative_contribution_pct",
                          color_discrete_sequence=[PALETTE["primary"]], markers=True)
            fig.add_hline(y=80, line_dash="dot", line_color=PALETTE["muted"],
                          annotation_text="80% threshold", annotation_position="bottom right",
                          annotation_font_size=10, annotation_font_color=PALETTE["muted"])
            st.plotly_chart(apply_chart_theme(fig, height=280, showlegend=False), use_container_width=True)

# ── INVENTORY ─────────────────────────────────────────────────
with t_inv:
    i1, i2 = st.columns(2)
    with i1:
        st.markdown(section_header("Stock Alerts", "Alert severity distribution."), unsafe_allow_html=True)
        if stock_alerts is not None and not stock_alerts.empty and "alert_severity" in stock_alerts.columns:
            sev = stock_alerts["alert_severity"].value_counts().reset_index()
            sev.columns = ["Severity", "Count"]
            color_map = {"critical": PALETTE["danger"], "warning": PALETTE["warning"], "normal": PALETTE["success"]}
            fig = px.bar(sev, x="Severity", y="Count",
                         color="Severity", color_discrete_map=color_map)
            st.plotly_chart(apply_chart_theme(fig, height=260, showlegend=False), use_container_width=True)
        else:
            st.info("No stock alert data.")

    with i2:
        st.markdown(section_header("Inventory Turnover", "Movement classification."), unsafe_allow_html=True)
        if inv_turnover is not None and not inv_turnover.empty:
            turn_col = "turnover_category" if "turnover_category" in inv_turnover.columns else "movement_category"
            if turn_col in inv_turnover.columns:
                tc = inv_turnover[turn_col].value_counts().reset_index()
                tc.columns = ["Category", "Count"]
                fig = px.pie(tc, names="Category", values="Count", hole=0.5,
                             color_discrete_sequence=PALETTE["sequence"])
                fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10)
                st.plotly_chart(apply_chart_theme(fig, height=260), use_container_width=True)

    st.markdown(section_header("Replenishment Queue", "Items requiring restock attention."), unsafe_allow_html=True)
    if stock_alerts is not None and not stock_alerts.empty:
        repl_cols = ["product_name", "store_name", "region", "quantity_on_hand", "reorder_level", "alert_severity", "suggested_reorder_qty"]
        available_cols = [c for c in repl_cols if c in stock_alerts.columns]
        st.dataframe(stock_alerts[available_cols].head(15), use_container_width=True, hide_index=True)

# ── FINANCE ───────────────────────────────────────────────────
with t_fin:
    st.markdown(section_header("Revenue to Profit Waterfall", "Financial flow from gross revenue to profit."), unsafe_allow_html=True)
    if not filtered_orders.empty:
        gross_rev = filtered_orders["line_total_gross"].sum() if "line_total_gross" in filtered_orders.columns else 0
        discounts = -filtered_orders["discount_amount"].sum() if "discount_amount" in filtered_orders.columns else 0
        net_rev = gross_rev + discounts
        cogs = -filtered_orders["line_cost"].sum() if "line_cost" in filtered_orders.columns else 0
        profit = net_rev + cogs

        fig_wf = go.Figure(go.Waterfall(
            name="", orientation="v",
            measure=["absolute", "relative", "total", "relative", "total"],
            x=["Gross Revenue", "Discounts", "Net Revenue", "COGS", "Gross Profit"],
            textposition="outside",
            text=[fmt_currency(x) for x in [gross_rev, discounts, net_rev, cogs, profit]],
            y=[gross_rev, discounts, net_rev, cogs, profit],
            connector={"line": {"color": "rgba(255,255,255,0.06)"}},
            decreasing={"marker": {"color": PALETTE["danger"]}},
            increasing={"marker": {"color": PALETTE["success"]}},
            totals={"marker": {"color": PALETTE["primary"]}},
        ))
        st.plotly_chart(apply_chart_theme(fig_wf, height=380), use_container_width=True)

    f1, f2 = st.columns(2)
    with f1:
        st.markdown(section_header("Refund Analysis", "Return categories and volume."), unsafe_allow_html=True)
        if refund_data is not None and not refund_data.empty:
            cat_col = "return_category" if "return_category" in refund_data.columns else refund_data.columns[0]
            cnt_col = "return_count" if "return_count" in refund_data.columns else refund_data.columns[1]
            fig = px.pie(refund_data, names=cat_col, values=cnt_col, hole=0.5,
                         color_discrete_sequence=PALETTE["sequence"])
            fig.update_traces(textposition="inside", textinfo="percent", textfont_size=10)
            st.plotly_chart(apply_chart_theme(fig, height=280), use_container_width=True)
    with f2:
        st.markdown(section_header("Payment Reliability", "Success rates by payment method."), unsafe_allow_html=True)
        if payment_rates is not None and not payment_rates.empty:
            pr_cols = ["payment_method", "total_transactions", "success_rate_pct", "reliability_tier"]
            available_cols = [c for c in pr_cols if c in payment_rates.columns]
            show_pr = payment_rates[available_cols].copy()
            if "success_rate_pct" in show_pr.columns:
                show_pr["success_rate_pct"] = show_pr["success_rate_pct"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(show_pr, use_container_width=True, hide_index=True)

# ── PROMOTIONS ────────────────────────────────────────────────
with t_promo:
    st.markdown(section_header("Promotion Effectiveness", "Performance of active and past promotions."), unsafe_allow_html=True)
    if promo_perf is not None and not promo_perf.empty:
        pr_display = promo_perf.copy()
        pr_cols = ["promotion_name", "promoted_orders", "unique_customers", "net_revenue", "total_discount_given", "total_profit", "is_currently_active"]
        available_cols = [c for c in pr_cols if c in pr_display.columns]
        show_promo = pr_display[available_cols].copy()
        if "net_revenue" in show_promo.columns:
            show_promo["net_revenue"] = show_promo["net_revenue"].apply(lambda x: f"{x:,.0f}")
        if "total_discount_given" in show_promo.columns:
            show_promo["total_discount_given"] = show_promo["total_discount_given"].apply(lambda x: f"{x:,.0f}")
        if "total_profit" in show_promo.columns:
            show_promo["total_profit"] = show_promo["total_profit"].apply(lambda x: f"{x:,.0f}")
        st.dataframe(show_promo, use_container_width=True, hide_index=True)

        st.markdown(section_header("Promotion Revenue Comparison"), unsafe_allow_html=True)
        fig = px.bar(promo_perf.sort_values("net_revenue", ascending=True).tail(15),
                     y="promotion_name", x="net_revenue", orientation="h",
                     color="is_currently_active",
                     color_discrete_map={True: PALETTE["success"], False: PALETTE["muted"]},
                     text=promo_perf.sort_values("net_revenue", ascending=True).tail(15)["net_revenue"].apply(lambda x: fmt_currency(x)))
        fig.update_traces(textposition="outside", textfont_size=10)
        st.plotly_chart(apply_chart_theme(fig, height=400), use_container_width=True)
    else:
        st.info("No promotion data available.")

# ── SUPPLY CHAIN ──────────────────────────────────────────────
with t_supply:
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(section_header("Delivery Performance", "On-time delivery trend by month."), unsafe_allow_html=True)
        if delivery_perf is not None and not delivery_perf.empty:
            fig = px.line(delivery_perf, x="shipping_month", y="on_time_pct",
                          color_discrete_sequence=[PALETTE["success"]], markers=True)
            fig.update_traces(line=dict(width=2))
            st.plotly_chart(apply_chart_theme(fig, height=280, showlegend=False), use_container_width=True)
        else:
            st.info("No delivery data available.")
    with sc2:
        st.markdown(section_header("Supplier Performance", "Top suppliers by stock volume."), unsafe_allow_html=True)
        if supplier_perf is not None and not supplier_perf.empty:
            sp = supplier_perf.sort_values("total_units_in_stock", ascending=False).head(15).copy()
            sp_cols = ["supplier_name", "supplier_city", "total_products_supplied", "total_units_in_stock"]
            available_cols = [c for c in sp_cols if c in sp.columns]
            show_sp = sp[available_cols].copy()
            if "total_units_in_stock" in show_sp.columns:
                show_sp["total_units_in_stock"] = show_sp["total_units_in_stock"].apply(lambda x: f"{int(x):,}")
            st.dataframe(show_sp, use_container_width=True, hide_index=True)
        else:
            st.info("No supplier data available.")

# ── ABOUT ─────────────────────────────────────────────────────
with t_about:
    # Executive summary
    top_region = region_rev.sort_values("net_revenue", ascending=False).iloc[0]["region"] if (region_rev is not None and not region_rev.empty) else "N/A"
    top_region_rev = region_rev.sort_values("net_revenue", ascending=False).iloc[0]["net_revenue"] if (region_rev is not None and not region_rev.empty) else 0
    top_product = top_prods.sort_values("total_revenue", ascending=False).iloc[0]["product_name"] if (top_prods is not None and not top_prods.empty) else "N/A"
    avg_clv = clv["estimated_clv"].mean() if (clv is not None and not clv.empty and "estimated_clv" in clv.columns) else 0

    st.markdown(f'''
    <div class="about-section">
        <div class="about-section-title">Executive Summary</div>
        <div class="about-section-body">
            The platform processed <strong>{fmt_number(total_orders)}</strong> orders generating <strong>{fmt_currency(total_net_rev)}</strong> in net revenue
            with a gross margin of <strong>{fmt_pct(gross_margin_val)}</strong>.
            The <strong>{top_region}</strong> region leads with <strong>{fmt_currency(top_region_rev)}</strong> in revenue.
            The top-performing product is <strong>{top_product}</strong>.
            Average customer lifetime value is <strong>{fmt_currency(avg_clv)}</strong> with a return rate of <strong>{fmt_pct(refund_rate)}</strong>.
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="about-section">
        <div class="about-section-title">Pipeline Architecture</div>
        <div class="about-section-body">
            <strong>Data Generation</strong> Synthetic retail data via Python scripts<br>
            <strong>Ingestion</strong> PostgreSQL Bronze layer (raw tables)<br>
            <strong>Transformation</strong> dbt models: Bronze &rarr; Silver (cleaned/joined) &rarr; Gold (dimensional marts)<br>
            <strong>Orchestration</strong> Apache Airflow DAG with scheduled runs<br>
            <strong>Visualization</strong> Streamlit dashboard consuming Gold schema
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="about-section">
        <div class="about-section-title">Metric Definitions</div>
        <div class="about-section-body">
            <strong>Net Revenue</strong> Gross revenue minus discounts<br>
            <strong>Gross Profit</strong> Net revenue minus cost of goods sold<br>
            <strong>AOV</strong> Average order value: net revenue / unique orders<br>
            <strong>Gross Margin</strong> Gross profit as a percentage of net revenue<br>
            <strong>Return Rate</strong> Refunded transactions as a percentage of total<br>
            <strong>On-Time Delivery</strong> Shipments delivered before or on estimated date<br>
            <strong>CLV</strong> Estimated customer lifetime value based on RFM scoring
        </div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown(f'''
    <div class="about-section">
        <div class="about-section-title">Data Lineage</div>
        <div class="about-section-body">
            This dashboard reads exclusively from the <strong>gold</strong> schema in PostgreSQL.<br>
            Source table: <strong>gold.fct_orders</strong> ({fmt_number(len(fct_orders))} records, {len(fct_orders.columns)} columns)<br>
            Supporting marts: daily_sales, customer_lifetime_value, churn_risk, top_products, revenue_by_region,
            payment_success_rate, stock_alerts, inventory_turnover, gross_margin, refund_analysis,
            promotion_performance, supplier_performance, delivery_performance
        </div>
    </div>
    ''', unsafe_allow_html=True)
