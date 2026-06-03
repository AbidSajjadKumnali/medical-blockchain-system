# modules/upload_reports.py
"""
File upload module for medical reports, prescriptions, and documents.
"""

import streamlit as st
import os
from pathlib import Path
from database.models import PatientModel, FileRecordModel, AuditLogModel
from utils.session_manager import get_current_user
from utils.validators import validate_file_extension
from utils.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB, ACTION_UPLOAD_FILE
from utils.helpers import generate_id, current_timestamp, format_datetime
from crypto.hash_util import hash_file

UPLOADS_DIR = os.getenv("UPLOADS_PATH", "data/uploads")


def render_upload_reports():
    """Render the file upload interface for medical reports."""
    st.markdown("## 📤 Upload Medical Reports")
    st.markdown("Upload prescriptions, lab reports, imaging, and other medical documents.")
    st.divider()

    user = get_current_user()
    doctor_id = user["user_id"]

    patients = PatientModel.get_all_with_users()
    if not patients:
        st.warning("No patients registered.")
        return

    patient_opts = {f"{p['username']} ({p['id'][:8]})": p["id"] for p in patients}

    col1, col2 = st.columns(2)
    with col1:
        selected = st.selectbox("Select Patient *", list(patient_opts.keys()))
        patient_id = patient_opts[selected]
    with col2:
        file_type = st.selectbox("Document Type *", [
            "lab_report", "prescription", "radiology",
            "discharge_summary", "consent_form", "other"
        ])

    uploaded_file = st.file_uploader(
        "Choose file",
        type=["pdf", "jpg", "jpeg", "png", "txt"],
        help=f"Max {MAX_FILE_SIZE_MB}MB. Allowed: PDF, JPG, PNG, TXT"
    )

    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"File too large: {file_size_mb:.1f}MB (max {MAX_FILE_SIZE_MB}MB).")
            return

        ok, msg = validate_file_extension(uploaded_file.name, ALLOWED_EXTENSIONS)
        if not ok:
            st.error(msg)
            return

        st.success(f"📄 Ready to upload: **{uploaded_file.name}** ({file_size_mb:.2f} MB)")

        if st.button("🔒 Upload & Secure", type="primary", use_container_width=True):
            with st.spinner("Saving file..."):
                try:
                    # Save file to disk
                    Path(UPLOADS_DIR).mkdir(parents=True, exist_ok=True)
                    unique_name = f"{generate_id()[:8]}_{uploaded_file.name}"
                    save_path = os.path.join(UPLOADS_DIR, unique_name)

                    with open(save_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    file_hash = hash_file(save_path)

                    # Record in database
                    file_id = FileRecordModel.create(
                        patient_id=patient_id,
                        doctor_id=doctor_id,
                        filename=uploaded_file.name,
                        filepath=save_path,
                        file_type=file_type,
                    )

                    AuditLogModel.log(
                        doctor_id, ACTION_UPLOAD_FILE,
                        f"Uploaded {uploaded_file.name} for patient {patient_id[:8]}"
                    )

                    st.success(f"✅ File uploaded successfully!")
                    st.code(f"File Hash (SHA-256): {file_hash}", language="text")
                    st.caption(f"Stored as: {unique_name}")

                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")

    st.divider()

    # Show existing files for selected patient
    st.markdown("### 📁 Uploaded Files for Patient")
    files = FileRecordModel.get_by_patient(patient_id)
    if not files:
        st.info("No files uploaded yet.")
        return

    for f in files:
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"📎 {f['filename']}")
        with col2:
            st.caption(f"{f['file_type']} | {format_datetime(f['uploaded_at'])}")
        with col3:
            # Download button
            file_path = f.get("filepath", "")
            if os.path.exists(file_path):
                with open(file_path, "rb") as fp:
                    st.download_button(
                        "⬇️",
                        data=fp.read(),
                        file_name=f["filename"],
                        key=f"dl_{f['id']}",
                    )
            else:
                st.caption("Missing")
