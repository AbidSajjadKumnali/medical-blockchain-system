# modules/update_record.py
"""
Update existing medical records (doctors/admins only).
"""

import streamlit as st
from database.models import MedicalRecordModel, PatientModel, AuditLogModel
from utils.session_manager import get_current_user
from utils.validators import sanitize_text
from utils.constants import ACTION_UPDATE_RECORD
from utils.helpers import format_datetime


def render_update_record():
    """Render the update medical record interface."""
    st.markdown("## ✏️ Update Medical Record")
    st.markdown("Select a record to update diagnosis or prescription.")
    st.divider()

    user = get_current_user()
    doctor_id = user["user_id"]

    # Select patient
    patients = PatientModel.get_all_with_users()
    if not patients:
        st.warning("No patients registered.")
        return

    patient_opts = {f"{p['username']}": p["id"] for p in patients}
    selected_patient_name = st.selectbox("Select Patient", list(patient_opts.keys()))
    patient_id = patient_opts[selected_patient_name]

    # Load records for selected patient
    records = MedicalRecordModel.get_by_patient(patient_id)
    active_records = [r for r in records if r.get("status") == "active"]

    if not active_records:
        st.info("No active records for this patient.")
        return

    record_opts = {
        f"[{r.get('record_type', 'record').upper()}] {format_datetime(r['created_at'])} — "
        f"Dr.{r.get('doctor_name', 'Unknown')}": r["id"]
        for r in active_records
    }

    selected_label = st.selectbox("Select Record to Update", list(record_opts.keys()))
    record_id = record_opts[selected_label]

    record = MedicalRecordModel.get_by_id(record_id)
    if not record:
        st.error("Record not found.")
        return

    st.info("⚠️ Note: Blockchain entries are immutable. Only the database copy is updated. "
            "The original encrypted record remains on the chain.")

    with st.form("update_record_form"):
        new_diagnosis = st.text_area("Updated Diagnosis *", value=record.get("diagnosis", ""), height=100)
        new_prescription = st.text_area("Updated Prescription", value=record.get("prescription", ""), height=100)

        submitted = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

        if submitted:
            if not new_diagnosis.strip():
                st.error("Diagnosis cannot be empty.")
                return

            new_diagnosis = sanitize_text(new_diagnosis)
            new_prescription = sanitize_text(new_prescription)

            success = MedicalRecordModel.update(record_id, new_diagnosis, new_prescription)
            if success:
                AuditLogModel.log(
                    doctor_id, ACTION_UPDATE_RECORD,
                    f"Updated record {record_id[:8]} for patient {patient_id[:8]}"
                )
                st.success("✅ Record updated successfully!")
                st.info(f"Record ID: {record_id[:8]}... — Original blockchain block preserved.")
            else:
                st.error("Failed to update record.")
