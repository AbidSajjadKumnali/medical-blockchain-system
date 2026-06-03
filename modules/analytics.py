# modules/analytics.py
"""
Analytics dashboard with Plotly charts for MedChain EMR.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.models import MedicalRecordModel, UserModel, PatientModel, AuditLogModel
from utils.helpers import format_datetime


def render_analytics():
    """Render system analytics with interactive charts."""
    st.markdown("## 📊 System Analytics")
    st.markdown("Real-time insights into the MedChain EMR system.")
    st.divider()

    records = MedicalRecordModel.get_all()
    users = UserModel.get_all()
    audit_logs = AuditLogModel.get_all(limit=500)

    # ── Record Type Distribution ──
    st.markdown("### 📋 Records by Type")
    if records:
        type_counts = {}
        for r in records:
            rtype = r.get("record_type", "other")
            type_counts[rtype] = type_counts.get(rtype, 0) + 1

        df_types = pd.DataFrame(
            list(type_counts.items()), columns=["Record Type", "Count"]
        )
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(
                df_types, names="Record Type", values="Count",
                title="Record Type Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            fig_bar = px.bar(
                df_types.sort_values("Count", ascending=False),
                x="Record Type", y="Count",
                title="Records per Type",
                color="Count",
                color_continuous_scale="Blues"
            )
            fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No records yet.")

    st.divider()

    # ── User Role Distribution ──
    st.markdown("### 👥 User Roles")
    if users:
        role_counts = {}
        for u in users:
            r = u.get("role", "unknown")
            role_counts[r] = role_counts.get(r, 0) + 1

        df_roles = pd.DataFrame(list(role_counts.items()), columns=["Role", "Count"])
        fig_roles = px.bar(
            df_roles, x="Role", y="Count", color="Role",
            title="Users by Role",
            color_discrete_sequence=["#e74c3c", "#3498db", "#2ecc71"]
        )
        fig_roles.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_roles, use_container_width=True)

    st.divider()

    # ── Activity Timeline ──
    st.markdown("### 📅 Activity Timeline (Last 30 Days)")
    if audit_logs:
        df_audit = pd.DataFrame(audit_logs)
        df_audit["date"] = pd.to_datetime(df_audit["timestamp"]).dt.date
        activity = df_audit.groupby(["date", "action"]).size().reset_index(name="count")
        activity["date"] = pd.to_datetime(activity["date"])
        activity = activity.sort_values("date").tail(300)

        fig_timeline = px.line(
            activity, x="date", y="count", color="action",
            title="Daily Activity by Action Type",
            markers=True
        )
        fig_timeline.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_timeline, use_container_width=True)

    st.divider()

    # ── Blood Group Distribution ──
    st.markdown("### 🩸 Patient Blood Group Distribution")
    patients = PatientModel.get_all_with_users()
    if patients:
        bg_counts = {}
        for p in patients:
            bg = p.get("blood_group", "Unknown") or "Unknown"
            bg_counts[bg] = bg_counts.get(bg, 0) + 1

        df_bg = pd.DataFrame(list(bg_counts.items()), columns=["Blood Group", "Count"])
        fig_bg = px.bar(
            df_bg, x="Blood Group", y="Count",
            title="Patients by Blood Group",
            color="Count",
            color_continuous_scale="Reds"
        )
        fig_bg.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_bg, use_container_width=True)

    # ── Summary Table ──
    st.divider()
    st.markdown("### 📊 Summary Statistics")
    summary = {
        "Metric": ["Total Users", "Total Patients", "Total Records", "Audit Events"],
        "Value": [
            len(users), len(patients), len(records), len(audit_logs)
        ]
    }
    st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
