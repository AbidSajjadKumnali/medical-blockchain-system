# blockchain/block.py
"""
Block data structure for the MedChain blockchain.
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime
from crypto.hash_util import compute_block_hash


@dataclass
class Block:
    """
    Represents a single block in the MedChain blockchain.

    Each block stores an encrypted medical record with cryptographic
    linkage to the previous block, ensuring tamper-evidence.
    """
    index: int
    timestamp: str
    encrypted_data: str
    previous_hash: str
    doctor_id: str
    patient_id: str
    nonce: int = 0
    hash: str = ""

    def __post_init__(self):
        """Compute hash after initialization if not provided."""
        if not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block contents."""
        return compute_block_hash(
            self.index,
            self.timestamp,
            self.encrypted_data,
            self.previous_hash,
            self.nonce
        )

    def to_dict(self) -> dict:
        """Serialize block to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Block":
        """Deserialize block from dictionary."""
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            encrypted_data=data["encrypted_data"],
            previous_hash=data["previous_hash"],
            doctor_id=data.get("doctor_id", "SYSTEM"),
            patient_id=data.get("patient_id", "GENESIS"),
            nonce=data.get("nonce", 0),
            hash=data.get("hash", "")
        )

    def is_valid(self) -> bool:
        """Verify block's hash integrity."""
        return self.hash == self.calculate_hash()

    def __repr__(self) -> str:
        return f"Block(index={self.index}, hash={self.hash[:12]}...)"
