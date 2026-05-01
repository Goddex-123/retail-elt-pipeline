"""
Retail ELT Platform — Executive Analytics Dashboard
=====================================================
Premium Streamlit dashboard connected directly to PostgreSQL
Gold schema. Glassmorphism design with real-time KPIs.

Access: http://localhost:8501
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os

# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Bombay Bazaar Analytics",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# Premium CSS — Glassmorphism, Animations, Dark Mode
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }

    @keyframes glow {
        0% { text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
        50% { text-shadow: 0 0 20px rgba(79, 172, 254, 0.8), 0 0 30px rgba(0, 242, 254, 0.6); }
        100% { text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    }

    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    h1 {
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s infinite;
        text-align: center;
        padding-bottom: 10px;
        font-size: 3.2rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 2.8rem !important;
        font-weight: 800 !important;
        background: linear-gradient(to right, #ffffff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    [data-testid="stMetricLabel"] {
        font-size: 1.1rem !important;
        color: #a0aec0 !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricDelta"] {
        font-size: 1rem !important;
    }

    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 25px 20px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        text-align: center;
        animation: slideUp 0.6s ease-out;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 40px rgba(79, 172, 254, 0.2);
        border: 1px solid rgba(79, 172, 254, 0.4);
        background: rgba(255, 255, 255, 0.05);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 10px;
        padding: 10px 20px;
        color: #a0aec0;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .stTabs [aria-selected="true"] {
        background: rgba(79, 172, 254, 0.15);
        border: 1px solid rgba(79, 172, 254, 0.4);
        color: #4facfe;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Database Connection
# ============================================================

DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('POSTGRES_USER', 'airflow')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'airflow')}@"
    f"{os.getenv('POSTGRES_HOST', 'postgres')}:"
    f"{os.getenv('POSTGRES_PORT', '5432')}/"
    f"{os.getenv('POSTGRES_DB', 'retail_warehouse')}"
)

CHART_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#a0aec0", "family": "Inter"},
    "margin": dict(l=20, r=20, t=50, b=20),
}


@st.cache_data(ttl=30)
def load_mart(table_name: str):
    """Load a gold mart table."""
    try:
        engine = create_engine(DB_URL)
        return pd.read_sql(f"SELECT * FROM gold.{table_name}", engine)
    except Exception:
        return None


# ============================================================
# Header
# ============================================================

st.title("💎 Bombay Bazaar Executive Analytics")
st.markdown(
    "<p style='text-align: center; color: #a0aec0; margin-bottom: 40px; font-size: 1.1rem;'>"
    "Real-time insights powered by the Modern Data Stack &nbsp;•&nbsp; "
    "Bronze → Silver → Gold"
    "</p>",
    unsafe_allow_html=True,
)

# ============================================================
# Load Data
# ============================================================

with st.spinner("Connecting to Data Warehouse..."):
    fct_orders = load_mart("fct_orders")
    daily_sales = load_mart("daily_sales")
    clv = load_mart("customer_lifetime_value")
    churn = load_mart("churn_risk")
    top_prods = load_mart("top_products")
    region_rev = load_mart("revenue_by_region")
    payment_rates = load_mart("payment_success_rate")

if fct_orders is None or (hasattr(fct_orders, 'empty') and fct_orders.empty):
    st.error(
        "⚠️ Unable to load Gold marts. Please ensure:\n"
        "1. Docker services are running (`make up`)\n"
        "2. The daily pipeline has completed in Airflow\n"
        "3. dbt marts have been built (`make dbt-run`)"
    )
    st.stop()

# ============================================================
# KPI Cards
# ============================================================

completed = fct_orders[fct_orders["order_status"] == "completed"] if "order_status" in fct_orders.columns else fct_orders

total_revenue = completed["line_total_net"].sum() if "line_total_net" in completed.columns else 0
total_orders = completed["order_id"].nunique() if "order_id" in completed.columns else 0
total_customers = completed["customer_id"].nunique() if "customer_id" in completed.columns else 0
avg_order_value = total_revenue / max(total_orders, 1)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
with col2:
    st.metric("Total Orders", f"{total_orders:,}")
with col3:
    st.metric("Unique Customers", f"{total_customers:,}")
with col4:
    st.metric("Avg Order Value", f"₹{avg_order_value:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# Tabbed Sections
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs(["📈 Sales", "👥 Customers", "💰 Finance", "📦 Products"])

with tab1:
    if daily_sales is not None and not daily_sales.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            fig = px.area(
                daily_sales, x="sale_date", y="net_revenue",
                title="Daily Revenue Trend",
                color_discrete_sequence=["#00f2fe"],
            )
            fig.update_layout(**CHART_LAYOUT, title_font=dict(size=18, color="#fff"))
            fig.update_traces(
                fillcolor="rgba(0, 242, 254, 0.12)",
                line=dict(color="#00f2fe", width=3),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col_b:
            if region_rev is not None and not region_rev.empty:
                fig = px.bar(
                    region_rev, x="region", y="net_revenue",
                    title="Revenue by Region",
                    color="region",
                    color_discrete_sequence=["#4facfe", "#00f2fe", "#02aab0", "#0072ff"],
                )
                fig.update_layout(**CHART_LAYOUT, title_font=dict(size=18, color="#fff"), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tab2:
    if clv is not None and not clv.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            segment_counts = clv["customer_segment"].value_counts().reset_index()
            segment_counts.columns = ["Segment", "Count"]
            fig = px.pie(
                segment_counts, values="Count", names="Segment",
                title="Customer Segmentation (RFM)",
                hole=0.5,
                color_discrete_sequence=["#00f2fe", "#4facfe", "#00c6ff", "#0072ff", "#02aab0", "#ffd700"],
            )
            fig.update_layout(**CHART_LAYOUT, title_font=dict(size=18, color="#fff"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col_b:
            if churn is not None and not churn.empty:
                churn_counts = churn["churn_status"].value_counts().reset_index()
                churn_counts.columns = ["Status", "Count"]
                fig = px.bar(
                    churn_counts, x="Status", y="Count",
                    title="Churn Risk Distribution",
                    color="Status",
                    color_discrete_map={
                        "active": "#00f2fe",
                        "warm": "#4facfe",
                        "cooling": "#ffd700",
                        "at_risk": "#ff6b6b",
                        "churned": "#e74c3c",
                    },
                )
                fig.update_layout(**CHART_LAYOUT, title_font=dict(size=18, color="#fff"), showlegend=False)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tab3:
    if payment_rates is not None and not payment_rates.empty:
        fig = px.bar(
            payment_rates, x="payment_method", y="success_rate_pct",
            title="Payment Method Success Rates",
            color="reliability_tier",
            color_discrete_map={
                "excellent": "#00f2fe",
                "good": "#4facfe",
                "fair": "#ffd700",
                "poor": "#e74c3c",
            },
        )
        fig.update_layout(**CHART_LAYOUT, title_font=dict(size=18, color="#fff"))
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with tab4:
    if top_prods is not None and not top_prods.empty:
        top10 = top_prods.head(10)
        fig = px.bar(
            top10, x="product_name", y="total_revenue",
            title="Top 10 Products by Revenue",
            color="revenue_contribution_pct",
            color_continuous_scale=["#0072ff", "#00f2fe"],
        )
        fig.update_layout(**CHART_LAYOUT, title_font=dict(size=18, color="#fff"))
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ============================================================
# Footer
# ============================================================

st.markdown(
    "<hr style='border-color: rgba(255,255,255,0.05); margin-top: 60px;'>"
    "<p style='text-align: center; color: #4a5568; font-size: 0.85rem;'>"
    "Retail ELT Platform v2.0 &nbsp;•&nbsp; Medallion Architecture &nbsp;•&nbsp; "
    "dbt + Airflow + PostgreSQL"
    "</p>",
    unsafe_allow_html=True,
)
