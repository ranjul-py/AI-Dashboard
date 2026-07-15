import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database.db_manager import DBManager
from components.styles import inject_styles
from components.kpi_cards import render_kpi_grid
from components.charts import plot_partner_funnel, COLOR_PALETTE, CHART_THEME_LAYOUT
from utils.helpers import format_currency, format_percent

def plot_target_vs_actual(df: pd.DataFrame) -> go.Figure:
    """Bar chart comparing actual pipeline against target values per partner."""
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['partner_name'],
        y=df['pipeline_value'],
        name='Actual Pipeline',
        marker_color=COLOR_PALETTE['blue']
    ))
    
    fig.add_trace(go.Bar(
        x=df['partner_name'],
        y=df['target_pipeline'],
        name='Target Goal',
        marker_color=COLOR_PALETTE['indigo'],
        opacity=0.6
    ))
    
    fig.update_layout(
        title="Partner Goal Performance: Target vs Actual Pipeline",
        barmode='group',
        **CHART_THEME_LAYOUT
    )
    return fig

def show_partners_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("🤝 Partner Sales Pipeline")
    st.markdown("### Partnership Performance, In-Flight Deals, and Target Achievement")
    
    db = DBManager()
    df_part = db.get_table_dataframe("partners")
    
    if df_part.empty:
        st.warning("No partner records found. Run the ETL pipeline first.")
        return
        
    # Calculations
    total_pipeline = df_part['pipeline_value'].sum()
    active_pipeline = df_part[~df_part['status'].isin(['Won', 'Lost'])]['pipeline_value'].sum()
    
    won_val = df_part[df_part['status'] == 'Won']['pipeline_value'].sum()
    lost_val = df_part[df_part['status'] == 'Lost']['pipeline_value'].sum()
    
    # Win rate = Won / (Won + Lost)
    win_rate = (won_val / (won_val + lost_val)) * 100 if (won_val + lost_val) > 0 else 0.0
    
    # 1. Partner KPIs
    kpis = [
        {"title": "Gross Portfolio Pipeline", "value": format_currency(total_pipeline), "delta": "All stages combined", "delta_type": "neutral", "icon": "📁", "status": "normal"},
        {"title": "Active Pipeline (In-Flight)", "value": format_currency(active_pipeline), "delta": "Under negotiation/proposal", "delta_type": "positive", "icon": "🤝", "status": "success"},
        {"title": "Closed Won Deals", "value": format_currency(won_val), "delta": "Contract completed", "delta_type": "positive", "icon": "💰", "status": "success"},
        {"title": "Pipeline Win Rate", "value": format_percent(win_rate), "delta": "Closed Won / Closed Total", "delta_type": "positive" if win_rate >= 50 else "negative", "icon": "🏆", "status": "normal"}
    ]
    render_kpi_grid(kpis, cols_per_row=4)
    st.markdown("---")
    
    # 2. Funnels and Visuals
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_funnel = plot_partner_funnel(df_part)
        st.plotly_chart(fig_funnel, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_goal = plot_target_vs_actual(df_part)
        st.plotly_chart(fig_goal, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 3. Partner details table
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Partnership Account Directory")
    
    disp_df = df_part.copy()
    disp_df['achievement_pct'] = (disp_df['pipeline_value'] / disp_df['target_pipeline']) * 100
    disp_df.loc[disp_df['target_pipeline'] == 0, 'achievement_pct'] = 100.0
    
    # Format displays
    disp_df['pipeline'] = disp_df['pipeline_value'].apply(format_currency)
    disp_df['target'] = disp_df['target_pipeline'].apply(lambda x: format_currency(x) if x > 0 else "N/A")
    disp_df['achievement'] = disp_df['achievement_pct'].apply(lambda x: f"{x:.1f}%")
    
    disp_table = disp_df[['partner_name', 'status', 'pipeline', 'target', 'achievement', 'partner_manager', 'contract_date']]
    disp_table.columns = ['Partner Account', 'Sales Stage', 'Actual Pipeline', 'Target Goal', 'Goal Achievement %', 'Partner Manager', 'Contract Date']
    
    st.dataframe(disp_table, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

show_partners_page()
