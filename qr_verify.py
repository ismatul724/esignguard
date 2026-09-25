import json

import cv2
import numpy as np


def decode_qr_code(qr_image_bytes: bytes) -> dict:
    """
    Membaca gambar QR Code dan mengembalikan isi JSON di dalamnya.
    """
    image_array = np.frombuffer(qr_image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("File gambar QR tidak dapat dibaca.")

    detector = cv2.QRCodeDetector()
    payload_text, _, _ = detector.detectAndDecode(image)

    if not payload_text:
        raise ValueError(
            "QR Code tidak terdeteksi atau tidak dapat dibaca."
        )

    try:
        return json.loads(payload_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "Isi QR Code bukan JSON eSignGuard yang valid."
        ) from error


def validate_qr_data(
    qr_data: dict,
    current_hash: str,
    signature_data: dict,
) -> dict:
    """
    Membandingkan data QR dengan dokumen saat ini dan signature JSON.
    """
    signed_hash = signature_data.get("document_sha256")
    metadata = signature_data.get("metadata", {})

    if qr_data.get("app") != "eSignGuard":
        return {
            "valid": False,
            "reason": "QR Code bukan milik aplikasi eSignGuard."
        }

    if qr_data.get("document_sha256") != current_hash:
        return {
            "valid": False,
            "reason": (
                "Hash di QR Code tidak cocok dengan dokumen yang diunggah."
            )
        }

    if qr_data.get("document_sha256") != signed_hash:
        return {
            "valid": False,
            "reason": (
                "Hash di QR Code tidak cocok dengan signature JSON."
            )
        }

    if qr_data.get("signer_name") != metadata.get("signer_name"):
        return {
            "valid": False,
            "reason": (
                "Nama penandatangan di QR Code tidak cocok dengan "
                "signature JSON."
            )
        }

    if qr_data.get("institution") != metadata.get("institution"):
        return {
            "valid": False,
            "reason": (
                "Institusi di QR Code tidak cocok dengan signature JSON."
            )
        }

    return {
        "valid": True,
        "reason": (
            "QR Code cocok dengan dokumen dan signature JSON."
        )
    }