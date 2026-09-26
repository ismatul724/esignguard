from pathlib import Path

from qr_verify import decode_qr_code


qr_path = Path("demo_berhasil/7. Tugas Proyek Aplikasi Kriptografi.pdf.qrcode.png")

qr_data = decode_qr_code(qr_path.read_bytes())

print("QR berhasil dibaca.")
print(qr_data)