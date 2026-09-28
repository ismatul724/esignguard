
import streamlit as st
import os
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

# Import configuration
from config import Config

# Import the secure app
from app_secure import secure_session

def main():
    """Run the secure eSignGuard application."""
    # Initialize session
    Config.initialize_session()

    # Check if session is active
    if not Config.is_session_active():
        st.session_state.clear()
        st.error("Sesi Anda telah kedaluwarsa. Silakan muat ulang halaman.")
        st.stop()

    # Update session activity
    Config.update_session_activity()

    # Set page configuration
    st.set_page_config(**Config.get_page_config())

    # Add custom CSS for better security and UI
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1000px;
        }
        .stAlert {
            padding: 1rem;
            border-radius: 0.5rem;
        }
        .stSuccess {
            background-color: #d4edda;
            border-left: 5px solid #28a745;
        }
        .stWarning {
            background-color: #fff3cd;
            border-left: 5px solid #ffc107;
        }
        .stError {
            background-color: #f8d7da;
            border-left: 5px solid #dc3545;
        }
        footer {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True)

    # Add security headers
    st.markdown("""
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'">
    <meta http-equiv="X-Frame-Options" content="DENY">
    <meta http-equiv="X-XSS-Protection" content="1; mode=block">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    """, unsafe_allow_html=True)

    # Display app version
    st.sidebar.markdown(f"**{Config.APP_NAME} v{Config.APP_VERSION}**")

    # Display security status
    if Config.is_session_active():
        st.sidebar.success("Sesi aman - Aktif")
    else:
        st.sidebar.error("Sesi tidak aman - Kedaluwarsa")

    # Run the secure app
    st.title(f"**{Config.APP_NAME}**")
    st.caption("Aplikasi Tanda Tangan Digital Dokumen yang Aman")

    # Add security notice
    st.info("""
    **Catatan Keamanan:** 
    - Pastikan Anda menggunakan kata sandi yang kuat
    - Simpan private key dan kata sandi dengan aman
    - Jangan pernah membagikan private key dengan orang lain
    - Sesi akan kedaluwarsa setelah 30 menit tidak aktif
    """)

if __name__ == "__main__":
    # Check for HTTPS configuration
    https_config = Config.get_https_config()

    if https_config:
        print(f"Starting HTTPS server on port {https_config['ssl_port']}")
        # In production, use this command to run with HTTPS:
        # streamlit run run_secure.py --server.ssl true --server.sslCertfile {https_config['ssl_certfile']} --server.sslKeyfile {https_config['ssl_keyfile']} --server.port {https_config['ssl_port']}
        st.run_server(
            port=8501,
            host="0.0.0.0",
            server="streamlit",
            ssl=True,
            ssl_certfile=https_config['ssl_certfile'],
            ssl_keyfile=https_config['ssl_keyfile']
        )
    else:
        print("Starting HTTP server on port 8501")
        # For development, use this command:
        # streamlit run run_secure.py
        st.run_server(
            port=8501,
            host="0.0.0.0",
            server="streamlit"
        )
