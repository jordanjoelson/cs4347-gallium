# CS 4347 - Team Gallium
import sqlite3
import os
from contextlib import contextmanager

# Path to library.db next to this file, so it works from any folder
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'library.db')

@contextmanager
def get_connection():
    # Usage: with get_connection() as conn: ...
    # Commits on success, rolls back on error, and always closes the connection
    conn = sqlite3.connect(DB_PATH)
    # SQLite does not enforce foreign keys unless this is turned on
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        with conn:
            yield conn
    finally:
        conn.close()
