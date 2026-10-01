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

# Safe Float Helper
def safe_float(val):
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

# Dynamic Cascading Selector with Auto-Selection for Single Options
def render_cascading_stock_selector(df_stock, key_prefix):
    st.subheader("🔍 Product & Specifications Selection")
    
    df = df_stock.copy() if not df_stock.empty else pd.DataFrame(columns=['Product', 'Width', 'Length', 'GSM', 'Grus', 'Pcs', 'Challan Weight'])
    
    if not df.empty:
        df['Product'] = df['Product'].astype(str)
        df['Width'] = pd.to_numeric(df['Width'], errors='coerce')
        df['Length'] = pd.to_numeric(df['Length'], errors='coerce')
        df['GSM'] = pd.to_numeric(df['GSM'], errors='coerce')

    # Retrieve current dropdown selections safely
    curr_prod = st.session_state.get(f"{key_prefix}_prod", "Select...")
    curr_w = st.session_state.get(f"{key_prefix}_w", "Select...")
    curr_l = st.session_state.get(f"{key_prefix}_l", "Select...")

    # Dynamic Cascading Dropdown Filtering
    # 1. Product options from the entire dataset
    avail_prods = ["Select..."] + sorted(df['Product'].dropna().unique().tolist()) + ["➕ Add New"] if not df.empty else ["Select...", "➕ Add New"]

    # 2. Width options depend on selected Product
    df_for_w = df[df['Product'] == curr_prod] if curr_prod not in ["Select...", "➕ Add New", ""] else df
    w_list = [str(w) for w in sorted(df_for_w['Width'].dropna().unique().tolist())]
    avail_widths = ["Select..."] + w_list + ["➕ Add New"] if not df_for_w.empty else ["Select...", "➕ Add New"]
    
    # Auto-select Width if only 1 option exists
    if len(w_list) == 1 and curr_w not in w_list and curr_w != "➕ Add New":
        st.session_state[f"{key_prefix}_w"] = w_list[0]
        curr_w = w_list[0]

    # 3. Length options depend on selected Product & Width
    df_for_l = df_for_w.copy()
    if safe_float(curr_w) is not None:
        df_for_l = df_for_l[df_for_l['Width'] == safe_float(curr_w)]
    l_list = [str(l) for l in sorted(df_for_l['Length'].dropna().unique().tolist())]
    avail_lengths = ["Select..."] + l_list + ["➕ Add New"] if not df_for_l.empty else ["Select...", "➕ Add New"]
    
    # Auto-select Length if only 1 option exists
    if len(l_list) == 1 and curr_l not in l_list and curr_l != "➕ Add New":
        st.session_state[f"{key_prefix}_l"] = l_list[0]
        curr_l = l_list[0]

    # 4. GSM options depend on selected Product, Width, & Length
    df_for_g = df_for_l.copy()
    if safe_float(curr_l) is not None:
        df_for_g = df_for_g[df_for_g['Length'] == safe_float(curr_l)]
    g_list = [str(g) for g in sorted(df_for_g['GSM'].dropna().unique().tolist())]
    avail_gsms = ["Select..."] + g_list + ["➕ Add New"] if not df_for_g.empty else ["Select...", "➕ Add New"]
    
    # Auto-select GSM if only 1 option exists
    curr_g = st.session_state.get(f"{key_prefix}_gsm", "Select...")
    if len(g_list) == 1 and curr_g not in g_list and curr_g != "➕ Add New":
        st.session_state[f"{key_prefix}_gsm"] = g_list[0]

    # Render 4 Dropdown Columns
    col_p, col_w, col_l, col_g = st.columns(4)

    final_prod, final_w, final_l, final_g = None, None, None, None

    with col_p:
        sel_prod = st.selectbox("Product", avail_prods, key=f"{key_prefix}_prod")
        if sel_prod == "➕ Add New":
            final_prod = st.text_input("Enter New Product Name", value="", placeholder="e.g. Maplitho", key=f"{key_prefix}_custom_prod").strip()
        elif sel_prod not in ["Select...", ""]:
            final_prod = sel_prod

    with col_w:
        sel_w = st.selectbox("Width", avail_widths, key=f"{key_prefix}_w")
        if sel_w == "➕ Add New":
            final_w = st.number_input("Enter New Width", min_value=0.0, value=None, placeholder="e.g. 20.0", step=0.1, key=f"{key_prefix}_custom_w")
        else:
            final_w = safe_float(sel_w)

    with col_l:
        sel_l = st.selectbox("Length", avail_lengths, key=f"{key_prefix}_l")
        if sel_l == "➕ Add New":
            final_l = st.number_input("Enter New Length", min_value=0.0, value=None, placeholder="e.g. 30.0", step=0.1, key=f"{key_prefix}_custom_l")
        else:
            final_l = safe_float(sel_l)

    with col_g:
        sel_g = st.selectbox("GSM", avail_gsms, key=f"{key_prefix}_gsm")
        if sel_g == "➕ Add New":
            final_g = st.number_input("Enter New GSM", min_value=0.0, value=None, placeholder="e.g. 70.0", step=1.0, key=f"{key_prefix}_custom_g")
        else:
            final_g = safe_float(sel_g)

    # Filter stock matching final selected parameters
    filtered_df = df.copy()
    if final_prod:
        filtered_df = filtered_df[filtered_df['Product'] == final_prod]
    if final_w is not None:
        filtered_df = filtered_df[filtered_df['Width'] == final_w]
    if final_l is not None:
        filtered_df = filtered_df[filtered_df['Length'] == final_l]
    if final_g is not None:
        filtered_df = filtered_df[filtered_df['GSM'] == final_g]

    # Evaluate Selection Result
    if len(filtered_df) == 1 and not filtered_df.empty:
        selected_row = filtered_df.iloc[0]
        st.success(
            f"**Selected Existing Stock Balance:** Gross/Grus: `{selected_row['Grus']}` | "
            f"Pcs: `{selected_row['Pcs']}` | Challan Weight: `{selected_row['Challan Weight']} kg`"
        )
        return {"status": "existing", "data": selected_row}

    elif final_prod and final_w is not None and final_l is not None and final_g is not None:
        st.info("✨ **New Specification Combination Ready!** Enter quantity details below.")
        return {
            "status": "new",
            "Product": final_prod,
            "Width": final_w,
            "Length": final_l,
            "GSM": final_g
        }
    
    elif len(filtered_df) > 1:
        st.info(f"💡 {len(filtered_df)} variants match your selection. Refine dropdowns to narrow down.")
        return None
    
    else:
        st.info("Please select or enter all 4 specifications (Product, Width, Length, GSM) to proceed.")
        return None


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

    df_p_stock = pd.DataFrame(data.get("primary_stock", [])) if data else pd.DataFrame()
    selection_res = render_cascading_stock_selector(df_p_stock, key_prefix="pur")

    if selection_res is not None:
        if selection_res["status"] == "existing":
            product = selection_res["data"]["Product"]
            width = float(selection_res["data"]["Width"])
            length = float(selection_res["data"]["Length"])
            gsm = float(selection_res["data"]["GSM"])
        else:
            product = selection_res["Product"]
            width = selection_res["Width"]
            length = selection_res["Length"]
            gsm = selection_res["GSM"]

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            entry_date = st.date_input("Purchase Date", datetime.now(), key="pur_date")
            remark = st.text_input("Remark", value="", placeholder="Supplier details / Lot notes", key="pur_rem")

        with col2:
            calc_mode = st.radio("Entry Based On:", ["Enter Pieces (Pcs)", "Enter Gross (144 pcs)", "Enter Ream (500 pcs)", "Enter Weight (kg)"], horizontal=True, key="pur_mode")

            if calc_mode == "Enter Pieces (Pcs)":
                input_pcs = st.number_input("Pcs", min_value=0, value=None, placeholder="Enter Pcs...", step=1, key="pur_pcs")
                if input_pcs:
                    calc_grus = input_pcs / 144.0
                    calc_weight = (width * length * gsm * input_pcs) / 1550000.0
                    st.info(f"💡 Calculated Gross: `{calc_grus:.2f}` | Calculated Weight: `{calc_weight:.3f} kg`")
                    challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(calc_weight), step=0.001, key="pur_cw")
                    diff_wt = challan_wt - calc_weight
                    pcs, grus, actual_wt = input_pcs, calc_grus, calc_weight
                else:
                    pcs = grus = actual_wt = challan_wt = diff_wt = 0.0

            elif calc_mode == "Enter Gross (144 pcs)":
                input_grus = st.number_input("Gross", min_value=0.0, value=None, placeholder="Enter Gross...", step=0.01, key="pur_grus")
                if input_grus:
                    calc_pcs = int(round(input_grus * 144))
                    calc_weight = (width * length * gsm * calc_pcs) / 1550000.0
                    st.info(f"💡 Calculated Pcs: `{calc_pcs}` | Calculated Weight: `{calc_weight:.3f} kg`")
                    challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(calc_weight), step=0.001, key="pur_cw")
                    diff_wt = challan_wt - calc_weight
                    pcs, grus, actual_wt = calc_pcs, input_grus, calc_weight
                else:
                    pcs = grus = actual_wt = challan_wt = diff_wt = 0.0

            elif calc_mode == "Enter Ream (500 pcs)":
                input_ream = st.number_input("Reams", min_value=0.0, value=None, placeholder="Enter Reams...", step=0.01, key="pur_ream")
                if input_ream:
                    calc_pcs = int(round(input_ream * 500))
                    calc_grus = calc_pcs / 144.0
                    calc_weight = (width * length * gsm * calc_pcs) / 1550000.0
                    st.info(f"💡 Calculated Pcs: `{calc_pcs}` | Gross Equivalent: `{calc_grus:.2f}` | Calculated Weight: `{calc_weight:.3f} kg`")
                    challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(calc_weight), step=0.001, key="pur_cw")
                    diff_wt = challan_wt - calc_weight
                    pcs, grus, actual_wt = calc_pcs, calc_grus, calc_weight
                else:
                    pcs = grus = actual_wt = challan_wt = diff_wt = 0.0

            else:
                input_wt = st.number_input("Weight (kg)", min_value=0.0, value=None, placeholder="Enter Weight (kg)...", step=0.1, key="pur_wt")
                if input_wt:
                    calc_pcs = int(round((input_wt * 1550000.0) / (width * length * gsm))) if width * length * gsm > 0 else 0
                    calc_grus = calc_pcs / 144.0
                    st.info(f"💡 Calculated Pcs: `{calc_pcs}` | Calculated Gross: `{calc_grus:.2f}`")
                    challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(input_wt), step=0.001, key="pur_cw")
                    diff_wt = challan_wt - input_wt
                    pcs, grus, actual_wt = calc_pcs, calc_grus, input_wt
                else:
                    pcs = grus = actual_wt = challan_wt = diff_wt = 0.0

        if pcs > 0:
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
        selection_res = render_cascading_stock_selector(df_p_stock, key_prefix="tr")

        if selection_res is not None and selection_res["status"] == "existing":
            selected_item = selection_res["data"]
            col1, col2 = st.columns(2)
            with col1:
                company = st.selectbox("Target Company", ["shivam enterprise", "GIRRAJ PACKAGING"])
                trans_date = st.date_input("Transfer Date", datetime.now(), key="tr_date")
                inv_number = st.text_input("Invoice Number", value="", placeholder="Enter Invoice #", key="tr_inv")
                inv_date = st.date_input("Invoice Date", datetime.now(), key="tr_inv_date")

            with col2:
                calc_mode_tr = st.radio("Entry Based On:", ["Enter Pieces (Pcs)", "Enter Gross (144 pcs)", "Enter Ream (500 pcs)", "Enter Weight (kg)"], horizontal=True, key="tr_mode")
                w, l, g = float(selected_item['Width']), float(selected_item['Length']), float(selected_item['GSM'])

                if calc_mode_tr == "Enter Pieces (Pcs)":
                    shift_pcs = st.number_input("Pcs to Shift", min_value=0, max_value=int(selected_item['Pcs']), value=None, placeholder="Enter Pcs...", step=1, key="tr_pcs")
                    if shift_pcs:
                        shift_grus = shift_pcs / 144.0
                        shift_wt = (w * l * g * shift_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                        st.info(f"💡 Calculated Gross: `{shift_grus:.2f}` | Calculated Weight: `{shift_wt:.3f} kg`")
                    else:
                        shift_pcs = shift_grus = shift_wt = 0.0
                
                elif calc_mode_tr == "Enter Gross (144 pcs)":
                    shift_grus = st.number_input("Gross to Shift", min_value=0.0, max_value=float(selected_item['Grus']), value=None, placeholder="Enter Gross...", step=0.01, key="tr_grus")
                    if shift_grus:
                        shift_pcs = int(round(shift_grus * 144))
                        shift_wt = (w * l * g * shift_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                        st.info(f"💡 Calculated Pcs: `{shift_pcs}` | Calculated Weight: `{shift_wt:.3f} kg`")
                    else:
                        shift_pcs = shift_grus = shift_wt = 0.0

                elif calc_mode_tr == "Enter Ream (500 pcs)":
                    shift_ream = st.number_input("Reams to Shift", min_value=0.0, value=None, placeholder="Enter Reams...", step=0.01, key="tr_ream")
                    if shift_ream:
                        shift_pcs = int(round(shift_ream * 500))
                        shift_grus = shift_pcs / 144.0
                        shift_wt = (w * l * g * shift_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                        st.info(f"💡 Calculated Pcs: `{shift_pcs}` | Calculated Weight: `{shift_wt:.3f} kg`")
                    else:
                        shift_pcs = shift_grus = shift_wt = 0.0

                else:
                    shift_wt = st.number_input("Weight to Shift (kg)", min_value=0.0, value=None, placeholder="Enter Weight (kg)...", step=0.1, key="tr_wt")
                    if shift_wt:
                        shift_pcs = int(round((shift_wt * 1550000.0) / (w * l * g))) if w * l * g > 0 else 0
                        shift_grus = shift_pcs / 144.0
                        st.info(f"💡 Calculated Pcs: `{shift_pcs}` | Calculated Gross: `{shift_grus:.2f}`")
                    else:
                        shift_pcs = shift_grus = shift_wt = 0.0

                challan_wt = st.number_input("Challan Weight (kg)", min_value=0.0, value=float(shift_wt) if shift_wt else None, placeholder="Challan Wt...", step=0.001, key="tr_cw")
                remark = st.text_input("Transfer Remark", value="", placeholder="Enter Remarks...", key="tr_rem")

            if shift_pcs > 0 and st.button("🚀 Execute Transfer"):
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
                    "challan_weight_change": challan_wt or shift_wt,
                    "weight_change": shift_wt,
                    "diff_weight_change": (challan_wt or shift_wt) - shift_wt,
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
        selection_res = render_cascading_stock_selector(df_c_stock, key_prefix="u")

        if selection_res is not None and selection_res["status"] == "existing":
            selected_item = selection_res["data"]
            col1, col2 = st.columns(2)
            with col1:
                entry_type = st.radio("Action Type", ["Used", "Adjusted"], horizontal=True, key="u_type")
                usage_date = st.date_input("Date", datetime.now(), key="u_date")
                remark = st.text_input("Remark", value="", placeholder="Production batch / notes", key="u_rem")

            with col2:
                calc_mode_u = st.radio("Quantity Input Method:", ["Enter Pieces (Pcs)", "Enter Gross (144 pcs)", "Enter Ream (500 pcs)", "Enter Weight (kg)"], horizontal=True, key="u_mode")
                w, l, g = float(selected_item['Width']), float(selected_item['Length']), float(selected_item['GSM'])

                if calc_mode_u == "Enter Pieces (Pcs)":
                    use_pcs = st.number_input("Pcs", min_value=0, value=None, placeholder="Enter Pcs...", step=1, key="u_pcs")
                    if use_pcs:
                        use_grus = use_pcs / 144.0
                        use_wt = (w * l * g * use_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                        st.info(f"💡 Calculated Gross: `{use_grus:.2f}` | Weight: `{use_wt:.3f} kg`")
                    else:
                        use_pcs = use_grus = use_wt = 0.0

                elif calc_mode_u == "Enter Gross (144 pcs)":
                    use_grus = st.number_input("Gross", min_value=0.0, value=None, placeholder="Enter Gross...", step=0.01, key="u_grus")
                    if use_grus:
                        use_pcs = int(round(use_grus * 144))
                        use_wt = (w * l * g * use_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                        st.info(f"💡 Calculated Pcs: `{use_pcs}` | Weight: `{use_wt:.3f} kg`")
                    else:
                        use_pcs = use_grus = use_wt = 0.0

                elif calc_mode_u == "Enter Ream (500 pcs)":
                    use_ream = st.number_input("Ream", min_value=0.0, value=None, placeholder="Enter Reams...", step=0.01, key="u_ream")
                    if use_ream:
                        use_pcs = int(round(use_ream * 500))
                        use_grus = use_pcs / 144.0
                        use_wt = (w * l * g * use_pcs) / 1550000.0 if w * l * g > 0 else 0.0
                        st.info(f"💡 Calculated Pcs: `{use_pcs}` | Weight: `{use_wt:.3f} kg`")
                    else:
                        use_pcs = use_grus = use_wt = 0.0

                else:
                    use_wt = st.number_input("Weight (kg)", min_value=0.0, value=None, placeholder="Enter Weight (kg)...", step=0.1, key="u_wt")
                    if use_wt:
                        use_pcs = int(round((use_wt * 1550000.0) / (w * l * g))) if w * l * g > 0 else 0
                        use_grus = use_pcs / 144.0
                        st.info(f"💡 Calculated Pcs: `{use_pcs}` | Gross: `{use_grus:.2f}`")
                    else:
                        use_pcs = use_grus = use_wt = 0.0

            if use_pcs > 0 and st.button(f"Submit {entry_type} Entry"):
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
