# Custom styles for the Glassmorphism Dark Theme in Streamlit

CSS_DARK_GLASS = """
<style>
/* 1. Overall Page and Background Styling - Forced Dark Mode */
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"], [data-testid="stToolbar"] {
    background-color: #0b0f19 !important;
    color: #f8fafc !important;
    font-family: 'Inter', 'Outfit', sans-serif !important;
}

h1, h2, h3, h4, h5, h6, p, span, label, li, ul, ol, .stMarkdown, div[data-testid="stMetricLabel"] {
    color: #f8fafc !important;
}

/* Force dark backgrounds on sidebar */
[data-testid="stSidebar"] {
    background-color: #080c14 !important;
}

/* Fix input fields and selectboxes to stay dark & readable */
input, select, textarea, [data-baseweb="select"], [data-baseweb="base-input"] {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}

/* Hide Streamlit default footer branding */
footer {visibility: hidden;}
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* 2. Glassmorphism Card Design */
.glass-card {
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2), 0 2px 4px -1px rgba(0, 0, 0, 0.1);
}

.glass-card:hover {
    transform: translateY(-4px);
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 12px 20px -3px rgba(56, 189, 248, 0.15), 0 4px 6px -2px rgba(56, 189, 248, 0.05);
}

/* 3. KPI Cards Layout and Elements */
.kpi-row {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 25px;
    width: 100%;
}

.kpi-card {
    flex: 1;
    min-width: 220px;
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 18px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.kpi-card:hover {
    transform: scale(1.03);
    border-color: rgba(56, 189, 248, 0.5);
    box-shadow: 0 8px 16px rgba(56, 189, 248, 0.12);
}

/* Highlight line inside cards */
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: #38bdf8; /* Accent light-blue */
}

.kpi-card.success::after { background: #10b981; } /* Emerald */
.kpi-card.warning::after { background: #f59e0b; } /* Amber */
.kpi-card.danger::after { background: #ef4444; }   /* Rose */

.kpi-icon {
    font-size: 24px;
    position: absolute;
    right: 15px;
    top: 15px;
    opacity: 0.85;
}

.kpi-title {
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.2;
}

.kpi-delta {
    font-size: 11px;
    font-weight: 500;
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
}

.kpi-delta.positive { color: #34d399; }
.kpi-delta.negative { color: #f87171; }
.kpi-delta.neutral { color: #94a3b8; }

/* 4. Glassmorphism Login Container */
.login-container {
    max-width: 450px;
    margin: 80px auto;
    background: rgba(30, 41, 59, 0.45);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 40px;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
}

.login-title {
    font-size: 24px;
    font-weight: 700;
    text-align: center;
    color: #f8fafc;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}

.login-subtitle {
    font-size: 13px;
    text-align: center;
    color: #94a3b8;
    margin-bottom: 30px;
}

/* 5. Custom Button Styles */
div.stButton > button {
    background-color: #1e293b;
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    background-color: #38bdf8;
    color: #0b0f19;
    border-color: #38bdf8;
    box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
}

/* Call to action buttons (WBR generation, etc.) */
.action-btn {
    width: 100%;
    margin-top: 15px;
}

/* 6. Sidebar Customizations */
section[data-testid="stSidebar"] {
    background-color: #080c14;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

section[data-testid="stSidebar"] .stMarkdown h1 {
    font-size: 18px;
    font-weight: 700;
    color: #38bdf8;
    letter-spacing: -0.02em;
}

/* 7. Chat Styling Customizations */
.chat-container {
    background: rgba(15, 23, 42, 0.5);
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    padding: 15px;
    margin-top: 10px;
}
</style>
"""

def inject_styles():
    """Helper to inject custom CSS styles into the current Streamlit page."""
    import streamlit as st
    st.markdown(CSS_DARK_GLASS, unsafe_allow_html=True)
