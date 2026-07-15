import streamlit as st
import os
from database.db_manager import DBManager
from llm.openai_client import OpenAIClient
from llm.chat_assistant import ChatAssistant
from automation.report_generator import ReportGenerator
from automation.email_service import EmailService
from components.styles import inject_styles
from utils.helpers import format_currency

def show_wbr_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("🤖 AI Weekly Business Review (WBR) Generator")
    st.markdown("### Automated cross-domain analytics and priority planning reviews")
    
    db = DBManager()
    client = OpenAIClient()
    assistant = ChatAssistant(db, client)
    pdf_generator = ReportGenerator()
    email_service = EmailService()
    
    # Check API key configuration alert
    if not client.is_api_configured():
        st.info("💡 **Local Simulation Active**: No OpenAI API Key found in settings. Generating high-fidelity mock WBR analytics for evaluation. You can enter an OpenAI API key in the System Settings page.")

    # Main Action Card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📝 Build New Business Review")
    st.write("Calculates real-time values for Revenue, Project completion percentages, delays, Workforce utilization, and Client NPS distributions before invoking LLM synthesis.")
    
    if st.button("🚀 Run AI Analysis & Generate WBR"):
        with st.spinner("Analyzing SQLite database tables and generating WBR report..."):
            report = assistant.generate_wbr(st.session_state.full_name)
            st.session_state.current_wbr_report = report
            # Clear previous PDF cache
            st.session_state.current_wbr_pdf = None
            
        st.success("Weekly Business Review generated successfully!")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Active Report
    if st.session_state.get("current_wbr_report"):
        report_text = st.session_state.current_wbr_report
        
        # Actions Layout
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Report Action Center")
        
        col_act1, col_act2 = st.columns(2)
        
        pdf_path = None
        with col_act1:
            st.write("📊 **Export Document**")
            # Build PDF if not already done
            if not st.session_state.get("current_wbr_pdf"):
                with st.spinner("Compiling PDF document using ReportLab..."):
                    try:
                        filename = f"WBR_{st.session_state.username}.pdf"
                        generated_path = pdf_generator.markdown_to_pdf(report_text, filename)
                        st.session_state.current_wbr_pdf = generated_path
                    except Exception as e:
                        st.error(f"Failed to generate PDF: {e}")
                        
            pdf_path = st.session_state.get("current_wbr_pdf")
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                    st.download_button(
                        label="📥 Download Executive PDF Report",
                        data=pdf_bytes,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        use_container_width=True
                    )
                    st.caption(f"PDF compiled and cached locally: `{pdf_path}`")
                    
        with col_act2:
            st.write("📧 **Distribute Report**")
            recipient_email = st.text_input("Recipient Email", value=st.session_state.email)
            if st.button("✉️ Send Report via Email", use_container_width=True):
                with st.spinner("Dispatching email..."):
                    result = email_service.send_report_email(
                        recipient_email=recipient_email,
                        subject="Confidential: Executive Weekly Business Review",
                        body_text="Dear Executive,\n\nPlease find attached the Weekly Business Review report compiled automatically by the CEO Office AI Assistant.\n\nBest regards,\nCEO AI Assistant",
                        attachment_path=pdf_path
                    )
                    
                    if result["status"] == "SENT":
                        st.success(f"Email sent successfully using live SMTP to {recipient_email}!")
                        db.log_action(st.session_state.username, "EMAIL_DISPATCH", f"WBR report sent via SMTP to {recipient_email}")
                    else:
                        st.success("Email generated and logged successfully (Offline Simulation)!")
                        st.info(f"Simulated outbox log updated at: `{result['outbox_log']}`")
                        db.log_action(st.session_state.username, "EMAIL_SIMULATED", f"Simulated WBR report email to {recipient_email}")
                        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display Report Text
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(report_text)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # 4. Historical Reports Archive
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📚 Saved Review History")
    
    df_history = db.get_wbr_reports(limit=5)
    if not df_history.empty:
        for idx, row in df_history.iterrows():
            formatted_date = row['generated_at'].split('.')[0].replace('T', ' ')
            with st.expander(f"Review: {formatted_date} (Generated by: {row['author']})"):
                st.markdown(row['report_text'])
                
                # Option to load this report as active
                if st.button("📂 Load in Action Center", key=f"load_{row['id']}"):
                    st.session_state.current_wbr_report = row['report_text']
                    st.session_state.current_wbr_pdf = None # Reset cache to recreate PDF
                    st.rerun()
    else:
        st.write("No historical reviews archived in database.")
    st.markdown('</div>', unsafe_allow_html=True)

show_wbr_page()
