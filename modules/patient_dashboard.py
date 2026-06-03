# modules/patient_dashboard.py
"""
Patient dashboard: overview of health records, blockchain status, file downloads.
"""

import streamlit as st
import pandas as pd
from database.models import MedicalRecordModel, PatientModel, FileRecordModel
from blockchain.blockchain import get_blockchain
from utils.session_manager import get_current_user
from utils.helpers import format_datetime
import os


def render_patient_dashboard():
    """Render the patient's personal health dashboard."""
    user = get_current_user()
    user_id = user["user_id"]
    username = user["username"]

    st.markdown(f"## 👤 Welcome, {username}")
    st.markdown("Your personal health record dashboard. All data is secured on the blockchain.")
    st.divider()

    # Get patient profile
    patient = PatientModel.get_by_user_id(user_id)
    if not patient:
        st.warning("Your patient profile is incomplete. Please contact your doctor or admin.")
        return

    patient_id = patient["id"]

    # Metrics row
    records = MedicalRecordModel.get_by_patient(patient_id)
    active_records = [r for r in records if r.get("status") == "active"]
    files = FileRecordModel.get_by_patient(patient_id)

    chain = get_blockchain()
    patient_blocks = chain.get_patient_blocks(patient_id)
    is_valid, _ = chain.validate()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Medical Records", len(active_records))
    col2.metric("📁 Uploaded Files", len(files))
    col3.metric("⛓️ Blockchain Blocks", len(patient_blocks))
    col4.metric("🔒 Chain Status", "✅ Valid" if is_valid else "⚠️ Issues")

    st.divider()

    # Profile card
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown("### 🪪 Health Profile")
        st.markdown(f"""
| Field | Value |
|-------|-------|
| **Age** | {patient.get('age', 'N/A')} |
| **Blood Group** | {patient.get('blood_group', 'N/A')} |
| **Allergies** | {patient.get('allergies', 'None')} |
| **Emergency Contact** | {patient.get('emergency_contact', 'N/A')} |
        """)

    with col_b:
        st.markdown("### 🕐 Recent Records")
        if active_records:
            for rec in active_records[:5]:
                rec_type_icons = {
                    "consultation": "🩺", "lab_report": "🧪",
                    "prescription": "💊", "radiology": "🔬",
                    "surgery": "⚕️", "vaccination": "💉", "follow_up": "📅"
                }
                icon = rec_type_icons.get(rec.get("record_type", ""), "📄")
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"{icon} **{rec.get('record_type','').title()}**: {rec.get('diagnosis','')[:80]}")
                        st.caption(f"Dr. {rec.get('doctor_name', 'N/A')} | {format_datetime(rec.get('created_at',''))}")
                    with c2:
                        # Verify block
                        block_hash = rec.get("blockchain_hash", "")
                        matching = next((b for b in chain.chain if b.hash == block_hash), None)
                        if matching and matching.is_valid():
                            st.success("✅")
                        else:
                            st.error("⚠️")
        else:
            st.info("No records yet.")

    st.divider()

    # Downloadable files
    st.markdown("### 📂 Your Documents")
    if files:
        for f in files:
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"📎 {f['filename']}")
            with col2:
                st.caption(f"{f['file_type']} | {format_datetime(f.get('uploaded_at', ''))}")
            with col3:
                fp = f.get("filepath", "")
                if os.path.exists(fp):
                    with open(fp, "rb") as file_obj:
                        st.download_button(
                            "⬇️ Download",
                            data=file_obj.read(),
                            file_name=f["filename"],
                            key=f"pat_dl_{f['id']}",
                        )
    else:
        st.info("No documents uploaded yet.")

    st.divider()

    # Blockchain verification
    st.markdown("### ⛓️ Blockchain Verification")
    if st.button("🔍 Verify My Blockchain Records", use_container_width=True):
        with st.spinner("Verifying chain integrity..."):
            valid, issues = chain.validate()
            if valid:
                st.success(f"✅ Blockchain is valid! {chain.length()} total blocks, {len(patient_blocks)} are yours.")
            else:
                st.error("⚠️ Blockchain integrity issues detected!")
                for issue in issues:
                    st.warning(issue)
