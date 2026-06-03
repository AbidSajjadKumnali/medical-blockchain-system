# tests/test_blockchain.py
"""
Unit tests for MedChain blockchain logic.
"""

import sys
import os
import json
import tempfile
import unittest

# Ensure imports work from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain.block import Block
from blockchain.blockchain import MedChain
from blockchain.validator import validate_chain, detect_tampering
from blockchain.proof import proof_of_integrity, verify_proof
from crypto.hash_util import sha256, compute_block_hash


class TestBlock(unittest.TestCase):
    """Tests for the Block class."""

    def setUp(self):
        self.block = Block(
            index=1,
            timestamp="2024-01-01T00:00:00",
            encrypted_data="ENCRYPTED_PAYLOAD",
            previous_hash="0" * 64,
            doctor_id="doc_001",
            patient_id="pat_001",
        )

    def test_hash_computed_on_creation(self):
        self.assertIsNotNone(self.block.hash)
        self.assertEqual(len(self.block.hash), 64)

    def test_is_valid_true(self):
        self.assertTrue(self.block.is_valid())

    def test_tamper_detection(self):
        """Modifying block data should invalidate it."""
        self.block.encrypted_data = "TAMPERED_DATA"
        self.assertFalse(self.block.is_valid())

    def test_to_dict_and_from_dict(self):
        d = self.block.to_dict()
        restored = Block.from_dict(d)
        self.assertEqual(restored.hash, self.block.hash)
        self.assertEqual(restored.index, self.block.index)


class TestBlockchain(unittest.TestCase):
    """Tests for the MedChain blockchain."""

    def setUp(self):
        # Use a temp file for each test
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)  # Let MedChain create it fresh
        self.chain = MedChain(filepath=self.tmp.name)

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_genesis_block_created(self):
        self.assertEqual(len(self.chain.chain), 1)
        self.assertEqual(self.chain.chain[0].index, 0)
        self.assertEqual(self.chain.chain[0].previous_hash, "0" * 64)

    def test_add_block(self):
        block = self.chain.add_block("ENCRYPTED_DATA_1", "doc_1", "pat_1")
        self.assertEqual(block.index, 1)
        self.assertEqual(len(self.chain.chain), 2)

    def test_chain_linkage(self):
        self.chain.add_block("DATA_1", "doc_1", "pat_1")
        self.chain.add_block("DATA_2", "doc_1", "pat_2")
        b1 = self.chain.chain[1]
        b2 = self.chain.chain[2]
        self.assertEqual(b2.previous_hash, b1.hash)

    def test_validate_valid_chain(self):
        self.chain.add_block("DATA_A", "doc_1", "pat_1")
        valid, issues = self.chain.validate()
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)

    def test_validate_tampered_chain(self):
        self.chain.add_block("DATA_B", "doc_1", "pat_1")
        # Tamper with the second block's data
        self.chain.chain[1].encrypted_data = "TAMPERED"
        valid, issues = self.chain.validate()
        self.assertFalse(valid)
        self.assertGreater(len(issues), 0)

    def test_get_patient_blocks(self):
        self.chain.add_block("DATA_PAT1", "doc_1", "patient_alpha")
        self.chain.add_block("DATA_PAT2", "doc_1", "patient_beta")
        self.chain.add_block("DATA_PAT1_2", "doc_1", "patient_alpha")
        blocks = self.chain.get_patient_blocks("patient_alpha")
        self.assertEqual(len(blocks), 2)

    def test_persistence(self):
        """Chain should survive reload from file."""
        self.chain.add_block("PERSIST_DATA", "doc_1", "pat_1")
        original_len = self.chain.length()

        # Reload from file
        reloaded = MedChain(filepath=self.tmp.name)
        self.assertEqual(reloaded.length(), original_len)


class TestValidator(unittest.TestCase):
    """Tests for blockchain validator."""

    def _make_valid_chain(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        tmp.close()
        os.unlink(tmp.name)
        chain = MedChain(filepath=tmp.name)
        chain.add_block("D1", "doc", "pat1")
        chain.add_block("D2", "doc", "pat2")
        os.unlink(tmp.name)
        return chain

    def test_valid_chain_passes(self):
        chain = self._make_valid_chain()
        valid, issues = validate_chain(chain.chain)
        self.assertTrue(valid)

    def test_detect_no_tampering(self):
        chain = self._make_valid_chain()
        tampered = detect_tampering(chain.chain)
        self.assertEqual(len(tampered), 0)

    def test_detect_tampering_on_modified_block(self):
        chain = self._make_valid_chain()
        chain.chain[1].encrypted_data = "MODIFIED"
        tampered = detect_tampering(chain.chain)
        self.assertIn(1, tampered)


class TestHashUtil(unittest.TestCase):
    """Tests for hash utility functions."""

    def test_sha256_consistent(self):
        h1 = sha256("hello world")
        h2 = sha256("hello world")
        self.assertEqual(h1, h2)

    def test_sha256_different_inputs(self):
        self.assertNotEqual(sha256("abc"), sha256("xyz"))

    def test_sha256_length(self):
        self.assertEqual(len(sha256("test")), 64)

    def test_compute_block_hash_deterministic(self):
        h1 = compute_block_hash(1, "2024-01-01", "DATA", "PREV", 0)
        h2 = compute_block_hash(1, "2024-01-01", "DATA", "PREV", 0)
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
