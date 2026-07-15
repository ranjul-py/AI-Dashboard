import streamlit as st
import sys
import os

# Add root folder to sys path to resolve relative module imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.db_manager import DBManager
from services.auth_service import AuthService
from components.styles import inject_styles

# 1. Global Page Layout Setup (MUST be first Streamlit command)
st.set_page_config(
    page_title="AI Executive Dashboard",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Initialize Database and Auth Services
db = DBManager()
auth = AuthService(db)

# 3. Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "full_name" not in st.session_state:
    st.session_state.full_name = None
if "email" not in st.session_state:
    st.session_state.email = None

def show_login_page():
    # Render Custom Glassmorphic Login Screen
    inject_styles()
    
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">💼 CEO OFFICE PLATFORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">AI-Powered Executive Review & Business Intelligence</div>', unsafe_allow_html=True)
    
    login_user = st.text_input("Username", placeholder="e.g. ceo", key="login_u")
    login_pass = st.text_input("Password", type="password", placeholder="••••••••", key="login_p")
    
    if st.button("Authenticate Identity", use_container_width=True):
        if login_user and login_pass:
            if auth.login(login_user, login_pass):
                st.success("Access Granted. Initializing workspace...")
                st.rerun()
            else:
                st.error("Authentication Failed. Check username/password.")
        else:
            st.warning("Please supply both credentials.")
            
    st.markdown("""
    <div style="margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; font-size: 11px; color: #94A3B8; text-align: center;">
        <strong>Demo Identities:</strong><br/>
        • CEO Access: <code>ceo</code> / <code>ceo123</code><br/>
        • Admin Access: <code>admin</code> / <code>admin123</code><br/>
        • Viewer Access: <code>viewer</code> / <code>viewer123</code>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 4. Routing Logic
if not st.session_state.authenticated:
    login_page = st.Page(show_login_page, title="Login", icon="🔒")
    pg = st.navigation([login_page], position="hidden")
    pg.run()
    
else:
    # User is Authenticated. Dynamic Multi-Page Setup.
    role = auth.get_role()
    
    # Base pages (Available to all roles: CEO, Admin, Viewer)
    pages = [
        st.Page("pages/home.py", title="Executive Summary", icon="🏠"),
        st.Page("pages/revenue.py", title="Revenue Analytics", icon="📊"),
        st.Page("pages/projects.py", title="Project Health", icon="🏥"),
        st.Page("pages/workforce.py", title="Workforce Analytics", icon="👥"),
        st.Page("pages/clients.py", title="Client Insights", icon="👤"),
        st.Page("pages/partners.py", title="Partner Pipeline", icon="🤝"),
    ]
    
    # CEO-only pages (Chatbot, WBR Generator)
    if role == "CEO":
        pages.append(st.Page("pages/wbr.py", title="AI WBR Generator", icon="🤖"))
        pages.append(st.Page("pages/chat.py", title="AI Chat Assistant", icon="💬"))
        
    # Admin/CEO-only pages (ETL triggers, user managements)
    if role in ["CEO", "Executive Admin"]:
        pages.append(st.Page("pages/settings.py", title="System Settings", icon="⚙️"))
        
    # Render Sidebar Branding & Profile
    st.sidebar.markdown('<div style="text-align: center; margin-bottom: 10px;">', unsafe_allow_html=True)
    st.sidebar.markdown(f"### 💼 CEO Office Platform")
    st.sidebar.markdown(f"**Member:** {st.session_state.full_name}")
    st.sidebar.markdown(f"**Level:** `{st.session_state.role}`")
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Render Logout Button
    if st.sidebar.button("🔒 Terminate Session", use_container_width=True):
        auth.logout()
        st.rerun()
        
    st.sidebar.markdown("---")
    
    # Load Sidebar Page Navigation
    pg = st.navigation(pages)
    pg.run()
