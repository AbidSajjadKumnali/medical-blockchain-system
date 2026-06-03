# crypto/encrypt.py
"""
AES-256-GCM encryption for sensitive patient data in MedChain EMR System.
"""

import os
import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .key_manager import get_aes_key
from utils.logger import get_logger

logger = get_logger(__name__)


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt plaintext using AES-256-GCM.

    Args:
        plaintext: The string data to encrypt

    Returns:
        str: Base64-encoded encrypted data (nonce + ciphertext)
    """
    try:
        key = get_aes_key()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        # Combine nonce + ciphertext and base64 encode
        combined = nonce + ciphertext
        encoded = base64.urlsafe_b64encode(combined).decode('utf-8')
        logger.debug("Data encrypted successfully.")
        return encoded
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise RuntimeError("Encryption error") from e


def encrypt_dict(data: dict) -> str:
    """
    Encrypt a dictionary as JSON string.

    Args:
        data: Dictionary to encrypt

    Returns:
        str: Encrypted base64 string
    """
    return encrypt_data(json.dumps(data, default=str))
