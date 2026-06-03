# database/migrations.py
"""
Database schema creation and migrations for MedChain EMR System.
Run once on startup to create all required tables.
"""

from .db import get_connection
from utils.logger import get_logger

logger = get_logger(__name__)

SCHEMA_SQL = """
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient')),
    is_active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    age INTEGER,
    blood_group TEXT,
    allergies TEXT DEFAULT '',
    emergency_contact TEXT DEFAULT '',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Medical records table
CREATE TABLE IF NOT EXISTS medical_records (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    diagnosis TEXT NOT NULL,
    prescription TEXT DEFAULT '',
    encrypted_data TEXT NOT NULL,
    blockchain_hash TEXT NOT NULL,
    record_type TEXT DEFAULT 'consultation',
    status TEXT DEFAULT 'active',
    created_at TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    details TEXT DEFAULT '',
    ip_address TEXT DEFAULT '127.0.0.1',
    timestamp TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- File records table
CREATE TABLE IF NOT EXISTS file_records (
    id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    file_type TEXT DEFAULT 'document',
    uploaded_at TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_medical_records_patient ON medical_records(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_records_doctor  ON medical_records(doctor_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user         ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp    ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_file_records_patient    ON file_records(patient_id);
"""


def run_migrations():
    """Execute schema creation SQL against the database."""
    try:
        conn = get_connection()
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        conn.close()
        logger.info("Database migrations applied successfully.")
    except Exception as e:
        logger.error(f"Migration error: {e}")
        raise
