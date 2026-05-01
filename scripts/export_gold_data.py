import pandas as pd
from sqlalchemy import create_engine
import os

# Database Connection (using the local Docker Postgres)
DB_URL = "postgresql+psycopg2://airflow:airflow@postgres:5432/airflow"

def export_gold_to_csv():
    """Extracts the final gold data and saves it as a CSV for the dashboard."""
    print("Starting Export of Gold Data...")
    engine = create_engine(DB_URL)
    
    # Ensure the shared data directory exists
    os.makedirs('/opt/airflow/shared_data', exist_ok=True)
    
    output_path = '/opt/airflow/shared_data/final_gold_data.csv'
    
    try:
        # Read from gold schema
        df = pd.read_sql("SELECT * FROM public_gold.fct_orders", engine)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"Successfully exported {len(df)} rows to {output_path}")
        
    except Exception as e:
        print(f"Failed to export gold data: {e}")
        raise e

if __name__ == "__main__":
    export_gold_to_csv()
