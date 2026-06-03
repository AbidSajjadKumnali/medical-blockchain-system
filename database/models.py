# database/models.py
"""
Database model operations for MedChain EMR System.
All queries are parameterized to prevent SQL injection.
"""

from datetime import datetime, timezone
from typing import Optional, List
from .db import execute_query, fetch_one, fetch_all
from utils.helpers import generate_id, current_timestamp
from utils.logger import get_logger

logger = get_logger(__name__)


# ─────────────────────────── USERS ───────────────────────────

class UserModel:
    """User CRUD operations."""

    @staticmethod
    def create(username: str, email: str, password_hash: str, role: str) -> Optional[str]:
        user_id = generate_id()
        result = execute_query(
            "INSERT INTO users (id, username, email, password_hash, role, created_at, is_active) VALUES (?,?,?,?,?,?,?)",
            (user_id, username, email, password_hash, role, current_timestamp(), 1)
        )
        return user_id if result else None

    @staticmethod
    def get_by_username(username: str) -> Optional[dict]:
        return fetch_one("SELECT * FROM users WHERE username = ?", (username,))

    @staticmethod
    def get_by_id(user_id: str) -> Optional[dict]:
        return fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))

    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        return fetch_one("SELECT * FROM users WHERE email = ?", (email,))

    @staticmethod
    def get_all() -> List[dict]:
        return fetch_all("SELECT id, username, email, role, created_at, is_active FROM users ORDER BY created_at DESC")

    @staticmethod
    def set_active(user_id: str, active: bool) -> bool:
        result = execute_query("UPDATE users SET is_active = ? WHERE id = ?", (int(active), user_id))
        return result is not None

    @staticmethod
    def count() -> int:
        row = fetch_one("SELECT COUNT(*) as cnt FROM users")
        return row["cnt"] if row else 0


# ─────────────────────────── PATIENTS ───────────────────────────

class PatientModel:
    """Patient profile CRUD operations."""

    @staticmethod
    def create(user_id: str, age: int, blood_group: str,
               allergies: str, emergency_contact: str) -> Optional[str]:
        patient_id = generate_id()
        result = execute_query(
            "INSERT INTO patients (id, user_id, age, blood_group, allergies, emergency_contact) VALUES (?,?,?,?,?,?)",
            (patient_id, user_id, age, blood_group, allergies, emergency_contact)
        )
        return patient_id if result else None

    @staticmethod
    def get_by_user_id(user_id: str) -> Optional[dict]:
        return fetch_one("SELECT * FROM patients WHERE user_id = ?", (user_id,))

    @staticmethod
    def get_by_id(patient_id: str) -> Optional[dict]:
        return fetch_one("SELECT * FROM patients WHERE id = ?", (patient_id,))

    @staticmethod
    def get_all_with_users() -> List[dict]:
        return fetch_all("""
            SELECT p.*, u.username, u.email, u.is_active
            FROM patients p JOIN users u ON p.user_id = u.id
            ORDER BY u.username
        """)

    @staticmethod
    def update(patient_id: str, age: int, blood_group: str,
               allergies: str, emergency_contact: str) -> bool:
        result = execute_query(
            "UPDATE patients SET age=?, blood_group=?, allergies=?, emergency_contact=? WHERE id=?",
            (age, blood_group, allergies, emergency_contact, patient_id)
        )
        return result is not None

    @staticmethod
    def count() -> int:
        row = fetch_one("SELECT COUNT(*) as cnt FROM patients")
        return row["cnt"] if row else 0


# ─────────────────────────── MEDICAL RECORDS ───────────────────────────

