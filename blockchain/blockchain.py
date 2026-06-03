# blockchain/blockchain.py
"""
Core blockchain logic for MedChain EMR System.
Manages the chain of medical record blocks with persistence.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List

from .block import Block
from .proof import proof_of_integrity
from .validator import validate_chain, detect_tampering
from utils.logger import get_logger
from utils.helpers import load_json, save_json

logger = get_logger(__name__)
BLOCKCHAIN_FILE = os.getenv("BLOCKCHAIN_PATH", "data/blockchain.json")


class MedChain:
    """
    MedChain blockchain for immutable medical record storage.

    Each medical record addition creates a new block linked
    cryptographically to all previous records.
    """

    def __init__(self, filepath: str = BLOCKCHAIN_FILE):
        self.filepath = filepath
        self.chain: List[Block] = []
        self._load_or_create()

    def _load_or_create(self):
        """Load existing chain from file or create genesis block."""
        data = load_json(self.filepath)
        if data and isinstance(data, list) and len(data) > 0:
            self.chain = [Block.from_dict(b) for b in data]
            logger.info(f"Loaded blockchain: {len(self.chain)} blocks.")
        else:
            logger.info("No existing chain found. Creating genesis block.")
            self._create_genesis_block()

    def _create_genesis_block(self):
        """Create and persist the genesis (first) block."""
        genesis = Block(
            index=0,
            timestamp=datetime.now(timezone.utc).isoformat(),
            encrypted_data="GENESIS_BLOCK",
            previous_hash="0" * 64,
            doctor_id="SYSTEM",
            patient_id="GENESIS",
            nonce=0
        )
        genesis.hash = genesis.calculate_hash()
        self.chain = [genesis]
        self._persist()
        logger.info(f"Genesis block created: {genesis.hash[:12]}...")

    def add_block(self, encrypted_data: str, doctor_id: str, patient_id: str) -> Block:
        """
        Add a new block to the chain.

        Args:
            encrypted_data: AES-encrypted medical record data
            doctor_id: ID of the doctor creating the record
            patient_id: ID of the patient

        Returns:
            Block: The newly created block
        """
        previous_block = self.chain[-1]
        timestamp = datetime.now(timezone.utc).isoformat()
        new_index = previous_block.index + 1

        nonce, valid_hash = proof_of_integrity(
            new_index, timestamp, encrypted_data, previous_block.hash
        )

        new_block = Block(
            index=new_index,
            timestamp=timestamp,
            encrypted_data=encrypted_data,
            previous_hash=previous_block.hash,
            doctor_id=doctor_id,
            patient_id=patient_id,
            nonce=nonce,
            hash=valid_hash
        )

        self.chain.append(new_block)
        self._persist()
        logger.info(f"Block {new_index} added. Hash: {valid_hash[:12]}...")
        return new_block

    def get_block(self, index: int) -> Optional[Block]:
        """Retrieve a block by index."""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None

    def get_patient_blocks(self, patient_id: str) -> List[Block]:
        """Retrieve all blocks for a specific patient."""
        return [b for b in self.chain if b.patient_id == patient_id]

    def validate(self) -> tuple[bool, list]:
        """Validate the entire chain."""
        return validate_chain(self.chain)

    def is_tampered(self) -> bool:
        """Quick check: is any block tampered?"""
        return len(detect_tampering(self.chain)) > 0

    def get_latest_hash(self) -> str:
        """Return the hash of the most recent block."""
        return self.chain[-1].hash if self.chain else "0" * 64

    def length(self) -> int:
        """Return chain length."""
        return len(self.chain)

    def to_list(self) -> List[dict]:
        """Export chain as list of dictionaries."""
        return [b.to_dict() for b in self.chain]

    def _persist(self):
        """Save chain to JSON file."""
        save_json(self.filepath, [b.to_dict() for b in self.chain])


# Singleton instance
_chain_instance: Optional[MedChain] = None


def get_blockchain() -> MedChain:
    """Get or create the singleton blockchain instance."""
    global _chain_instance
    if _chain_instance is None:
        _chain_instance = MedChain()
    return _chain_instance
