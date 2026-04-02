import random
import time

from .config import OTP_EXPIRY_SECONDS, OTP_LENGTH


class OTPService:
    def __init__(self):
        self._otp_store: dict[str, dict[str, float | str]] = {}

    def generate_otp(self, username: str) -> str:
        otp = "".join(str(random.randint(0, 9)) for _ in range(OTP_LENGTH))
        expires_at = time.time() + OTP_EXPIRY_SECONDS
        self._otp_store[username] = {"otp": otp, "expires_at": expires_at}
        print(f"[OTP] OTP for {username}: {otp} (valid for {OTP_EXPIRY_SECONDS}s)")
        return otp

    def verify_otp(self, username: str, otp_input: str) -> tuple[bool, str]:
        record = self._otp_store.get(username)
        if not record:
            return False, "No OTP generated. Please login again."
        if time.time() > float(record["expires_at"]):
            self._otp_store.pop(username, None)
            return False, "OTP expired. Please login again."
        if str(record["otp"]) != otp_input.strip():
            return False, "Invalid OTP."
        self._otp_store.pop(username, None)
        return True, "OTP verified."

