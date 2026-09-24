import sqlite3
import os

DB_PATH = "report.db"

def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables if they don't exist."""
    conn = get_db()
    cursor = conn.cursor()
    
    # Orders table (for the shop dataset)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            product TEXT NOT NULL,
            amount REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Reports table (bookkeeping)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()