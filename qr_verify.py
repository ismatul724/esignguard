import json

import cv2
import numpy as np


def decode_qr_code(qr_image_bytes: bytes) -> dict:
    """
    Membaca gambar QR Code dan mengembalikan isi JSON di dalamnya.
    """
    image_array = np.frombuffer(qr_image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_GRAYSCALE)

    if image is None:
        raise ValueError("File gambar QR tidak dapat dibaca.")

    detector = cv2.QRCodeDetector()
    candidates = [image]

    enlarged_image = cv2.resize(
        image,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_NEAREST,
    )
    candidates.append(enlarged_image)
    candidates.append(
        cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    )

    height, width = image.shape
    margin = max(1, min(height, width) // 20)
    if height > margin * 2 and width > margin * 2:
        cropped_image = image[margin:-margin, margin:-margin]
        candidates.extend([
            cropped_image,
            cv2.resize(
                cropped_image,
                None,
                fx=2,
                fy=2,
                interpolation=cv2.INTER_NEAREST,
            ),
        ])

    candidates.extend([
        cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE),
        cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE),
    ])

    payload_text = ""
    for candidate in candidates:
        payload_text, _, _ = detector.detectAndDecode(candidate)
        if payload_text:
            break

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