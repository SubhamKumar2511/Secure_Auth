import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple

from .config import DB_PATH


class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._create_tables()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_tables(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    hashed_password TEXT NOT NULL,
                    failed_attempts INTEGER NOT NULL DEFAULT 0,
                    account_locked INTEGER NOT NULL DEFAULT 0,
                    role TEXT NOT NULL DEFAULT 'user',
                    profile_photo_path TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(users)").fetchall()
            }
            if "profile_photo_path" not in columns:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN profile_photo_path TEXT NOT NULL DEFAULT ''"
                )
            conn.commit()

    def create_user(self, username: str, hashed_password: str, role: str = "user") -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO users (username, hashed_password, failed_attempts, account_locked, role)
                    VALUES (?, ?, 0, 0, ?)
                    """,
                    (username, hashed_password, role),
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_user(self, username: str) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            return conn.execute(
                "SELECT username, hashed_password, failed_attempts, account_locked, role, profile_photo_path FROM users WHERE username = ?",
                (username,),
            ).fetchone()

    def update_profile_photo(self, username: str, photo_path: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET profile_photo_path = ? WHERE username = ?",
                (photo_path, username),
            )
            conn.commit()

    def update_failed_attempts(self, username: str, failed_attempts: int):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET failed_attempts = ? WHERE username = ?",
                (failed_attempts, username),
            )
            conn.commit()

    def lock_account(self, username: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET account_locked = 1 WHERE username = ?",
                (username,),
            )
            conn.commit()

    def reset_attempts(self, username: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET failed_attempts = 0 WHERE username = ?",
                (username,),
            )
            conn.commit()

    def unlock_account(self, username: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET account_locked = 0, failed_attempts = 0 WHERE username = ?",
                (username,),
            )
            conn.commit()

    def update_password(self, username: str, hashed_password: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE users SET hashed_password = ? WHERE username = ?",
                (hashed_password, username),
            )
            conn.commit()

    def add_log(self, username: str, status: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO logs (username, timestamp, status) VALUES (?, ?, ?)",
                (username, now, status),
            )
            conn.commit()

    def get_all_users(self) -> List[Tuple[str, int, int, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT username, failed_attempts, account_locked, role FROM users ORDER BY username"
            ).fetchall()
            return [tuple(row) for row in rows]

    def get_logs(self) -> List[Tuple[str, str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT username, timestamp, status FROM logs ORDER BY id DESC"
            ).fetchall()
            return [tuple(row) for row in rows]

