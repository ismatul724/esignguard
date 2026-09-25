import io
import json

import qrcode


def create_qr_code(signature_data: dict) -> bytes:
    """
    Membuat QR Code PNG dari informasi penting verifikasi dokumen.
    """
    qr_payload = {
        "app": signature_data["app_name"],
        "version": signature_data["signature_version"],
        "algorithm": signature_data["algorithm"],
        "document_name": signature_data["document_name"],
        "document_sha256": signature_data["document_sha256"],
        "signer_name": signature_data["metadata"]["signer_name"],
        "institution": signature_data["metadata"]["institution"],
        "signed_at_utc": signature_data["metadata"]["signed_at_utc"]
    }

    payload_text = json.dumps(
        qr_payload,
        ensure_ascii=False,
        separators=(",", ":")
    )

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=12,
        border=4
    )

    qr.add_data(payload_text)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    ).convert("L")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return buffer.getvalue()