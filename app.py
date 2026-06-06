import os
import re
import hashlib
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st

# --- 1. PAGE CONFIG MUST BE FIRST ---
st.set_page_config(page_title="PharmaSales Intelligence", page_icon="💊", layout="wide")

# --- 2. ENTERPRISE AUTHENTICATION GATEWAY ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    if len(password) < 8: return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password): return "Password must contain an uppercase letter."
    if not re.search(r"[a-z]", password): return "Password must contain a lowercase letter."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return "Password must contain a special symbol."
    return "Valid"

if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center;'>💊 Global Pharma Analytics Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 50px;'>Authorized Personnel Only.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register New Admin"])
        
        with tab2:
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass")
            new_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_conf")
            if st.button("Register Account", type="primary", use_container_width=True):
                if new_user in st.session_state['users_db']: st.error("Username already exists!")
                elif new_pass != new_pass_confirm: st.error("Passwords do not match!")
                else:
                    status = validate_password(new_pass)
                    if status == "Valid":
                        st.session_state['users_db'][new_user] = hash_password(new_pass)
                        st.success("Account created! Switch to Login tab.")
                    else: st.error(status)

        with tab1:
            auth_user = st.text_input("Username")
            auth_pass = st.text_input("Password", type="password")
            if st.button("Authenticate", type="primary", use_container_width=True):
                if auth_user in st.session_state['users_db'] and st.session_state['users_db'][auth_user] == hash_password(auth_pass):
                    st.session_state['logged_in'] = True
                    st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

# --- 3. MAIN DASHBOARD ---
st.sidebar.button("Log Out", on_click=lambda: st.session_state.update(logged_in=False))

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

@st.cache_data(ttl=60)
def fetch_data():
    try:
        engine = create_engine(DATABASE_URL)
        return pd.read_sql("SELECT * FROM pharma_sales", engine)
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()

df = fetch_data()
if df.empty:
    st.warning("No data found in the cloud warehouse. Please run the ETL pipeline.")
    st.stop()

st.title("💊 PharmaSales Intelligence Dashboard")

# --- 4. DYNAMIC INGESTION PORTAL ---
with st.expander("📥 Enterprise Data Ingestion Portal (Upload Custom Files)", expanded=False):
    st.caption("Enterprise Evaluator Sandbox: Upload any custom commercial CSV dataset to test the dynamic schema mapping engine.")
    uploaded_file = st.file_uploader("Drop raw vendor sales file here", type=["csv"])
    
    if uploaded_file is not None:
        raw_uploaded_df = pd.read_csv(uploaded_file)
        st.dataframe(raw_uploaded_df.head(3))
        
        target_columns = ['Region', 'Drug_Name', 'Units_Dispensed', 'Unit_Price']
        user_mappings = {}
        cols = st.columns(4)
        available_cols = ["-- Select Column --"] + list(raw_uploaded_df.columns)
        
        for i, col in enumerate(target_columns):
            with cols[i]: user_mappings[col] = st.selectbox(f"Target: {col}", available_cols, key=f"map_{col}")
            
        if all(user_mappings[col] != "-- Select Column --" for col in target_columns):
            if st.button("🚀 Execute Cloud Ingestion", type="primary"):
                with st.spinner("Processing ETL..."):
                    try:
                        rename_dict = {user_mappings[col]: col for col in target_columns}
                        processed_df = raw_uploaded_df[list(rename_dict.keys())].rename(columns=rename_dict)
                        
                        processed_df['Units_Dispensed'] = pd.to_numeric(processed_df['Units_Dispensed'], errors='coerce')
                        processed_df['Unit_Price'] = pd.to_numeric(processed_df['Unit_Price'], errors='coerce')
                        processed_df['Total_Revenue'] = processed_df['Units_Dispensed'] * processed_df['Unit_Price']
                        processed_df = processed_df.dropna()
                        
                        engine = create_engine(DATABASE_URL)
                        processed_df.to_sql('pharma_sales', engine, if_exists='append', index=False)
                        
                        st.success("Custom file live!")
                        fetch_data.clear()
                        st.rerun()
                    except Exception as e: st.error(f"Ingestion Aborted: {e}")

st.markdown("---")

# --- 5. ANALYTICS & CHARTS ---
st.sidebar.header("Filter Analytics")
selected_region = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
selected_drug = st.sidebar.multiselect("Drug", df['Drug_Name'].unique(), default=df['Drug_Name'].unique())

filtered_df = df[(df['Region'].isin(selected_region)) & (df['Drug_Name'].isin(selected_drug))]

# --- NEW: POWER BI EXPORT BUTTON ---
st.sidebar.markdown("---")
st.sidebar.header("Export Data")
csv_data = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button(
    label="⬇️ Download CSV for Power BI",
    data=csv_data,
    file_name="pharma_sales_export.csv",
    mime="text/csv"
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${filtered_df['Total_Revenue'].sum():,.2f}")
col2.metric("Units Dispensed", f"{filtered_df['Units_Dispensed'].sum():,.0f}")
col3.metric("Average Unit Price", f"${filtered_df['Unit_Price'].mean():,.2f}")
st.markdown("---")

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    fig_region = px.bar(filtered_df.groupby('Region')['Total_Revenue'].sum().reset_index(), x='Region', y='Total_Revenue', color_discrete_sequence=['#4C62F5'], title="Revenue by Region")
    st.plotly_chart(fig_region, use_container_width=True)

with col_chart2:
    fig_drug = px.pie(filtered_df, names='Drug_Name', values='Total_Revenue', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel, title="Top Performing Drugs")
    st.plotly_chart(fig_drug, use_container_width=True)