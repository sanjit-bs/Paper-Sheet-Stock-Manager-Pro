import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Paper Stock Management",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Paper Stock Management Dashboard")

# Sidebar - Web App Configuration
st.sidebar.header("Settings")
WEB_APP_URL = st.sidebar.text_input(
    "https://script.google.com/macros/s/AKfycbxsPxP17kHYPRIAKi1Knc9nP6UCPC63ggilvwAFVOwmx8uuOHe6PmVGuZ6W0MnEie3w/exec",
    value="",
    type="password",
    help="Paste your deployed Apps Script URL ending in /exec"
)

if not WEB_APP_URL:
    st.warning("Please enter your Google Apps Script Web App URL in the sidebar to proceed")
    st.stop()

# Helper function to send GET requests to Apps Script
def fetch_all_data():
    try:
        response = requests.get(f"{WEB_APP_URL}?action=read_all")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data. Server status: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error connecting to Apps Script: {e}")
        return None

# Fetch data
data = fetch_all_data()

# Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "📊 Stock & History View", 
    "➕ Add Primary Stock", 
    "🚚 Transfer Stock to Company"
])

# -------------------------------------------------------------------
# TAB 1: VIEW STOCKS & HISTORIES
# -------------------------------------------------------------------
with tab1:
    st.header("Stock & History Overview")
    
    if st.button("🔄 Refresh Data"):
        st.rerun()

    if data and data.get("status") == "success":
        sub_tab1, sub_tab2, sub_tab3 = st.tabs([
            "Primary Warehouse", 
            "Shivam Enterprise", 
            "Girraj Packaging"
        ])

        with sub_tab1:
            st.subheader("Primary Stock")
            df_p_stock = pd.DataFrame(data.get("primary_stock", []))
            st.dataframe(df_p_stock, use_container_width=True)

            st.subheader("Primary History")
            df_p_hist = pd.DataFrame(data.get("primary_history", []))
            st.dataframe(df_p_hist, use_container_width=True)

        with sub_tab2:
            st.subheader("Shivam Enterprise Stock")
            df_s_stock = pd.DataFrame(data.get("stock_shivam", []))
            st.dataframe(df_s_stock, use_container_width=True)

            st.subheader("Shivam Enterprise History")
            df_s_hist = pd.DataFrame(data.get("history_shivam", []))
            st.dataframe(df_s_hist, use_container_width=True)

        with sub_tab3:
            st.subheader("Girraj Packaging Stock")
            df_g_stock = pd.DataFrame(data.get("stock_girraj", []))
            st.dataframe(df_g_stock, use_container_width=True)

            st.subheader("Girraj Packaging History")
            df_g_hist = pd.DataFrame(data.get("history_girraj", []))
            st.dataframe(df_g_hist, use_container_width=True)

# -------------------------------------------------------------------
# TAB 2: ADD PRIMARY STOCK
# -------------------------------------------------------------------
with tab2:
    st.header("Add Purchase Stock to Primary Warehouse")
    
    with st.form("add_primary_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            entry_date = st.date_input("Date", datetime.now())
            product = st.text_input("Product Name", placeholder="e.g. Maplitho")
            width = st.number_input("Width", min_value=0.0, step=0.1)
            length = st.number_input("Length", min_value=0.0, step=0.1)
            
        with col2:
            gsm = st.number_input("GSM", min_value=0.0, step=1.0)
            grus = st.number_input("Grus", min_value=0.0, step=0.01)
            pcs = st.number_input("Pcs", min_value=0, step=1)
            challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, step=0.001)

        with col3:
            actual_wt = st.number_input("Actual Weight (kg)", min_value=0.0, step=0.001)
            diff_wt = st.number_input("Diff Weight (kg)", min_value=0.0, step=0.001)
            remark = st.text_area("Remark", placeholder="Supplier or lot notes...")

        submitted = st.form_submit_button("Submit Purchase Entry")
        
        if submitted:
            params = {
                "action": "add_primary_stock",
                "date": entry_date.strftime("%d/%m/%Y"),
                "product": product,
                "width": width,
                "length": length,
                "gsm": gsm,
                "grus_change": grus,
                "pcs_change": pcs,
                "challan_weight_change": challan_wt,
                "weight_change": actual_wt,
                "diff_weight_change": diff_wt,
                "remark": remark
            }
            res = requests.get(WEB_APP_URL, params=params)
            if res.status_code == 200:
                st.success("Primary stock added successfully!")
            else:
                st.error("Failed to post entry.")

# -------------------------------------------------------------------
# TAB 3: TRANSFER TO COMPANY
# -------------------------------------------------------------------
with tab3:
    st.header("Shift Stock from Primary to Company")

    with st.form("transfer_form", clear_on_submit=True):
        company = st.selectbox("Select Target Company", ["shivam enterprise", "GIRRAJ PACKAGING"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            trans_date = st.date_input("Transfer Date", datetime.now())
            inv_number = st.text_input("Invoice Number")
            inv_date = st.date_input("Invoice Date", datetime.now())
            
        with col2:
            product = st.text_input("Product", key="tr_prod")
            width = st.number_input("Width", min_value=0.0, step=0.1, key="tr_w")
            length = st.number_input("Length", min_value=0.0, step=0.1, key="tr_l")
            gsm = st.number_input("GSM", min_value=0.0, step=1.0, key="tr_gsm")
            
        with col3:
            grus = st.number_input("Grus to Shift", min_value=0.0, step=0.01)
            pcs = st.number_input("Pcs to Shift", min_value=0, step=1)
            challan_wt = st.number_input("Challan Weight", min_value=0.0, step=0.001)
            actual_wt = st.number_input("Actual Weight", min_value=0.0, step=0.001)
            diff_wt = st.number_input("Diff Weight", min_value=0.0, step=0.001)
            remark = st.text_input("Remark", key="tr_rem")

        transfer_submitted = st.form_submit_button("Execute Transfer")

        if transfer_submitted:
            params = {
                "action": "transfer_to_company",
                "company_name": company,
                "date": trans_date.strftime("%d/%m/%Y"),
                "invoice_number": inv_number,
                "invoice_date": inv_date.strftime("%d/%m/%Y"),
                "product": product,
                "width": width,
                "length": length,
                "gsm": gsm,
                "grus_change": grus,
                "pcs_change": pcs,
                "challan_weight_change": challan_wt,
                "weight_change": actual_wt,
                "diff_weight_change": diff_wt,
                "remark": remark
            }
            res = requests.get(WEB_APP_URL, params=params)
            if res.status_code == 200:
                st.success(f"Successfully shifted stock to {company}!")
            else:
                st.error("Transfer failed.")
