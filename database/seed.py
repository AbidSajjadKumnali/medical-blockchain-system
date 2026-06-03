# database/seed.py
"""
Seed initial data for MedChain EMR System.
Creates default admin, doctor, and patient accounts for demo/testing.
"""

from .db import row_exists
from .models import UserModel, PatientModel, AuditLogModel
from auth.password_utils import hash_password
from utils.logger import get_logger

logger = get_logger(__name__)

SEED_USERS = [
    {
        "username": "admin",
        "email": "admin@medchain.com",
        "password": "Admin@1234",
        "role": "admin",
    },
    {
        "username": "dr_smith",
        "email": "smith@medchain.com",
        "password": "Doctor@1234",
        "role": "doctor",
    },
    {
        "username": "dr_patel",
        "email": "patel@medchain.com",
        "password": "Doctor@1234",
        "role": "doctor",
    },
    {
        "username": "patient_john",
        "email": "john@medchain.com",
        "password": "Patient@1234",
        "role": "patient",
    },
    {
        "username": "patient_sara",
        "email": "sara@medchain.com",
        "password": "Patient@1234",
        "role": "patient",
    },
]

SEED_PATIENTS = [
    {
        "username": "patient_john",
        "age": 34,
        "blood_group": "O+",
        "allergies": "Penicillin, Pollen",
        "emergency_contact": "+91-9876543210",
    },
    {
        "username": "patient_sara",
        "age": 28,
        "blood_group": "A-",
        "allergies": "None",
        "emergency_contact": "+91-8765432109",
    },
]


def seed_database():
    """Seed all initial data if not already present."""
    seeded = 0

    # Seed users
    for u in SEED_USERS:
        if not row_exists("users", "username", u["username"]):
            pw_hash = hash_password(u["password"])
            user_id = UserModel.create(u["username"], u["email"], pw_hash, u["role"])
            if user_id:
                logger.info(f"Seeded user: {u['username']} ({u['role']})")
                seeded += 1

    # Seed patient profiles
    for p in SEED_PATIENTS:
        user = UserModel.get_by_username(p["username"])
        if user and not row_exists("patients", "user_id", user["id"]):
            PatientModel.create(
                user_id=user["id"],
                age=p["age"],
                blood_group=p["blood_group"],
                allergies=p["allergies"],
                emergency_contact=p["emergency_contact"],
            )
            logger.info(f"Seeded patient profile for: {p['username']}")

    if seeded > 0:
        logger.info(f"Database seeded with {seeded} new users.")
    else:
        logger.info("Database already seeded. Skipping.")
