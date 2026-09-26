import json
import streamlit as st

from crypto_utils import (
    create_signature_data,
    generate_key_pair,
    signature_json_bytes,
    verify_document_signature,
    validate_password,
    sanitize_input,
)
from qr_utils import create_qr_code
from qr_verify import decode_qr_code, validate_qr_data


st.set_page_config(
    page_title="eSignGuard",
    page_icon="✍️",
    layout="centered"
)

# ============================================================
# GLOBAL STYLE
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

:root {
    --primary: #5AA9D6;
    --primary-dark: #3D7EA6;
    --accent: #6FCF97;
    --bg-page: #14181F;
    --bg-card: #1D222B;
    --bg-input: #262B35;
    --border: #333A46;
    --text-main: #E6E9EE;
    --text-muted: #A9B1BD;
    --radius: 14px;
}

/* Dark background across the whole app */
.stApp {
    background-color: var(--bg-page);
}
.stApp, .stApp p, .stApp li, .stApp span, .stApp label {
    color: var(--text-main) !important;
}
[data-testid="stMain"], [data-testid="stAppViewContainer"], .main .block-container {
    background-color: var(--bg-page);
}

/* Streamlit's own top header/toolbar */
[data-testid="stHeader"] {
    background-color: var(--bg-page) !important;
}
[data-testid="stHeader"] * {
    color: var(--text-main) !important;
}
[data-testid="stToolbar"] svg, [data-testid="stHeader"] svg {
    fill: var(--text-main) !important;
}

/* Hero banner */
.hero-banner {
    background: linear-gradient(120deg, #0F2A40 0%, #1D4E68 100%);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.6rem;
    border: 1px solid #2A5170;
    color: white;
}
.hero-banner h1 {
    color: #FFFFFF !important;
    text-align: left !important;
    font-family: 'Poppins', sans-serif;
    font-size: 2rem !important;
    padding: 0 !important;
    margin: 0 !important;
}
.hero-banner p {
    color: rgba(255,255,255,0.75) !important;
    font-size: 1rem;
    margin-top: 0.3rem !important;
}
.hero-icon {
    font-size: 2.8rem;
    text-align: center;
}

/* Headings */
h2, h3 {
    color: #7FC3EC !important;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
}

/* Buttons */
.stButton > button {
    background: var(--primary-dark);
    color: #FFFFFF !important;
    font-weight: 600;
    padding: 0.55rem 1.8rem;
    border-radius: 10px;
    border: none;
    transition: all 0.2s ease;
}
.stButton > button p {
    color: #FFFFFF !important;
}
.stButton > button:hover {
    background: var(--primary);
}

/* Download buttons */
.stDownloadButton > button {
    background-color: var(--bg-input);
    color: var(--primary) !important;
    font-weight: 600;
    border-radius: 10px;
    border: 2px solid var(--primary-dark);
    transition: all 0.2s ease;
}
.stDownloadButton > button p {
    color: var(--primary) !important;
}
.stDownloadButton > button:hover {
    background-color: #2C3341;
}

/* Alerts - distinguish by testid kind Streamlit assigns, darkened fills */
div[data-testid="stAlert"] {
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    border-left-width: 5px;
    border-left-style: solid;
    background-color: var(--bg-card) !important;
}
div[data-testid="stAlert"] p, div[data-testid="stAlert"] li {
    color: var(--text-main) !important;
}
div[data-testid="stAlertContentSuccess"], div[data-testid="stAlert"]:has(svg[title="Success"]) {
    border-left-color: #3FB56D;
}
div[data-testid="stAlertContentError"] {
    border-left-color: #E05260;
}
div[data-testid="stAlertContentInfo"] {
    border-left-color: #33B5CC;
}
div[data-testid="stAlertContentWarning"] {
    border-left-color: #E0B23D;
}

/* Input fields */
.stTextInput > div > div > input {
    border: 2px solid var(--border);
    border-radius: 10px;
    padding: 0.55rem 0.75rem;
    font-size: 1rem;
    background-color: var(--bg-input) !important;
    color: var(--text-main) !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px rgba(90, 169, 214, 0.2);
    background-color: var(--bg-input) !important;
}
.stTextInput label p {
    color: var(--text-main) !important;
}
/* the show/hide password eye button */
[data-testid="stTextInput"] button {
    background-color: var(--bg-input) !important;
    border: 2px solid var(--border) !important;
    border-left: none !important;
    border-radius: 0 10px 10px 0 !important;
}
[data-testid="stTextInput"] button svg {
    fill: var(--text-main) !important;
}

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    border: 2px dashed var(--primary-dark);
    border-radius: var(--radius);
    background-color: var(--bg-card);
    padding: 0.5rem;
}
[data-testid="stFileUploaderDropzone"] * {
    color: var(--text-main) !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background-color: var(--bg-input) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: var(--bg-card);
    padding: 6px;
    border-radius: 12px;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    padding: 0.6rem 1.1rem;
    border-radius: 9px;
}
.stTabs [data-baseweb="tab"] p {
    color: var(--text-muted) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--primary-dark);
}
.stTabs [data-baseweb="tab"][aria-selected="true"] p {
    color: #FFFFFF !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--bg-card);
}
[data-testid="stSidebar"] h3 {
    color: var(--primary);
}

