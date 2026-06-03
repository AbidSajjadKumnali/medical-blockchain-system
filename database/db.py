# database/db.py
"""
SQLite database connection manager for MedChain EMR System.
Uses parameterized queries to prevent SQL injection.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Any
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

DB_PATH = os.getenv("DB_PATH", "data/database.db")


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.
    Row factory set to return dict-like rows.
    """
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def db_context():
    """Context manager for database operations with auto-commit/rollback."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def execute_query(query: str, params: tuple = ()) -> Optional[sqlite3.Cursor]:
    """Execute a write query (INSERT/UPDATE/DELETE)."""
    try:
        with db_context() as conn:
            cursor = conn.execute(query, params)
            return cursor
    except Exception as e:
        logger.error(f"Query execution error: {e}\nQuery: {query}")
        return None


def fetch_one(query: str, params: tuple = ()) -> Optional[dict]:
    """Fetch a single row as dictionary."""
    try:
        conn = get_connection()
        cursor = conn.execute(query, params)
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        logger.error(f"Fetch one error: {e}")
        return None


def fetch_all(query: str, params: tuple = ()) -> List[dict]:
    """Fetch all rows as list of dictionaries."""
    try:
        conn = get_connection()
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        logger.error(f"Fetch all error: {e}")
        return []


def row_exists(table: str, column: str, value: Any) -> bool:
    """Check if a row exists in a table."""
    result = fetch_one(f"SELECT 1 FROM {table} WHERE {column} = ?", (value,))
    return result is not None
