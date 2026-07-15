import streamlit as st
import pandas as pd
from database.db_manager import DBManager
from components.styles import inject_styles
from components.kpi_cards import render_kpi_grid
from components.charts import plot_workforce_distribution, plot_workforce_utilization
from utils.helpers import format_percent

def show_workforce_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("👥 Workforce Analytics")
    st.markdown("### Headcount, Resource Allocation, and Capacity Utilization")
    
    db = DBManager()
    df_emp = db.get_table_dataframe("employees")
    
    if df_emp.empty:
        st.warning("No employee records found. Run the ETL pipeline first.")
        return
        
    # Calculations
    total_headcount = len(df_emp)
    active_headcount = len(df_emp[df_emp['status'] == 'Active'])
    inactive_headcount = len(df_emp[df_emp['status'] == 'Inactive'])
    
    attrition_rate = (inactive_headcount / total_headcount) * 100 if total_headcount > 0 else 0.0
    
    active_utilization = df_emp[df_emp['status'] == 'Active']['utilization_pct'].mean()
    
    # 1. Workforce KPIs
    kpis = [
        {"title": "Total Talent Registry", "value": str(total_headcount), "delta": "All historical records", "delta_type": "neutral", "icon": "🗂️", "status": "normal"},
        {"title": "Active Headcount", "value": str(active_headcount), "delta": f"{inactive_headcount} departed employees", "delta_type": "neutral", "icon": "👥", "status": "success"},
        {"title": "Average Resource Utilization", "value": format_percent(active_utilization), "delta": "Capacity threshold (80-90%)", "delta_type": "positive" if 80 <= active_utilization <= 90 else "neutral", "icon": "⚡", "status": "success" if 80 <= active_utilization <= 90 else "warning"},
        {"title": "Company Attrition Rate", "value": format_percent(attrition_rate), "delta": "Rolling annual", "delta_type": "negative" if attrition_rate > 15 else "positive", "icon": "🚪", "status": "normal" if attrition_rate < 15 else "danger"}
    ]
    render_kpi_grid(kpis, cols_per_row=4)
    st.markdown("---")
    
    # 2. Charts Row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_dist = plot_workforce_distribution(df_emp)
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_util = plot_workforce_utilization(df_emp)
        st.plotly_chart(fig_util, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 3. Interactive Filtered Table
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Resource Roster Directory")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_dept = st.multiselect(
            "Filter by Department",
            options=df_emp['department'].unique().tolist(),
            default=df_emp['department'].unique().tolist()
        )
    with col_f2:
        selected_status = st.multiselect(
            "Filter by Status",
            options=df_emp['status'].unique().tolist(),
            default=df_emp['status'].unique().tolist()
        )
        
    filtered_emp = df_emp[
        df_emp['department'].isin(selected_dept) & 
        df_emp['status'].isin(selected_status)
    ]
    
    # Prettify table
    disp_emp = filtered_emp.copy()
    disp_emp['utilization_pct'] = disp_emp['utilization_pct'].apply(lambda x: f"{x}%" if x > 0 else "N/A")
    disp_emp.columns = ["Employee ID", "Full Name", "Department", "Work Status", "Join Date", "Utilization Rate"]
    
    st.dataframe(disp_emp, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Attrition Log
    inactive_df = df_emp[df_emp['status'] == 'Inactive']
    if not inactive_df.empty:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🚪 Attrition & Offboarding Log")
        for idx, row in inactive_df.iterrows():
            st.info(f"🛑 **{row['name']}** ({row['department']}) departed. (Joined on {row['join_date']}).")
        st.markdown('</div>', unsafe_allow_html=True)

show_workforce_page()
