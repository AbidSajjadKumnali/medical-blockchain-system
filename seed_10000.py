import sqlite3
import uuid
import random
from faker import Faker
from datetime import datetime

fake = Faker()

conn = sqlite3.connect("data/database.db")
cur = conn.cursor()

# Find a doctor
cur.execute("""
SELECT id
FROM users
WHERE role='doctor'
LIMIT 1
""")

doctor = cur.fetchone()

if not doctor:
    print("No doctor found!")
    exit()

doctor_id = doctor[0]

blood_groups = [
    "O+","O-","A+","A-",
    "B+","B-","AB+","AB-"
]

diagnoses = [
    "Hypertension",
    "Diabetes",
    "Fever",
    "Migraine",
    "Asthma",
    "Allergy",
    "Viral Infection",
    "Back Pain",
    "Gastritis",
    "Flu"
]

print("Creating 5000 patients and 10000 records...")

for i in range(5000):

    user_id = str(uuid.uuid4())
    patient_id = str(uuid.uuid4())

    username = f"patient_bulk_{i}"

    cur.execute("""
    INSERT INTO users
    (
        id,
        username,
        email,
        password_hash,
        role,
        is_active,
        created_at
    )
    VALUES (?,?,?,?,?,?,?)
    """,(
        user_id,
        username,
        f"{username}@mail.com",
        "bulk_import_hash",
        "patient",
        1,
        datetime.now().isoformat()
    ))

    cur.execute("""
    INSERT INTO patients
    (
        id,
        user_id,
        age,
        blood_group,
        allergies,
        emergency_contact
    )
    VALUES (?,?,?,?,?,?)
    """,(
        patient_id,
        user_id,
        random.randint(18,80),
        random.choice(blood_groups),
        random.choice([
            "None",
            "Penicillin",
            "Dust",
            "Pollen"
        ]),
        fake.phone_number()
    ))

    # 2 records per patient
    for _ in range(2):

        cur.execute("""
        INSERT INTO medical_records
        (
            id,
            patient_id,
            doctor_id,
            diagnosis,
            prescription,
            encrypted_data,
            blockchain_hash,
            record_type,
            status,
            created_at
        )
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """,(
            str(uuid.uuid4()),
            patient_id,
            doctor_id,
            random.choice(diagnoses),
            "Paracetamol 500mg",
            str(uuid.uuid4()),
            str(uuid.uuid4()),
            "consultation",
            "active",
            datetime.now().isoformat()
        ))

    if i % 500 == 0:
        print(f"{i} patients inserted...")

conn.commit()
conn.close()

print("DONE!")
print("5000 patients inserted")
print("10000 medical records inserted")