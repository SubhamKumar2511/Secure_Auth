import time
from typing import Optional, Tuple

from .config import FAILED_ATTEMPT_DELAY_SECONDS, MAX_FAILED_ATTEMPTS
from .database import DatabaseManager
from .otp_service import OTPService
from .security import (
    hash_password,
    validate_password_strength,
    validate_username,
    verify_password,
)


class AuthService:
    def __init__(self, db: DatabaseManager, otp_service: OTPService):
        self.db = db
        self.otp_service = otp_service
        self.current_user: Optional[str] = None
        self.pending_mfa_user: Optional[str] = None
        self._seed_default_users()

    def _seed_default_users(self):
        admin = self.db.get_user("admin")
        if not admin:
            self.db.create_user("admin", hash_password("Admin@123"), role="admin")
        user = self.db.get_user("student")
        if not user:
            self.db.create_user("student", hash_password("Student@123"), role="user")

    def register_user(self, username: str, password: str, role: str = "user") -> Tuple[bool, str]:
        username = username.strip()
        valid_username, msg = validate_username(username)
        if not valid_username:
            return False, msg

        valid_password, msg = validate_password_strength(password)
        if not valid_password:
            return False, msg

        hashed = hash_password(password)
        created = self.db.create_user(username, hashed, role=role)
        if not created:
            return False, "Username already exists."

        return True, "Registration successful."

    def login_step_one(self, username: str, password: str) -> Tuple[bool, str]:
        username = username.strip()
        if not username or not password:
            return False, "Username and password are required."

        user = self.db.get_user(username)
        if not user:
            self.db.add_log(username, "Failed")
            time.sleep(FAILED_ATTEMPT_DELAY_SECONDS)
            return False, "Invalid username or password."

        if user["account_locked"] == 1:
            self.db.add_log(username, "Failed")
            return False, "Account is locked. Contact admin."

        if not verify_password(password, user["hashed_password"]):
            new_attempts = user["failed_attempts"] + 1
            self.db.update_failed_attempts(username, new_attempts)
            if new_attempts >= MAX_FAILED_ATTEMPTS:
                self.db.lock_account(username)
                self.db.add_log(username, "Failed")
                time.sleep(FAILED_ATTEMPT_DELAY_SECONDS)
                return False, "Account locked after 3 failed attempts."
            self.db.add_log(username, "Failed")
            time.sleep(FAILED_ATTEMPT_DELAY_SECONDS)
            attempts_left = MAX_FAILED_ATTEMPTS - new_attempts
            return False, f"Invalid password. Attempts left: {attempts_left}."

        self.db.reset_attempts(username)
        self.pending_mfa_user = username
        self.otp_service.generate_otp(username)
        return True, "OTP sent (check console)."

    def verify_login_otp(self, otp_input: str) -> Tuple[bool, str]:
        if not self.pending_mfa_user:
            return False, "No pending login request."

        username = self.pending_mfa_user
        ok, message = self.otp_service.verify_otp(username, otp_input)
        if not ok:
            self.db.add_log(username, "Failed")
            return False, message

        self.current_user = username
        self.pending_mfa_user = None
        self.db.add_log(username, "Success")
        return True, "Login successful."

    def logout(self):
        self.current_user = None
        self.pending_mfa_user = None

    def get_current_user_role(self) -> Optional[str]:
        if not self.current_user:
            return None
        user = self.db.get_user(self.current_user)
        return user["role"] if user else None

    def start_password_reset(self, username: str) -> Tuple[bool, str]:
        username = username.strip()
        user = self.db.get_user(username)
        if not user:
            return False, "User not found."
        if user["account_locked"] == 1:
            return False, "Account is locked. Ask admin to unlock first."
        self.pending_mfa_user = username
        self.otp_service.generate_otp(username)
        return True, "Reset OTP sent (check console)."

    def complete_password_reset(self, otp_input: str, new_password: str) -> Tuple[bool, str]:
        if not self.pending_mfa_user:
            return False, "No password reset request found."
        valid_password, msg = validate_password_strength(new_password)
        if not valid_password:
            return False, msg

        username = self.pending_mfa_user
        ok, message = self.otp_service.verify_otp(username, otp_input)
        if not ok:
            return False, message

        self.db.update_password(username, hash_password(new_password))
        self.pending_mfa_user = None
        return True, "Password reset successful."

