# utils/constants.py
"""
Application-wide constants for MedChain EMR System.
"""

# Roles
ROLE_ADMIN = "admin"
ROLE_DOCTOR = "doctor"
ROLE_PATIENT = "patient"

ALL_ROLES = [ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT]

# Blood groups
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Medical record statuses
STATUS_ACTIVE = "active"
STATUS_ARCHIVED = "archived"

# Audit actions
ACTION_LOGIN = "LOGIN"
ACTION_LOGOUT = "LOGOUT"
ACTION_REGISTER = "REGISTER"
ACTION_ADD_RECORD = "ADD_RECORD"
ACTION_VIEW_RECORD = "VIEW_RECORD"
ACTION_UPDATE_RECORD = "UPDATE_RECORD"
ACTION_DELETE_RECORD = "DELETE_RECORD"
ACTION_UPLOAD_FILE = "UPLOAD_FILE"
ACTION_DOWNLOAD_FILE = "DOWNLOAD_FILE"
ACTION_VALIDATE_CHAIN = "VALIDATE_CHAIN"
ACTION_USER_ACTIVATE = "USER_ACTIVATE"
ACTION_USER_DEACTIVATE = "USER_DEACTIVATE"

# File upload
ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".txt", ".docx"]
MAX_FILE_SIZE_MB = 10

# Pagination
RECORDS_PER_PAGE = 10

# App metadata
APP_NAME = "MedChain EMR"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Secure Blockchain-based Electronic Medical Records"