/* Code blocks */
.stCode, code {
    border-radius: 10px !important;
    background-color: var(--bg-input) !important;
    color: #A9E6C4 !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background-color: var(--bg-card);
    padding: 1rem;
    border-radius: var(--radius);
    border: 1px solid var(--border);
}
[data-testid="stMetric"] * {
    color: var(--text-main) !important;
}

/* Section card wrapper */
.section-card {
    background-color: var(--bg-card);
    border-radius: var(--radius);
    padding: 1.5rem;
    border: 1px solid var(--border);
    margin-bottom: 1rem;
}

/* Divider */
hr {
    border: none;
    border-top: 2px solid var(--border);
    margin: 1.5rem 0;
}

/* Feature cards on Tentang tab */
.feature-card {
    padding: 1.5rem;
    border-radius: 14px;
    height: 100%;
    background-color: var(--bg-card) !important;
}
.feature-card h3 { margin-top: 0; color: #FFFFFF !important; }
.feature-card p { margin: 0; color: var(--text-muted) !important; }

/* Tables (Anggota Kelompok) */
[data-testid="stMarkdownContainer"] table {
    color: var(--text-main) !important;
}
[data-testid="stMarkdownContainer"] th {
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
}
[data-testid="stMarkdownContainer"] td {
    background-color: var(--bg-page) !important;
    border-color: var(--border) !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO HEADER
# ============================================================
st.markdown("""
<div class="hero-banner">
    <div style="display:flex; align-items:center; gap:1.2rem;">
        <div class="hero-icon">🔐</div>
        <div>
            <h1>eSignGuard</h1>
            <p>Sistem Tanda Tangan Digital Dokumen dengan Ed25519 & SHA-256</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if "generated_private_pem" not in st.session_state:
    st.session_state.generated_private_pem = None


if "generated_public_pem" not in st.session_state:
    st.session_state.generated_public_pem = None


if "signed_signature_data" not in st.session_state:
    st.session_state.signed_signature_data = None


if "signed_document_name" not in st.session_state:
    st.session_state.signed_document_name = None


if "signed_document_hash" not in st.session_state:
    st.session_state.signed_document_hash = None


if "signed_json_bytes" not in st.session_state:
    st.session_state.signed_json_bytes = None


if "signed_qr_bytes" not in st.session_state:
    st.session_state.signed_qr_bytes = None


tab_key, tab_sign, tab_verify, tab_info = st.tabs([
    "🔑 Generate Key",
    "✍️ Sign Document",
    "✅ Verify Document",
    "ℹ️ Tentang"
])


with tab_key:
    st.subheader("Buat Pasangan Key Ed25519")

    st.write(
        "Masukkan password untuk mengenkripsi private key. "
        "Private key hanya digunakan untuk menandatangani dokumen."
    )

    # Tampilkan persyaratan password
    st.info(
        "**Persyaratan password:**\n"
        "- Minimal 8 karakter\n"
        "- Harus mengandung huruf\n"
        "- Harus mengandung angka"
    )

    password = st.text_input(
        "Password private key",
        type="password",
        help="Minimal 8 karakter, harus ada huruf dan angka.",
        key="generate_password"
    )

    confirm_password = st.text_input(
        "Konfirmasi password",
        type="password",
        key="generate_confirm_password"
    )

    if st.button("Generate Key Pair", type="primary"):
        if not password:
            st.warning("Masukkan password terlebih dahulu.")
        elif password != confirm_password:
            st.error("Konfirmasi password tidak sama.")
        else:
            try:
                # Validasi password
                is_valid, error_msg = validate_password(password)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                    st.stop()

                private_pem, public_pem = generate_key_pair(password)

                st.session_state.generated_private_pem = private_pem
                st.session_state.generated_public_pem = public_pem

                st.success(
                    "Key pair Ed25519 berhasil dibuat. "
                    "Silakan download kedua file di bawah ini."
                )

            except ValueError as error:
                st.error(str(error))

    if st.session_state.generated_private_pem is not None:
        st.success(
            "Key pair siap diunduh. Download private key dan public key "
            "dari pasangan yang sama."
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="⬇️ Download Private Key Terenkripsi",
                data=st.session_state.generated_private_pem,
                file_name="private_key_encrypted.pem",
                mime="application/x-pem-file",
                key="download_private_key"
            )

        with col2:
            st.download_button(
                label="⬇️ Download Public Key",
                data=st.session_state.generated_public_pem,
                file_name="public_key.pem",
                mime="application/x-pem-file",
                key="download_public_key"
            )

        st.warning(
            "Simpan private key dan password dengan aman. Jangan unggah "
            "private key ke GitHub atau membagikannya kepada orang lain."
        )


with tab_sign:
    st.subheader("Tandatangani Dokumen")

    st.write(
        "Unggah dokumen dan private key terenkripsi untuk membuat "
        "digital signature Ed25519."
    )

    document_file = st.file_uploader(
        "Pilih dokumen (PDF atau file lain)",
        type=None,
        key="sign_document"
    )

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

    signer_name = st.text_input(
        "Nama penandatangan",
        key="signer_name",
        help="Maksimal 100 karakter"
    )

    signer_role = st.text_input(
        "Jabatan / peran penandatangan",
        key="signer_role",
        help="Maksimal 100 karakter"
    )

    institution = st.text_input(
        "Institusi",
        value="Universitas Siliwangi",
        key="sign_institution",
        help="Maksimal 150 karakter"
    )

    if st.button("Tandatangani Dokumen", type="primary"):
        if document_file is None:
            st.warning("Pilih dokumen yang akan ditandatangani.")
        elif private_key_file is None:
            st.warning("Pilih private key terenkripsi.")
        elif not key_password:
            st.warning("Masukkan password private key.")
        elif not signer_name:
            st.warning("Nama penandatangan wajib diisi.")
        else:
            try:
                document_bytes = document_file.getvalue()
                private_key_bytes = private_key_file.getvalue()

                # Sanitasi input
                signer_name_clean = sanitize_input(signer_name, max_length=100)
                signer_role_clean = sanitize_input(signer_role, max_length=100)
                institution_clean = sanitize_input(institution, max_length=150)

                signature_data, document_hash = create_signature_data(
                    document_bytes=document_bytes,
                    document_name=document_file.name,
                    private_key_pem=private_key_bytes,
                    password=key_password,
                    signer_name=signer_name_clean,
                    signer_role=signer_role_clean,
                    institution=institution_clean,
                )

                st.session_state.signed_document_name = document_file.name
                st.session_state.signed_document_hash = document_hash
                st.session_state.signed_signature_data = signature_data
                st.session_state.signed_json_bytes = signature_json_bytes(
                    signature_data
                )
                st.session_state.signed_qr_bytes = create_qr_code(
                    signature_data
                )

                st.success("Dokumen berhasil ditandatangani.")

            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                st.error(f"Terjadi kesalahan saat signing: {error}")

    if st.session_state.signed_signature_data is not None:
        signature_data = st.session_state.signed_signature_data
        document_hash = st.session_state.signed_document_hash
        json_bytes = st.session_state.signed_json_bytes
        qr_bytes = st.session_state.signed_qr_bytes
        document_name = st.session_state.signed_document_name

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


with tab_verify:
    st.subheader("Verifikasi Dokumen")

    st.write(
        "Unggah dokumen asli, signature JSON, public key, dan QR Code "
        "untuk memeriksa keaslian serta integritas dokumen."
    )

    verify_document_file = st.file_uploader(
        "Pilih dokumen yang akan diverifikasi",
        type=None,
        key="verify_document"
    )

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

    if st.button("Verifikasi Dokumen", type="primary"):
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

                result = verify_document_signature(
                    document_bytes=document_bytes,
                    signature_json_bytes=signature_bytes,
                    public_key_pem=public_key_bytes,
                )

                if result["valid"]:
                    st.success("VALID — Dokumen autentik dan tidak berubah.")
                else:
                    st.error(f"INVALID — {result['reason']}")

                if qr_file is not None:
                    try:
                        signature_data = json.loads(
                            signature_bytes.decode("utf-8")
                        )

                        qr_data = decode_qr_code(qr_file.getvalue())

                        qr_result = validate_qr_data(
                            qr_data=qr_data,
                            current_hash=result["current_hash"],
                            signature_data=signature_data,
                        )

                        if qr_result["valid"]:
                            st.success(
                                f"QR VALID — {qr_result['reason']}"
                            )
                        else:
                            st.warning(
                                f"QR TIDAK COCOK — {qr_result['reason']}"
                            )

                    except ValueError as error:
                        st.warning(f"QR TIDAK TERBACA — {error}")

                st.subheader("Informasi Verifikasi")

                col1, col2 = st.columns(2)

                with col1:
                    st.caption("Hash dokumen saat ini")
                    st.code(result["current_hash"], language=None)

                with col2:
                    st.caption("Hash saat dokumen ditandatangani")
                    st.code(result["signed_hash"], language=None)

                metadata = result["metadata"]

                st.write(
                    f"**Nama penandatangan:** "
                    f"{metadata.get('signer_name', '-')}"
                )
                st.write(
                    f"**Jabatan/peran:** "
                    f"{metadata.get('signer_role', '-')}"
                )
                st.write(
                    f"**Institusi:** "
                    f"{metadata.get('institution', '-')}"
                )
                st.write(
                    f"**Waktu tanda tangan (UTC):** "
                    f"{metadata.get('signed_at_utc', '-')}"
                )

            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                st.error(f"Terjadi kesalahan saat verifikasi: {error}")


with tab_info:
    st.subheader("📖 Tentang eSignGuard")

    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="background-color: #E8F4F8; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2E86AB;">
            <h3 style="margin-top: 0; color: #1D3557;">🔒 Aman</h3>
            <p style="margin: 0; color: #555;">Ed25519 + SHA-256 dengan enkripsi password</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="background-color: #E8F8F0; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #28A745;">
            <h3 style="margin-top: 0; color: #1D3557;">✅ Valid</h3>
            <p style="margin: 0; color: #555;">Deteksi tampering & wrong key</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="background-color: #FFF8E8; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #FFC107;">
            <h3 style="margin-top: 0; color: #1D3557;">📱 QR Code</h3>
            <p style="margin: 0; color: #555;">Verifikasi cepat dengan QR</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("""
    **eSignGuard** adalah aplikasi tanda tangan digital untuk dokumen.
    
    Gunakan aplikasi ini untuk:
    - ✍️ Menandatangani dokumen dengan kunci kriptografi
    - 🔒 Memastikan dokumen tidak diubah setelah ditandatangani
    - ✅ Memverifikasi keaslian dokumen dan tanda tangan
    
    ---
    
    ## Cara Penggunaan
    
    1. **Generate Key** - Buat pasangan kunci (private & public)
    2. **Sign Document** - Tanda tangani dokumen dengan private key
    3. **Verify Document** - Verifikasi dokumen dengan public key
    
    ---
    
    ## Keamanan
    
    ⚠️ **PENTING:**
    - Simpan **private key** dan **password** dengan aman
    - **JANGAN** share private key atau password ke siapapun
    - Backup private key ke tempat aman (USB, cloud pribadi)
    
    ---
    
    ## Teknologi
    
    - **Ed25519** - Algoritma tanda tangan digital
    - **SHA-256** - Hash kriptografis
    - **AES-256** - Enkripsi private key
    
    ---
    
    ## Anggota Kelompok
    
    | Nama | NIM |
    |------|-----|
    | Ismatul Ilmi | 247006111137 |
    | Nabila Rohmatul Aulia | 247006111143 |
    | Refa Adinda | 247006111197 |
    
    ---
    

    """)