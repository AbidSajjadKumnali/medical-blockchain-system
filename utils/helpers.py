# utils/helpers.py
"""
Common helper utilities for MedChain EMR System.
"""

import hashlib
import uuid
from datetime import datetime
from pathlib import Path
import json
import os


def generate_id() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


def current_timestamp() -> str:
    """Return ISO format timestamp."""
    return datetime.utcnow().isoformat()


def format_datetime(dt_str: str) -> str:
    """Format ISO datetime string for display."""
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d %b %Y, %H:%M")
    except Exception:
        return dt_str


def sha256_hash(data: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(data.encode()).hexdigest()


def ensure_dirs():
    """Ensure all required data directories exist."""
    dirs = [
        "data", "data/uploads", "data/logs", "static"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def load_json(path: str) -> any:
    """Safely load a JSON file."""
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json(path: str, data: any) -> bool:
    """Safely save data to a JSON file."""
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception:
        return False


def get_file_size_mb(filepath: str) -> float:
    """Get file size in megabytes."""
    try:
        return os.path.getsize(filepath) / (1024 * 1024)
    except OSError:
        return 0.0


def mask_sensitive(value: str, visible: int = 4) -> str:
    """Mask sensitive data, showing only last N characters."""
    if not value or len(value) <= visible:
        return "****"
    return "*" * (len(value) - visible) + value[-visible:]
