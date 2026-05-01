import pandas as pd
from sqlalchemy import create_engine

# Database Connection (using the local Docker Postgres)
# In a real scenario, SOURCE_DB and DESTINATION_DB would be different.
DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

def extract_and_load():
    """
    Simulates an ELT tool like Airbyte.
    Extracts from 'source' schema and loads raw data into 'bronze' schema.
    """
    print("Starting Extraction Process...")
    engine = create_engine(DB_URL)
    
    # Create bronze schema if not exists
    with engine.connect() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS bronze;")
    
    tables = ['customers', 'products', 'orders']
    
    for table in tables:
        print(f"Extracting {table} from source...")
        try:
            # Extract
            df = pd.read_sql(f"SELECT * FROM source.{table}", engine)
            
            # Load to Bronze (Raw Layer - No transformations!)
            # In ELT, we load it exactly as it is.
            print(f"Loading {table} to bronze...")
            df.to_sql(table, engine, schema='bronze', if_exists='replace', index=False)
            print(f"Successfully loaded {len(df)} rows into bronze.{table}")
            
        except Exception as e:
            print(f"Failed to extract/load {table}: {e}")

if __name__ == "__main__":
    extract_and_load()
