import sqlite3

conn = sqlite3.connect("data/database.db")
cur = conn.cursor()

tables = ["users", "patients", "medical_records", "audit_logs"]

for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table}: {cur.fetchone()[0]}")

conn.close()