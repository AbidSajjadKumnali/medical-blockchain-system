# auth/roles.py
"""
Role-Based Access Control (RBAC) definitions for MedChain EMR System.
"""

from utils.constants import ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT

# Permission registry: maps action names to allowed roles
PERMISSIONS: dict[str, list[str]] = {
    # Admin-only
    "manage_users":         [ROLE_ADMIN],
    "view_audit_logs":      [ROLE_ADMIN],
    "monitor_blockchain":   [ROLE_ADMIN, ROLE_DOCTOR],
    "system_analytics":     [ROLE_ADMIN],
    "activate_users":       [ROLE_ADMIN],

    # Doctor permissions
    "add_record":           [ROLE_ADMIN, ROLE_DOCTOR],
    "update_record":        [ROLE_ADMIN, ROLE_DOCTOR],
    "delete_record":        [ROLE_ADMIN],
    "upload_report":        [ROLE_ADMIN, ROLE_DOCTOR],
    "search_patients":      [ROLE_ADMIN, ROLE_DOCTOR],
    "view_patient_history": [ROLE_ADMIN, ROLE_DOCTOR],

    # Patient permissions
    "view_own_records":     [ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT],
    "download_report":      [ROLE_PATIENT, ROLE_DOCTOR, ROLE_ADMIN],
    "verify_blockchain":    [ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT],
}


def has_permission(role: str, action: str) -> bool:
    """
    Check whether a role is permitted to perform an action.

    Args:
        role: User's role string
        action: Action key from PERMISSIONS

    Returns:
        bool: True if role is allowed
    """
    allowed_roles = PERMISSIONS.get(action, [])
    return role in allowed_roles


def get_role_permissions(role: str) -> list[str]:
    """Return all actions a given role is permitted to perform."""
    return [action for action, roles in PERMISSIONS.items() if role in roles]
