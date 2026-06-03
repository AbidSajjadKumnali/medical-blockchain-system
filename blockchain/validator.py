# blockchain/validator.py
"""
Blockchain validation and tamper detection for MedChain EMR.
"""

from typing import List
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_chain(chain: list) -> tuple[bool, list]:
    """
    Validate the entire blockchain for integrity.

    Checks:
    1. Each block's hash is correctly computed
    2. Each block's previous_hash matches the prior block's hash
    3. Genesis block is valid

    Args:
        chain: List of Block objects

    Returns:
        tuple: (is_valid: bool, issues: list of error strings)
    """
    issues = []

    if not chain:
        return True, []

    # Validate genesis block
    genesis = chain[0]
    if genesis.previous_hash != "0" * 64:
        issues.append(f"Block 0 (Genesis): Invalid previous_hash.")

    if not genesis.is_valid():
        issues.append(f"Block 0 (Genesis): Hash mismatch — possible tampering!")

    # Validate subsequent blocks
    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]

        # Check hash integrity of current block
        if not current.is_valid():
            issues.append(f"Block {i}: Hash mismatch — data may have been tampered!")

        # Check hash linkage
        if current.previous_hash != previous.hash:
            issues.append(f"Block {i}: previous_hash does not match Block {i-1}'s hash — chain broken!")

        # Check index continuity
        if current.index != previous.index + 1:
            issues.append(f"Block {i}: Index discontinuity (expected {previous.index + 1}, got {current.index}).")

    is_valid = len(issues) == 0
    if is_valid:
        logger.info(f"Blockchain validation passed. {len(chain)} blocks verified.")
    else:
        logger.warning(f"Blockchain validation FAILED. {len(issues)} issue(s) found.")

    return is_valid, issues


def detect_tampering(chain: list) -> list:
    """
    Detect and report which blocks have been tampered with.

    Returns:
        list: Indices of tampered blocks
    """
    tampered = []
    for i, block in enumerate(chain):
        if not block.is_valid():
            tampered.append(i)
            logger.warning(f"Tampering detected at Block {i}.")
    return tampered
