# auth/password_utils.py
"""
Password hashing and verification for MedChain EMR.
Uses bcrypt (preferred) with a fallback to PBKDF2-HMAC-SHA256 via cryptography lib.
"""

import os
import base64
import hashlib
from utils.logger import get_logger

logger = get_logger(__name__)

# Try to use bcrypt first; fall back to PBKDF2 if not installed
try:
    import bcrypt
    _USE_BCRYPT = True
    logger.debug("Using bcrypt for password hashing.")
except ImportError:
    _USE_BCRYPT = False
    logger.warning("bcrypt not available — using PBKDF2-HMAC-SHA256 fallback. "
                   "Install bcrypt for production use.")

_PBKDF2_ITERATIONS = 600_000
_PBKDF2_PREFIX = "pbkdf2$"


def hash_password(plain_password: str) -> str:
    """
    Hash a plain-text password.

    Uses bcrypt if available, otherwise PBKDF2-HMAC-SHA256.

    Args:
        plain_password: Raw password string

    Returns:
        str: Hashed password string
    """
    if _USE_BCRYPT:
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return hashed.decode("utf-8")
    else:
        # PBKDF2 fallback: format is "pbkdf2$<salt_hex>$<hash_hex>"
        salt = os.urandom(32)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            _PBKDF2_ITERATIONS
        )
        return f"{_PBKDF2_PREFIX}{salt.hex()}${dk.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain-text password against its hash.

    Args:
        plain_password: Raw password to check
        hashed_password: Stored hash (bcrypt or pbkdf2)

    Returns:
        bool: True if password matches
    """
    try:
        if hashed_password.startswith(_PBKDF2_PREFIX):
            # PBKDF2 verification
            _, salt_hex, hash_hex = hashed_password.split("$")
            salt = bytes.fromhex(salt_hex)
            stored_hash = bytes.fromhex(hash_hex)
            dk = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                salt,
                _PBKDF2_ITERATIONS
            )
            return dk == stored_hash
        elif _USE_BCRYPT:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        else:
            logger.error("Cannot verify bcrypt hash without bcrypt installed.")
            return False
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False
