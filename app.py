# app.py
"""
MedChain EMR — Main Streamlit Application Entry Point
Blockchain-based Secure Electronic Medical Records System
"""
import json
import webbrowser
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Ensure data directories exist
from utils.helpers import ensure_dirs
ensure_dirs()

# Initialize DB
from database.migrations import run_migrations
from database.seed import seed_database

run_migrations()
seed_database()

# Session management
from utils.session_manager import (
    init_session,
    is_authenticated,
    clear_session,
    get_current_user,
    set_user
)
init_session()

# Auth
from auth.auth import login_user, register_user, logout_user

# Modules
from modules.add_record import render_add_record
from modules.view_records import render_view_records
from modules.update_record import render_update_record
from modules.delete_record import render_delete_record
from modules.upload_reports import render_upload_reports
from modules.patient_dashboard import render_patient_dashboard
from modules.doctor_dashboard import render_doctor_dashboard
from modules.admin_dashboard import render_admin_dashboard
from modules.analytics import render_analytics
from modules.audit_logs import render_audit_logs
from modules.login_page import render_login_page   # ← ADDED: 3D-styled login

from utils.constants import ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT, APP_NAME, APP_VERSION

# ─────────────────────────── PAGE CONFIG ───────────────────────────

st.set_page_config(
    page_title=f"{APP_NAME}",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── CUSTOM CSS ───────────────────────────

def load_css():
    css_path = Path("static/style.css")
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Inline critical styles
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

    :root {
        --primary: #00b4d8;
        --primary-dark: #0077b6;
        --accent: #06d6a0;
        --danger: #ef476f;
        --warning: #ffd166;
        --bg-dark: #0d1117;
        --bg-card: #161b22;
        --bg-sidebar: #010409;
        --text-primary: #e6edf3;
        --text-muted: #8b949e;
        --border: #30363d;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #0f1923 50%, #0d1117 100%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #010409 0%, #0d1117 100%);
        border-right: 1px solid #30363d;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: #c9d1d9;
    }

    /* Cards / Containers */
    .stContainer, [data-testid="stVerticalBlock"] > div {
        border-radius: 10px;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #161b22, #1c2333);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
    }

    [data-testid="stMetricValue"] {
        color: #00b4d8 !important;
        font-family: 'Space Mono', monospace;
        font-size: 1.8rem !important;
    }

    [data-testid="stMetricLabel"] {
        color: #8b949e;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00b4d8, #0077b6);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #0077b6, #005f99);
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(0,180,216,0.4);
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        color: #c9d1d9 !important;
    }

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #c9d1d9;
    }

    /* Dataframe */
    .dataframe {
        background: #161b22 !important;
    }

    /* Success/Error/Warning */
    .stSuccess {
        background: rgba(6,214,160,0.15) !important;
        border: 1px solid #06d6a0 !important;
        border-radius: 8px !important;
    }
    .stError {
        background: rgba(239,71,111,0.15) !important;
        border: 1px solid #ef476f !important;
        border-radius: 8px !important;
    }
    .stWarning {
        background: rgba(255,209,102,0.15) !important;
        border: 1px solid #ffd166 !important;
        border-radius: 8px !important;
    }
    .stInfo {
        background: rgba(0,180,216,0.1) !important;
        border: 1px solid #00b4d8 !important;
        border-radius: 8px !important;
    }

    /* Divider */
    hr {
        border: none;
        border-top: 1px solid #30363d;
        margin: 1rem 0;
    }

    /* Sidebar nav items */
    .nav-item {
        padding: 8px 16px;
        border-radius: 8px;
        margin: 2px 0;
        cursor: pointer;
        transition: background 0.2s;
    }

    .nav-item:hover {
        background: rgba(0,180,216,0.1);
    }

    /* Header brand */
    .brand-header {
        text-align: center;
        padding: 20px 10px;
        border-bottom: 1px solid #30363d;
        margin-bottom: 16px;
    }

    .brand-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00b4d8;
        font-family: 'Space Mono', monospace;
    }

    .brand-subtitle {
        font-size: 0.7rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    </style>
    """, unsafe_allow_html=True)



# ─────────────────────────── LOGIN PAGE ───────────────────────────
# render_login_page() is now in modules/login_page.py (3D-styled version).
# Imported above. No changes needed to the call site in main().


# ─────────────────────────── SIDEBAR ───────────────────────────

def render_sidebar():
    """Render the navigation sidebar."""
    user = get_current_user()
    role = user["role"]
    username = user["username"]

    with st.sidebar:
        # Brand
        st.markdown(f"""
        <div class="brand-header">
            <div class="brand-title">⚕️ MedChain</div>
            <div class="brand-subtitle">EMR System v{APP_VERSION}</div>
        </div>
        """, unsafe_allow_html=True)

        # User info
        role_icons = {ROLE_ADMIN: "🛡️", ROLE_DOCTOR: "🩺", ROLE_PATIENT: "👤"}
        st.markdown(f"""
        <div style="padding:10px; background:#161b22; border-radius:8px; margin-bottom:16px; border:1px solid #30363d;">
            <span style="color:#00b4d8;">{role_icons.get(role,'👤')} {username}</span><br>
            <span style="color:#8b949e; font-size:0.8rem; text-transform:uppercase;">{role}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Navigation**")

        # Navigation based on role
        pages = _get_nav_pages(role)

        for page_key, page_label in pages.items():
            is_current = st.session_state.page == page_key
            btn_type = "primary" if is_current else "secondary"
            if st.button(page_label, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

        st.divider()

        # Chain status
        from blockchain.blockchain import get_blockchain
        chain = get_blockchain()
        is_valid, _ = chain.validate()
        status_color = "#06d6a0" if is_valid else "#ef476f"
        st.markdown(f"""
        <div style="padding:8px; background:#161b22; border-radius:8px; border:1px solid #30363d; text-align:center;">
            <span style="color:{status_color}; font-size:0.8rem;">
                {'✅' if is_valid else '⚠️'} Chain: {chain.length()} blocks
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Logout
        if st.button("🚪 Logout", use_container_width=True):

            clear_session()

           # st.session_state.clear()

            st.rerun()


def _get_nav_pages(role: str) -> dict:
    """Return navigation pages based on user role."""
    common = {"dashboard": "🏠 Dashboard"}

    if role == ROLE_ADMIN:
        return {
            **common,
            "view_records": "📋 All Records",
            "analytics": "📊 Analytics",
            "audit_logs": "📜 Audit Logs",
            "delete_record": "🗑️ Delete Records",
        }
    elif role == ROLE_DOCTOR:
        return {
            **common,
            "add_record": "➕ Add Record",
            "view_records": "📋 View Records",
            "update_record": "✏️ Update Record",
            "upload_reports": "📤 Upload Reports",
            "analytics": "📊 Analytics",
            "audit_logs": "📜 Audit Logs",
        }
    else:  # Patient
        return {
            **common,
            "view_records": "📋 My Records",
        }


# ─────────────────────────── ROUTER ───────────────────────────

def render_page():
    """Route to the appropriate page/module."""
    page = st.session_state.get("page", "dashboard")
    role = st.session_state.get("role")

    if page == "dashboard":
        if role == ROLE_ADMIN:
            render_admin_dashboard()
        elif role == ROLE_DOCTOR:
            render_doctor_dashboard()
        else:
            render_patient_dashboard()

    elif page == "add_record":
        if role in [ROLE_ADMIN, ROLE_DOCTOR]:
            render_add_record()
        else:
            st.error("Access denied.")

    elif page == "view_records":
        render_view_records()

    elif page == "update_record":
        if role in [ROLE_ADMIN, ROLE_DOCTOR]:
            render_update_record()
        else:
            st.error("Access denied.")

    elif page == "delete_record":
        if role == ROLE_ADMIN:
            render_delete_record()
        else:
            st.error("Access denied.")

    elif page == "upload_reports":
        if role in [ROLE_ADMIN, ROLE_DOCTOR]:
            render_upload_reports()
        else:
            st.error("Access denied.")

    elif page == "analytics":
        if role in [ROLE_ADMIN, ROLE_DOCTOR]:
            render_analytics()
        else:
            st.error("Access denied.")

    elif page == "audit_logs":
        if role in [ROLE_ADMIN, ROLE_DOCTOR]:
            render_audit_logs()
        else:
            st.error("Access denied.")

    else:
        st.error(f"Page '{page}' not found.")


# ─────────────────────────── MAIN ───────────────────────────
def auto_login_from_session():

    params = st.query_params

    if "username" not in params:
        return

    try:

        set_user(
            params.get("user_id", ""),
            params.get("username", ""),
            params.get("role", ""),
            params.get("token", "")
        )

        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Auto login failed: {e}")
def main():
    load_css()
    auto_login_from_session()
    if not is_authenticated():
        st.markdown(
        """
        <meta http-equiv="refresh"
        content="0; url=https://medchain-auth.onrender.com">
        """,
        unsafe_allow_html=True
    )
        st.stop()
    else:
        render_sidebar()
        render_page()


if __name__ == "__main__":
    main()
