# modules/delete_record.py
"""
Soft-delete medical records (admin only).
Blockchain entries remain immutable — only DB status is changed.
"""

import streamlit as st
from database.models import MedicalRecordModel, PatientModel, AuditLogModel
from utils.session_manager import get_current_user
from utils.constants import ACTION_DELETE_RECORD
from utils.helpers import format_datetime


def render_delete_record():
    """Render the delete record interface (admin only)."""
    st.markdown("## 🗑️ Delete Medical Record")
    st.warning("⚠️ Admin only. Records are soft-deleted (blockchain remains intact).")
    st.divider()

    user = get_current_user()
    admin_id = user["user_id"]

    patients = PatientModel.get_all_with_users()
    if not patients:
        st.info("No patients found.")
        return

    patient_opts = {f"{p['username']} ({p['id'][:8]})": p["id"] for p in patients}
    selected = st.selectbox("Select Patient", list(patient_opts.keys()))
    patient_id = patient_opts[selected]

    records = MedicalRecordModel.get_by_patient(patient_id)
    active_records = [r for r in records if r.get("status") == "active"]

    if not active_records:
        st.info("No active records found for this patient.")
        return

    st.markdown(f"**{len(active_records)} active record(s)** for selected patient:")

    for rec in active_records:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"📄 {rec.get('record_type', 'record').title()}: {rec.get('diagnosis', '')[:60]}...")
        with col2:
            st.caption(f"By Dr.{rec.get('doctor_name', 'N/A')} | {format_datetime(rec.get('created_at', ''))}")
        with col3:
            if st.button("🗑️ Delete", key=f"del_{rec['id']}"):
                st.session_state[f"confirm_delete_{rec['id']}"] = True

        # Confirmation step
        if st.session_state.get(f"confirm_delete_{rec['id']}"):
            st.error(f"Are you sure you want to soft-delete record `{rec['id'][:8]}`?")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("✅ Yes, Delete", key=f"yes_{rec['id']}", type="primary"):
                    if MedicalRecordModel.delete(rec["id"]):
                        AuditLogModel.log(
                            admin_id, ACTION_DELETE_RECORD,
                            f"Soft-deleted record {rec['id'][:8]}"
                        )
                        st.success("Record soft-deleted.")
                        st.session_state.pop(f"confirm_delete_{rec['id']}", None)
                        st.rerun()
                    else:
                        st.error("Delete failed.")
            with cc2:
                if st.button("❌ Cancel", key=f"no_{rec['id']}"):
                    st.session_state.pop(f"confirm_delete_{rec['id']}", None)
                    st.rerun()
