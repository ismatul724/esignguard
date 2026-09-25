import json
import streamlit as st

from crypto_utils import (
    create_signature_data,
    generate_key_pair,
    signature_json_bytes,
    verify_document_signature,
)
from qr_utils import create_qr_code
from qr_verify import decode_qr_code, validate_qr_data


st.set_page_config(
    page_title="eSignGuard",
    page_icon="✍️",
    layout="centered"
)

st.title("eSignGuard")
st.caption("Aplikasi Tanda Tangan Digital Dokumen")

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

    password = st.text_input(
        "Password private key",
        type="password",
        help="Gunakan minimal 8 karakter.",
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
        key="signer_name"
    )

    signer_role = st.text_input(
        "Jabatan / peran penandatangan",
        key="signer_role"
    )

    institution = st.text_input(
        "Institusi",
        value="Universitas Siliwangi",
        key="sign_institution"
    )

    if st.button("Tandatangani Dokumen", type="primary"):
        if document_file is None:
            st.warning("Pilih dokumen yang akan ditandatangani.")
        elif private_key_file is None:
            st.warning("Pilih private key terenkripsi.")
        elif not key_password:
            st.warning("Masukkan password private key.")
        else:
            try:
                document_bytes = document_file.getvalue()
                private_key_bytes = private_key_file.getvalue()

                signature_data, document_hash = create_signature_data(
                    document_bytes=document_bytes,
                    document_name=document_file.name,
                    private_key_pem=private_key_bytes,
                    password=key_password,
                    signer_name=signer_name,
                    signer_role=signer_role,
                    institution=institution,
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
    st.subheader("Tentang eSignGuard")

    st.write(
        "eSignGuard menggunakan SHA-256 untuk membuat hash dokumen "
        "dan Ed25519 untuk menandatangani hash tersebut. "
        "Private key disimpan dalam format PEM terenkripsi."
    )

    st.info(
        "Tahap saat ini: Generate Key, Sign Document, dan Verify Document."
    )