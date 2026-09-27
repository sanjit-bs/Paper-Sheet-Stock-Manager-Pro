import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Paper Stock Management", page_icon="📦", layout="wide")

st.title("📦 Paper Stock Management Dashboard")

# Sidebar Configuration
st.sidebar.header("Settings")
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbxsPxP17kHYPRIAKi1Knc9nP6UCPC63ggilvwAFVOwmx8uuOHe6PmVGuZ6W0MnEie3w/exec"

ADMIN_PASSWORD = "1234"
user_password = st.sidebar.text_input("Enter Admin Password:", type="password")

if user_password != ADMIN_PASSWORD:
    st.sidebar.error("❌ Incorrect Password")
    st.warning("Please enter the correct password in the sidebar to access the dashboard.")
    st.stop()

st.sidebar.success("🔓 Access Granted")

# Fetch Data Helper
def fetch_all_data():
    try:
        res = requests.get(f"{WEB_APP_URL}?action=read_all")
        if res.status_code == 200:
            return res.json()
    except Exception as e:
        st.error(f"Error connecting to Google Apps Script: {e}")
    return None

data = fetch_all_data()

# Helper function for cascading stock selection UI
def render_cascading_stock_selector(df_stock, key_prefix):
    st.subheader("🔍 Product & Specifications Selection")
    
    if df_stock.empty:
        st.warning("No stock available.")
        return None

    col_p, col_w, col_l, col_g = st.columns(4)

    # 1. Product Selection
    products = sorted(df_stock['Product'].astype(str).unique().tolist())
    with col_p:
        sel_product = st.selectbox("Product", ["Select Product..."] + products, key=f"{key_prefix}_prod")

    if sel_product == "Select Product...":
        st.info("Select Product, Width, Length, and GSM to proceed.")
        return None

    # Filter by Product
    df_filtered_p = df_stock[df_stock['Product'].astype(str) == sel_product]

    # 2. Width Selection
    widths = sorted(df_filtered_p['Width'].astype(float).unique().tolist())
    with col_w:
        sel_width = st.selectbox("Width", ["Select Width..."] + [str(w) for w in widths], key=f"{key_prefix}_w")

    if sel_width == "Select Width...":
        st.info("Select Product, Width, Length, and GSM to proceed.")
        return None

    # Filter by Width
    df_filtered_w = df_filtered_p[df_filtered_p['Width'].astype(float) == float(sel_width)]

    # 3. Length Selection
    lengths = sorted(df_filtered_w['Length'].astype(float).unique().tolist())
    with col_l:
        sel_length = st.selectbox("Length", ["Select Length..."] + [str(l) for l in lengths], key=f"{key_prefix}_l")

    if sel_length == "Select Length...":
        st.info("Select Product, Width, Length, and GSM to proceed.")
        return None

    # Filter by Length
    df_filtered_l = df_filtered_w[df_filtered_w['Length'].astype(float) == float(sel_length)]

    # 4. GSM Selection
    gsms = sorted(df_filtered_l['GSM'].astype(float).unique().tolist())
    with col_g:
        sel_gsm = st.selectbox("GSM", ["Select GSM..."] + [str(g) for g in gsms], key=f"{key_prefix}_gsm")

    if sel_gsm == "Select GSM...":
        st.info("Select Product, Width, Length, and GSM to proceed.")
        return None

    # Final Selected Row
    selected_row = df_filtered_l[df_filtered_l['GSM'].astype(float) == float(sel_gsm)].iloc[0]

    st.success(
        f"**Selected Stock Balance:** Gross/Grus: `{selected_row['Grus']}` | "
        f"Pcs: `{selected_row['Pcs']}` | Challan Weight: `{selected_row['Challan Weight']} kg`"
    )
    
    return selected_row


# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Stock & History View", 
    "➕ Purchase Primary Stock", 
    "🚚 Transfer Stock to Company",
    "📝 Company Stock Usage / Adjustment"
])

