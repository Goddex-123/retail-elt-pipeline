import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import random
from datetime import datetime, timedelta

# Database Connection (using the local Docker Postgres)
DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

def generate_customers(n=100):
    """Generates messy customer data."""
    print("Generating Customers...")
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Pune', None, 'mumbai', ' DEL ']
    data = {
        'customer_id': range(1, n + 1),
        'name': [f"Customer_{i}" for i in range(1, n + 1)],
        'city': [random.choice(cities) for _ in range(n)],
        'signup_date': [(datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d') for _ in range(n)]
    }
    df = pd.DataFrame(data)
    # Introduce duplicates
    df = pd.concat([df, df.sample(int(n * 0.1))])
    return df

def generate_products():
    """Generates product catalog."""
    print("Generating Products...")
    data = {
        'product_id': [101, 102, 103, 104, 105],
        'product_name': ['Laptop', 'Smartphone', 'Headphones', 'Monitor', 'Keyboard'],
        'category': ['Electronics', 'Electronics', 'Accessories', 'Electronics', 'Accessories'],
        'price': [50000, 30000, 2000, 15000, 1000]
    }
    return pd.DataFrame(data)

def generate_orders(customers_df, products_df, n=500):
    """Generates messy order data."""
    print("Generating Orders...")
    data = {
        'order_id': range(1001, 1001 + n),
        'customer_id': [random.choice(customers_df['customer_id'].dropna().tolist()) for _ in range(n)],
        'product_id': [random.choice(products_df['product_id'].tolist()) for _ in range(n)],
        'quantity': [random.randint(1, 5) for _ in range(n)],
        'order_date': [(datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S') for _ in range(n)]
    }
    df = pd.DataFrame(data)
    
    # Introduce some bad data
    bad_rows = df.sample(int(n * 0.05)).index
    df.loc[bad_rows, 'quantity'] = -1  # Negative quantity
    
    return df

def load_to_db():
    engine = create_engine(DB_URL)
    
    # Create source schema if not exists
    with engine.connect() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS source;")
    
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders(customers, products)
    
    # Load to source schema
    customers.to_sql('customers', engine, schema='source', if_exists='replace', index=False)
    products.to_sql('products', engine, schema='source', if_exists='replace', index=False)
    orders.to_sql('orders', engine, schema='source', if_exists='replace', index=False)
    
    print("Data loaded to 'source' schema successfully!")

if __name__ == "__main__":
    load_to_db()
