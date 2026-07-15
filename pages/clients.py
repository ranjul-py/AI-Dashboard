import streamlit as st
import pandas as pd
from database.db_manager import DBManager
from components.styles import inject_styles
from components.kpi_cards import render_kpi_grid
from components.charts import plot_client_satisfaction

def show_clients_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("👤 Client Insights & Relationship Sentiment")
    st.markdown("### Client Satisfaction Scores, NPS Tracking, and Account Health Risks")
    
    db = DBManager()
    df_cli = db.get_table_dataframe("clients")
    df_proj = db.get_table_dataframe("projects")
    
    if df_cli.empty:
        st.warning("No client records found. Run the ETL pipeline first.")
        return
        
    # Calculations
    avg_csat = df_cli['csat'].mean()
    avg_nps = df_cli['nps'].mean()
    total_clients = len(df_cli)
    retained_clients = len(df_cli[df_cli['retention_status'] == 'Retained'])
    at_risk_clients = len(df_cli[df_cli['retention_status'] == 'At Risk'])
    
    # 1. Client KPIs
    kpis = [
        {"title": "Accounts Managed", "value": str(total_clients), "delta": "Enterprise portfolio", "delta_type": "neutral", "icon": "🏢", "status": "normal"},
        {"title": "Net Promoter Score (Avg)", "value": f"{avg_nps:.1f}", "delta": "Industry Benchmark: 50+", "delta_type": "positive" if avg_nps >= 50 else "negative", "icon": "❤️", "status": "success" if avg_nps >= 50 else "warning"},
        {"title": "CSAT Satisfaction (Avg)", "value": f"{avg_csat:.2f}/10", "delta": "Target CSAT: 8.0+", "delta_type": "positive" if avg_csat >= 8.0 else "negative", "icon": "⭐", "status": "success" if avg_csat >= 8.0 else "warning"},
        {"title": "Accounts At Retention Risk", "value": str(at_risk_clients), "delta": f"{(at_risk_clients/total_clients)*100:.0f}% of accounts", "delta_type": "negative" if at_risk_clients > 0 else "neutral", "icon": "⚠️", "status": "danger" if at_risk_clients > 0 else "normal"}
    ]
    render_kpi_grid(kpis, cols_per_row=4)
    st.markdown("---")
    
    # 2. Charts & Matrix
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_sat = plot_client_satisfaction(df_cli)
        st.plotly_chart(fig_sat, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚠️ Retention Risk Intervention")
        
        risk_df = df_cli[df_cli['retention_status'] == 'At Risk']
        if not risk_df.empty:
            for idx, row in risk_df.iterrows():
                # Cross-reference with projects
                client_proj = df_proj[df_proj['client_name'] == row['client_name']]
                proj_names = ", ".join(client_proj['project_name'].tolist()) if not client_proj.empty else "No active projects"
                st.error(f"""
                🔴 **{row['client_name']}** (NPS: **{row['nps']}** | CSAT: **{row['csat']}**)
                *   **Impacted Projects:** {proj_names}
                *   **Action Needed:** VP account review.
                """)
        else:
            st.success("🟢 No clients currently flagged at retention risk.")
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 3. Client Directory
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📋 Client Account Ledger")
    
    # Merge client with project budget for high-level visibility
    merged_df = pd.merge(df_cli, df_proj.groupby('client_name')['budget'].sum().reset_index(), on='client_name', how='left').fillna(0.0)
    merged_df['budget'] = merged_df['budget'].apply(lambda x: format_currency(x) if x > 0 else "$0")
    
    merged_df.columns = ["Client Name", "Net Promoter Score", "CSAT (10pt Scale)", "Retention Health Status", "Total Project Budget Allocation"]
    st.dataframe(merged_df, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

show_clients_page()
