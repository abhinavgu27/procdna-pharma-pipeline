import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_pharma_data(num_records=10000):
    print(f"Generating {num_records} rows of mock pharmaceutical data...")
    
    # Mock Data Arrays
    drugs = ['CardioZest', 'NeuroCalm', 'Immunex', 'DiabetoReg', 'PulmoClear']
    regions = ['North America', 'Europe', 'APAC', 'Latin America', 'MENA']
    specialties = ['Cardiology', 'Neurology', 'Internal Medicine', 'Endocrinology', 'Pulmonology']
    
    # Generate random dates over the last year
    start_date = datetime.now() - timedelta(days=365)
    dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(num_records)]
    
    # Build the DataFrame
    df = pd.DataFrame({
        'Transaction_ID': [f"TRX-{100000 + i}" for i in range(num_records)],
        'Date': dates,
        'Drug_Name': np.random.choice(drugs, num_records),
        'Region': np.random.choice(regions, num_records),
        'Physician_Specialty': np.random.choice(specialties, num_records),
        'Units_Dispensed': np.random.randint(10, 500, num_records),
        'Unit_Price': np.random.uniform(45.50, 350.00, num_records).round(2)
    })
    
    # Inject a few missing values to prove your ETL cleaning skills later
    missing_indices = np.random.choice(df.index, size=int(num_records * 0.02), replace=False)
    df.loc[missing_indices, 'Physician_Specialty'] = np.nan
    
    # Save to CSV inside the data folder
    filename = 'data/raw_pharma_sales.csv'
    df.to_csv(filename, index=False)
    print(f"Success! Data saved to {filename}")

if __name__ == "__main__":
    generate_pharma_data()