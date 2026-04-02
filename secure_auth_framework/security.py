import re
import hashlib
import hmac
import os

try:
    import bcrypt  # type: ignore
except ImportError:
    bcrypt = None


def validate_username(username: str) -> tuple[bool, str]:
    if not username or not username.strip():
        return False, "Username cannot be empty."
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."
    if not re.fullmatch(r"[A-Za-z0-9_]+", username.strip()):
        return False, "Username can contain only letters, numbers, and underscore."
    return True, "Valid username."


def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must include at least one number."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must include at least one special character."
    return True, "Strong password."


def hash_password(password: str) -> str:
    if bcrypt is not None:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        return "bcrypt$" + hashed.decode("utf-8")
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 120000).hex()
    return f"pbkdf2${salt}${digest}"


def verify_password(password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("bcrypt$"):
        if bcrypt is None:
            return False
        real_hash = hashed_password.split("$", 1)[1]
        return bcrypt.checkpw(password.encode("utf-8"), real_hash.encode("utf-8"))

    if hashed_password.startswith("pbkdf2$"):
        _, salt, digest = hashed_password.split("$", 2)
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            120000,
        ).hex()
        return hmac.compare_digest(candidate, digest)

    # Backward compatibility for older plain bcrypt strings without prefix
    if bcrypt is not None:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    return False

