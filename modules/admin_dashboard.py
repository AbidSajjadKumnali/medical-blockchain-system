# modules/admin_dashboard.py
"""
Admin dashboard: system overview, user management, blockchain monitoring.
"""

import streamlit as st
import pandas as pd
from database.models import UserModel, PatientModel, MedicalRecordModel, AuditLogModel
from blockchain.blockchain import get_blockchain
from utils.session_manager import get_current_user
from utils.helpers import format_datetime
from utils.constants import ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT


def render_admin_dashboard():
    """Render the full admin system dashboard."""
    user = get_current_user()
    st.markdown(f"## 🛡️ Admin Control Panel")
    st.markdown("System overview and management for MedChain EMR.")
    st.divider()

    # System stats
    total_users = UserModel.count()
    total_patients = PatientModel.count()
    total_records = MedicalRecordModel.count()
    chain = get_blockchain()
    is_valid, _ = chain.validate()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("👥 Total Users", total_users)
    col2.metric("🏥 Patients", total_patients)
    col3.metric("📋 Records", total_records)
    col4.metric("⛓️ Blocks", chain.length())
    col5.metric("🔐 Chain", "✅ OK" if is_valid else "⚠️ Alert")

    st.divider()

    # User Management
    st.markdown("### 👥 User Management")

    all_users = UserModel.get_all()
    role_filter = st.selectbox("Filter by Role", ["All", "admin", "doctor", "patient"], key="admin_role_filter")

    filtered = all_users if role_filter == "All" else [u for u in all_users if u["role"] == role_filter]

    for u in filtered:
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            role_icons = {"admin": "🛡️", "doctor": "🩺", "patient": "👤"}
            st.write(f"{role_icons.get(u['role'], '👤')} **{u['username']}**")
            st.caption(u["email"])
        with col2:
            st.caption(f"Role: {u['role'].title()} | Joined: {format_datetime(u.get('created_at', ''))}")
        with col3:
            status = "🟢 Active" if u.get("is_active") else "🔴 Inactive"
            st.write(status)
        with col4:
            if u["role"] != ROLE_ADMIN:  # Protect admin accounts
                btn_label = "Deactivate" if u.get("is_active") else "Activate"
                if st.button(btn_label, key=f"toggle_{u['id']}"):
                    new_status = not bool(u.get("is_active"))
                    UserModel.set_active(u["id"], new_status)
                    action = "USER_ACTIVATE" if new_status else "USER_DEACTIVATE"
                    AuditLogModel.log(
                        user["user_id"], action,
                        f"{'Activated' if new_status else 'Deactivated'} user {u['username']}"
                    )
                    st.rerun()

    st.divider()

    # Blockchain monitor
    st.markdown("### ⛓️ Blockchain Monitor")
    col_v, col_s = st.columns(2)
    with col_v:
        if st.button("🔍 Validate Full Chain", use_container_width=True):
            with st.spinner("Validating..."):
                valid, issues = chain.validate()
                if valid:
                    st.success(f"✅ All {chain.length()} blocks valid!")
                else:
                    st.error(f"⚠️ {len(issues)} issue(s) found:")
                    for issue in issues:
                        st.warning(issue)

    with col_s:
        stats = {
            "Total Blocks": chain.length(),
            "Latest Hash": chain.get_latest_hash()[:20] + "...",
            "Status": "Valid" if is_valid else "COMPROMISED",
        }
        for k, v in stats.items():
            st.metric(k, v)
