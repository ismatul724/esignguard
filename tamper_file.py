from pathlib import Path


demo_folder = Path("demo_berhasil")

source_file = demo_folder / "7. Tugas Proyek Aplikasi Kriptografi.pdf"
tampered_file = demo_folder / "dokumen_tampered.pdf"

if not demo_folder.exists():
    raise FileNotFoundError(
        "Folder 'demo_berhasil' tidak ditemukan."
    )

if not source_file.exists():
    raise FileNotFoundError(
        f"File asli tidak ditemukan: {source_file}"
    )

data = bytearray(source_file.read_bytes())

if not data:
    raise ValueError("Dokumen kosong, tidak dapat dimodifikasi.")

index_to_change = len(data) // 2
data[index_to_change] ^= 0x01

tampered_file.write_bytes(data)

print(f"File asli     : {source_file}")
print(f"File tampered : {tampered_file}")