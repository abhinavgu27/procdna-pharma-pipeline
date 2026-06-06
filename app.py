import os
import streamlit as pd
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st

# 1. Page Configuration & Data Loading
st.set_page_config(page_title="PharmaSales Intelligence Dashboard", layout="wide")

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

@st.cache_data(ttl=60)  # Caches data for 1 minute to save cloud bandwidth
def fetch_data():
    engine = create_engine(DATABASE_URL)
    query = "SELECT * FROM pharma_sales"
    df = pd.read_sql(query, engine)
    return df

try:
    df = fetch_data()
except Exception as e:
    st.error(f"Failed to connect to the cloud database: {e}")
    st.stop()

# 2. Sidebar Filters (ProcDNA Analytics Style)
st.sidebar.header("Filter Analytics")
selected_region = st.sidebar.multiselect("Select Region", options=df['Region'].unique(), default=df['Region'].unique())
selected_drug = st.sidebar.multiselect("Select Drug", options=df['Drug_Name'].unique(), default=df['Drug_Name'].unique())

# Filter the dataset based on selections
filtered_df = df[(df['Region'].isin(selected_region)) & (df['Drug_Name'].isin(selected_drug))]

# 3. Header & High-Level KPIs
st.title("💊 PharmaSales Intelligence Dashboard")
st.markdown("Real-time commercial analytics tracking revenue, drug performance, and physician demographics.")
st.markdown("---")

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="Total Revenue", value=f"${filtered_df['Total_Revenue'].sum():,.2f}")
with kpi2:
    st.metric(label="Units Dispensed", value=f"{filtered_df['Units_Dispensed'].sum():,}")
with kpi3:
    st.metric(label="Average Unit Price", value=f"${filtered_df['Unit_Price'].mean():,.2f}")

st.markdown("---")

# 4. Data Visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue by Region")
    fig_region = px.bar(
        filtered_df.groupby('Region')['Total_Revenue'].sum().reset_index(),
        x='Region', y='Total_Revenue',
        labels={'Total_Revenue': 'Revenue ($)'},
        template='plotly_white'
    )
    st.plotly_chart(fig_region, use_container_width=True)

with col2:
    st.subheader("Top Performing Drugs")
    fig_drug = px.pie(
        filtered_df.groupby('Drug_Name')['Total_Revenue'].sum().reset_index(),
        values='Total_Revenue', names='Drug_Name',
        hole=0.4,
        template='plotly_white'
    )
    st.plotly_chart(fig_drug, use_container_width=True)

# 5. Advanced Drill-down (Physician Segments)
st.markdown("---")
st.subheader("Physician Specialty Revenue Distribution")
fig_spec = px.box(
    filtered_df,
    x='Physician_Specialty', y='Total_Revenue',
    color='Drug_Name',
    labels={'Physician_Specialty': 'Specialty', 'Total_Revenue': 'Revenue Per Order ($)'},
    template='plotly_white'
)
st.plotly_chart(fig_spec, use_container_width=True)