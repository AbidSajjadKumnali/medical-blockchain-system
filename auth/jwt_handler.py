# auth/jwt_handler.py
"""
JWT token creation and verification for MedChain EMR System.
"""

import jwt
import os
from datetime import datetime, timezone, timedelta
from typing import Optional
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "insecure-fallback-key-change-me")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "8"))
ALGORITHM = "HS256"


def create_token(user_id: str, username: str, role: str) -> str:
    """
    Create a signed JWT token for an authenticated user.

    Args:
        user_id: Unique user ID
        username: Username
        role: User role (admin/doctor/patient)

    Returns:
        str: Signed JWT token
    """
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"JWT created for user: {username}")
    return token


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired.")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def get_user_from_token(token: str) -> Optional[dict]:
    """
    Extract user information from a valid JWT token.

    Returns:
        dict with keys: user_id, username, role — or None
    """
    payload = verify_token(token)
    if payload:
        return {
            "user_id": payload.get("sub"),
            "username": payload.get("username"),
            "role": payload.get("role"),
        }
    return None
