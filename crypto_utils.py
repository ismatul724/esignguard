from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import qrcode
import qrcode.constants
import base64
import hashlib
import json
from datetime import datetime, timezone
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.serialization import load_pem_public_key


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validasi kekuatan password.
    
    Args:
        password: Password yang akan divalidasi
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password minimal 8 karakter"
    
    if not any(c.isalpha() for c in password):
        return False, "Password harus mengandung huruf"
    
    if not any(c.isdigit() for c in password):
        return False, "Password harus mengandung angka"
    
    return True, "Password valid"


def generate_qr_code(data: str, output_path: str) -> None:
    """
    Generate QR code dari data string.
    
    Args:
        data: Data yang akan di-encode ke QR code
        output_path: Path untuk menyimpan file QR code
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)


def generate_key_pair(password: str) -> tuple[bytes, bytes]:
    """
    Membuat pasangan key Ed25519.

    Private key disimpan sebagai PEM PKCS8 yang dienkripsi password.
    Public key disimpan sebagai PEM SubjectPublicKeyInfo.
    """
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        raise ValueError(error_msg)

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    encrypted_private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(
            password.encode("utf-8")
        ),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return encrypted_private_pem, public_pem


def calculate_sha256(file_bytes: bytes) -> str:
    """
    Menghasilkan hash SHA-256 dalam format heksadesimal.
    """
    return hashlib.sha256(file_bytes).hexdigest()


def load_private_key(
    private_key_pem: bytes,
    password: str
) -> Ed25519PrivateKey:
    """
    Membaca private key PEM terenkripsi menggunakan password.
    """
    try:
        private_key = load_pem_private_key(
            private_key_pem,
            password=password.encode("utf-8")
        )
    except Exception as error:
        raise ValueError(
            "Private key tidak dapat dibuka. "
            "Password mungkin salah atau file key tidak valid."
        ) from error

    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("File yang diunggah bukan private key Ed25519.")

    return private_key


def sanitize_input(text: str, max_length: int = 100) -> str:
    """
    Sanitasi input user untuk mencegah XSS.
    
    Args:
        text: Input text yang akan disanitasi
        max_length: Panjang maksimal input
        
    Returns:
        Text yang sudah disanitasi
    """
    if not text:
        return ""
    
    # Batasi panjang
    text = text[:max_length]
    
    # Hapus karakter HTML berbahaya
    dangerous_chars = ['<', '>', '"', "'", '&', '\\', '/']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    return text.strip()


def create_signature_data(
    document_bytes: bytes,
    document_name: str,
    private_key_pem: bytes,
    password: str,
    signer_name: str,
    signer_role: str,
    institution: str,
) -> tuple[dict, str]:
    """
    Membuat hash SHA-256 dan signature Ed25519 untuk dokumen.

    Mengembalikan dictionary untuk signature JSON dan hash SHA-256.
    """
    if not signer_name.strip():
        raise ValueError("Nama penandatangan wajib diisi.")

    if not institution.strip():
        raise ValueError("Institusi wajib diisi.")

    # Sanitasi input
    signer_name = sanitize_input(signer_name, max_length=100)
    signer_role = sanitize_input(signer_role, max_length=100)
    institution = sanitize_input(institution, max_length=150)

    private_key = load_private_key(private_key_pem, password)

    document_hash = calculate_sha256(document_bytes)
    signed_message = document_hash.encode("utf-8")

    signature_bytes = private_key.sign(signed_message)
    signature_base64 = base64.b64encode(signature_bytes).decode("utf-8")

    signature_data = {
        "app_name": "eSignGuard",
        "signature_version": "1.1",
        "algorithm": "Ed25519",
        "hash_algorithm": "SHA-256",
        "signed_message_format": "sha256-hex-utf8",
        "document_name": document_name,
        "document_sha256": document_hash,
        "signature_base64": signature_base64,
        "signature_size_bytes": len(signature_bytes),
        "metadata": {
            "signer_name": signer_name,
            "signer_role": signer_role,
            "institution": institution,
            "signed_at_utc": datetime.now(timezone.utc).isoformat()
        }
    }

    return signature_data, document_hash


def signature_json_bytes(signature_data: dict) -> bytes:
    """
    Mengubah data signature menjadi JSON bytes agar dapat diunduh.
    """
    return json.dumps(
        signature_data,
        indent=2,
        ensure_ascii=False
    ).encode("utf-8")


def load_public_key(public_key_pem: bytes):
    """
    Membaca public key PEM untuk proses verifikasi.
    """
    try:
        public_key = load_pem_public_key(public_key_pem)
    except Exception as error:
        raise ValueError(
            "Public key tidak dapat dibaca atau file key tidak valid."
        ) from error

    return public_key


def verify_document_signature(
    document_bytes: bytes,
    signature_json_bytes: bytes,
    public_key_pem: bytes,
) -> dict:
    """
    Memverifikasi dokumen dengan signature JSON dan public key.

    Hasil berupa dictionary dengan status valid/invalid,
    hash dokumen saat ini, hash dari signature JSON, serta metadata.
    """
    try:
        signature_data = json.loads(
            signature_json_bytes.decode("utf-8")
        )
    except Exception as error:
        raise ValueError(
            "File signature JSON tidak valid."
        ) from error

    required_fields = [
        "algorithm",
        "hash_algorithm",
        "document_sha256",
        "signature_base64",
        "metadata",
    ]

    for field in required_fields:
        if field not in signature_data:
            raise ValueError(
                f"Field '{field}' tidak ditemukan dalam signature JSON."
            )

    if signature_data["algorithm"] != "Ed25519":
        raise ValueError("Algoritma signature harus Ed25519.")

    if signature_data["hash_algorithm"] != "SHA-256":
        raise ValueError("Algoritma hash harus SHA-256.")

    current_hash = calculate_sha256(document_bytes)
    signed_hash = signature_data["document_sha256"]

    if current_hash != signed_hash:
        return {
            "valid": False,
            "reason": (
                "Hash dokumen berbeda. Dokumen telah diubah "
                "atau bukan dokumen yang ditandatangani."
            ),
            "current_hash": current_hash,
            "signed_hash": signed_hash,
            "metadata": signature_data["metadata"],
        }

    public_key = load_public_key(public_key_pem)

    if not hasattr(public_key, "verify"):
        raise ValueError(
            "Public key tidak mendukung proses verifikasi."
        )

    try:
        signature_bytes = base64.b64decode(
            signature_data["signature_base64"],
            validate=True
        )
    except Exception as error:
        raise ValueError(
            "Isi signature Base64 tidak valid."
        ) from error

    try:
        public_key.verify(
            signature_bytes,
            signed_hash.encode("utf-8")
        )
    except InvalidSignature:
        return {
            "valid": False,
            "reason": (
                "Signature tidak cocok dengan public key. "
                "Gunakan public key yang benar."
            ),
            "current_hash": current_hash,
            "signed_hash": signed_hash,
            "metadata": signature_data["metadata"],
        }

    return {
        "valid": True,
        "reason": (
            "Dokumen asli, signature, dan public key berhasil diverifikasi."
        ),
        "current_hash": current_hash,
        "signed_hash": signed_hash,
        "metadata": signature_data["metadata"],
    }