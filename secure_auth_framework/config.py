from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "secure_auth.db"
MAX_FAILED_ATTEMPTS = 3
FAILED_ATTEMPT_DELAY_SECONDS = 2
OTP_EXPIRY_SECONDS = 120
OTP_LENGTH = 4
ADMIN_CONTACT_EMAIL = "subhamkumar98997gmail.com"
ADMIN_CONTACT_PHONE = "+91-7087652920"

