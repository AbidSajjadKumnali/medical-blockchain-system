# auth/auth.py
"""
Authentication logic: login, registration, logout for MedChain EMR.
"""

from typing import Optional, Tuple
from database.models import UserModel, PatientModel, AuditLogModel
from .password_utils import hash_password, verify_password
from .jwt_handler import create_token
from utils.validators import validate_username, validate_email, validate_password, validate_age
from utils.logger import get_logger
from utils.constants import ROLE_PATIENT, BLOOD_GROUPS, ACTION_LOGIN, ACTION_LOGOUT, ACTION_REGISTER

logger = get_logger(__name__)


def login_user(username: str, password: str, ip: str = "127.0.0.1") -> tuple[bool, str, Optional[dict]]:
    """
    Authenticate a user by username and password.

    Returns:
        tuple: (success, message, user_data)
            user_data includes: user_id, username, role, token
    """
    if not username or not password:
        return False, "Username and password are required.", None

    user = UserModel.get_by_username(username.strip())

    if not user:
        logger.warning(f"Login attempt for unknown user: {username}")
        return False, "Invalid username or password.", None

    if not user.get("is_active", 1):
        return False, "Your account has been deactivated. Contact admin.", None

    if not verify_password(password, user["password_hash"]):
        logger.warning(f"Failed login attempt for user: {username}")
        AuditLogModel.log(user["id"], "FAILED_LOGIN", f"Failed password attempt", ip)
        return False, "Invalid username or password.", None

    token = create_token(user["id"], user["username"], user["role"])
    AuditLogModel.log(user["id"], ACTION_LOGIN, "Successful login", ip)
    logger.info(f"User '{username}' logged in successfully.")

    return True, "Login successful.", {
        "user_id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "token": token,
    }


def register_user(
    username: str, email: str, password: str, confirm_password: str,
    role: str = ROLE_PATIENT,
    age: int = 0, blood_group: str = "O+",
    allergies: str = "", emergency_contact: str = ""
) -> tuple[bool, str]:
    """
    Register a new user with optional patient profile creation.

    Returns:
        tuple: (success, message)
    """
    # Validate inputs
    ok, msg = validate_username(username)
    if not ok:
        return False, msg

    ok, msg = validate_email(email)
    if not ok:
        return False, msg

    ok, msg = validate_password(password)
    if not ok:
        return False, msg

    if password != confirm_password:
        return False, "Passwords do not match."

    if UserModel.get_by_username(username):
        return False, "Username already taken."

    if UserModel.get_by_email(email):
        return False, "Email already registered."

    # Create user
    pw_hash = hash_password(password)
    user_id = UserModel.create(username, email, pw_hash, role)

    if not user_id:
        return False, "Registration failed. Please try again."

    # Create patient profile if role is patient
    if role == ROLE_PATIENT:
        if age:
            ok, msg = validate_age(age)
            if not ok:
                return False, msg
        PatientModel.create(user_id, age or 0, blood_group, allergies, emergency_contact)

    AuditLogModel.log(user_id, ACTION_REGISTER, f"New {role} account created")
    logger.info(f"New user registered: {username} ({role})")
    return True, f"Account created successfully! You can now log in."


def logout_user(user_id: str, username: str):
    """Log the logout action."""
    AuditLogModel.log(user_id, ACTION_LOGOUT, "User logged out")
    logger.info(f"User '{username}' logged out.")
