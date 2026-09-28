
import os
import streamlit as st
from pathlib import Path

# Configuration for the application
class Config:
    # App Configuration
    APP_NAME = "eSignGuard"
    APP_VERSION = "1.1.0"

    # Security Configuration
    SESSION_TIMEOUT = 30  # minutes
    MAX_PASSWORD_LENGTH = 100
    MAX_INPUT_LENGTH = 255
    MAX_FILE_SIZE_MB = 10
    ALLOWED_FILE_EXTENSIONS = ['pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png']

    # Rate Limiting
    RATE_LIMIT_REQUESTS = 10
    RATE_LIMIT_TIME_WINDOW = 60  # seconds

    # Password Requirements
    MIN_PASSWORD_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True

    # Session State Keys
    SESSION_KEYS = {
        "private_pem": "generated_private_pem",
        "public_pem": "generated_public_pem",
        "signature_data": "signed_signature_data",
        "document_name": "signed_document_name",
        "document_hash": "signed_document_hash",
        "json_bytes": "signed_json_bytes",
        "qr_bytes": "signed_qr_bytes",
        "security_logs": "security_logs",
        "secure_session": "secure_session"
    }

    # Certificate paths (for HTTPS)
    CERTIFICATE_PATH = None
    PRIVATE_KEY_PATH = None

    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = "esignguard.log"
    MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5

    @staticmethod
    def get_page_config():
        """Get Streamlit page configuration."""
        return {
            "page_title": Config.APP_NAME,
            "page_icon": "✍️",
            "layout": "centered",
            "initial_sidebar_state": "expanded"
        }

    @staticmethod
    def get_https_config():
        """Get HTTPS configuration if certificates are available."""
        if Config.CERTIFICATE_PATH and Config.PRIVATE_KEY_PATH:
            return {
                "server": "streamlit",
                "ssl_port": 8502,
                "ssl_certfile": Config.CERTIFICATE_PATH,
                "ssl_keyfile": Config.PRIVATE_KEY_PATH
            }
        return None

    @staticmethod
    def initialize_session():
        """Initialize session state with default values."""
        for key in Config.SESSION_KEYS.values():
            if key not in st.session_state:
                if key == Config.SESSION_KEYS["security_logs"]:
                    st.session_state[key] = []
                elif key == Config.SESSION_KEYS["secure_session"]:
                    st.session_state[key] = {
                        "data": {},
                        "last_activity": Config.get_current_time(),
                        "session_id": Config.generate_session_id()
                    }
                else:
                    st.session_state[key] = None

    @staticmethod
    def get_current_time():
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    @staticmethod
    def generate_session_id():
        """Generate a secure session ID."""
        import secrets
        return secrets.token_urlsafe(16)

    @staticmethod
    def update_session_activity():
        """Update the last activity time in session."""
        if Config.SESSION_KEYS["secure_session"] in st.session_state:
            st.session_state[Config.SESSION_KEYS["secure_session"]]["last_activity"] = Config.get_current_time()

    @staticmethod
    def is_session_active():
        """Check if session is still active."""
        if Config.SESSION_KEYS["secure_session"] not in st.session_state:
            return False

        session_data = st.session_state[Config.SESSION_KEYS["secure_session"]]
        from datetime import datetime, timedelta

        last_activity = datetime.fromisoformat(session_data["last_activity"])
        elapsed = datetime.now() - last_activity

        return elapsed < timedelta(minutes=Config.SESSION_TIMEOUT)

    @staticmethod
    def get_security_headers():
        """Get security headers for the application."""
        return {
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
        }

    @staticmethod
    def get_allowed_origins():
        """Get allowed origins for CORS."""
        return [
            "http://localhost:8501",
            "http://localhost:8502",
            "https://yourdomain.com"
        ]
