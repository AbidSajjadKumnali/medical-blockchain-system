import sqlite3
import pandas as pd

DB_PATH = "data/database.db"

conn = sqlite3.connect(DB_PATH)

# Get all tables
tables = pd.read_sql_query(
    "SELECT name FROM sqlite_master WHERE type='table';",
    conn
)

print("\n========== TABLES ==========\n")
print(tables)

for table in tables["name"]:

    print("\n" + "=" * 80)
    print(f"TABLE: {table}")
    print("=" * 80)

    # Column names
    columns = pd.read_sql_query(
        f"PRAGMA table_info({table});",
        conn
    )

    print("\nCOLUMNS:")
    print(columns[["name", "type"]])

    # Record count
    count = pd.read_sql_query(
        f"SELECT COUNT(*) as total FROM {table}",
        conn
    )

    print("\nTOTAL RECORDS:")
    print(count.iloc[0]["total"])

    # Sample records
    sample = pd.read_sql_query(
        f"SELECT * FROM {table} LIMIT 5",
        conn
    )

    print("\nFIRST 5 RECORDS:")
    print(sample)

print("\n\nDATABASE SUMMARY COMPLETE")

conn.close()