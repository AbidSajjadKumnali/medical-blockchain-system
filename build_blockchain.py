import sqlite3
from blockchain.blockchain import get_blockchain

print("Loading blockchain...")

chain = get_blockchain()

conn = sqlite3.connect("data/database.db")
conn.row_factory = sqlite3.Row

cur = conn.cursor()

cur.execute("""
SELECT id,
       patient_id,
       doctor_id,
       diagnosis,
       prescription,
       encrypted_data
FROM medical_records
LIMIT 1000
""")

records = cur.fetchall()

print(f"Found {len(records)} records")

count = 0

for r in records:

    data = f"""
Diagnosis: {r['diagnosis']}
Prescription: {r['prescription']}
Encrypted: {r['encrypted_data']}
"""

    chain.add_block(
        encrypted_data=data,
        doctor_id=r["doctor_id"],
        patient_id=r["patient_id"]
    )

    count += 1

    if count % 100 == 0:
        print(f"{count} blocks created")

conn.close()

valid, issues = chain.validate()

print()
print("================================")
print("Blockchain Length:", chain.length())
print("Valid:", valid)
print("Issues:", len(issues))
print("================================")