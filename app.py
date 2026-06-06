import os
import re
import hashlib
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
import streamlit as st

# 1. PAGE CONFIG MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="PharmaSales Intelligence", page_icon="💊", layout="wide")

# ---------------------------------------------------------
# 🔒 MODULE 1: ENTERPRISE AUTHENTICATION & SECURITY GATEWAY
# ---------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'users_db' not in st.session_state:
    # Initialize dictionary to hold registered users securely
    st.session_state['users_db'] = {}

def hash_password(password):
    """Securely hash the password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def validate_password(password):
    """Enforce strict enterprise password requirements"""
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special symbol (e.g., !@#$)."
    return "Valid"

# If the user is NOT logged in, show the Login/Register screens
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center;'>💊 ProcDNA Analytics Portal</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 50px;'>Authorized Personnel Only. Please log in to access the cloud warehouse.</p>", unsafe_allow_html=True)
    
    # Center the login box on the screen
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register New Admin"])
        
        with tab2:
            st.subheader("Create a New Account")
            new_user = st.text_input("New Username", key="reg_user")
            new_pass = st.text_input("New Password", type="password", key="reg_pass", help="Must contain 8+ characters, an uppercase letter, a lowercase letter, and a special symbol.")
            new_pass_confirm = st.text_input("Confirm Password", type="password", key="reg_pass_conf")
            
            if st.button("Register Account", type="primary", use_container_width=True):
                if new_user in st.session_state['users_db']:
                    st.error("Username already exists!")
                elif new_pass != new_pass_confirm:
                    st.error("Passwords do not match!")
                else:
                    validation_status = validate_password(new_pass)
                    if validation_status == "Valid":
                        # Save user securely using the hash
                        st.session_state['users_db'][new_user] = hash_password(new_pass)
                        st.success("Account created successfully! You can now switch to the Login tab.")
                    else:
                        st.error(validation_status)

        with tab1:
            st.subheader("System Login")
            auth_user = st.text_input("Username")
            auth_pass = st.text_input("Password", type="password")
            
            if st.button("Authenticate", type="primary", use_container_width=True):
                if auth_user in st.session_state['users_db']:
                    # Compare the hashed input against the stored hash
                    if st.session_state['users_db'][auth_user] == hash_password(auth_pass):
                        st.session_state['logged_in'] = True
                        st.rerun() # Refresh page to show dashboard
                    else:
                        st.error("Invalid password.")
                else:
                    st.error("User not found.")
                    
    # Stop the script here so the dashboard doesn't load for unauthenticated users
    st.stop()

# ---------------------------------------------------------
# 📊 MODULE 2: MAIN DASHBOARD APPLICATION
# ---------------------------------------------------------

# Add a logout button to the top sidebar
st.sidebar.button("Log Out", on_click=lambda: st.session_state.update(logged_in=False))

# Load Environment Variables securely
load_dotenv()
DATABASE_URL = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")

@st.cache_data(ttl=60)
def fetch_data():
    try:
        engine = create_engine(DATABASE_URL)
        query = "SELECT * FROM pharma_sales"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

df = fetch_data()

if df.empty:
    st.warning("No data found in the cloud warehouse. Please run the ETL pipeline.")
    st.stop()

# --- Main UI Headers ---
st.title("💊 PharmaSales Intelligence Dashboard")
st.caption("Real-time commercial analytics tracking revenue, drug performance, and physician demographics.")

# --- Dynamic Ingestion Portal ---
# Tucked inside an expander so it keeps the dashboard clean until clicked
with st.expander("📥 Enterprise Data Ingestion Portal (Upload Custom Files)", expanded=False):
    st.caption("ProcDNA Evaluator Sandbox: Upload any custom commercial CSV dataset to test the dynamic schema mapping engine.")
    uploaded_file = st.file_uploader("Drop raw vendor sales file here", type=["csv"])

    if uploaded_file is not None:
        raw_uploaded_df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        
        st.markdown("### 🔍 Raw File Preview (First 3 Rows)")
        st.dataframe(raw_uploaded_df.head(3))
        
        st.markdown("### ⚙️ Dynamic Schema Mapping Engine")
        st.info("Map your file's columns to align them with the cloud database schema:")
        
        target_columns = ['Region', 'Drug_Name', 'Units_Dispensed', 'Unit_Price']
        user_mappings = {}
        
        col1, col2, col3, col4 = st.columns(4)
        available_cols = ["-- Select Column --"] + list(raw_uploaded_df.columns)
        
        with col1:
            user_mappings['Region'] = st.selectbox("Target: Region", available_cols, key="map_reg")
        with col2:
            user_mappings['Drug_Name'] = st.selectbox("Target: Drug Name", available_cols, key="map_drug")
        with col3:
            user_mappings['Units_Dispensed'] = st.selectbox("Target: Units Sold", available_cols, key="map_units")
        with col4:
            user_mappings['Unit_Price'] = st.selectbox("Target: Unit Price", available_cols, key="map_price")
            
        all_mapped = all(user_mappings[col] != "-- Select Column --" for col in target_columns)
        
        if all_mapped:
            if st.button("🚀 Execute Cloud Ingestion & Re-Align Pipeline", type="primary"):
                with st.spinner("Processing ETL and updating cloud warehouse..."):
                    try:
                        rename_dict = {user_mappings[col]: col for col in target_columns}
                        processed_df = raw_uploaded_df[list(rename_dict.keys())].rename(columns=rename_dict)
                        
                        processed_df['Units_Dispensed'] = pd.to_numeric(processed_df['Units_Dispensed'], errors='coerce')
                        processed_df['Unit_Price'] = pd.to_numeric(processed_df['Unit_Price'], errors='coerce')
                        processed_df['Total_Revenue'] = processed_df['Units_Dispensed'] * processed_df['Unit_Price']
                        processed_df = processed_df.dropna()
                        
                        engine = create_engine(DATABASE_URL)
                        processed_df.to_sql('pharma_sales', engine, if_exists='append', index=False)
                        
                        st.toast("Database updated!", icon="🔥")
                        st.success("ETL executed successfully. Your custom file is now live!")
                        
                        # Flush the cache so the dashboard grabs the newly uploaded data immediately
                        fetch_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Ingestion Aborted due to Data Quality issues: {e}")
        else:
            st.warning("Please map all 4 baseline target fields to execute the ETL pipeline.")
st.markdown("---")

# --- Sidebar Filters ---
st.sidebar.header("Filter Analytics")
selected_region = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
selected_drug = st.sidebar.multiselect("Select Drug", df['Drug_Name'].unique(), default=df['Drug_Name'].unique())

filtered_df = df[(df['Region'].isin(selected_region)) & (df['Drug_Name'].isin(selected_drug))]

# --- KPIs ---
total_revenue = filtered_df['Total_Revenue'].sum()
total_units = filtered_df['Units_Dispensed'].sum()
avg_price = filtered_df['Unit_Price'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Revenue", f"${total_revenue:,.2f}")
col2.metric("Units Dispensed", f"{total_units:,.0f}")
col3.metric("Average Unit Price", f"${avg_price:,.2f}")
st.markdown("---")

# --- Charts ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Revenue by Region")
    fig_region = px.bar(filtered_df.groupby('Region')['Total_Revenue'].sum().reset_index(), x='Region', y='Total_Revenue', color_discrete_sequence=['#4C62F5'])
    st.plotly_chart(fig_region, use_container_width=True)

with col_chart2:
    st.subheader("Top Performing Drugs")
    fig_drug = px.pie(filtered_df, names='Drug_Name', values='Total_Revenue', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig_drug, use_container_width=True)