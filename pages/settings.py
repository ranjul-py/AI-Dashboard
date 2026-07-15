import streamlit as st
import pandas as pd
from database.db_manager import DBManager
from services.etl_service import ETLService
from components.styles import inject_styles

def show_settings_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("⚙️ System Settings & Administration")
    st.markdown("### Data pipeline triggers, security audit trails, and role configurations")
    
    db = DBManager()
    etl = ETLService(db)
    
    # 1. API Configuration
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔑 OpenAI API Key Configuration")
    
    current_key = st.session_state.get("openai_api_key", "")
    key_input = st.text_input(
        "Enter OpenAI API Key",
        value=current_key,
        type="password",
        placeholder="sk-...",
        help="API Key will be stored securely in the active session context."
    )
    
    if st.button("💾 Save API Key"):
        st.session_state["openai_api_key"] = key_input
        st.success("API Key saved to session state successfully!")
        db.log_action(st.session_state.username, "SAVE_API_KEY", "Configured custom OpenAI API key")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. ETL Management
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🔄 Automated ETL Pipeline Management")
    st.write("Extracts raw CSV tables, reads partner targets from Excel sheets, merges project details from JSON manifests, fetches exchange rates from live endpoints, and refreshes the SQLite database.")
    
    if st.button("⚡ Execute ETL Pipeline Run"):
        with st.spinner("Extracting, cleaning and loading data sources..."):
            result = etl.run_pipeline()
            if result["status"] == "SUCCESS":
                st.success("ETL Pipeline completed successfully!")
                st.write(result["summary"])
                db.log_action(st.session_state.username, "MANUAL_ETL", "Manually triggered successful ETL run")
            else:
                st.error(f"ETL Execution failed: {result['error']}")
                db.log_action(st.session_state.username, "MANUAL_ETL_FAILED", result["error"])
                
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. User Management
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("👥 Platform User Management")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("**Add New Member**")
        new_user = st.text_input("Username", key="new_u")
        new_pass = st.text_input("Password", type="password", key="new_p")
        new_role = st.selectbox("Role Permission", ["CEO", "Executive Admin", "Viewer"], key="new_r")
        new_name = st.text_input("Full Name", key="new_n")
        new_email = st.text_input("Email", key="new_e")
        
        if st.button("➕ Add User"):
            if new_user and new_pass and new_name and new_email:
                success = db.add_user(
                    username=new_user,
                    password=new_pass,
                    role=new_role,
                    full_name=new_name,
                    email=new_email,
                    operator=st.session_state.username
                )
                if success:
                    st.success(f"User '{new_user}' created!")
                    st.rerun()
                else:
                    st.error("Username already exists.")
            else:
                st.warning("Please fill all fields.")
                
    with col2:
        st.write("**Registered Accounts**")
        df_users = db.get_users()
        st.dataframe(df_users, hide_index=True, use_container_width=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 4. Audit Log View
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("🛡️ Security Audit & Operations Log")
    st.write("System activity logs recorded inside SQLite:")
    
    df_audit = db.get_audit_logs(limit=50)
    # Format timestamp for better scanning
    if not df_audit.empty:
        df_audit['timestamp'] = df_audit['timestamp'].apply(lambda x: x.split('.')[0].replace('T', ' '))
    st.dataframe(df_audit, hide_index=True, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

show_settings_page()
