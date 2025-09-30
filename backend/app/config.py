import os
from pathlib import Path

# Authentication and authorization
AUTH_ADMIN_KEY = "skedeedleskedoodle"
AUTH_KEY = "Authorization"
AUTH_SESSION_EXPIRE = 48

# Password reset and verification
PASSWORD_RESET_EXPIRE_HOURS = 24
VERIFY_TOKEN_EXPIRE_HOURS = 24

# Organization settings
INVITE_EXPIRATION_DAYS = 7

# URL prefix for the application
URL_PREFIX: str = os.getenv("URL_PREFIX", "http://optimap.local")
ENGINE_URL_PREFIX: str = os.getenv("ENGINE_URL_PREFIX", "http://engine.local")

# Asset configuration
ASSETS_PATH = Path(__file__).resolve().parent.parent / "assets"
TEMPLATE_PATH = ASSETS_PATH / "mails" / "templates"
LOGO_PATH = ASSETS_PATH / "img" / "logo.base64"

# Upload directory
UPLOAD_DIR_ENV: str = os.getenv("UPLOAD_DIR", "uploads")
UPLOAD_DIR = Path(UPLOAD_DIR_ENV)

# Maximum upload size
MAX_UPLOAD_SIZE_BYTES = 30 * 1024 * 1024  # 30MB
