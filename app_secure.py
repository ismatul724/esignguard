
import json
import streamlit as st
import base64
import os
from datetime import datetime, timedelta
import pandas as pd

# Import security utilities
from security_utils import (
    SecureSession,
    validate_password_strength,
    sanitize_input,
    validate_file_upload,
    log_security_event,
    RateLimiter
)

# Import original app functionality
from crypto_utils import (
    create_signature_data,
    generate_key_pair,
    signature_json_bytes,
    verify_document_signature,
)
from qr_utils import create_qr_code
from qr_verify import decode_qr_code, validate_qr_data

# Configure Streamlit
st.set_page_config(
    page_title="eSignGuard",
    page_icon="✍️",
    layout="centered"
)

# Initialize session and security features
secure_session = SecureSession()
rate_limiter = RateLimiter(max_requests=10, time_window=60)

# Check if session is active
if not secure_session.is_session_active():
    st.session_state.clear()
    st.error("Sesi Anda telah kedaluwarsa. Silakan muat ulang halaman.")
    st.stop()

# Title and description
st.title("eSignGuard")
st.caption("Aplikasi Tanda Tangan Digital Dokumen")

# Initialize rate limiting for the whole app
if not rate_limiter.is_allowed("app_access"):
    st.error("Anda telah melebihi batas akses. Silakan coba lagi dalam beberapa menit.")
    st.stop()

# Import audit trail
from audit_utils import AuditTrail, create_document_id, create_user_id

# Initialize audit trail
audit_trail = AuditTrail()

# Create tabs
tab_key, tab_sign, tab_verify, tab_audit, tab_info = st.tabs([
    "🔑 Generate Key",
    "✍️ Sign Document",
    "✅ Verify Document",
    "📊 Audit Trail",
    "ℹ️ Tentang"
])

