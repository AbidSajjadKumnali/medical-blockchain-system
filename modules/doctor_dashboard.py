# modules/doctor_dashboard.py
"""
Doctor dashboard: patient overview, quick access to add/view records.
"""

import streamlit as st
import pandas as pd
from database.models import MedicalRecordModel, PatientModel, AuditLogModel
from blockchain.blockchain import get_blockchain
from utils.session_manager import get_current_user
from utils.helpers import format_datetime


def render_doctor_dashboard():
    """Render the doctor's operational dashboard."""
    user = get_current_user()
    doctor_id = user["user_id"]
    username = user["username"]

    st.markdown(f"## 🩺 Dr. {username}'s Dashboard")
    st.markdown("Manage your patients and medical records efficiently.")
    st.divider()

    # Fetch records created by this doctor
    all_records = MedicalRecordModel.get_all()
    my_records = [r for r in all_records if r.get("doctor_id") == doctor_id]
    active_records = [r for r in my_records if r.get("status") == "active"]

    patients = PatientModel.get_all_with_users()
    chain = get_blockchain()
    is_valid, _ = chain.validate()

    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Total Patients", len(patients))
    col2.metric("📋 My Records", len(active_records))
    col3.metric("⛓️ Chain Length", chain.length())
    col4.metric("🔒 Blockchain", "✅ Valid" if is_valid else "⚠️ Alert")

    st.divider()

    # Quick actions
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ Add New Record", use_container_width=True, type="primary"):
            st.session_state.page = "add_record"
            st.rerun()
    with col_b:
        if st.button("📤 Upload Report", use_container_width=True):
            st.session_state.page = "upload_reports"
            st.rerun()

    st.divider()

    # Patient list
    st.markdown("### 👥 Patient List")
    search = st.text_input("🔍 Search patients", "")

    filtered_patients = [
        p for p in patients
        if search.lower() in p.get("username", "").lower() or
           search.lower() in p.get("email", "").lower()
    ] if search else patients

    if filtered_patients:
        df_patients = pd.DataFrame([{
            "Username": p.get("username", ""),
            "Email": p.get("email", ""),
            "Age": p.get("age", "N/A"),
            "Blood Group": p.get("blood_group", "N/A"),
            "Allergies": p.get("allergies", "None") or "None",
            "Status": "🟢 Active" if p.get("is_active") else "🔴 Inactive",
        } for p in filtered_patients])
        st.dataframe(df_patients, use_container_width=True, hide_index=True)
    else:
        st.info("No patients found.")

    st.divider()

    # Recent records
    st.markdown("### 📋 My Recent Records")
    if active_records:
        for rec in active_records[:8]:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"📄 {rec.get('record_type','').title()}: **{rec.get('diagnosis','')[:70]}**")
            with col2:
                st.caption(f"Patient: {rec.get('patient_name','N/A')} | {format_datetime(rec.get('created_at',''))}")
            with col3:
                block_hash = rec.get("blockchain_hash", "")
                matching = next((b for b in chain.chain if b.hash == block_hash), None)
                if matching and matching.is_valid():
                    st.success("✅ Verified")
                else:
                    st.warning("⚠️ Check")
    else:
        st.info("No records created yet. Add your first record!")
