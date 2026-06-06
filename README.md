# 💊 ProcDNA PharmaSales Intelligence Pipeline

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Cloud-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Engineering-green.svg)

## 📌 Executive Summary
An end-to-end, cloud-native Commercial Analytics SaaS platform engineered for the pharmaceutical industry. This project demonstrates full-stack data engineering capabilities, transitioning from synthetic data generation and defensive ETL processing to secure cloud warehousing and dynamic data ingestion.

## 🚀 Key Enterprise Features

* **Dynamic Vendor Ingestion Engine:** A UI-driven portal that allows users to upload disparate, messy third-party vendor CSV files. It features a dynamic schema-mapping engine that normalizes custom column names to the database target schema, enforces data types (`errors='coerce'`), and appends the clean data to the cloud warehouse in real-time.
* **Enterprise Security Gateway:** Implemented Role-Based Access Control (RBAC) utilizing SHA-256 password cryptography, strict regex password validation, and Streamlit session state management to protect sensitive commercial data.
* **Defensive ETL Pipeline:** Automated Python pipeline that extracts raw data, performs Quality Gatekeeping (detecting negative pricing, dropping null critical identifiers), transforms KPIs, and securely loads to a Render-hosted PostgreSQL database.
* **Synthetic Data Engineering:** Programmatic generation of 10,000+ rows of realistic pharmaceutical sales data utilizing `numpy` normal distributions and probability to simulate accurate enterprise data volume.
* **Real-Time BI Dashboard:** A reactive frontend built on Streamlit and Plotly that caches database queries for high-performance KPI rendering and multidimensional filtering.

## 🏗️ System Architecture

1. **Source:** `generate_data.py` (Creates baseline corporate data) OR Vendor CSV Upload.
2. **Transform (ETL):** `etl_pipeline.py` (Validates types, cleans anomalies, calculates revenue).
3. **Warehouse:** PostgreSQL Database (Hosted securely on Render).
4. **Application Layer:** `app.py` (Handles Auth, UI, Data Viz, and Dynamic Schema Mapping).

## 💻 Technology Stack
* **Data Processing & Analytics:** Python, Pandas, NumPy
* **Cloud Database:** PostgreSQL, SQLAlchemy
* **Frontend Application:** Streamlit, Plotly Express
* **Security & Auth:** `hashlib` (SHA-256), `re` (Regex)
* **DevOps & Hosting:** Git, Render Cloud Services

## ⚙️ Local Development Setup

If you wish to run this pipeline locally on your machine:

1. **Clone the repository:**

        git clone [https://github.com/abhinavgu27E/procdna-pharma-pipeline.git](https://github.com/abhinavgu27E/procdna-pharma-pipeline.git)
        cd procdna-pharma-pipeline

2. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your PostgreSQL connection string:

        DATABASE_URL=postgresql://username:password@host/database_name

3. **Install Dependencies:**

        pip install -r requirements.txt

4. **Initialize the Data Pipeline:**

        # 1. Generate the initial synthetic dataset
        python generate_data.py
   
        # 2. Run the ETL pipeline to clean and push data to your database
        python etl_pipeline.py

5. **Launch the Application:**

        streamlit run app.py

---
*Developed as a demonstration of production-grade Data Engineering and Commercial Analytics architecture.*