# Custom CSS for better security and UI
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
</style>
""", unsafe_allow_html=True)

# Tab Generate Key
with tab_key:
    st.subheader("Buat Pasangan Key Ed25519")

    # Log access to key generation
    log_security_event("KEY_GENERATION_ACCESS", {"time": datetime.now().isoformat()})
    
    # Record audit event
    audit_trail.add_audit_event(
        event_type="KEY_GENERATION_ACCESS",
        user_id=st.session_state.get("user_id", create_user_id()),
        details={"time": datetime.now().isoformat()}
    )

    st.write(
        "Masukkan password untuk mengenkripsi private key. "
        "Private key hanya digunakan untuk menandatangani dokumen."
    )

    # Password validation
    password = st.text_input(
        "Password private key",
        type="password",
        help="Gunakan minimal 12 karakter dengan kombinasi huruf kapital, huruf kecil, angka, dan simbol.",
        key="generate_password"
    )

    # Real-time password strength indicator
    if password:
        is_valid, message = validate_password_strength(password)
        if is_valid:
            st.success("Password kuat!")
        else:
            st.warning(message)

    confirm_password = st.text_input(
        "Konfirmasi password",
        type="password",
        key="generate_confirm_password"
    )

    # Enhanced button with better styling
    if st.button("Generate Key Pair", type="primary", use_container_width=True):
        # Rate limiting for key generation
        if not rate_limiter.is_allowed("key_generation"):
            st.error("Anda telah melebihi batas pembuatan key. Silakan coba lagi dalam beberapa menit.")
            st.stop()

        if not password:
            st.warning("Masukkan password terlebih dahulu.")
        elif password != confirm_password:
            st.error("Konfirmasi password tidak sama.")
        elif not validate_password_strength(password)[0]:
            st.error("Password tidak memenuhi persyaratan keamanan.")
        else:
            try:
                # Generate keys
                private_pem, public_pem = generate_key_pair(password)

                # Securely store in session
                secure_session.store_data("generated_private_pem", private_pem, encrypt=True, password=password)
                secure_session.store_data("generated_public_pem", public_pem)

                # Log successful key generation
                log_security_event("KEY_GENERATION_SUCCESS", {
                    "time": datetime.now().isoformat(),
                    "algorithm": "Ed25519"
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="KEY_GENERATION_SUCCESS",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    details={
                        "time": datetime.now().isoformat(),
                        "algorithm": "Ed25519"
                    },
                    severity="INFO"
                )

                st.success(
                    "Key pair Ed25519 berhasil dibuat. "
                    "Silakan download kedua file di bawah ini."
                )

            except ValueError as error:
                st.error(f"Terjadi kesalahan: {str(error)}")
                log_security_event("KEY_GENERATION_ERROR", {
                    "time": datetime.now().isoformat(),
                    "error": str(error)
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="KEY_GENERATION_ERROR",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    details={
                        "time": datetime.now().isoformat(),
                        "error": str(error)
                    },
                    severity="ERROR"
                )

    # Download buttons if keys exist
    try:
        private_pem = secure_session.get_data("generated_private_pem", password)
        public_pem = secure_session.get_data("generated_public_pem")

        if private_pem and public_pem:
            st.success(
                "Key pair siap diunduh. Download private key dan public key "
                "dari pasangan yang sama."
            )

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="⬇️ Download Private Key Terenkripsi",
                    data=private_pem,
                    file_name="private_key_encrypted.pem",
                    mime="application/x-pem-file",
                    key="download_private_key"
                )

            with col2:
                st.download_button(
                    label="⬇️ Download Public Key",
                    data=public_pem,
                    file_name="public_key.pem",
                    mime="application/x-pem-file",
                    key="download_public_key"
                )

            st.warning(
                "Simpan private key dan password dengan aman. Jangan unggah "
                "private key ke GitHub atau membagikannya kepada orang lain."
            )
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengakses key: {str(e)}")

# Tab Sign Document
with tab_sign:
    st.subheader("Tandatangani Dokumen")

    # Log access to document signing
    log_security_event("SIGN_DOCUMENT_ACCESS", {"time": datetime.now().isoformat()})
    
    # Record audit event
    audit_trail.add_audit_event(
        event_type="SIGN_DOCUMENT_ACCESS",
        user_id=st.session_state.get("user_id", create_user_id()),
        details={"time": datetime.now().isoformat()}
    )

    st.write(
        "Unggah dokumen dan private key terenkripsi untuk membuat "
        "digital signature Ed25519."
    )

    # Document upload with validation
    document_file = st.file_uploader(
        "Pilih dokumen (PDF, DOC, DOCX, TXT, JPG, PNG)",
        type=["pdf", "doc", "docx", "txt", "jpg", "png"],
        key="sign_document"
    )

    # Validate uploaded document
    if document_file:
        is_valid, message = validate_file_upload(document_file, max_size_mb=10)
        if not is_valid:
            st.error(message)

    private_key_file = st.file_uploader(
        "Pilih private key terenkripsi (.pem)",
        type=["pem"],
        key="sign_private_key"
    )

    key_password = st.text_input(
        "Password private key",
        type="password",
        key="sign_password"
    )

    # Sanitize text inputs
    signer_name = st.text_input(
        "Nama penandatangan",
        key="signer_name"
    )
    signer_name = sanitize_input(signer_name, max_length=100)

    signer_role = st.text_input(
        "Jabatan / peran penandatangan",
        key="signer_role"
    )
    signer_role = sanitize_input(signer_role, max_length=100)

    institution = st.text_input(
        "Institusi",
        value="Universitas Siliwangi",
        key="sign_institution"
    )
    institution = sanitize_input(institution, max_length=100)

    # Enhanced button with better styling
    if st.button("Tandatangani Dokumen", type="primary", use_container_width=True):
        # Rate limiting for document signing
        if not rate_limiter.is_allowed("document_signing"):
            st.error("Anda telah melebihi batas penandatangan dokumen. Silakan coba lagi dalam beberapa menit.")
            st.stop()

        if document_file is None:
            st.warning("Pilih dokumen yang akan ditandatangani.")
        elif private_key_file is None:
            st.warning("Pilih private key terenkripsi.")
        elif not key_password:
            st.warning("Masukkan password private key.")
        elif not signer_name:
            st.warning("Masukkan nama penandatangan.")
        else:
            try:
                document_bytes = document_file.getvalue()
                private_key_bytes = private_key_file.getvalue()

                # Create signature data
                signature_data, document_hash = create_signature_data(
                    document_bytes=document_bytes,
                    document_name=document_file.name,
                    private_key_pem=private_key_bytes,
                    password=key_password,
                    signer_name=signer_name,
                    signer_role=signer_role,
                    institution=institution,
                )

                # Securely store in session
                secure_session.store_data("signed_document_name", document_file.name)
                secure_session.store_data("signed_document_hash", document_hash)
                secure_session.store_data("signed_signature_data", signature_data)
                secure_session.store_data("signed_json_bytes", signature_json_bytes(signature_data))
                secure_session.store_data("signed_qr_bytes", create_qr_code(signature_data))

                # Create document ID for audit trail
                document_id = create_document_id(document_bytes)
                
                # Log successful signing
                log_security_event("DOCUMENT_SIGNING_SUCCESS", {
                    "time": datetime.now().isoformat(),
                    "document_name": document_file.name,
                    "signer_name": signer_name
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="DOCUMENT_SIGNING_SUCCESS",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    document_id=document_id,
                    details={
                        "time": datetime.now().isoformat(),
                        "document_name": document_file.name,
                        "document_id": document_id,
                        "signer_name": signer_name,
                        "signer_role": signer_role,
                        "institution": institution
                    },
                    severity="INFO"
                )

                st.success("Dokumen berhasil ditandatangani.")

            except ValueError as error:
                st.error(f"Terjadi kesalahan saat signing: {str(error)}")
                
                # Record audit event
                document_id = create_document_id(document_bytes) if document_file else None
                
                log_security_event("DOCUMENT_SIGNING_ERROR", {
                    "time": datetime.now().isoformat(),
                    "error": str(error)
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="DOCUMENT_SIGNING_ERROR",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    document_id=document_id,
                    details={
                        "time": datetime.now().isoformat(),
                        "error": str(error)
                    },
                    severity="ERROR"
                )
            except Exception as error:
                st.error(f"Terjadi kesalahan saat signing: {error}")
                
                # Record audit event
                document_id = create_document_id(document_bytes) if document_file else None
                
                log_security_event("DOCUMENT_SIGNING_ERROR", {
                    "time": datetime.now().isoformat(),
                    "error": str(error)
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="DOCUMENT_SIGNING_ERROR",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    document_id=document_id,
                    details={
                        "time": datetime.now().isoformat(),
                        "error": str(error)
                    },
                    severity="ERROR"
                )

    # Display signing results if available
    try:
        signature_data = secure_session.get_data("signed_signature_data")
        document_hash = secure_session.get_data("signed_document_hash")
        json_bytes = secure_session.get_data("signed_json_bytes")
        qr_bytes = secure_session.get_data("signed_qr_bytes")
        document_name = secure_session.get_data("signed_document_name")

        if signature_data and document_hash:
            st.success(
                "Hasil signing siap diunduh. Kamu dapat mengunduh JSON "
                "dan QR Code satu per satu."
            )

            st.caption("SHA-256 dokumen")
            st.code(document_hash, language=None)

            metric_1, metric_2 = st.columns(2)

            with metric_1:
                st.metric(
                    "Algoritma",
                    signature_data["algorithm"]
                )

            with metric_2:
                st.metric(
                    "Ukuran signature",
                    f"{signature_data['signature_size_bytes']} byte"
                )

            st.subheader("QR Code Verifikasi")
            st.image(qr_bytes, width=420)

            download_1, download_2 = st.columns(2)

            with download_1:
                st.download_button(
                    label="⬇️ Download Signature JSON",
                    data=json_bytes,
                    file_name=f"{document_name}.signature.json",
                    mime="application/json",
                    key="download_signature_json"
                )

            with download_2:
                st.download_button(
                    label="⬇️ Download QR Code",
                    data=qr_bytes,
                    file_name=f"{document_name}.qrcode.png",
                    mime="image/png",
                    key="download_qr_code"
                )

            st.info(
                "Simpan dokumen asli, signature JSON, public key, dan QR Code. "
                "Keempatnya digunakan untuk verifikasi."
            )
    except Exception as e:
        st.error(f"Terjadi kesalahan saat menampilkan hasil signing: {str(e)}")

# Tab Verify Document
with tab_verify:
    st.subheader("Verifikasi Dokumen")

    # Log access to document verification
    log_security_event("VERIFY_DOCUMENT_ACCESS", {"time": datetime.now().isoformat()})
    
    # Record audit event
    audit_trail.add_audit_event(
        event_type="VERIFY_DOCUMENT_ACCESS",
        user_id=st.session_state.get("user_id", create_user_id()),
        details={"time": datetime.now().isoformat()}
    )

    st.write(
        "Unggah dokumen asli, signature JSON, public key, dan QR Code "
        "untuk memeriksa keaslian serta integritas dokumen."
    )

    verify_document_file = st.file_uploader(
        "Pilih dokumen yang akan diverifikasi",
        type=["pdf", "doc", "docx", "txt", "jpg", "png"],
        key="verify_document"
    )

    # Validate uploaded document
    if verify_document_file:
        is_valid, message = validate_file_upload(verify_document_file, max_size_mb=10)
        if not is_valid:
            st.error(message)

    signature_file = st.file_uploader(
        "Pilih file signature (.json)",
        type=["json"],
        key="verify_signature"
    )

    public_key_file = st.file_uploader(
        "Pilih public key (.pem)",
        type=["pem"],
        key="verify_public_key"
    )

    qr_file = st.file_uploader(
        "Upload file QR Code hasil download (PNG/JPG, jangan screenshot atau crop)",
        type=["png", "jpg", "jpeg"],
        key="verify_qr_code"
    )

    # Enhanced button with better styling
    if st.button("Verifikasi Dokumen", type="primary", use_container_width=True):
        # Rate limiting for document verification
        if not rate_limiter.is_allowed("document_verification"):
            st.error("Anda telah melebihi batas verifikasi dokumen. Silakan coba lagi dalam beberapa menit.")
            st.stop()

        if verify_document_file is None:
            st.warning("Pilih dokumen yang akan diverifikasi.")
        elif signature_file is None:
            st.warning("Pilih file signature JSON.")
        elif public_key_file is None:
            st.warning("Pilih public key.")
        else:
            try:
                document_bytes = verify_document_file.getvalue()
                signature_bytes = signature_file.getvalue()
                public_key_bytes = public_key_file.getvalue()

                # Verify document signature
                verification_result = verify_document_signature(
                    document_bytes=document_bytes,
                    signature_json_bytes=signature_bytes,
                    public_key_pem=public_key_bytes,
                )

                # Verify QR code if provided
                qr_validity = None
                qr_result = None

                if qr_file is not None:
                    try:
                        qr_bytes = qr_file.getvalue()
                        qr_data = decode_qr_code(qr_bytes)
                        current_hash = verification_result.get("document_hash")
                        signature_data = verification_result.get("signature_data")

                        qr_result = validate_qr_data(qr_data, current_hash, signature_data)
                        qr_validity = qr_result.get("valid", False)
                    except Exception as e:
                        qr_validity = False
                        qr_result = {"valid": False, "reason": f"QR Code error: {str(e)}"}

                # Store verification results
                secure_session.store_data("verification_result", verification_result)
                secure_session.store_data("qr_validity", qr_validity)
                secure_session.store_data("qr_result", qr_result)

                # Create document ID for audit trail
                document_id = create_document_id(document_bytes)
                
                # Log successful verification
                log_security_event("DOCUMENT_VERIFICATION_SUCCESS", {
                    "time": datetime.now().isoformat(),
                    "document_name": verify_document_file.name,
                    "is_valid": verification_result.get("is_valid", False),
                    "qr_valid": qr_validity
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="DOCUMENT_VERIFICATION_SUCCESS",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    document_id=document_id,
                    details={
                        "time": datetime.now().isoformat(),
                        "document_name": verify_document_file.name,
                        "document_id": document_id,
                        "is_valid": verification_result.get("is_valid", False),
                        "qr_valid": qr_validity,
                        "signer_name": verification_result.get("signature_data", {}).get("metadata", {}).get("signer_name")
                    },
                    severity="INFO" if verification_result.get("is_valid", False) else "WARNING"
                )

                # Display verification results
                st.subheader("Hasil Verifikasi")

                # Document verification result
                if verification_result.get("is_valid", False):
                    st.success("✅ VALID - Dokumen autentik dan tidak berubah.")
                else:
                    st.error("❌ INVALID - Dokumen telah diubah atau signature tidak valid.")

                # QR code verification result
                if qr_validity is not None:
                    if qr_validity:
                        st.success("✅ QR VALID - QR Code cocok dengan dokumen dan signature JSON.")
                    else:
                        st.error(f"❌ QR INVALID - {qr_result.get('reason', 'QR Code tidak valid')}")

                # Display detailed information
                with st.expander("Lihat Detail Verifikasi"):
                    st.json({
                        "document_name": verify_document_file.name,
                        "document_hash": verification_result.get("document_hash"),
                        "algorithm": verification_result.get("signature_data", {}).get("algorithm"),
                        "signer_name": verification_result.get("signature_data", {}).get("metadata", {}).get("signer_name"),
                        "signed_at": verification_result.get("signature_data", {}).get("metadata", {}).get("signed_at_utc"),
                        "verification_time": datetime.now().isoformat()
                    })

            except ValueError as error:
                st.error(f"Verifikasi gagal: {str(error)}")
                
                # Record audit event
                document_id = create_document_id(document_bytes) if verify_document_file else None
                
                log_security_event("DOCUMENT_VERIFICATION_ERROR", {
                    "time": datetime.now().isoformat(),
                    "error": str(error)
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="DOCUMENT_VERIFICATION_ERROR",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    document_id=document_id,
                    details={
                        "time": datetime.now().isoformat(),
                        "error": str(error)
                    },
                    severity="ERROR"
                )
            except Exception as error:
                st.error(f"Terjadi kesalahan saat verifikasi: {error}")
                
                # Record audit event
                document_id = create_document_id(document_bytes) if verify_document_file else None
                
                log_security_event("DOCUMENT_VERIFICATION_ERROR", {
                    "time": datetime.now().isoformat(),
                    "error": str(error)
                })
                
                # Record audit event
                audit_trail.add_audit_event(
                    event_type="DOCUMENT_VERIFICATION_ERROR",
                    user_id=st.session_state.get("user_id", create_user_id()),
                    document_id=document_id,
                    details={
                        "time": datetime.now().isoformat(),
                        "error": str(error)
                    },
                    severity="ERROR"
                )

    # Show previous verification results if available
    try:
        verification_result = secure_session.get_data("verification_result")
        qr_validity = secure_session.get_data("qr_validity")
        qr_result = secure_session.get_data("qr_result")

        if verification_result:
            st.subheader("Hasil Verifikasi Sebelumnya")

            if verification_result.get("is_valid", False):
                st.success("✅ VALID - Dokumen autentik dan tidak berubah.")
            else:
                st.error("❌ INVALID - Dokumen telah diubah atau signature tidak valid.")

            if qr_validity is not None:
                if qr_validity:
                    st.success("✅ QR VALID - QR Code cocok dengan dokumen dan signature JSON.")
                else:
                    st.error(f"❌ QR INVALID - {qr_result.get('reason', 'QR Code tidak valid')}")
    except Exception as e:
        pass  # No previous results to display

# Tab Audit Trail
with tab_audit:
    st.subheader("Audit Trail")
    
    st.write("Audit trail melacak semua aktivitas penting dalam aplikasi eSignGuard.")
    
    # Get user ID
    user_id = st.session_state.get("user_id", create_user_id())
    
    # Add user ID to session if not exists
    if "user_id" not in st.session_state:
        st.session_state.user_id = user_id
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        event_type_filter = st.selectbox(
            "Filter Jenis Event",
            options=["SEMUA"] + list(set([ev["event_type"] for ev in audit_trail.get_audit_events()]))
        )
    
    with col2:
        user_filter = st.text_input(
            "Filter User ID",
            value="SEMUA",
            help="Kosongkan untuk menampilkan semua user"
        )
    
    # Date range filter
    col3, col4 = st.columns(2)
    
    with col3:
        start_date = st.date_input(
            "Tanggal Mulai",
            value=datetime.now().date() - timedelta(days=7),
            help="Pilih tanggal mulai untuk filter"
        )
    
    with col4:
        end_date = st.date_input(
            "Tanggal Akhir",
            value=datetime.now().date(),
            help="Pilih tanggal akhir untuk filter"
        )
    
    # Convert to datetime
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Get filtered events
    events = audit_trail.get_audit_events(
        event_type=None if event_type_filter == "SEMUA" else event_type_filter,
        user_id=None if user_filter == "SEMUA" else user_filter,
        start_date=start_datetime,
        end_date=end_datetime
    )
    
    # Show summary
    summary = audit_trail.get_audit_summary(start_datetime, end_datetime)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Total Event",
            summary["total_events"]
        )
    
    with col2:
        valid_count = sum(1 for ev in events if ev.get("is_valid") if ev.get("is_valid") is not None)
        st.metric(
            "Verifikasi Valid",
            valid_count
        )
    
    with col3:
        error_count = sum(1 for ev in events if ev["severity"] == "ERROR")
        st.metric(
            "Error",
            error_count
        )
    
    # Show event counts
    st.subheader("Distribusi Jenis Event")
    
    # Create chart for event types
    event_types = summary["event_type_counts"]
    if event_types:
        # Create bar chart
        chart_data = pd.DataFrame({
            "event_type": list(event_types.keys()),
            "count": list(event_types.values())
        })
        
        st.bar_chart(chart_data, x="event_type", y="count")
    
    # Show severity counts
    st.subheader("Distribusi Tingkat Keparahan")
    
    severity_counts = summary["severity_counts"]
    if severity_counts:
        # Create bar chart
        severity_data = pd.DataFrame({
            "severity": list(severity_counts.keys()),
            "count": list(severity_counts.values())
        })
        
        st.bar_chart(severity_data, x="severity", y="count")
    
    # Display events
    st.subheader("Daftar Event Audit")
    
    if events:
        # Create a table
        event_data = []
        
        for event in events:
            event_data.append({
                "Timestamp": event["timestamp"],
                "Event Type": event["event_type"],
                "User ID": event["user_id"],
                "Document ID": event.get("document_id", "-"),
                "Severity": event["severity"]
            })
        
        df = pd.DataFrame(event_data)
        st.dataframe(df, use_container_width=True)
        
        # Show details
        selected_event = st.selectbox(
            "Pilih Event untuk Detail",
            options=range(len(events)),
            format_func=lambda x: f"{events[x]['timestamp']} - {events[x]['event_type']}"
        )
        
        if selected_event is not None:
            event = events[selected_event]
            
            with st.expander("Detail Event"):
                st.json(event)
    
    else:
        st.info("Tidak ada event audit yang sesuai dengan filter.")

# Tab Info
with tab_info:
    st.subheader("Tentang eSignGuard")
    st.markdown("""
    eSignGuard adalah aplikasi tanda tangan digital yang menggunakan algoritma Ed25519 dan hash SHA-256 
    untuk memastikan integritas dan autentisitas dokumen.

    ## Cara Kerja

    1. **Pembuatan Key Pair**: Aplikasi membuat pasangan kunci Ed25519. Private key dienkripsi dengan password 
       dan hanya digunakan untuk membuat tanda tangan. Public key digunakan untuk verifikasi.

    2. **Tanda Tangan**: Dokumen ditandatangani dengan private key. Aplikasi menghitung hash SHA-256 dokumen 
       dan membuat tanda tangan Ed25519 dari hash tersebut. Hasilnya adalah file JSON dan QR code.

    3. **Verifikasi**: Dokumen diverifikasi dengan membandingkan hash yang dihitung ulang dengan hash yang 
       disimpan di signature JSON. Tanda tangan juga diverifikasi dengan public key.

    ## Keamanan

    - Private key dienkripsi dengan password yang Anda berikan
    - Tanda tangan menggunakan algoritma Ed25519 yang aman
    - Hash SHA-256 memastikan integritas dokumen
    - QR code dengan metadata verifikasi memastikan autentisitas

    ## Peringatan Keamanan

    - Simpan private key dan password dengan aman
    - Jangan unggah private key ke situs publik seperti GitHub
    - Pastikan semua file (dokumen asli, signature JSON, public key, QR code) berasal dari proses signing yang sama
    """)

    # Security information
    st.subheader("Informasi Keamanan")
    st.markdown("""
    ### Fitur Keamanan yang Diterapkan

    1. **Session State Aman**: Data sensitif dienkripsi sebelum disimpan di session state.
    2. **Validasi Input**: Input divalidasi dan disanitasi untuk mencegah injeksi.
    3. **Rate Limiting**: Batasi jumlah permintaan untuk mencegah serangan brute force.
    4. **Logging Aktivitas**: Semua aktivitas sensitif dicatat untuk monitoring.
    5. **Validasi File**: File upload divalidasi untuk ukuran dan tipe yang diperbolehkan.
    6. **Password Strength**: Persyaratan kekuatan password yang ketat.
    """)

    # Show security logs if available
    if "security_logs" in st.session_state:
        with st.expander("Log Keamanan"):
            st.markdown("### Aktivitas Terkini")
            for i, log in enumerate(reversed(st.session_state.security_logs[-10:])):
                timestamp = log["timestamp"]
                event_type = log["event_type"]
                details = log["details"]

                st.markdown(f"**{timestamp}** - {event_type}")
                st.json(details)
                st.markdown("---")

# Update session activity
secure_session.update_activity()

# Add session timeout warning
if "session_timeout_warning" not in st.session_state:
    st.session_state.session_timeout_warning = False

# Show session timeout warning
if not st.session_state.session_timeout_warning and time.time() - secure_session.last_activity > (secure_session.session_timeout - 5) * 60:
    st.warning("Sesi Anda akan segera kedaluwarsa. Simpan pekerjaan Anda.")
    st.session_state.session_timeout_warning = True
