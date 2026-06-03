# tests/test_auth.py
"""
Unit tests for authentication, JWT, and password utilities.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.password_utils import hash_password, verify_password
from auth.jwt_handler import create_token, verify_token, get_user_from_token
from auth.roles import has_permission, get_role_permissions
from utils.validators import (
    validate_username, validate_email,
    validate_password, sanitize_text, validate_age
)


class TestPasswordUtils(unittest.TestCase):
    """Tests for bcrypt password hashing."""

    def test_hash_is_not_plaintext(self):
        hashed = hash_password("Secret@123")
        self.assertNotEqual(hashed, "Secret@123")

    def test_verify_correct_password(self):
        hashed = hash_password("MyPass@999")
        self.assertTrue(verify_password("MyPass@999", hashed))

    def test_verify_wrong_password(self):
        hashed = hash_password("RightPass@1")
        self.assertFalse(verify_password("WrongPass@1", hashed))

    def test_different_hashes_same_password(self):
        """bcrypt should generate different salts each time."""
        h1 = hash_password("SamePass@1")
        h2 = hash_password("SamePass@1")
        self.assertNotEqual(h1, h2)


class TestJWTHandler(unittest.TestCase):
    """Tests for JWT token creation and verification."""

    def test_create_and_verify_token(self):
        token = create_token("user_123", "testuser", "doctor")
        payload = verify_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload["username"], "testuser")
        self.assertEqual(payload["role"], "doctor")

    def test_invalid_token_returns_none(self):
        result = verify_token("not.a.valid.token")
        self.assertIsNone(result)

    def test_get_user_from_token(self):
        token = create_token("uid_456", "drpatel", "admin")
        user = get_user_from_token(token)
        self.assertEqual(user["user_id"], "uid_456")
        self.assertEqual(user["username"], "drpatel")
        self.assertEqual(user["role"], "admin")

    def test_get_user_from_invalid_token(self):
        result = get_user_from_token("invalid")
        self.assertIsNone(result)


class TestRBAC(unittest.TestCase):
    """Tests for role-based access control."""

    def test_admin_can_manage_users(self):
        self.assertTrue(has_permission("admin", "manage_users"))

    def test_doctor_cannot_manage_users(self):
        self.assertFalse(has_permission("doctor", "manage_users"))

    def test_patient_cannot_delete_records(self):
        self.assertFalse(has_permission("patient", "delete_record"))

    def test_doctor_can_add_record(self):
        self.assertTrue(has_permission("doctor", "add_record"))

    def test_patient_can_view_own_records(self):
        self.assertTrue(has_permission("patient", "view_own_records"))

    def test_admin_has_all_permissions(self):
        perms = get_role_permissions("admin")
        self.assertIn("manage_users", perms)
        self.assertIn("delete_record", perms)
        self.assertIn("view_audit_logs", perms)

    def test_unknown_action_returns_false(self):
        self.assertFalse(has_permission("admin", "nonexistent_action"))


class TestValidators(unittest.TestCase):
    """Tests for input validation utilities."""

    def test_valid_username(self):
        ok, _ = validate_username("dr_smith99")
        self.assertTrue(ok)

    def test_short_username(self):
        ok, msg = validate_username("ab")
        self.assertFalse(ok)

    def test_invalid_username_chars(self):
        ok, _ = validate_username("user<script>")
        self.assertFalse(ok)

    def test_valid_email(self):
        ok, _ = validate_email("doctor@hospital.org")
        self.assertTrue(ok)

    def test_invalid_email(self):
        ok, _ = validate_email("not-an-email")
        self.assertFalse(ok)

    def test_strong_password(self):
        ok, _ = validate_password("SecurePass@9")
        self.assertTrue(ok)

    def test_weak_password_no_uppercase(self):
        ok, _ = validate_password("weakpass1")
        self.assertFalse(ok)

    def test_weak_password_too_short(self):
        ok, _ = validate_password("Ab1!")
        self.assertFalse(ok)

    def test_sanitize_removes_html(self):
        result = sanitize_text("<script>alert('xss')</script>Hello")
        self.assertNotIn("<script>", result)
        self.assertIn("Hello", result)

    def test_sanitize_removes_sql(self):
        result = sanitize_text("'; DROP TABLE users; --")
        self.assertNotIn("DROP", result)

    def test_valid_age(self):
        ok, _ = validate_age(25)
        self.assertTrue(ok)

    def test_invalid_age_negative(self):
        ok, _ = validate_age(-5)
        self.assertFalse(ok)

    def test_invalid_age_string(self):
        ok, _ = validate_age("not_a_number")
        self.assertFalse(ok)


if __name__ == "__main__":
    unittest.main(verbosity=2)
