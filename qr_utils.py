import io
import json

import qrcode
from PIL import Image


def create_qr_code(signature_data: dict) -> bytes:
    """
    Membuat QR Code PNG yang memuat metadata ringkas verifikasi dokumen.

    Mendukung:
    - Signature tunggal versi 1.1
    - Multi-signature versi 1.2
    """
    is_multisignature = (
        signature_data.get("signature_type") == "multi-signature"
    )

    if is_multisignature:
        signatures = signature_data.get("signatures", [])

        if not signatures:
            raise ValueError(
                "Data multi-signature tidak memiliki penandatangan."
            )

        first_signature = signatures[0]
        first_metadata = first_signature.get("metadata", {})

        qr_payload = {
            "app": signature_data.get("app_name", "eSignGuard"),
            "version": signature_data.get("signature_version", "1.2"),
            "signature_type": "multi-signature",
            "algorithm": first_signature.get("algorithm", "Ed25519"),
            "document_name": signature_data.get("document_name", ""),
            "document_sha256": signature_data.get("document_sha256", ""),
            "signer_count": len(signatures),
            "first_signer_name": first_metadata.get("signer_name", ""),
            "institution": first_metadata.get("institution", ""),
            "signed_at_utc": first_metadata.get("signed_at_utc", ""),
        }
    else:
        metadata = signature_data.get("metadata", {})

        qr_payload = {
            "app": signature_data.get("app_name", "eSignGuard"),
            "version": signature_data.get("signature_version", "1.1"),
            "signature_type": "single-signature",
            "algorithm": signature_data.get("algorithm", "Ed25519"),
            "document_name": signature_data.get("document_name", ""),
            "document_sha256": signature_data.get("document_sha256", ""),
            "signer_count": 1,
            "first_signer_name": metadata.get("signer_name", ""),
            "institution": metadata.get("institution", ""),
            "signed_at_utc": metadata.get("signed_at_utc", ""),
        }

    payload_text = json.dumps(
        qr_payload,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=4,
    )

    qr.add_data(payload_text)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    ).convert("L")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()


def decode_qr_code(image_bytes: bytes) -> dict:
    """
    Membaca QR Code dari file gambar dan mengembalikan payload JSON.
    """
    image = Image.open(io.BytesIO(image_bytes))

    try:
        import cv2
        import numpy as np
    except ImportError:
        raise ValueError(
            "OpenCV (cv2) belum terinstal. Jalankan: "
            "pip install opencv-python"
        )

    image_cv = cv2.cvtColor(
        np.array(image),
        cv2.COLOR_RGB2BGR,
    )

    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(image_cv)

    if data is None or data.strip() == "":
        raise ValueError(
            "QR Code tidak terdeteksi atau tidak dapat dibaca."
        )

    try:
        return json.loads(data)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"QR Code tidak berisi JSON yang valid: {error}"
        ) from error