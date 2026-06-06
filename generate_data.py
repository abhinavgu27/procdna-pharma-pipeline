import pandas as pd
import numpy as np
import random

def generate_pharma_data(num_rows=10000):
    np.random.seed(42)
    
    regions = ['North America', 'Europe', 'APAC', 'MENA', 'Latin America']
    drugs = ['CardioZest', 'NeuroCalm', 'Immunex', 'PulmoClear', 'DiabetoReg']
    
    data = {
        'Transaction_ID': [f"TXN-{i+1000}" for i in range(num_rows)],
        'Region': np.random.choice(regions, num_rows),
        'Drug_Name': np.random.choice(drugs, num_rows),
        'Units_Dispensed': np.random.randint(50, 500, num_rows),
        # Generates a realistic price with slight variations
        'Unit_Price': np.round(np.random.normal(200, 20, num_rows), 2) 
    }
    
    df = pd.DataFrame(data)
    
    # Save to the data folder
    df.to_csv('raw_pharma_sales.csv', index=False)
    print(f"✅ Successfully generated {num_rows} rows of raw pharmaceutical data.")

if __name__ == "__main__":
    generate_pharma_data()