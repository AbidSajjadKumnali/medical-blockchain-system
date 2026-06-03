# crypto/hash_util.py
"""
Hashing utilities using SHA-256 for MedChain EMR System.
"""

import hashlib
import json
from typing import Any


def sha256(data: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def hash_dict(data: dict) -> str:
    """Compute SHA-256 hash of a dictionary (sorted keys for consistency)."""
    serialized = json.dumps(data, sort_keys=True, default=str)
    return sha256(serialized)


def hash_file(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except FileNotFoundError:
        return ""


def verify_hash(data: str, expected_hash: str) -> bool:
    """Verify that data matches an expected hash."""
    return sha256(data) == expected_hash


def compute_block_hash(index: int, timestamp: str, data: str,
                       previous_hash: str, nonce: int = 0) -> str:
    """
    Compute the hash for a blockchain block.

    Args:
        index: Block index
        timestamp: Block creation timestamp
        data: Encrypted block data
        previous_hash: Hash of the previous block
        nonce: Proof-of-work nonce

    Returns:
        str: SHA-256 hash of the block
    """
    block_string = f"{index}{timestamp}{data}{previous_hash}{nonce}"
    return sha256(block_string)
