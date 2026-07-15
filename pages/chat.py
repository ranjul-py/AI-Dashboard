import streamlit as st
from database.db_manager import DBManager
from llm.openai_client import OpenAIClient
from llm.chat_assistant import ChatAssistant
from components.styles import inject_styles

def show_chat_page():
    if not st.session_state.get("authenticated", False):
        st.warning("⚠️ Access Denied. Please authenticate via the Main Portal.")
        st.stop()

    inject_styles()
    
    st.title("💬 AI Executive Chat Assistant")
    st.markdown("### Query your databases, analyze portfolio risks, and synthesize cross-domain metrics")
    
    db = DBManager()
    client = OpenAIClient()
    assistant = ChatAssistant(db, client)
    
    if not client.is_api_configured():
        st.info("💡 **Local Simulation Active**: No OpenAI API Key found. The assistant is operating using robust local query templates. To experience complete natural-language parsing, configure your OpenAI API key in System Settings.")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Welcome. I am your AI Executive Assistant. I have read the current state of our SQLite database tables. Ask me anything about financial metrics, project delays, workforce utilization, or client retention risks."}
        ]

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Suggestion Pills
    st.markdown("### Suggested Prompts")
    col1, col2, col3 = st.columns(3)
    suggestion = None
    
    with col1:
        if st.button("📁 Which projects are delayed?", use_container_width=True):
            suggestion = "Which projects are delayed?"
    with col2:
        if st.button("📈 Show revenue growth.", use_container_width=True):
            suggestion = "Show revenue growth."
    with col3:
        if st.button("⚠️ What risks should I focus on?", use_container_width=True):
            suggestion = "What risks should I focus on?"

    # Handle input (either suggestion pill or chat input)
    user_input = st.chat_input("Ask about financials, projects, workforce, or client sentiment...")
    
    prompt = user_input or suggestion

    if prompt:
        # Display user message
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from AI assistant
        with st.spinner("Analyzing data and generating answer..."):
            response = assistant.ask_assistant(prompt)
            
        # Display assistant message
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
            
        # Record login action / audit log
        db.log_action(st.session_state.username, "CHAT_QUERY", f"Queried chat: '{prompt[:60]}...'")

show_chat_page()
