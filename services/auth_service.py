import streamlit as st
import logging
from database.db_manager import DBManager

logger = logging.getLogger(__name__)

class AuthService:
    """
    Manages user sessions, authentication, and role-based permissions
    inside Streamlit applications.
    """
    def __init__(self, db_manager: DBManager):
        self.db = db_manager

    def login(self, username, password) -> bool:
        """
        Authenticates a user. Sets streamlit session variables if successful.
        """
        user_info = self.db.authenticate_user(username, password)
        if user_info:
            st.session_state.authenticated = True
            st.session_state.username = user_info["username"]
            st.session_state.role = user_info["role"]
            st.session_state.full_name = user_info["full_name"]
            st.session_state.email = user_info["email"]
            return True
        else:
            st.session_state.authenticated = False
            return False

    def logout(self):
        """Clears user session from streamlit state."""
        username = st.session_state.get("username", "ANONYMOUS")
        self.db.log_action(username, "LOGOUT", "User logged out")
        
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.full_name = None
        st.session_state.email = None

    @staticmethod
    def is_authenticated() -> bool:
        """Checks if there is an active authenticated session."""
        return st.session_state.get("authenticated", False)

    @staticmethod
    def get_role() -> str:
        """Returns the role of the logged in user, or None."""
        return st.session_state.get("role", None)

    @staticmethod
    def get_username() -> str:
        """Returns the username of the logged in user."""
        return st.session_state.get("username", "Anonymous")

    def check_permission(self, required_roles) -> bool:
        """
        Verifies if the current user role matches the required roles.
        required_roles can be a string or list of strings.
        """
        if not self.is_authenticated():
            return False
            
        current_role = self.get_role()
        if isinstance(required_roles, str):
            required_roles = [required_roles]
            
        return current_role in required_roles