# -------------------------------------------------------------------
# TAB 1: VIEW STOCKS & HISTORIES
# -------------------------------------------------------------------
with tab1:
    st.header("Stock & History Overview")
    if st.button("🔄 Refresh Data"):
        st.rerun()

    if data and data.get("status") == "success":
        sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Primary Warehouse", "Shivam Enterprise", "Girraj Packaging"])

        with sub_tab1:
            st.subheader("Primary Stock")
            st.dataframe(pd.DataFrame(data.get("primary_stock", [])), use_container_width=True)
            st.subheader("Primary History (Transfers Out)")
            st.dataframe(pd.DataFrame(data.get("primary_history", [])), use_container_width=True)

        with sub_tab2:
            st.subheader("Shivam Enterprise Stock")
            st.dataframe(pd.DataFrame(data.get("stock_shivam", [])), use_container_width=True)
            st.subheader("Shivam Enterprise History")
            st.dataframe(pd.DataFrame(data.get("history_shivam", [])), use_container_width=True)

        with sub_tab3:
            st.subheader("Girraj Packaging Stock")
            st.dataframe(pd.DataFrame(data.get("stock_girraj", [])), use_container_width=True)
            st.subheader("Girraj Packaging History")
            st.dataframe(pd.DataFrame(data.get("history_girraj", [])), use_container_width=True)

# -------------------------------------------------------------------
# TAB 2: PURCHASE PRIMARY STOCK
# -------------------------------------------------------------------
with tab2:
    st.header("Add Purchase Stock to Primary Warehouse")

    col1, col2 = st.columns(2)
    with col1:
        entry_date = st.date_input("Purchase Date", datetime.now())
        product = st.text_input("Product Name", placeholder="e.g. Maplitho")
        width = st.number_input("Width (inches)", min_value=0.0, value=20.0, step=0.1)
        length = st.number_input("Length (inches)", min_value=0.0, value=30.0, step=0.1)
        gsm = st.number_input("GSM", min_value=0.0, value=70.0, step=1.0)

    with col2:
        calc_mode = st.radio("Entry Based On:", ["Enter Pieces (Pcs)", "Enter Gross (144 pcs)", "Enter Ream (500 pcs)", "Enter Weight (kg)"], horizontal=True)

        if calc_mode == "Enter Pieces (Pcs)":
            input_pcs = st.number_input("Pcs", min_value=0, value=144, step=1)
            calc_grus = input_pcs / 144.0
            calc_weight = (width * length * gsm * input_pcs) / 1550000.0
            
            st.info(f"💡 Calculated Gross: `{calc_grus:.2f}` | Calculated Weight: `{calc_weight:.3f} kg`")
            challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(calc_weight), step=0.001)
            diff_wt = challan_wt - calc_weight
            pcs = input_pcs
            grus = calc_grus
            actual_wt = calc_weight

        elif calc_mode == "Enter Gross (144 pcs)":
            input_grus = st.number_input("Gross", min_value=0.0, value=1.0, step=0.01)
            calc_pcs = int(round(input_grus * 144))
            calc_weight = (width * length * gsm * calc_pcs) / 1550000.0

            st.info(f"💡 Calculated Pcs: `{calc_pcs}` | Calculated Weight: `{calc_weight:.3f} kg`")
            challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(calc_weight), step=0.001)
            diff_wt = challan_wt - calc_weight
            pcs = calc_pcs
            grus = input_grus
            actual_wt = calc_weight

        elif calc_mode == "Enter Ream (500 pcs)":
            input_ream = st.number_input("Reams", min_value=0.0, value=1.0, step=0.01)
            calc_pcs = int(round(input_ream * 500))
            calc_grus = calc_pcs / 144.0
            calc_weight = (width * length * gsm * calc_pcs) / 1550000.0

            st.info(f"💡 Calculated Pcs: `{calc_pcs}` | Gross Equivalent: `{calc_grus:.2f}` | Calculated Weight: `{calc_weight:.3f} kg`")
            challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(calc_weight), step=0.001)
            diff_wt = challan_wt - calc_weight
            pcs = calc_pcs
            grus = calc_grus
            actual_wt = calc_weight

        else:
            input_wt = st.number_input("Weight (kg)", min_value=0.0, value=10.0, step=0.1)
            if width * length * gsm > 0:
                calc_pcs = int(round((input_wt * 1550000.0) / (width * length * gsm)))
                calc_grus = calc_pcs / 144.0
            else:
                calc_pcs, calc_grus = 0, 0.0

            st.info(f"💡 Calculated Pcs: `{calc_pcs}` | Calculated Gross: `{calc_grus:.2f}`")
            challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(input_wt), step=0.001)
            diff_wt = challan_wt - input_wt
            pcs = calc_pcs
            grus = calc_grus
            actual_wt = input_wt

        remark = st.text_input("Remark", placeholder="Supplier details / Lot notes")

    st.write(f"**Summary:** `Diff Weight`: `{diff_wt:.3f} kg`")
    if st.button("Submit Purchase Entry"):
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
            st.success("✅ Primary stock added successfully!")
            st.rerun()

