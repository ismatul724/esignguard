import json
import streamlit as st

from crypto_utils import (
    add_document_signature,
    create_multisignature_data,
    create_signature_data,
    generate_key_pair,
    signature_json_bytes,
    verify_document_signature,
    verify_multisignature_document,
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

/* Hide the little link/anchor icon Streamlit shows on hover next to headings */
[data-testid="stHeaderActionElements"] {
    display: none !important;
}
/* Also covers anchor icons Streamlit injects into raw <h1>-<h6> tags
   inside custom HTML (e.g. the hero banner title) */
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    display: none !important;
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

/* ---- Team member cards ---- */
.team-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.2rem;
    text-align: center;
    height: 100%;
    transition: all 0.2s ease;
}
.team-card:hover {
    border-color: var(--primary-dark);
    transform: translateY(-3px);
}
.team-avatar {
    width: 84px;
    height: 84px;
    border-radius: 50%;
    margin: 0 auto 0.9rem auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.1rem;
    font-weight: 700;
    color: #FFFFFF;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    border: 3px solid #2A313D;
    overflow: hidden;
}
.team-avatar img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}
.team-name {
    color: #FFFFFF;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 1.05rem;
    margin-bottom: 0.15rem;
}
.team-role {
    display: inline-block;
    color: var(--primary);
    background-color: rgba(90, 169, 214, 0.12);
    border: 1px solid rgba(90, 169, 214, 0.35);
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.15rem 0.7rem;
    margin-bottom: 0.9rem;
    letter-spacing: 0.02em;
}
.team-links {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
}
.team-links a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    color: var(--text-main) !important;
    background-color: var(--bg-input);
    border: 1px solid var(--border);
    border-radius: 10px;
    transition: all 0.2s ease;
}
.team-links a svg {
    width: 18px;
    height: 18px;
    fill: var(--text-main);
    transition: fill 0.2s ease;
}
.team-links a:hover {
    background-color: var(--primary-dark);
    border-color: var(--primary-dark);
}
.team-links a:hover svg {
    fill: #FFFFFF;
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

if "generated_private_pem_2" not in st.session_state:
    st.session_state.generated_private_pem_2 = None

if "generated_public_pem_2" not in st.session_state:
    st.session_state.generated_public_pem_2 = None

if "is_multisignature_mode" not in st.session_state:
    st.session_state.is_multisignature_mode = False


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

if "multisignature_json_bytes" not in st.session_state:
    st.session_state.multisignature_json_bytes = None

if "multisignature_document_name" not in st.session_state:
    st.session_state.multisignature_document_name = None

if "multisignature_qr_bytes" not in st.session_state:
    st.session_state.multisignature_qr_bytes = None


tab_key, tab_sign, tab_add_signature, tab_verify, tab_info = st.tabs([
    "🔑 Generate Key",
    "✍️ Sign Document",
    "➕ Tambah Tanda Tangan",
    "✅ Verify Document",
    "ℹ️ Tentang"
])


with tab_key:
    st.subheader("Buat Pasangan Key Ed25519")

    st.write(
        "Masukkan password untuk mengenkripsi private key. "
        "Private key hanya digunakan untuk menandatangani dokumen."
    )

    st.info(
        "**Persyaratan password:**\n"
        "- Minimal 8 karakter\n"
        "- Harus mengandung huruf\n"
        "- Harus mengandung angka"
    )

    # ── Form Penandatangan 1 ─────────────────────────────────
    password = st.text_input(
        "Password private key",
        type="password",
        help="Minimal 8 karakter, harus ada huruf dan angka.",
        key="generate_password",
    )

    confirm_password = st.text_input(
        "Konfirmasi password",
        type="password",
        key="generate_confirm_password",
    )

    # ── Checkbox (sebelum tombol Generate) ───────────────────
    enable_multisignature_key = st.checkbox(
        "Aktifkan multi-signature (generate key untuk 2 penandatangan)",
        value=st.session_state.is_multisignature_mode,
        help="Centang jika dokumen akan ditandatangani oleh lebih dari satu orang.",
        key="enable_multisignature_key",
    )

    # ── Form Penandatangan 2 (muncul jika checkbox dicentang) ─
    if enable_multisignature_key:

        password_2 = st.text_input(
            "Password private key — Penandatangan 2",
            type="password",
            help="Boleh sama atau berbeda dengan password penandatangan 1.",
            key="generate_password_2",
        )

        confirm_password_2 = st.text_input(
            "Konfirmasi password — Penandatangan 2",
            type="password",
            key="generate_confirm_password_2",
        )

    # ── Tombol generate ──────────────────────────────────────
    btn_label = "Generate Key Pair" if not enable_multisignature_key else "Generate 2 Key Pair"

    if st.button(btn_label, type="primary"):
        # Validasi penandatangan 1
        if not password:
            st.warning("Masukkan password penandatangan 1 terlebih dahulu.")
        elif password != confirm_password:
            st.error("Konfirmasi password penandatangan 1 tidak sama.")
        elif enable_multisignature_key and not password_2:
            st.warning("Masukkan password penandatangan 2 terlebih dahulu.")
        elif enable_multisignature_key and password_2 != confirm_password_2:
            st.error("Konfirmasi password penandatangan 2 tidak sama.")
        else:
            try:
                is_valid, error_msg = validate_password(password)
                if not is_valid:
                    st.error(f"❌ Penandatangan 1: {error_msg}")
                    st.stop()

                if enable_multisignature_key:
                    is_valid_2, error_msg_2 = validate_password(password_2)
                    if not is_valid_2:
                        st.error(f"❌ Penandatangan 2: {error_msg_2}")
                        st.stop()

                # Generate key pertama
                private_pem, public_pem = generate_key_pair(password)
                st.session_state.generated_private_pem = private_pem
                st.session_state.generated_public_pem = public_pem

                if enable_multisignature_key:
                    # Generate key kedua
                    private_pem_2, public_pem_2 = generate_key_pair(password_2)
                    st.session_state.generated_private_pem_2 = private_pem_2
                    st.session_state.generated_public_pem_2 = public_pem_2
                    st.session_state.is_multisignature_mode = True
                    st.success(
                        "2 key pair Ed25519 berhasil dibuat untuk multi-signature. "
                        "Silakan download keempat file di bawah ini."
                    )
                else:
                    st.session_state.generated_private_pem_2 = None
                    st.session_state.generated_public_pem_2 = None
                    st.session_state.is_multisignature_mode = False
                    st.success(
                        "Key pair Ed25519 berhasil dibuat. "
                        "Silakan download kedua file di bawah ini."
                    )

            except ValueError as error:
                st.error(str(error))

    # ── Hasil download ───────────────────────────────────────
    if st.session_state.generated_private_pem is not None:

        if st.session_state.is_multisignature_mode and st.session_state.generated_private_pem_2 is not None:
            st.success("2 key pair siap diunduh.")

            st.markdown("**Penandatangan 1**")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="⬇️ Download Private Key 1",
                    data=st.session_state.generated_private_pem,
                    file_name="private_key_1_encrypted.pem",
                    mime="application/x-pem-file",
                    key="download_private_key_1",
                )
            with col2:
                st.download_button(
                    label="⬇️ Download Public Key 1",
                    data=st.session_state.generated_public_pem,
                    file_name="public_key_1.pem",
                    mime="application/x-pem-file",
                    key="download_public_key_1",
                )

            st.markdown("**Penandatangan 2**")
            col3, col4 = st.columns(2)
            with col3:
                st.download_button(
                    label="⬇️ Download Private Key 2",
                    data=st.session_state.generated_private_pem_2,
                    file_name="private_key_2_encrypted.pem",
                    mime="application/x-pem-file",
                    key="download_private_key_2",
                )
            with col4:
                st.download_button(
                    label="⬇️ Download Public Key 2",
                    data=st.session_state.generated_public_pem_2,
                    file_name="public_key_2.pem",
                    mime="application/x-pem-file",
                    key="download_public_key_2",
                )

        else:
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
                    key="download_private_key",
                )
            with col2:
                st.download_button(
                    label="⬇️ Download Public Key",
                    data=st.session_state.generated_public_pem,
                    file_name="public_key.pem",
                    mime="application/x-pem-file",
                    key="download_public_key",
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
        key="sign_document",
    )

    private_key_file = st.file_uploader(
        "Pilih private key terenkripsi (.pem)",
        type=["pem"],
        key="sign_private_key",
    )

    key_password = st.text_input(
        "Password private key",
        type="password",
        key="sign_password",
    )

    signer_name = st.text_input(
        "Nama penandatangan",
        key="signer_name",
        help="Maksimal 100 karakter",
    )

    signer_role = st.text_input(
        "Jabatan / peran penandatangan",
        key="signer_role",
        help="Maksimal 100 karakter",
    )

    institution = st.text_input(
        "Institusi",
        value="Universitas Siliwangi",
        key="sign_institution",
        help="Maksimal 150 karakter",
    )

    enable_multisignature = st.session_state.is_multisignature_mode

    if enable_multisignature:
        st.info(
            "🔐 **Mode multi-signature aktif.** Key pair untuk 2 penandatangan "
            "sudah digenerate. Dokumen ini akan ditandatangani oleh penandatangan pertama. "
            "Penandatangan kedua menambahkan tanda tangan di tab **➕ Tambah Tanda Tangan**."
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

                signer_name_clean = sanitize_input(
                    signer_name,
                    max_length=100,
                )
                signer_role_clean = sanitize_input(
                    signer_role,
                    max_length=100,
                )
                institution_clean = sanitize_input(
                    institution,
                    max_length=150,
                )

                if enable_multisignature:
                    signature_data, document_hash = (
                        create_multisignature_data(
                            document_bytes=document_bytes,
                            document_name=document_file.name,
                            private_key_pem=private_key_bytes,
                            password=key_password,
                            signer_name=signer_name_clean,
                            signer_role=signer_role_clean,
                            institution=institution_clean,
                        )
                    )
                else:
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

        if signature_data.get("signature_type") == "multi-signature":
            first_signature = signature_data["signatures"][0]

            with metric_1:
                st.metric(
                    "Algoritma",
                    first_signature["algorithm"],
                )

            with metric_2:
                st.metric(
                    "Jumlah penandatangan",
                    len(signature_data["signatures"]),
                )
        else:
            with metric_1:
                st.metric(
                    "Algoritma",
                    signature_data["algorithm"],
                )

            with metric_2:
                st.metric(
                    "Ukuran signature",
                    f"{signature_data['signature_size_bytes']} byte",
                )

        st.subheader("QR Code Verifikasi")

        if signature_data.get("signature_type") == "multi-signature":
            st.info(
                "📋 **QR Code belum tersedia.**\n\n"
                "Pergi ke tab **➕ Tambah Tanda Tangan** untuk menyelesaikan "
                "proses multi-signature. QR Code akan otomatis tergenerate "
                "setelah penandatangan kedua selesai menambahkan tanda tangan."
            )
        elif qr_bytes is not None:
            st.image(qr_bytes, width=420)
        else:
            st.warning(
                "QR Code belum tersedia. Silakan lakukan proses signing "
                "ulang setelah memperbaiki generator QR Code."
            )

        download_1, download_2 = st.columns(2)

        with download_1:
            st.download_button(
                label="⬇️ Download Signature JSON",
                data=json_bytes,
                file_name=f"{document_name}.signature.json",
                mime="application/json",
                key="download_signature_json",
            )

        with download_2:
            if signature_data.get("signature_type") == "multi-signature":
                st.caption("QR Code tersedia setelah penandatangan 2 selesai.")
            elif qr_bytes is not None:
                st.download_button(
                    label="⬇️ Download QR Code",
                    data=qr_bytes,
                    file_name=f"{document_name}.qrcode.png",
                    mime="image/png",
                    key="download_qr_code",
                )
            else:
                st.caption("QR Code belum tersedia.")

        st.info(
            "Simpan dokumen asli, signature JSON, public key, dan QR Code. "
            "Keempatnya digunakan untuk verifikasi."
        )

with tab_add_signature:
    st.subheader("➕ Tambah Tanda Tangan")

    st.write(
        "Gunakan fitur ini untuk menambahkan tanda tangan penandatangan "
        "kedua atau berikutnya pada dokumen yang sama."
    )

    st.info(
        "Dokumen yang diunggah harus sama persis dengan dokumen saat "
        "signature JSON sebelumnya dibuat. Jika dokumen berubah satu byte "
        "saja, tanda tangan tambahan tidak dapat dibuat."
    )

    multi_document_file = st.file_uploader(
        "Pilih dokumen asli",
        type=None,
        key="multi_document",
    )

    multi_signature_file = st.file_uploader(
        "Pilih signature JSON multi-signature sebelumnya",
        type=["json"],
        key="multi_signature_json",
    )

    multi_private_key_file = st.file_uploader(
        "Pilih private key penandatangan 2 (.pem)",
        type=["pem"],
        key="multi_private_key",
    )

    multi_password = st.text_input(
        "Password private key penandatangan 2",
        type="password",
        key="multi_password",
    )

    multi_signer_name = st.text_input(
        "Nama penandatangan 2",
        key="multi_signer_name",
    )

    multi_signer_role = st.text_input(
        "Jabatan / peran penandatangan 2",
        key="multi_signer_role",
    )

    multi_institution = st.text_input(
        "Institusi penandatangan 2",
        value="Universitas Siliwangi",
        key="multi_institution",
    )

    if st.button("Tambahkan Tanda Tangan", type="primary"):
        if multi_document_file is None:
            st.warning("Pilih dokumen asli terlebih dahulu.")
        elif multi_signature_file is None:
            st.warning("Pilih signature JSON multi-signature.")
        elif multi_private_key_file is None:
            st.warning("Pilih private key penandatangan 2.")
        elif not multi_password:
            st.warning("Masukkan password private key.")
        elif not multi_signer_name:
            st.warning("Nama penandatangan wajib diisi.")
        else:
            try:
                updated_signature_data = add_document_signature(
                    document_bytes=multi_document_file.getvalue(),
                    signature_json_bytes=multi_signature_file.getvalue(),
                    private_key_pem=multi_private_key_file.getvalue(),
                    password=multi_password,
                    signer_name=multi_signer_name,
                    signer_role=multi_signer_role,
                    institution=multi_institution,
                )

                st.session_state.multisignature_json_bytes = (
                    signature_json_bytes(updated_signature_data)
                )
                st.session_state.multisignature_document_name = (
                    multi_document_file.name
                )
                st.session_state.multisignature_qr_bytes = create_qr_code(
                    updated_signature_data
                )

                signer_count = len(updated_signature_data["signatures"])

                st.success(
                    f"Tanda tangan berhasil ditambahkan. "
                    f"Total penandatangan: {signer_count}."
                )

            except ValueError as error:
                st.error(str(error))
            except Exception as error:
                st.error(
                    f"Terjadi kesalahan saat menambahkan tanda tangan: "
                    f"{error}"
                )

    if st.session_state.multisignature_json_bytes is not None:
        st.success(
            "Signature JSON multi-signature yang diperbarui siap diunduh."
        )

        doc_name = st.session_state.multisignature_document_name
        dl_col1, dl_col2 = st.columns(2)

        with dl_col1:
            st.download_button(
                label="⬇️ Download Multi-Signature JSON",
                data=st.session_state.multisignature_json_bytes,
                file_name=f"{doc_name}.multisignature.json",
                mime="application/json",
                key="download_multisignature_json",
            )

        with dl_col2:
            if st.session_state.multisignature_qr_bytes is not None:
                st.download_button(
                    label="⬇️ Download QR Code",
                    data=st.session_state.multisignature_qr_bytes,
                    file_name=f"{doc_name}.multisignature.qrcode.png",
                    mime="image/png",
                    key="download_multisignature_qr",
                )

        if st.session_state.multisignature_qr_bytes is not None:
            st.subheader("QR Code Verifikasi")
            st.image(st.session_state.multisignature_qr_bytes, width=420)
            st.info(
                "QR Code ini menyegel seluruh penandatangan. Simpan bersama "
                "dokumen asli, signature JSON, dan semua public key untuk verifikasi."
            )


with tab_verify:
    st.subheader("Verifikasi Dokumen")

    st.write(
        "Unggah dokumen, signature JSON, dan public key untuk memeriksa "
        "keaslian, integritas, serta validitas tanda tangan digital."
    )

    verify_document_file = st.file_uploader(
        "Pilih dokumen yang akan diverifikasi",
        type=None,
        key="verify_document",
    )

    signature_file = st.file_uploader(
        "Pilih file signature (.json)",
        type=["json"],
        key="verify_signature",
    )

    if signature_file is not None:
        try:
            preview_signature_data = json.loads(
                signature_file.getvalue().decode("utf-8")
            )
        except Exception:
            preview_signature_data = None
    else:
        preview_signature_data = None

    is_multisignature = (
        preview_signature_data is not None
        and preview_signature_data.get("signature_type")
        == "multi-signature"
    )

    if is_multisignature:
        signatures = preview_signature_data.get("signatures", [])
        signer_count = len(signatures)

        st.info(
            f"Signature JSON multi-signature terdeteksi. "
            f"Jumlah penandatangan: {signer_count}."
        )

        public_key_files = []

        for index, signature_entry in enumerate(signatures, start=1):
            metadata = signature_entry.get("metadata", {})
            signer_name = metadata.get(
                "signer_name",
                f"Penandatangan {index}",
            )

            public_key_file = st.file_uploader(
                f"Public key untuk penandatangan {index}: {signer_name}",
                type=["pem"],
                key=f"verify_multi_public_key_{index}",
            )

            public_key_files.append(public_key_file)

    else:
        public_key_file = st.file_uploader(
            "Pilih public key (.pem)",
            type=["pem"],
            key="verify_public_key",
        )
        public_key_files = [public_key_file]

    qr_file = st.file_uploader(
        "Upload file QR Code hasil download (PNG/JPG, jangan screenshot "
        "atau crop)",
        type=["png", "jpg", "jpeg"],
        key="verify_qr_code",
    )

    if st.button("Verifikasi Dokumen", type="primary"):
        if verify_document_file is None:
            st.warning("Pilih dokumen yang akan diverifikasi.")
        elif signature_file is None:
            st.warning("Pilih file signature JSON.")
        elif preview_signature_data is None:
            st.warning("File signature JSON tidak valid.")
        elif any(key_file is None for key_file in public_key_files):
            st.warning(
                "Upload semua public key sesuai dengan jumlah "
                "penandatangan."
            )
        else:
            try:
                document_bytes = verify_document_file.getvalue()
                signature_bytes = signature_file.getvalue()

                if is_multisignature:
                    public_key_bytes_list = [
                        key_file.getvalue()
                        for key_file in public_key_files
                    ]

                    result = verify_multisignature_document(
                        document_bytes=document_bytes,
                        signature_json_bytes=signature_bytes,
                        public_key_pems=public_key_bytes_list,
                    )

                    if result["valid"]:
                        st.success(
                            "VALID — Dokumen autentik dan seluruh "
                            "tanda tangan valid."
                        )
                    else:
                        st.error(f"INVALID — {result['reason']}")

                    st.subheader("Hasil Verifikasi Penandatangan")

                    for signer_result in result["signer_results"]:
                        signer_label = (
                            f"{signer_result['index']}. "
                            f"{signer_result['signer_name']}"
                        )

                        if signer_result["valid"]:
                            st.success(
                                f"{signer_label} — VALID. "
                                f"{signer_result['reason']}"
                            )
                        else:
                            st.error(
                                f"{signer_label} — INVALID. "
                                f"{signer_result['reason']}"
                            )

                else:
                    result = verify_document_signature(
                        document_bytes=document_bytes,
                        signature_json_bytes=signature_bytes,
                        public_key_pem=public_key_files[0].getvalue(),
                    )

                    if result["valid"]:
                        st.success(
                            "VALID — Dokumen autentik dan tidak berubah."
                        )
                    else:
                        st.error(f"INVALID — {result['reason']}")

                if qr_file is not None:
                    try:
                        qr_data = decode_qr_code(qr_file.getvalue())

                        if (
                            qr_data.get("document_sha256")
                            != result["current_hash"]
                        ):
                            st.warning(
                                "QR TIDAK COCOK — Hash di QR Code tidak "
                                "cocok dengan dokumen yang diunggah."
                            )
                        else:
                            st.success(
                                "QR VALID — Hash QR Code cocok dengan "
                                "dokumen yang diunggah."
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

                if is_multisignature:
                    st.write(
                        f"**Jumlah penandatangan:** "
                        f"{result['total_signers']}"
                    )
                    st.write(
                        f"**Tanda tangan valid:** "
                        f"{result['valid_signatures']} dari "
                        f"{result['total_signers']}"
                    )
                else:
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
        <div class="feature-card" style="border-left: 4px solid #2E86AB;">
            <h3>🔒 Aman</h3>
            <p>Ed25519 + SHA-256 dengan enkripsi password</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature-card" style="border-left: 4px solid #28A745;">
            <h3>✅ Valid</h3>
            <p>Deteksi tampering & wrong key</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card" style="border-left: 4px solid #FFC107;">
            <h3>📱 QR Code</h3>
            <p>Verifikasi cepat dengan QR</p>
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
    """)

    st.subheader("👥 Tim Pengembang")
    st.caption("Kelompok pengembang eSignGuard — Universitas Siliwangi")

    import base64
    import os

    def _avatar_html(image_path: str, initials: str) -> str:
        """Return an <img> tag if the photo exists on disk, otherwise a
        gradient circle with the person's initials so the layout never
        breaks when assets/*.jpg is missing."""
        if os.path.exists(image_path):
            with open(image_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode()
            return f'<img src="data:image/jpeg;base64,{encoded}" />'
        return initials

    team_members = [
        {
            "name": "Ismatul Ilmi",
            "role": "Backend Developer",
            "initials": "II",
            "image": "assets/ismatul.jpg",
            "links": [
                ("Instagram", "https://instagram.com/Ilmysma"),
                ("GitHub", "https://github.com/Ismatul724"),
            ],
        },
        {
            "name": "Nabila Rohmatul Aulia",
            "role": "UI/UX Designer",
            "initials": "NR",
            "image": "assets/nabila.jpeg",
            "links": [
                ("Instagram", "https://instagram.com/nabilaara_"),
                ("GitHub", "https://github.com/NABILAARA"),
            ],
        },
        {
            "name": "Refa Adinda",
            "role": "QA & Documentation",
            "initials": "RA",
            "image": "assets/refa.jpeg",
            "links": [
                ("Instagram", "https://instagram.com/refaadinda"),
                ("GitHub", "https://github.com/247006111197-web"),
            ],
        },
    ]

    ICONS = {
        "Instagram": (
            '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M12 2c2.72 0 3.06.01 4.12.06 1.06.05 1.79.22 2.43.47.66.26 1.21.6 1.76 1.15.5.5.87 1.05 1.15 1.76.25.64.42 1.37.47 2.43.05 1.06.06 1.4.06 4.13s-.01 3.07-.06 4.13c-.05 1.06-.22 1.79-.47 2.43a4.93 4.93 0 0 1-1.15 1.76 4.93 4.93 0 0 1-1.76 1.15c-.64.25-1.37.42-2.43.47-1.06.05-1.4.06-4.12.06s-3.07-.01-4.13-.06c-1.06-.05-1.79-.22-2.43-.47a4.93 4.93 0 0 1-1.76-1.15 4.93 4.93 0 0 1-1.15-1.76c-.25-.64-.42-1.37-.47-2.43C2.01 15.07 2 14.73 2 12s.01-3.07.06-4.13c.05-1.06.22-1.79.47-2.43.26-.66.6-1.21 1.15-1.76A4.93 4.93 0 0 1 5.44 2.53c.64-.25 1.37-.42 2.43-.47C8.93 2.01 9.27 2 12 2Zm0 1.8c-2.67 0-2.99.01-4.04.06-.87.04-1.34.18-1.65.3-.42.16-.71.35-1.02.66-.31.31-.5.6-.66 1.02-.12.31-.26.78-.3 1.65C4.29 8.54 4.28 8.86 4.28 11.5v1c0 2.64.01 2.96.05 4.01.04.87.18 1.34.3 1.65.16.42.35.71.66 1.02.31.31.6.5 1.02.66.31.12.78.26 1.65.3 1.05.05 1.37.06 4.04.06s2.99-.01 4.04-.06c.87-.04 1.34-.18 1.65-.3.42-.16.71-.35 1.02-.66.31-.31.5-.6.66-1.02.12-.31.26-.78.3-1.65.05-1.05.06-1.37.06-4.01v-1c0-2.64-.01-2.96-.06-4.01-.04-.87-.18-1.34-.3-1.65a2.73 2.73 0 0 0-.66-1.02 2.73 2.73 0 0 0-1.02-.66c-.31-.12-.78-.26-1.65-.3C14.99 3.81 14.67 3.8 12 3.8Zm0 3.05a5.15 5.15 0 1 1 0 10.3 5.15 5.15 0 0 1 0-10.3Zm0 1.8a3.35 3.35 0 1 0 0 6.7 3.35 3.35 0 0 0 0-6.7Zm5.36-1.99a1.2 1.2 0 1 1 0 2.4 1.2 1.2 0 0 1 0-2.4Z"/>'
            '</svg>'
        ),
        "GitHub": (
            '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M12 2C6.48 2 2 6.58 2 12.19c0 4.49 2.87 8.3 6.84 9.65.5.1.68-.22.68-.49 0-.24-.01-1.04-.01-1.88-2.78.51-3.5-.7-3.72-1.33-.13-.33-.68-1.35-1.16-1.62-.4-.22-.97-.75-.01-.77.9-.01 1.54.84 1.76 1.19 1.03 1.75 2.67 1.25 3.32.96.1-.75.4-1.26.73-1.55-2.55-.29-5.23-1.29-5.23-5.72 0-1.26.44-2.3 1.16-3.11-.12-.3-.5-1.5.11-3.12 0 0 .95-.31 3.12 1.19a10.6 10.6 0 0 1 2.84-.39c.96.01 1.93.13 2.84.39 2.17-1.5 3.12-1.19 3.12-1.19.61 1.62.23 2.82.11 3.12.72.81 1.16 1.84 1.16 3.11 0 4.44-2.69 5.42-5.25 5.71.42.37.78 1.08.78 2.18 0 1.58-.01 2.85-.01 3.24 0 .27.18.6.69.49A10.02 10.02 0 0 0 22 12.19C22 6.58 17.52 2 12 2Z"/>'
            '</svg>'
        ),
    }

    team_cols = st.columns(3)

    for col, member in zip(team_cols, team_members):
        with col:
            avatar_content = _avatar_html(member["image"], member["initials"])
            links_html = "".join(
                f'<a href="{url}" target="_blank" title="{label}">{ICONS[label]}</a>'
                for label, url in member["links"]
            )
            st.markdown(f"""
            <div class="team-card">
                <div class="team-avatar">{avatar_content}</div>
                <div class="team-name">{member["name"]}</div>
                <div class="team-role">{member["role"]}</div>
                <div class="team-links">{links_html}</div>
            </div>
            """, unsafe_allow_html=True)