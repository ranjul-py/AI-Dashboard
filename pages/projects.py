import streamlit as st
import pandas as pd
from database.db_manager import DBManager
from components.styles import inject_styles
from components.kpi_cards import render_kpi_grid
from components.charts import plot_project_completion_status, plot_project_risk_bubble
from utils.helpers import format_currency, format_percent

def calculate_risk_score(row) -> float:
    """Computes a standardized risk score from 0 to 100."""
    score = (row['delay_days'] * 1.5) + (100 - row['completion_pct']) * 0.5
    if row['status'] == 'At Risk':
        score += 30
    elif row['status'] == 'Delayed':
        score += 50
    return min(100.0, max(0.0, score))

def get_risk_label(score: float) -> str:
    if score >= 65:
        return "🔴 HIGH"
    elif score >= 35:
        return "🟡 MEDIUM"
    else:
        return "🟢 LOW"

def show_projects_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("🏥 Project Health Portfolio")
    st.markdown("### Budget Utilization, Status Tracking, & Portfolio Risk Indexing")
    
    db = DBManager()
    df_proj = db.get_table_dataframe("projects")
    
    if df_proj.empty:
        st.warning("No project records found. Execute ETL pipeline first.")
        return
        
    # Calculate derived fields
    df_proj['risk_score'] = df_proj.apply(calculate_risk_score, axis=1)
    df_proj['risk_label'] = df_proj['risk_score'].apply(get_risk_label)
    df_proj['budget_spent'] = df_proj['budget'] * (df_proj['completion_pct'] / 100.0)
    df_proj['budget_remaining'] = df_proj['budget'] - df_proj['budget_spent']
    
    # 1. Project KPIs
    total_budget = df_proj['budget'].sum()
    total_spent = df_proj['budget_spent'].sum()
    avg_completion = df_proj['completion_pct'].mean()
    delayed_count = len(df_proj[df_proj['status'] == 'Delayed'])
    at_risk_budget = df_proj[df_proj['status'].isin(['Delayed', 'At Risk'])]['budget'].sum()
    
    kpis = [
        {"title": "Total Portfolio Budget", "value": format_currency(total_budget), "delta": "Across 5 major initiatives", "delta_type": "neutral", "icon": "💳", "status": "normal"},
        {"title": "Capital Invested YTD", "value": format_currency(total_spent), "delta": f"{total_spent/total_budget*100:.1f}% spent", "delta_type": "positive", "icon": "⚙️", "status": "success"},
        {"title": "Average Completion", "value": format_percent(avg_completion), "delta": "Portfolio progress", "delta_type": "neutral", "icon": "📈", "status": "normal"},
        {"title": "Capital At Risk", "value": format_currency(at_risk_budget), "delta": f"{delayed_count} delayed, 1 at risk", "delta_type": "negative" if at_risk_budget > 0 else "neutral", "icon": "⚠️", "status": "danger" if at_risk_budget > 0 else "normal"}
    ]
    render_kpi_grid(kpis, cols_per_row=4)
    st.markdown("---")
    
    # 2. Charts Row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_comp = plot_project_completion_status(df_proj)
        st.plotly_chart(fig_comp, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_bubble = plot_project_risk_bubble(df_proj)
        st.plotly_chart(fig_bubble, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 3. Dynamic Health Table
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Project Portfolio Detail & Risk Assessments")
    
    # Format details table
    disp_df = df_proj.copy()
    disp_df['total_budget'] = disp_df['budget'].apply(format_currency)
    disp_df['value_spent'] = disp_df['budget_spent'].apply(format_currency)
    disp_df['delay'] = disp_df['delay_days'].apply(lambda x: f"{x} Days")
    disp_df['risk_index'] = disp_df['risk_score'].apply(lambda x: f"{x:.1f}/100")
    
    # Reorder columns
    disp_cols = ['project_id', 'project_name', 'client_name', 'status', 'completion_pct', 'delay', 'total_budget', 'value_spent', 'risk_index', 'risk_label']
    disp_table = disp_df[disp_cols]
    disp_table.columns = ['ID', 'Project Name', 'Client Name', 'Status', 'Completion', 'Delay', 'Budget', 'Capital Spent', 'Risk Score', 'Risk Level']
    
    st.dataframe(disp_table, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

show_projects_page()
