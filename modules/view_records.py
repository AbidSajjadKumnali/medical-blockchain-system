# modules/view_records.py
"""
View and search medical records with blockchain verification.
"""

import streamlit as st
import pandas as pd
from database.models import MedicalRecordModel, PatientModel
from crypto.decrypt import decrypt_dict
from blockchain.blockchain import get_blockchain
from utils.session_manager import get_current_user
from utils.helpers import format_datetime
from utils.constants import ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN


def render_view_records():
    """Render medical records viewer with search and filter."""
    st.markdown("## 📋 Medical Records")
    user = get_current_user()
    role = user["role"]
    user_id = user["user_id"]

    # Determine which records to show
    if role == ROLE_PATIENT:
        patient = PatientModel.get_by_user_id(user_id)
        if not patient:
            st.warning("Patient profile not found. Please complete your profile.")
            return
        records = MedicalRecordModel.get_by_patient(patient["id"])
        title_suffix = "Your Medical Records"
    else:
        # Doctor / Admin: let them search by patient
        patients = PatientModel.get_all_with_users()
        patient_options = {"-- All Patients --": None}
        patient_options.update({
            f"{p['username']} ({p['id'][:8]})": p["id"] for p in patients
        })

        col1, col2 = st.columns([3, 1])
        with col1:
            selected = st.selectbox("Filter by Patient", list(patient_options.keys()))
        with col2:
            record_type_filter = st.selectbox("Type", ["All", "consultation", "lab_report",
                                                         "prescription", "radiology", "surgery",
                                                         "vaccination", "follow_up"])

        selected_patient_id = patient_options[selected]
        if selected_patient_id:
            records = MedicalRecordModel.get_by_patient(selected_patient_id)
        else:
            records = MedicalRecordModel.get_all()

        if record_type_filter != "All":
            records = [r for r in records if r.get("record_type") == record_type_filter]
        title_suffix = f"{len(records)} Records"

    # Search
    search = st.text_input("🔍 Search records (diagnosis, doctor)", "")
    if search:
        records = [r for r in records if
                   search.lower() in r.get("diagnosis", "").lower() or
                   search.lower() in r.get("doctor_name", "").lower()]

    st.markdown(f"**{title_suffix}** — {len(records)} found")
    st.divider()

    if not records:
        st.info("No records found.")
        return

    for rec in records:
        _render_record_card(rec, role)


def _render_record_card(rec: dict, role: str):
    """Render a single medical record card."""
    record_type_icons = {
        "consultation": "🩺",
        "lab_report": "🧪",
        "prescription": "💊",
        "radiology": "🔬",
        "surgery": "⚕️",
        "vaccination": "💉",
        "follow_up": "📅",
    }
    icon = record_type_icons.get(rec.get("record_type", ""), "📄")

    with st.expander(
        f"{icon} {rec.get('record_type', 'Record').title()} — "
        f"Dr. {rec.get('doctor_name', 'Unknown')} | "
        f"{format_datetime(rec.get('created_at', ''))}"
    ):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("**Diagnosis:**")
            st.write(rec.get("diagnosis", "N/A"))
            st.markdown("**Prescription:**")
            st.write(rec.get("prescription", "N/A") or "None prescribed")

        with col2:
            st.markdown("**Blockchain Verification**")
            _verify_record_block(rec)

        # FIX: Replaced nested st.expander with st.toggle to avoid
        # "Expanders may not be nested inside other expanders" error.
        if role in [ROLE_DOCTOR, ROLE_ADMIN]:
            show_details = st.toggle(
                "🔓 View Encrypted Details",
                key=f"toggle_{rec['id']}"  # unique key per record to avoid duplicate widget errors
            )
            if show_details:
                try:
                    decrypted = decrypt_dict(rec["encrypted_data"])
                    vitals = decrypted.get("vitals", {})
                    if any(vitals.values()):
                        st.markdown("**Vitals:**")
                        vcol1, vcol2 = st.columns(2)
                        with vcol1:
                            if vitals.get("blood_pressure"):
                                st.metric("Blood Pressure", vitals["blood_pressure"])
                            if vitals.get("temperature"):
                                st.metric("Temperature", vitals["temperature"])
                        with vcol2:
                            if vitals.get("pulse_rate"):
                                st.metric("Pulse Rate", vitals["pulse_rate"])
                            if vitals.get("weight"):
                                st.metric("Weight", vitals["weight"])
                    if decrypted.get("notes"):
                        st.markdown("**Clinical Notes:**")
                        st.write(decrypted["notes"])
                except Exception:
                    st.warning("Unable to decrypt record details.")

        st.caption(f"Record ID: {rec['id'][:8]}... | Hash: {rec.get('blockchain_hash', 'N/A')[:20]}...")


def _verify_record_block(rec: dict):
    """Show blockchain verification status for a record."""
    chain = get_blockchain()
    block_hash = rec.get("blockchain_hash", "")

    # Find matching block
    matching_block = next(
        (b for b in chain.chain if b.hash == block_hash), None
    )

    if matching_block and matching_block.is_valid():
        st.success("✅ Verified")
        st.caption(f"Block #{matching_block.index}")
    elif matching_block:
        st.error("⚠️ Tampered!")
        st.caption(f"Block #{matching_block.index} — INVALID")
    else:
        st.warning("❓ Not found in chain")