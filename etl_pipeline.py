import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load database URL from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file!")

# Convert connection string from 'postgresql://' to 'postgresql+psycopg2://' for SQLAlchemy compatibility
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

def run_etl():
    print("--- Starting ETL Pipeline ---")
    
    # 1. EXTRACT
    csv_path = 'data/raw_pharma_sales.csv'
    print(f"Extracting data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: {csv_path} not found. Please run generate_data.py first.")
        return

    # 2. TRANSFORM
    print("Transforming data...")
    
    # Clean Missing Values (Data Quality Rule)
    # If Physician_Specialty is missing, fill with 'Unknown'
    missing_count = df['Physician_Specialty'].isnull().sum()
    df['Physician_Specialty'] = df['Physician_Specialty'].fillna('Unknown')
    print(f"-> Handled missing data: Filled {missing_count} rows in 'Physician_Specialty' with 'Unknown'.")
    
    # Ensure proper data types
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Business Logic Calculation: Total Revenue
    df['Total_Revenue'] = (df['Units_Dispensed'] * df['Unit_Price']).round(2)
    print("-> Calculated business metric: 'Total_Revenue' = Units * Price.")
    
    # 3. LOAD
    print("Connecting to Render Cloud PostgreSQL...")
    engine = create_engine(DATABASE_URL)
    
    print("Loading data into 'pharma_sales' table...")
    # if_exists='replace' automatically creates the table schema structure for us on Render!
    df.to_sql('pharma_sales', engine, if_exists='replace', index=False)
    
    print("--- ETL Pipeline Completed Successfully! ---")
    print(f"Loaded {len(df)} rows into the cloud.")

if __name__ == "__main__":
    run_etl()