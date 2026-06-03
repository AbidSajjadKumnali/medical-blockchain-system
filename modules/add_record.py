# modules/add_record.py
"""
Add medical record module — creates DB entry + blockchain block.
"""

import streamlit as st
from database.models import MedicalRecordModel, PatientModel, UserModel, AuditLogModel
from blockchain.blockchain import get_blockchain
from crypto.encrypt import encrypt_dict
from utils.validators import sanitize_text
from utils.session_manager import get_current_user
from utils.constants import ACTION_ADD_RECORD
from utils.helpers import current_timestamp


def render_add_record():
    """Render the Add Medical Record form for doctors."""
    st.markdown("## 🩺 Add Medical Record")
    st.markdown("Fill in the patient's medical details. All data is encrypted and stored on the blockchain.")
    st.divider()

    user = get_current_user()
    doctor_id = user["user_id"]

    # Fetch all patients
    patients = PatientModel.get_all_with_users()
    if not patients:
        st.warning("No patients found. Ask patients to register first.")
        return

    patient_options = {f"{p['username']} (ID: {p['id'][:8]}...)": p["id"] for p in patients}

    with st.form("add_record_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            selected_label = st.selectbox("Select Patient *", list(patient_options.keys()))
            record_type = st.selectbox("Record Type *", [
                "consultation", "lab_report", "prescription",
                "radiology", "surgery", "vaccination", "follow_up"
            ])

        with col2:
            patient_id = patient_options[selected_label]
            # Show selected patient info
            selected_patient = next((p for p in patients if p["id"] == patient_id), None)
            if selected_patient:
                st.info(f"""
                **Patient:** {selected_patient['username']}
                **Age:** {selected_patient.get('age', 'N/A')}
                **Blood Group:** {selected_patient.get('blood_group', 'N/A')}
                **Allergies:** {selected_patient.get('allergies', 'None')}
                """)

        diagnosis = st.text_area("Diagnosis *", height=100,
                                  placeholder="Describe the diagnosis in detail...")
        prescription = st.text_area("Prescription / Treatment Plan", height=100,
                                     placeholder="Medications, dosage, treatment instructions...")
        notes = st.text_area("Clinical Notes", height=80,
                              placeholder="Additional clinical observations...")

        col3, col4 = st.columns(2)
        with col3:
            vitals_bp = st.text_input("Blood Pressure", placeholder="e.g. 120/80 mmHg")
            vitals_temp = st.text_input("Temperature", placeholder="e.g. 98.6°F")
        with col4:
            vitals_pulse = st.text_input("Pulse Rate", placeholder="e.g. 72 bpm")
            vitals_weight = st.text_input("Weight", placeholder="e.g. 70 kg")

        submitted = st.form_submit_button("🔒 Save & Add to Blockchain", type="primary", use_container_width=True)

        if submitted:
            if not diagnosis.strip():
                st.error("Diagnosis is required.")
                return

            diagnosis = sanitize_text(diagnosis)
            prescription = sanitize_text(prescription)
            notes = sanitize_text(notes)

            # Prepare data for encryption + blockchain
            record_payload = {
                "diagnosis": diagnosis,
                "prescription": prescription,
                "notes": notes,
                "vitals": {
                    "blood_pressure": vitals_bp,
                    "temperature": vitals_temp,
                    "pulse_rate": vitals_pulse,
                    "weight": vitals_weight,
                },
                "record_type": record_type,
                "doctor_id": doctor_id,
                "patient_id": patient_id,
                "timestamp": current_timestamp(),
            }

            with st.spinner("🔐 Encrypting data and writing to blockchain..."):
                try:
                    # Encrypt sensitive data
                    encrypted_data = encrypt_dict(record_payload)

                    # Add to blockchain
                    chain = get_blockchain()
                    block = chain.add_block(encrypted_data, doctor_id, patient_id)

                    # Save to database
                    record_id = MedicalRecordModel.create(
                        patient_id=patient_id,
                        doctor_id=doctor_id,
                        diagnosis=diagnosis,
                        prescription=prescription,
                        encrypted_data=encrypted_data,
                        blockchain_hash=block.hash,
                        record_type=record_type,
                    )

                    if record_id:
                        AuditLogModel.log(
                            doctor_id, ACTION_ADD_RECORD,
                            f"Record {record_id[:8]} added for patient {patient_id[:8]}"
                        )
                        st.success(f"✅ Medical record added successfully!")
                        st.code(f"Blockchain Hash: {block.hash}", language="text")
                        st.info(f"Block Index: #{block.index} | Record ID: {record_id[:8]}...")
                    else:
                        st.error("Failed to save record to database.")
                except Exception as e:
                    st.error(f"Error creating record: {str(e)}")
