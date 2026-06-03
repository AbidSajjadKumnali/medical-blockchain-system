# crypto/decrypt.py
"""
AES-256-GCM decryption for sensitive patient data in MedChain EMR System.
"""

import base64
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .key_manager import get_aes_key
from utils.logger import get_logger

logger = get_logger(__name__)


def decrypt_data(encrypted_b64: str) -> str:
    """
    Decrypt AES-256-GCM encrypted data.

    Args:
        encrypted_b64: Base64-encoded encrypted data (nonce + ciphertext)

    Returns:
        str: Decrypted plaintext string
    """
    try:
        key = get_aes_key()
        aesgcm = AESGCM(key)
        combined = base64.urlsafe_b64decode(encrypted_b64.encode('utf-8'))
        nonce = combined[:12]
        ciphertext = combined[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        logger.debug("Data decrypted successfully.")
        return plaintext.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise RuntimeError("Decryption error. Data may be corrupted or key mismatch.") from e


def decrypt_dict(encrypted_b64: str) -> dict:
    """
    Decrypt and parse JSON dictionary.

    Args:
        encrypted_b64: Encrypted base64 string

    Returns:
        dict: Decrypted dictionary
    """
    raw = decrypt_data(encrypted_b64)
    return json.loads(raw)
