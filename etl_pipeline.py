import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import logging

# Set up enterprise logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def run_etl():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        logging.error("DATABASE_URL is missing. Check your .env file.")
        return

    try:
        # 1. Extract
        logging.info("Extracting raw data...")
        df = pd.read_csv('raw_pharma_sales.csv')
        
        # 2. Validate (Quality Gatekeeping)
        if (df['Unit_Price'] < 0).any():
            raise ValueError("CRITICAL: Negative pricing detected in source data.")
        if df['Region'].isnull().any():
            logging.warning("Missing regions found. Dropping incomplete records.")
            df = df.dropna(subset=['Region'])
            
        # 3. Transform
        logging.info("Transforming data...")
        df['Total_Revenue'] = df['Units_Dispensed'] * df['Unit_Price']
        
        # 4. Load
        logging.info("Connecting to Render Cloud Database...")
        engine = create_engine(db_url)
        df.to_sql('pharma_sales', engine, if_exists='replace', index=False)
        
        logging.info("✅ ETL Pipeline completed successfully. Data is live in the cloud.")
        
    except Exception as e:
        logging.error(f"ETL Pipeline Failed: {e}")

if __name__ == "__main__":
    run_etl()