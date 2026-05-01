import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import time

st.set_page_config(page_title="Bombay Bazaar Analytics", page_icon="💎", layout="wide")

# Custom Premium CSS with Glassmorphism and Animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    /* Global Styles */
    .stApp {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Animation */
    @keyframes glow {
        0% { text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
        50% { text-shadow: 0 0 20px rgba(79, 172, 254, 0.8), 0 0 30px rgba(0, 242, 254, 0.6); }
        100% { text-shadow: 0 0 10px rgba(0, 242, 254, 0.5); }
    }
    
    h1 {
        background: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow 3s infinite;
        text-align: center;
        padding-bottom: 20px;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
    }

    /* Metric Cards Glassmorphism & Hover */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: linear-gradient(to right, #ffffff 0%, #e2e8f0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1.2rem !important;
        color: #a0aec0 !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 30px 20px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0; left: -100%;
        width: 50%; height: 100%;
        background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0) 100%);
        transform: skewX(-25deg);
        transition: all 0.7s ease;
    }
    
    div[data-testid="metric-container"]:hover::before {
        left: 200%;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(79, 172, 254, 0.2);
        border: 1px solid rgba(79, 172, 254, 0.4);
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("💎 Bombay Bazaar Executive Analytics")
st.markdown("<p style='text-align: center; color: #a0aec0; margin-bottom: 50px; font-size: 1.2rem;'>Live real-time insights powered by our Modern Data Stack</p>", unsafe_allow_html=True)

# Database Connection directly to PostgreSQL container
DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

@st.cache_data(ttl=30)
def load_data():
    try:
        engine = create_engine(DB_URL)
        df = pd.read_sql("SELECT * FROM public_gold.fct_orders", engine)
        return df
    except Exception as e:
        return None

with st.spinner("Connecting to PostgreSQL Data Warehouse..."):
    df = load_data()

if df is None or df.empty:
    st.error("⚠️ Unable to load data from the Gold Schema. Please check if PostgreSQL is running and the ELT pipeline has completed.")
else:
    # Top KPI Cards
    total_orders = df['order_id'].nunique()
    total_items = df['quantity'].sum()
    top_city = df['customer_city'].value_counts().index[0] if 'customer_city' in df.columns else "N/A"
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Orders", f"{total_orders:,}")
    with col2:
        st.metric("Total Items Sold", f"{total_items:,}")
    with col3:
        st.metric("Top City", top_city)
        
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Dark Theme Chart Configurations
    chart_config = {
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'font': {'color': '#a0aec0', 'family': 'Inter'},
        'margin': dict(l=20, r=20, t=50, b=20)
    }
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if 'customer_city' in df.columns:
            city_counts = df['customer_city'].value_counts().reset_index()
            city_counts.columns = ['City', 'Orders']
            fig_city = px.bar(city_counts, x='City', y='Orders', title="Order Distribution by City",
                              color_discrete_sequence=['#4facfe'])
            fig_city.update_layout(**chart_config, title_font=dict(size=20, color='#ffffff', family='Inter'))
            fig_city.update_traces(marker_line_width=0, opacity=0.85, hovertemplate="<b>%{x}</b><br>%{y} Orders<extra></extra>")
            
            # Make chart hover slightly zoom
            st.plotly_chart(fig_city, use_container_width=True, config={'displayModeBar': False})
            
    with col_b:
        if 'product_id' in df.columns:
            product_sales = df.groupby('product_id')['quantity'].sum().reset_index()
            product_sales = product_sales.sort_values(by='quantity', ascending=False).head(5)
            product_names = {101: 'Laptop', 102: 'Smartphone', 103: 'Headphones', 104: 'Monitor', 105: 'Keyboard'}
            product_sales['Product Name'] = product_sales['product_id'].map(product_names).fillna('Unknown')
            
            fig_prod = px.pie(product_sales, values='quantity', names='Product Name', title="Top Selling Products",
                              hole=0.5, color_discrete_sequence=['#00f2fe', '#4facfe', '#00c6ff', '#0072ff', '#02aab0'])
            fig_prod.update_layout(**chart_config, title_font=dict(size=20, color='#ffffff', family='Inter'))
            fig_prod.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=14,
                                  marker=dict(line=dict(color='#0e1117', width=3)))
            st.plotly_chart(fig_prod, use_container_width=True, config={'displayModeBar': False})

    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'order_date' in df.columns:
        df['date'] = pd.to_datetime(df['order_date']).dt.date
        daily_orders = df.groupby('date')['order_id'].count().reset_index()
        daily_orders.columns = ['Date', 'Orders']
        fig_trend = px.area(daily_orders, x='Date', y='Orders', title="Daily Order Volume Trend",
                            color_discrete_sequence=['#00f2fe'])
        fig_trend.update_layout(**chart_config, title_font=dict(size=20, color='#ffffff', family='Inter'))
        fig_trend.update_traces(fillcolor='rgba(0, 242, 254, 0.15)', line=dict(color='#00f2fe', width=4),
                                mode='lines+markers', marker=dict(size=8, color='#ffffff', line=dict(width=2, color='#00f2fe')),
                                hovertemplate="<b>%{x}</b><br>%{y} Orders<extra></extra>")
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
