# utils/validators.py
"""
Input validation utilities for MedChain EMR System.
Prevents injection attacks and ensures data integrity.
"""

import re
from typing import Optional


def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format."""
    if not username or len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if len(username) > 50:
        return False, "Username must be 50 characters or fewer."
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, dots, hyphens."
    return True, "OK"


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(pattern, email):
        return False, "Invalid email address format."
    return True, "OK"


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    return True, "OK"


def sanitize_text(text: str) -> str:
    """
    Sanitize text input to prevent XSS/injection.
    Strips dangerous characters while preserving medical text.
    """
    if not text:
        return ""
    # Remove script tags and HTML
    text = re.sub(r'<[^>]+>', '', text)
    # Remove SQL injection patterns
    text = re.sub(r"(--|;|DROP|SELECT|INSERT|UPDATE|DELETE|'|\"|\\)", '', text, flags=re.IGNORECASE)
    return text.strip()


def validate_age(age) -> tuple[bool, str]:
    """Validate patient age."""
    try:
        age_int = int(age)
        if age_int < 0 or age_int > 150:
            return False, "Age must be between 0 and 150."
        return True, "OK"
    except (ValueError, TypeError):
        return False, "Age must be a valid number."


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate phone number."""
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)
    if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
        return False, "Invalid phone number format."
    return True, "OK"


def validate_file_extension(filename: str, allowed: list) -> tuple[bool, str]:
    """Validate uploaded file extension."""
    ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in allowed:
        return False, f"File type not allowed. Permitted: {', '.join(allowed)}"
    return True, "OK"
