# crypto/key_manager.py
"""
AES encryption key management for MedChain EMR System.
Keys are derived from environment variables for production security.
"""

import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv

load_dotenv()

# Salt for key derivation (in production, store securely)
_SALT = b'MedChain_Salt_2024'


def get_aes_key() -> bytes:
    """
    Derive a 32-byte AES key from the environment variable.

    Returns:
        bytes: 32-byte AES-256 key
    """
    raw_key = os.getenv("AES_KEY", "default-insecure-key-change-in-production!!")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_SALT,
        iterations=100_000,
        backend=default_backend()
    )
    return kdf.derive(raw_key.encode('utf-8'))


def get_secret_key() -> str:
    """Get JWT secret key from environment."""
    return os.getenv("SECRET_KEY", "fallback-insecure-secret-change-me")


def generate_random_key(length: int = 32) -> str:
    """Generate a cryptographically secure random key."""
    return base64.urlsafe_b64encode(os.urandom(length)).decode('utf-8')