class MedicalRecordModel:
    """Medical record CRUD operations."""

    @staticmethod
    def create(patient_id: str, doctor_id: str, diagnosis: str,
               prescription: str, encrypted_data: str,
               blockchain_hash: str, record_type: str = "consultation") -> Optional[str]:
        record_id = generate_id()
        result = execute_query(
            """INSERT INTO medical_records
               (id, patient_id, doctor_id, diagnosis, prescription, encrypted_data,
                blockchain_hash, record_type, created_at, status)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (record_id, patient_id, doctor_id, diagnosis, prescription,
             encrypted_data, blockchain_hash, record_type, current_timestamp(), "active")
        )
        return record_id if result else None

    @staticmethod
    def get_by_patient(patient_id: str) -> List[dict]:
        return fetch_all("""
            SELECT mr.*, u.username as doctor_name
            FROM medical_records mr
            LEFT JOIN users u ON mr.doctor_id = u.id
            WHERE mr.patient_id = ?
            ORDER BY mr.created_at DESC
        """, (patient_id,))

    @staticmethod
    def get_by_id(record_id: str) -> Optional[dict]:
        return fetch_one("SELECT * FROM medical_records WHERE id = ?", (record_id,))

    @staticmethod
    def get_all() -> List[dict]:
        return fetch_all("""
            SELECT mr.*, u.username as doctor_name, p.id as pat_id,
                   up.username as patient_name
            FROM medical_records mr
            LEFT JOIN users u ON mr.doctor_id = u.id
            LEFT JOIN patients p ON mr.patient_id = p.id
            LEFT JOIN users up ON p.user_id = up.id
            ORDER BY mr.created_at DESC
        """)

    @staticmethod
    def update(record_id: str, diagnosis: str, prescription: str) -> bool:
        result = execute_query(
            "UPDATE medical_records SET diagnosis=?, prescription=? WHERE id=?",
            (diagnosis, prescription, record_id)
        )
        return result is not None

    @staticmethod
    def delete(record_id: str) -> bool:
        result = execute_query(
            "UPDATE medical_records SET status='deleted' WHERE id=?",
            (record_id,)
        )
        return result is not None

    @staticmethod
    def count() -> int:
        row = fetch_one("SELECT COUNT(*) as cnt FROM medical_records WHERE status='active'")
        return row["cnt"] if row else 0

    @staticmethod
    def count_by_type() -> List[dict]:
        return fetch_all("""
            SELECT record_type, COUNT(*) as count
            FROM medical_records WHERE status='active'
            GROUP BY record_type
        """)


# ─────────────────────────── AUDIT LOGS ───────────────────────────

class AuditLogModel:
    """Audit log write/read operations."""

    @staticmethod
    def log(user_id: str, action: str, details: str = "", ip_address: str = "127.0.0.1"):
        log_id = generate_id()
        execute_query(
            "INSERT INTO audit_logs (id, user_id, action, details, ip_address, timestamp) VALUES (?,?,?,?,?,?)",
            (log_id, user_id, action, details, ip_address, current_timestamp())
        )

    @staticmethod
    def get_all(limit: int = 100) -> List[dict]:
        return fetch_all("""
            SELECT al.*, u.username
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            ORDER BY al.timestamp DESC
            LIMIT ?
        """, (limit,))

    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> List[dict]:
        return fetch_all("""
            SELECT * FROM audit_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC LIMIT ?
        """, (user_id, limit))


# ─────────────────────────── FILE RECORDS ───────────────────────────

class FileRecordModel:
    """Uploaded file record operations."""

    @staticmethod
    def create(patient_id: str, doctor_id: str, filename: str,
               filepath: str, file_type: str) -> Optional[str]:
        file_id = generate_id()
        result = execute_query(
            """INSERT INTO file_records (id, patient_id, doctor_id, filename, filepath, file_type, uploaded_at)
               VALUES (?,?,?,?,?,?,?)""",
            (file_id, patient_id, doctor_id, filename, filepath, file_type, current_timestamp())
        )
        return file_id if result else None

    @staticmethod
    def get_by_patient(patient_id: str) -> List[dict]:
        return fetch_all("""
            SELECT fr.*, u.username as doctor_name
            FROM file_records fr
            LEFT JOIN users u ON fr.doctor_id = u.id
            WHERE fr.patient_id = ?
            ORDER BY fr.uploaded_at DESC
        """, (patient_id,))
