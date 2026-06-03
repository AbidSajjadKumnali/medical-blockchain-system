# utils/session_manager.py
"""
Streamlit session state management for MedChain EMR System.
"""

import streamlit as st
from typing import Optional


def init_session():
    """Initialize all session state variables."""
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "role": None,
        "token": None,
        "page": "login",
        "selected_patient": None,
        "selected_record": None,
        "search_query": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def set_user(user_id: str, username: str, role: str, token: str):
    """Set authenticated user session."""
    st.session_state.authenticated = True
    st.session_state.user_id = user_id
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.token = token
    st.session_state.page = "dashboard"


def clear_session():
    """Clear user session on logout."""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.token = None
    st.session_state.page = "login"
    st.session_state.selected_patient = None
    st.session_state.selected_record = None


def get_current_user() -> dict:
    """Get current user info from session."""
    return {
        "user_id": st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "role": st.session_state.get("role"),
    }


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def require_role(role: str) -> bool:
    """Check if current user has the required role."""
    return st.session_state.get("role") == role


def require_roles(roles: list) -> bool:
    """Check if current user has one of the required roles."""
    return st.session_state.get("role") in roles
