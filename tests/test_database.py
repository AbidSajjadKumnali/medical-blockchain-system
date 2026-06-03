# tests/test_database.py
"""
Unit tests for database models and migrations.
"""

import sys
import os
import unittest
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Point to a temp DB for tests
_tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp_db.close()
os.environ["DB_PATH"] = _tmp_db.name

from database.migrations import run_migrations
from database.models import UserModel, PatientModel, MedicalRecordModel, AuditLogModel
from auth.password_utils import hash_password


class TestDatabaseModels(unittest.TestCase):
    """Integration tests for database models using a temp SQLite DB."""

    @classmethod
    def setUpClass(cls):
        run_migrations()
        # Create test users
        cls.admin_id = UserModel.create(
            "test_admin", "admin@test.com",
            hash_password("Admin@1234"), "admin"
        )
        cls.doctor_id = UserModel.create(
            "test_doctor", "doctor@test.com",
            hash_password("Doctor@1234"), "doctor"
        )
        cls.patient_user_id = UserModel.create(
            "test_patient", "patient@test.com",
            hash_password("Patient@1234"), "patient"
        )
        cls.patient_id = PatientModel.create(
            user_id=cls.patient_user_id,
            age=30,
            blood_group="B+",
            allergies="Aspirin",
            emergency_contact="+91-1234567890"
        )

    @classmethod
    def tearDownClass(cls):
        os.unlink(_tmp_db.name)

    # ── User Tests ──

    def test_create_user_returns_id(self):
        self.assertIsNotNone(self.admin_id)

    def test_get_user_by_username(self):
        user = UserModel.get_by_username("test_admin")
        self.assertIsNotNone(user)
        self.assertEqual(user["role"], "admin")

    def test_get_user_by_email(self):
        user = UserModel.get_by_email("doctor@test.com")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "test_doctor")

    def test_get_user_by_id(self):
        user = UserModel.get_by_id(self.admin_id)
        self.assertIsNotNone(user)

    def test_user_is_active_by_default(self):
        user = UserModel.get_by_username("test_admin")
        self.assertEqual(user["is_active"], 1)

    def test_set_user_inactive(self):
        UserModel.set_active(self.patient_user_id, False)
        user = UserModel.get_by_id(self.patient_user_id)
        self.assertEqual(user["is_active"], 0)
        # Restore
        UserModel.set_active(self.patient_user_id, True)

    def test_user_count(self):
        count = UserModel.count()
        self.assertGreaterEqual(count, 3)

    # ── Patient Tests ──

    def test_create_patient_returns_id(self):
        self.assertIsNotNone(self.patient_id)

    def test_get_patient_by_user_id(self):
        patient = PatientModel.get_by_user_id(self.patient_user_id)
        self.assertIsNotNone(patient)
        self.assertEqual(patient["blood_group"], "B+")

    def test_get_patient_by_id(self):
        patient = PatientModel.get_by_id(self.patient_id)
        self.assertIsNotNone(patient)
        self.assertEqual(patient["age"], 30)

    def test_get_all_patients_with_users(self):
        patients = PatientModel.get_all_with_users()
        self.assertGreaterEqual(len(patients), 1)
        self.assertIn("username", patients[0])

    def test_update_patient(self):
        success = PatientModel.update(
            self.patient_id, 31, "A+", "None", "+91-9876543210"
        )
        self.assertTrue(success)
        patient = PatientModel.get_by_id(self.patient_id)
        self.assertEqual(patient["age"], 31)
        self.assertEqual(patient["blood_group"], "A+")

    # ── Medical Record Tests ──

    def test_create_medical_record(self):
        record_id = MedicalRecordModel.create(
            patient_id=self.patient_id,
            doctor_id=self.doctor_id,
            diagnosis="Test Diagnosis",
            prescription="Test Prescription",
            encrypted_data="ENCRYPTED_TEST",
            blockchain_hash="a" * 64,
            record_type="consultation"
        )
        self.assertIsNotNone(record_id)

    def test_get_records_by_patient(self):
        records = MedicalRecordModel.get_by_patient(self.patient_id)
        self.assertGreaterEqual(len(records), 1)

    def test_update_record(self):
        records = MedicalRecordModel.get_by_patient(self.patient_id)
        if records:
            rid = records[0]["id"]
            ok = MedicalRecordModel.update(rid, "Updated Diagnosis", "Updated Rx")
            self.assertTrue(ok)

    def test_soft_delete_record(self):
        records = MedicalRecordModel.get_by_patient(self.patient_id)
        if records:
            rid = records[0]["id"]
            ok = MedicalRecordModel.delete(rid)
            self.assertTrue(ok)
            rec = MedicalRecordModel.get_by_id(rid)
            self.assertEqual(rec["status"], "deleted")

    # ── Audit Log Tests ──

    def test_create_audit_log(self):
        AuditLogModel.log(self.admin_id, "TEST_ACTION", "Test log entry")
        logs = AuditLogModel.get_all(limit=10)
        actions = [l["action"] for l in logs]
        self.assertIn("TEST_ACTION", actions)

    def test_get_logs_by_user(self):
        AuditLogModel.log(self.doctor_id, "DOCTOR_ACTION", "Doctor did something")
        logs = AuditLogModel.get_by_user(self.doctor_id)
        self.assertGreaterEqual(len(logs), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
