# tests/test_crypto.py
"""
Unit tests for encryption, decryption, and hashing utilities.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test AES key
os.environ["AES_KEY"] = "TestAESKey_ForUnitTests_32chars!!"

from crypto.encrypt import encrypt_data, encrypt_dict
from crypto.decrypt import decrypt_data, decrypt_dict
from crypto.hash_util import (
    sha256, hash_dict, verify_hash,
    compute_block_hash, hash_file
)


class TestEncryptDecrypt(unittest.TestCase):
    """Tests for AES-256-GCM encryption and decryption."""

    def test_encrypt_returns_string(self):
        result = encrypt_data("hello world")
        self.assertIsInstance(result, str)
        self.assertNotEqual(result, "hello world")

    def test_decrypt_roundtrip(self):
        original = "Sensitive Patient Data 12345"
        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, original)

    def test_encrypt_produces_different_output_each_time(self):
        """AES-GCM uses random nonce — ciphertext must differ."""
        e1 = encrypt_data("same data")
        e2 = encrypt_data("same data")
        self.assertNotEqual(e1, e2)

    def test_decrypt_both_ciphertexts_give_same_plaintext(self):
        plain = "same data"
        e1 = encrypt_data(plain)
        e2 = encrypt_data(plain)
        self.assertEqual(decrypt_data(e1), decrypt_data(e2))

    def test_encrypt_dict_roundtrip(self):
        data = {
            "diagnosis": "Hypertension",
            "prescription": "Amlodipine 5mg",
            "vitals": {"bp": "140/90", "pulse": "80"}
        }
        encrypted = encrypt_dict(data)
        decrypted = decrypt_dict(encrypted)
        self.assertEqual(decrypted["diagnosis"], "Hypertension")
        self.assertEqual(decrypted["vitals"]["bp"], "140/90")

    def test_tampered_ciphertext_raises_error(self):
        encrypted = encrypt_data("test data")
        # Corrupt the middle of the ciphertext
        corrupted = encrypted[:10] + "XXXXXXXXXXXX" + encrypted[22:]
        with self.assertRaises(Exception):
            decrypt_data(corrupted)

    def test_empty_string_encrypt_decrypt(self):
        encrypted = encrypt_data("")
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, "")

    def test_long_text_roundtrip(self):
        long_text = "Medical diagnosis. " * 500
        encrypted = encrypt_data(long_text)
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, long_text)

    def test_unicode_data_roundtrip(self):
        unicode_text = "Patient: José García — Diagnóstico: Fiebre alta 🤒"
        encrypted = encrypt_data(unicode_text)
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, unicode_text)


class TestHashUtil(unittest.TestCase):
    """Tests for SHA-256 hashing utilities."""

    def test_sha256_known_value(self):
        # sha256("abc") is well-known
        result = sha256("abc")
        self.assertEqual(result, "ba7816bf8f01cfea414140de5dae2ec73b00361bbef0469fa72a444b7fe9f8f8")[:len(result)]
        self.assertEqual(len(result), 64)

    def test_sha256_consistency(self):
        self.assertEqual(sha256("test"), sha256("test"))

    def test_sha256_avalanche(self):
        """One-bit change should produce completely different hash."""
        h1 = sha256("medchain1")
        h2 = sha256("medchain2")
        self.assertNotEqual(h1, h2)

    def test_hash_dict_sorted_keys(self):
        """Dict hash must be deterministic regardless of key order."""
        d1 = {"b": 2, "a": 1}
        d2 = {"a": 1, "b": 2}
        self.assertEqual(hash_dict(d1), hash_dict(d2))

    def test_hash_dict_different_values(self):
        d1 = {"key": "value1"}
        d2 = {"key": "value2"}
        self.assertNotEqual(hash_dict(d1), hash_dict(d2))

    def test_verify_hash_true(self):
        data = "verify me"
        h = sha256(data)
        self.assertTrue(verify_hash(data, h))

    def test_verify_hash_false(self):
        self.assertFalse(verify_hash("data", sha256("other data")))

    def test_compute_block_hash_deterministic(self):
        h1 = compute_block_hash(5, "2024-06-01", "DATA", "PREV_HASH", 42)
        h2 = compute_block_hash(5, "2024-06-01", "DATA", "PREV_HASH", 42)
        self.assertEqual(h1, h2)

    def test_compute_block_hash_nonce_changes_result(self):
        h1 = compute_block_hash(1, "ts", "data", "prev", 0)
        h2 = compute_block_hash(1, "ts", "data", "prev", 1)
        self.assertNotEqual(h1, h2)

    def test_hash_file_nonexistent(self):
        result = hash_file("/nonexistent/path/file.txt")
        self.assertEqual(result, "")

    def test_hash_file_real_file(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test file content")
            fname = f.name
        result = hash_file(fname)
        self.assertEqual(len(result), 64)
        os.unlink(fname)


if __name__ == "__main__":
    unittest.main(verbosity=2)
