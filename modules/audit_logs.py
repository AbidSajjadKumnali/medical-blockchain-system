# modules/audit_logs.py
"""
Audit log viewer for admin and doctor roles.
"""

import streamlit as st
import pandas as pd
from database.models import AuditLogModel
from utils.helpers import format_datetime
from utils.session_manager import get_current_user
from utils.constants import ROLE_ADMIN


def render_audit_logs():
    """Render the audit logs viewer with search and filter."""
    st.markdown("## 📜 Audit Logs")
    st.markdown("Complete activity trail for compliance and security monitoring.")
    st.divider()

    user = get_current_user()

    col1, col2 = st.columns(2)
    with col1:
        limit = st.selectbox("Show last N entries", [50, 100, 250, 500], index=1)
    with col2:
        action_filter = st.text_input("🔍 Filter by action or user", "")

    logs = AuditLogModel.get_all(limit=limit)

    if action_filter:
        logs = [l for l in logs if
                action_filter.upper() in l.get("action", "").upper() or
                action_filter.lower() in l.get("username", "").lower()]

    st.markdown(f"**{len(logs)}** log entries shown")
    st.divider()

    if not logs:
        st.info("No audit logs found.")
        return

    # Display as DataFrame
    df = pd.DataFrame([{
        "Timestamp": format_datetime(l.get("timestamp", "")),
        "User": l.get("username", "Unknown"),
        "Action": l.get("action", ""),
        "Details": l.get("details", "")[:80],
        "IP Address": l.get("ip_address", ""),
    } for l in logs])

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Export
    if st.button("📥 Export as CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="medchain_audit_logs.csv",
            mime="text/csv"
        )