# -------------------------------------------------------------------
# TAB 3: TRANSFER STOCK TO COMPANY
# -------------------------------------------------------------------
with tab3:
    st.header("Shift Stock from Primary Warehouse to Company")

    if data and data.get("primary_stock"):
        df_p_stock = pd.DataFrame(data.get("primary_stock"))
        
        selected_item = render_cascading_stock_selector(df_p_stock, key_prefix="tr")

        if selected_item is not None:
            col1, col2 = st.columns(2)
            with col1:
                company = st.selectbox("Target Company", ["shivam enterprise", "GIRRAJ PACKAGING"])
                trans_date = st.date_input("Transfer Date", datetime.now(), key="tr_date")
                inv_number = st.text_input("Invoice Number", key="tr_inv")
                inv_date = st.date_input("Invoice Date", datetime.now(), key="tr_inv_date")

            with col2:
                calc_mode_tr = st.radio("Entry Based On:", ["Enter Pieces (Pcs)", "Enter Gross (144 pcs)", "Enter Ream (500 pcs)", "Enter Weight (kg)"], horizontal=True, key="tr_mode")
                w, l, g = float(selected_item['Width']), float(selected_item['Length']), float(selected_item['GSM'])

                if calc_mode_tr == "Enter Pieces (Pcs)":
                    shift_pcs = st.number_input("Pcs to Shift", min_value=0, max_value=int(selected_item['Pcs']), step=1, key="tr_pcs")
                    shift_grus = shift_pcs / 144.0
                    shift_wt = (w * l * g * shift_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                    st.info(f"💡 Calculated Gross: `{shift_grus:.2f}` | Calculated Weight: `{shift_wt:.3f} kg`")
                
                elif calc_mode_tr == "Enter Gross (144 pcs)":
                    shift_grus = st.number_input("Gross to Shift", min_value=0.0, max_value=float(selected_item['Grus']), step=0.01, key="tr_grus")
                    shift_pcs = int(round(shift_grus * 144))
                    shift_wt = (w * l * g * shift_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                    st.info(f"💡 Calculated Pcs: `{shift_pcs}` | Calculated Weight: `{shift_wt:.3f} kg`")

                elif calc_mode_tr == "Enter Ream (500 pcs)":
                    shift_ream = st.number_input("Reams to Shift", min_value=0.0, step=0.01, key="tr_ream")
                    shift_pcs = int(round(shift_ream * 500))
                    shift_grus = shift_pcs / 144.0
                    shift_wt = (w * l * g * shift_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                    st.info(f"💡 Calculated Pcs: `{shift_pcs}` | Calculated Weight: `{shift_wt:.3f} kg`")

                else:
                    shift_wt = st.number_input("Weight to Shift (kg)", min_value=0.0, step=0.1, key="tr_wt")
                    shift_pcs = int(round((shift_wt * 1550000.0) / (w * l * g))) if w * l * g > 0 else 0
                    shift_grus = shift_pcs / 144.0
                    st.info(f"💡 Calculated Pcs: `{shift_pcs}` | Calculated Gross: `{shift_grus:.2f}`")

                challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(shift_wt), step=0.001, key="tr_cw")
                remark = st.text_input("Transfer Remark", key="tr_rem")

            if st.button("🚀 Execute Transfer"):
                params = {
                    "action": "transfer_to_company",
                    "company_name": company,
                    "date": trans_date.strftime("%d/%m/%Y"),
                    "invoice_number": inv_number,
                    "invoice_date": inv_date.strftime("%d/%m/%Y"),
                    "product": selected_item['Product'],
                    "width": w,
                    "length": l,
                    "gsm": g,
                    "grus_change": shift_grus,
                    "pcs_change": shift_pcs,
                    "challan_weight_change": challan_wt,
                    "weight_change": shift_wt,
                    "diff_weight_change": challan_wt - shift_wt,
                    "remark": remark
                }
                res = requests.get(WEB_APP_URL, params=params)
                if res.status_code == 200:
                    st.success(f"✅ Transferred stock to {company}!")
                    st.rerun()

# -------------------------------------------------------------------
# TAB 4: COMPANY USAGE & ADJUSTMENT
# -------------------------------------------------------------------
with tab4:
    st.header("📝 Record Company Stock Usage or Adjustment")

    company = st.selectbox("Select Company Name", ["shivam enterprise", "GIRRAJ PACKAGING"], key="u_comp")
    target_stock = data.get("stock_shivam", []) if company == "shivam enterprise" else data.get("stock_girraj", [])

    if not target_stock:
        st.warning(f"No stock records found for {company}.")
    else:
        df_c_stock = pd.DataFrame(target_stock)
        selected_item = render_cascading_stock_selector(df_c_stock, key_prefix="u")

        if selected_item is not None:
            col1, col2 = st.columns(2)
            with col1:
                entry_type = st.radio("Action Type", ["Used", "Adjusted"], horizontal=True, key="u_type")
                usage_date = st.date_input("Date", datetime.now(), key="u_date")
                remark = st.text_input("Remark", placeholder="Production batch or adjustment notes", key="u_rem")

            with col2:
                calc_mode_u = st.radio("Quantity Input Method:", ["Enter Pieces (Pcs)", "Enter Gross (144 pcs)", "Enter Ream (500 pcs)", "Enter Weight (kg)"], horizontal=True, key="u_mode")
                w, l, g = float(selected_item['Width']), float(selected_item['Length']), float(selected_item['GSM'])

                if calc_mode_u == "Enter Pieces (Pcs)":
                    use_pcs = st.number_input("Pcs", min_value=0, step=1, key="u_pcs")
                    use_grus = use_pcs / 144.0
                    use_wt = (w * l * g * use_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                    st.info(f"💡 Calculated Gross: `{use_grus:.2f}` | Weight: `{use_wt:.3f} kg`")

                elif calc_mode_u == "Enter Gross (144 pcs)":
                    use_grus = st.number_input("Gross", min_value=0.0, step=0.01, key="u_grus")
                    use_pcs = int(round(use_grus * 144))
                    use_wt = (w * l * g * use_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                    st.info(f"💡 Calculated Pcs: `{use_pcs}` | Weight: `{use_wt:.3f} kg`")

                elif calc_mode_u == "Enter Ream (500 pcs)":
                    use_ream = st.number_input("Ream", min_value=0.0, step=0.01, key="u_ream")
                    use_pcs = int(round(use_ream * 500))
                    use_grus = use_pcs / 144.0
                    use_wt = (w * l * g * use_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                    st.info(f"💡 Calculated Pcs: `{use_pcs}` | Weight: `{use_wt:.3f} kg`")

                else:
                    use_wt = st.number_input("Weight (kg)", min_value=0.0, step=0.1, key="u_wt")
                    use_pcs = int(round((use_wt * 1550000.0) / (w * l * g))) if w * l * g > 0 else 0
                    use_grus = use_pcs / 144.0
                    st.info(f"💡 Calculated Pcs: `{use_pcs}` | Gross: `{use_grus:.2f}`")

            if st.button(f"Submit {entry_type} Entry"):
                params = {
                    "action": "company_stock_action",
                    "company_name": company,
                    "type": entry_type,
                    "date": usage_date.strftime("%d/%m/%Y"),
                    "invoice_number": "-",
                    "invoice_date": "-",
                    "product": selected_item['Product'],
                    "width": w,
                    "length": l,
                    "gsm": g,
                    "grus_change": use_grus,
                    "pcs_change": use_pcs,
                    "challan_weight_change": use_wt,
                    "weight_change": use_wt,
                    "diff_weight_change": 0.0,
                    "remark": remark
                }
                res = requests.get(WEB_APP_URL, params=params)
                if res.status_code == 200:
                    st.success(f"✅ Recorded **{entry_type}** entry for {company}!")
                    st.rerun()
