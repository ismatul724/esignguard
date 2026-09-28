
import os
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import json
import streamlit as st
import re
import time
from datetime import datetime, timedelta

# Inisialisasi Fernet untuk enkripsi data sementara
def generate_encryption_key(password: str, salt: bytes = None) -> tuple:
    """Generate encryption key from password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_data(data: str, password: str) -> dict:
    """Encrypt data with password and return encrypted bytes and salt."""
    key, salt = generate_encryption_key(password)
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data.encode())
    return {
        "data": encrypted_data,
        "salt": salt
    }

def decrypt_data(encrypted_dict: dict, password: str) -> str:
    """Decrypt data with password."""
    key, _ = generate_encryption_key(password, encrypted_dict["salt"])
    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(encrypted_dict["data"])
    return decrypted_data.decode()

# Password validation
def validate_password_strength(password: str) -> tuple:
    """Validate password strength and return (is_valid, message)."""
    if len(password) < 12:  # Increased from 8 to 12
        return False, "Password minimal 12 karakter"
    if not re.search(r"[A-Z]", password):
        return False, "Password harus mengandung minimal satu huruf kapital"
    if not re.search(r"[a-z]", password):
        return False, "Password harus mengandung minimal satu huruf kecil"
    if not re.search(r"\d", password):
        return False, "Password harus mengandung minimal satu angka"
    if not re.search(r"[!@#$%^&*(),.?":{}|<>]", password):
        return False, "Password harus mengandung minimal satu karakter khusus"
    return True, "Password valid"

# Input sanitization
def sanitize_input(text: str, max_length: int = 255) -> str:
    """Sanitize input text to prevent XSS and injection."""
    if not text:
        return ""

    # Remove potentially dangerous characters
    text = re.sub(r"<[^>]*>", "", text)  # Remove HTML tags
    text = re.sub(r"["'`]", "", text)   # Remove quotes
    text = text[:max_length]  # Limit length

    return text.strip()

# Session security
class SecureSession:
    """Class to handle secure session management."""

    def __init__(self):
        self.session_timeout = 30  # minutes
        self.last_activity = time.time()
        self._initialize_session()

    def _initialize_session(self):
        """Initialize secure session."""
        if "secure_session" not in st.session_state:
            st.session_state.secure_session = {
                "data": {},
                "last_activity": time.time(),
                "session_id": secrets.token_urlsafe(16)
            }

    def is_session_active(self) -> bool:
        """Check if session is still active based on timeout."""
        if "secure_session" not in st.session_state:
            return False

        elapsed = time.time() - st.session_state.secure_session["last_activity"]
        return elapsed < (self.session_timeout * 60)

    def update_activity(self):
        """Update last activity time."""
        if "secure_session" in st.session_state:
            st.session_state.secure_session["last_activity"] = time.time()

    def store_data(self, key: str, value: str, encrypt: bool = True, password: str = ""):
        """Store data securely in session."""
        self.update_activity()

        if encrypt and password:
            # Encrypt sensitive data
            encrypted = encrypt_data(value, password)
            st.session_state.secure_session["data"][key] = {
                "encrypted": True,
                "data": encrypted
            }
        else:
            # Store non-sensitive data
            st.session_state.secure_session["data"][key] = {
                "encrypted": False,
                "data": value
            }

    def get_data(self, key: str, password: str = ""):
        """Retrieve data from session."""
        self.update_activity()

        if key not in st.session_state.secure_session["data"]:
            return None

        data_entry = st.session_state.secure_session["data"][key]

        if data_entry["encrypted"]:
            if not password:
                raise ValueError("Password required to decrypt data")
            return decrypt_data(data_entry["data"], password)
        else:
            return data_entry["data"]

    def clear_data(self, key: str = None):
        """Clear data from session."""
        self.update_activity()

        if key:
            if key in st.session_state.secure_session["data"]:
                del st.session_state.secure_session["data"][key]
        else:
            st.session_state.secure_session["data"] = {}

    def clear_all_session(self):
        """Clear all session data."""
        st.session_state.secure_session = {
            "data": {},
            "last_activity": time.time(),
            "session_id": secrets.token_urlsafe(16)
        }

# File security
def validate_file_upload(uploaded_file, max_size_mb: int = 10) -> tuple:
    """Validate uploaded file for security and size."""
    if not uploaded_file:
        return False, "No file uploaded"

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        return False, f"File too large. Maximum size is {max_size_mb}MB"

    # Check file type by extension
    allowed_extensions = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png']
    file_extension = uploaded_file.name.split('.')[-1].lower()

    if file_extension not in allowed_extensions:
        return False, f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"

    return True, "File is valid"

# Logging security events
def log_security_event(event_type: str, details: dict):
    """Log security events for monitoring."""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "event_type": event_type,
        "details": details
    }

    # In production, this would write to a secure log file
    # For now, we'll store in session state
    if "security_logs" not in st.session_state:
        st.session_state.security_logs = []

    st.session_state.security_logs.append(log_entry)

    # Keep only last 100 logs to prevent memory issues
    if len(st.session_state.security_logs) > 100:
        st.session_state.security_logs = st.session_state.security_logs[-100:]

# Rate limiting
class RateLimiter:
    """Simple rate limiter for API endpoints."""

    def __init__(self, max_requests: int = 5, time_window: int = 60):
        self.max_requests = max_requests
        self.time_window = time_window  # seconds
        self.requests = []

    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit."""
        now = time.time()

        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]

        # Check if we're under the limit
        if len(self.requests) < self.max_requests:
            self.requests.append(now)
            return True

        return False

# Initialize session when module is imported
secure_session = SecureSession()
