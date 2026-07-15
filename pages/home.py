import streamlit as st
import pandas as pd
from database.db_manager import DBManager
from components.styles import inject_styles
from components.kpi_cards import render_kpi_grid
from utils.helpers import format_currency, format_percent

def show_home_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    # Inject Glassmorphism Styling
    inject_styles()
    
    st.title("💼 Executive Dashboard")
    st.markdown("### CEO Office Overview | Real-Time Operations & Finance")
    
    db = DBManager()
    
    # 1. Fetch data from SQLite
    df_rev = db.get_table_dataframe("revenue")
    df_emp = db.get_table_dataframe("employees")
    df_proj = db.get_table_dataframe("projects")
    df_part = db.get_table_dataframe("partners")
    df_cli = db.get_table_dataframe("clients")
    
    # 2. Dynamic KPI Calculations
    # Revenue calculations
    total_rev = df_rev['revenue'].sum() if not df_rev.empty else 0
    if len(df_rev) >= 2:
        df_rev_sorted = df_rev.sort_values('month')
        latest_rev = df_rev_sorted.iloc[-1]['revenue']
        prev_rev = df_rev_sorted.iloc[-2]['revenue']
        rev_growth = ((latest_rev - prev_rev) / prev_rev) * 100
    else:
        rev_growth = 0.0
        
    # Project calculations
    active_projs = len(df_proj[df_proj['completion_pct'] < 100])
    delayed_projs = len(df_proj[df_proj['status'] == 'Delayed'])
    
    # Workforce calculations
    active_headcount = len(df_emp[df_emp['status'] == 'Active'])
    # Assume 2025+ is new hires for demonstration
    new_hires = len(df_emp[(df_emp['status'] == 'Active') & (df_emp['join_date'].str.startswith('2025'))])
    
    # Partner pipeline calculations
    # Active pipeline excludes Won/Lost stages
    active_pipeline = df_part[~df_part['status'].isin(['Won', 'Lost'])]['pipeline_value'].sum()
    
    # Client satisfaction calculations
    avg_csat = df_cli['csat'].mean() if not df_cli.empty else 0.0
    avg_nps = df_cli['nps'].mean() if not df_cli.empty else 0.0
    
    # 3. Compile and Render KPI Cards
    kpis = [
        {"title": "Total Cumulative Revenue", "value": format_currency(total_rev), "delta": f"{format_percent(rev_growth)} MoM", "delta_type": "positive" if rev_growth > 0 else "negative", "icon": "💰", "status": "normal"},
        {"title": "Revenue Growth Rate", "value": format_percent(rev_growth), "delta": "Month-over-Month", "delta_type": "positive", "icon": "📈", "status": "normal"},
        {"title": "Active Projects", "value": str(active_projs), "delta": "Under execution", "delta_type": "neutral", "icon": "📁", "status": "normal"},
        {"title": "Delayed Projects", "value": str(delayed_projs), "delta": f"{(delayed_projs/max(1, len(df_proj)))*100:.0f}% of portfolio", "delta_type": "negative" if delayed_projs > 0 else "neutral", "icon": "⚠️", "status": "danger" if delayed_projs > 0 else "normal"},
        {"title": "Employee Headcount", "value": f"{active_headcount} Active", "delta": f"+{new_hires} this year", "delta_type": "positive" if new_hires > 0 else "neutral", "icon": "👥", "status": "success"},
        {"title": "Partner Pipeline Value", "value": format_currency(active_pipeline), "delta": "Active negotiation", "delta_type": "positive", "icon": "🤝", "status": "normal"},
        {"title": "Client CSAT (Avg)", "value": f"{avg_csat:.2f}/10", "delta": "Satisfaction index", "delta_type": "positive" if avg_csat >= 7.5 else "negative", "icon": "⭐", "status": "success" if avg_csat >= 7.5 else "warning"},
        {"title": "Net Promoter Score (NPS)", "value": f"{avg_nps:.0f}", "delta": "Out of 100 scale", "delta_type": "positive" if avg_nps >= 50 else "negative", "icon": "❤️", "status": "success" if avg_nps >= 50 else "warning"}
    ]
    
    # Render in 4-columns grids
    render_kpi_grid(kpis[:4], cols_per_row=4)
    render_kpi_grid(kpis[4:], cols_per_row=4)
    
    st.markdown("---")
    
    # 4. Detailed visual columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📢 Key Executive Alerts")
        
        # Display dynamic alerts
        alert_count = 0
        if delayed_projs > 0:
            st.error(f"🔴 **Operational Risk**: {delayed_projs} projects are currently delayed (Project Beta, Project Omega). Total budget delayed: **{format_currency(df_proj[df_proj['status']=='Delayed']['budget'].sum())}**.")
            alert_count += 1
            
        at_risk_clients = df_cli[df_cli['retention_status'] == 'At Risk']
        if not at_risk_clients.empty:
            clients_list = ", ".join(at_risk_clients['client_name'].tolist())
            st.warning(f"🟡 **Client Retention Risk**: {len(at_risk_clients)} client relations are flagged as 'At Risk' ({clients_list}) with low NPS scores.")
            alert_count += 1
            
        negotiation_partners = df_part[df_part['status'] == 'Negotiation']
        if not negotiation_partners.empty:
            pipeline_sum = negotiation_partners['pipeline_value'].sum()
            st.info(f"🔵 **Sales Opportunity**: {len(negotiation_partners)} partnerships are in late-stage negotiations, representing a pipeline value of **{format_currency(pipeline_sum)}**.")
            alert_count += 1
            
        if alert_count == 0:
            st.success("🟢 All operations and client retention statuses are running smoothly.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ingest API rates/benchmarks as supporting info
        df_api = db.get_table_dataframe("api_metrics")
        if not df_api.empty:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.subheader("🌎 Global Market Benchmarks")
            cols = st.columns(len(df_api))
            for idx, row in df_api.iterrows():
                with cols[idx]:
                    name = row['metric_name'].replace('_', ' ').upper()
                    val = row['metric_value']
                    if "rate" in name.lower() or "growth" in name.lower():
                        val_str = f"{val*100:.2f}%"
                    else:
                        val_str = f"{val:.2f}"
                    st.metric(label=name, value=val_str)
            st.markdown('</div>', unsafe_allow_html=True)
            
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📊 Portfolio Status")
        
        proj_counts = df_proj['status'].value_counts()
        
        # Display simple visual bar charts
        for status, count in proj_counts.items():
            color = "#10B981" if status == 'On Track' else ("#F59E0B" if status == 'At Risk' else "#EF4444")
            st.write(f"**{status}** ({count})")
            st.progress(int((count / len(df_proj)) * 100))
            
        st.markdown("---")
        st.write(f"**Total Portfolio Value:** {format_currency(df_proj['budget'].sum())}")
        st.write(f"**Average Completion:** {df_proj['completion_pct'].mean():.1f}%")
        st.markdown('</div>', unsafe_allow_html=True)

show_home_page()
