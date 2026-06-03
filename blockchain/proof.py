# blockchain/proof.py
"""
Proof-of-Integrity mechanism for MedChain blockchain.
Lightweight consensus mechanism suitable for medical EMR.
"""

from crypto.hash_util import compute_block_hash
from utils.logger import get_logger

logger = get_logger(__name__)

DIFFICULTY = 2  # Number of leading zeros required


def proof_of_integrity(index: int, timestamp: str, data: str,
                        previous_hash: str) -> tuple[int, str]:
    """
    Find a nonce such that the block hash starts with DIFFICULTY zeros.
    This is a lightweight proof mechanism for tamper-evident records.

    Args:
        index: Block index
        timestamp: Block timestamp
        data: Encrypted block data
        previous_hash: Hash of the previous block

    Returns:
        tuple: (nonce, valid_hash)
    """
    nonce = 0
    while True:
        candidate = compute_block_hash(index, timestamp, data, previous_hash, nonce)
        if candidate.startswith("0" * DIFFICULTY):
            logger.debug(f"Block {index}: Proof found. Nonce={nonce}, Hash={candidate[:12]}...")
            return nonce, candidate
        nonce += 1


def verify_proof(index: int, timestamp: str, data: str,
                  previous_hash: str, nonce: int, expected_hash: str) -> bool:
    """
    Verify that a block's proof-of-integrity is valid.

    Returns:
        bool: True if valid
    """
    computed = compute_block_hash(index, timestamp, data, previous_hash, nonce)
    valid = computed == expected_hash and computed.startswith("0" * DIFFICULTY)
    if not valid:
        logger.warning(f"Proof verification failed for block {index}.")
    return valid
