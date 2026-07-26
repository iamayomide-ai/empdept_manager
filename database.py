"""
database.py
Encapsulates the raw SQLite connection so no other module has to
know SQL connection details directly. This is the single point of
contact between the OOP model layer and the database.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "empdept.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


class Database:
    """Singleton-style wrapper around a SQLite connection."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._connection = None
        return cls._instance

    def get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(DB_PATH, check_same_thread=False)
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def execute(self, query, params=()):
        """Run an INSERT/UPDATE/DELETE statement and commit."""
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid

    def fetch_one(self, query, params=()):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchone()

    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None


def init_db(force=False):
    """Initialize the database from schema.sql. Safe to call once at startup."""
    if force or not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
