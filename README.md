# eSignGuard

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.64.0-red)
![License](https://img.shields.io/badge/License-MIT-green)

Aplikasi web tanda tangan digital dokumen berbasis Python dan Streamlit menggunakan algoritma **Ed25519** dan **SHA-256**.

## 🚀 Live Demo

Aplikasi ini sudah di-deploy dan bisa diakses di:

👉 [https://esignguard.streamlit.app/](https://esignguard.streamlit.app/)

---

## Fitur

- Generate pasangan key Ed25519 (single atau multi-signature)
- Private key disimpan dalam format PEM terenkripsi password (AES-256)
- Tanda tangan dokumen menggunakan hash SHA-256
- Dukungan multi-signature (lebih dari satu penandatangan)
- Pembuatan signature dalam format JSON (versi 1.1 dan 1.2)
- QR Code verifikasi yang menyegel seluruh penandatangan
- Verifikasi dokumen asli (single maupun multi-signature)
- Deteksi perubahan/tampering dokumen
- Deteksi public key yang salah
- **Password strength indicator** real-time (`app_secure.py`)
- **Audit Trail** — pencatatan aktivitas penting, persistent via localStorage browser

---

## Teknologi

- **Python 3.8+**
- **Streamlit 1.64** — framework aplikasi web
- **cryptography 50.0** — library kriptografi (Ed25519, PKCS8, AES-256)
- **SHA-256** — fungsi hash kriptografis untuk integritas dokumen
- **qrcode 8.2** — generator QR Code
- **OpenCV (opencv-python-headless)** — dekoder QR Code
- **Pillow 12.3** — pemrosesan gambar
- **streamlit-local-storage** — persistensi audit trail di browser

---

## Struktur Folder

```
esignguard/
├── app.py                    # Aplikasi Streamlit utama
├── app_secure.py             # Versi secure dengan password strength indicator
├── crypto_utils.py           # Engine kriptografi (generate key, sign, verify)
├── qr_utils.py               # Generator QR Code PNG
├── qr_verify.py              # Dekoder QR Code (OpenCV)
├── audit_utils.py            # Audit trail (session state + localStorage)
├── local_storage.py          # Jembatan ke localStorage browser
├── security_utils.py         # Utilitas keamanan tambahan
├── config.py                 # Konfigurasi aplikasi
├── benchmark.py              # Script benchmark performa
├── tamper_file.py            # Script demo tampering dokumen
├── test_qr_read.py           # Script uji baca QR Code
├── run_secure.py             # Entry point versi secure
├── assets/                   # Foto tim pengembang
│   ├── ismatul.jpg
│   ├── nabila.jpeg
│   └── refa.jpeg
├── tests/
│   └── test_crypto.py        # 5 unit test kriptografi
├── data/
│   └── benchmark_results.json
├── requirements.txt          # Dependensi utama
├── requirements_secure.txt   # Dependensi versi secure
└── .gitignore
```

---

## Instalasi

### Linux atau macOS

```bash
git clone <URL_REPOSITORI>
cd esignguard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```powershell
git clone <URL_REPOSITORI>
cd esignguard
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Menjalankan Aplikasi

```bash
# Versi standar
streamlit run app.py

# Versi secure (password strength indicator + audit trail lebih lengkap)
streamlit run app_secure.py
```

Buka aplikasi di:

```
http://localhost:8501
```

---

## Alur Penggunaan Lengkap

### A. Tanda Tangan Tunggal (Single Signature)

Digunakan ketika dokumen hanya ditandatangani oleh satu orang.

#### Langkah 1 — Generate Key

1. Buka tab **🔑 Generate Key**.
2. Isi kolom **"Password private key"** — minimal 8 karakter, harus mengandung huruf dan angka.
3. Isi kolom **"Konfirmasi password"** dengan password yang sama.
4. Pastikan checkbox **"Aktifkan multi-signature (generate key untuk 2 penandatangan)"** **tidak** dicentang.
5. Klik tombol **Generate Key Pair**.
6. Download dua file yang muncul:
   - `private_key_encrypted.pem` — kunci privat terenkripsi
   - `public_key.pem` — kunci publik untuk verifikasi

> ⚠️ Simpan `private_key_encrypted.pem` dan passwordnya di tempat aman. Jangan unggah ke GitHub atau bagikan ke siapapun.

---

#### Langkah 2 — Tanda Tangani Dokumen

1. Buka tab **✍️ Sign Document**.
2. Upload dokumen yang akan ditandatangani (PDF atau format lain).
3. Upload `private_key_encrypted.pem`.
4. Masukkan password private key.
5. Isi kolom:
   - **Nama penandatangan** (wajib)
   - **Jabatan / peran** (opsional)
   - **Institusi** (default: Universitas Siliwangi)
6. Klik tombol **Tandatangani Dokumen**.
7. Download dua file hasil:
   - `nama_dokumen.signature.json` — berisi hash SHA-256, signature Ed25519, dan metadata
   - `nama_dokumen.qrcode.png` — QR Code untuk verifikasi cepat

> Simpan dokumen asli, `signature.json`, `public_key.pem`, dan `qrcode.png` sebagai satu paket — keempatnya dibutuhkan saat verifikasi.

---

#### Langkah 3 — Verifikasi Dokumen

1. Buka tab **✅ Verify Document**.
2. Upload dokumen yang akan diverifikasi.
3. Upload file `nama_dokumen.signature.json`.
4. Upload `public_key.pem`.
5. Upload `nama_dokumen.qrcode.png` (opsional — gunakan file asli hasil download, bukan screenshot).
6. Klik tombol **Verifikasi Dokumen**.

Hasil yang diharapkan:

```
VALID — Dokumen autentik dan tidak berubah.
QR VALID — Hash QR Code cocok dengan dokumen yang diunggah.
```

---

### B. Multi-Signature (Dua Penandatangan)

Digunakan ketika dokumen harus ditandatangani oleh dua orang atau lebih.

#### Langkah 1 — Generate 2 Key Pair

1. Buka tab **🔑 Generate Key**.
2. Isi kolom **"Password private key"** dan **"Konfirmasi password"** untuk **Penandatangan 1**.
3. Centang checkbox **"Aktifkan multi-signature (generate key untuk 2 penandatangan)"**.
4. Form untuk **Penandatangan 2** akan muncul — isi **"Password private key — Penandatangan 2"** dan konfirmasinya.
5. Klik tombol **Generate 2 Key Pair**.
6. Download empat file yang muncul:
   - `private_key_1_encrypted.pem` dan `public_key_1.pem` — untuk Penandatangan 1
   - `private_key_2_encrypted.pem` dan `public_key_2.pem` — untuk Penandatangan 2

---

#### Langkah 2 — Penandatangan 1 Menandatangani

1. Buka tab **✍️ Sign Document**.
2. Banner info biru muncul: *"Mode multi-signature aktif. Dokumen ini akan ditandatangani oleh penandatangan pertama."*
3. Upload dokumen, lalu upload `private_key_1_encrypted.pem`.
4. Masukkan password Penandatangan 1.
5. Isi nama, jabatan, dan institusi Penandatangan 1.
6. Klik tombol **Tandatangani Dokumen**.
7. Download satu file hasil:
   - `nama_dokumen.signature.json` — berisi signature Penandatangan 1

> QR Code belum tersedia di tahap ini — akan dibuat setelah semua penandatangan selesai.

---

#### Langkah 3 — Penandatangan 2 Menambahkan Tanda Tangan

1. Buka tab **➕ Tambah Tanda Tangan**.
2. Upload dokumen yang **sama persis** dengan dokumen pada Langkah 2 (tidak boleh berubah satu byte pun).
3. Upload `nama_dokumen.signature.json` dari Langkah 2.
4. Upload `private_key_2_encrypted.pem`.
5. Masukkan password Penandatangan 2.
6. Isi nama, jabatan, dan institusi Penandatangan 2.
7. Klik tombol **Tambahkan Tanda Tangan**.
8. Download dua file hasil:
   - `nama_dokumen.multisignature.json` — berisi signature kedua penandatangan
   - `nama_dokumen.multisignature.qrcode.png` — QR Code yang menyegel seluruh tanda tangan

> QR Code baru dibuat di tahap ini karena QR menyegel semua penandatangan sekaligus. Simpan dokumen asli, `multisignature.json`, kedua public key, dan `qrcode.png` sebagai satu paket.

---

#### Langkah 4 — Verifikasi Multi-Signature

1. Buka tab **✅ Verify Document**.
2. Upload dokumen asli.
3. Upload `nama_dokumen.multisignature.json`.
4. Aplikasi otomatis mendeteksi multi-signature dan menampilkan slot upload public key untuk setiap penandatangan.
5. Upload `public_key_1.pem` pada slot Penandatangan 1.
6. Upload `public_key_2.pem` pada slot Penandatangan 2.
7. Upload `nama_dokumen.multisignature.qrcode.png` (opsional).
8. Klik tombol **Verifikasi Dokumen**.

Hasil yang diharapkan:

```
VALID — Dokumen autentik dan seluruh tanda tangan valid.
1. [Nama Penandatangan 1] — VALID. Signature valid.
2. [Nama Penandatangan 2] — VALID. Signature valid.
QR VALID — Hash QR Code cocok dengan dokumen yang diunggah.
```

---

### C. Audit Trail

Tab **📊 Audit Trail** mencatat seluruh aktivitas penting selama sesi berlangsung.

Aktivitas yang dicatat secara otomatis:

| Event | Severity | Kapan dicatat |
|---|---|---|
| `KEY_GENERATION_SUCCESS` | INFO | Generate key pair berhasil (single maupun multi-signature) |
| `KEY_GENERATION_ERROR` | ERROR | Error saat generate key pair |
| `DOCUMENT_SIGNED` | INFO | Penandatanganan dokumen berhasil |
| `DOCUMENT_SIGN_ERROR` | ERROR | Error saat proses signing |
| `MULTI_SIGNATURE_ADDED` | INFO | Penambahan tanda tangan kedua berhasil |
| `MULTI_SIGNATURE_ERROR` | ERROR | Error saat menambahkan tanda tangan |
| `DOCUMENT_VERIFIED` | INFO | Verifikasi dokumen selesai dan valid |
| `DOCUMENT_VERIFIED` | WARNING | Verifikasi dokumen selesai namun tidak valid |
| `DOCUMENT_VERIFY_ERROR` | ERROR | Error saat proses verifikasi |

Setiap event mencatat: **timestamp (UTC)**, **jenis event**, **nama user**, **document ID** (SHA-256 dokumen), **severity** (INFO / WARNING / ERROR), dan **detail tambahan**.

**Penyimpanan:**
- Data disimpan di **session state** Streamlit selama sesi aktif
- Setiap event baru langsung disinkronkan ke **localStorage browser**
- Audit trail tetap ada setelah refresh halaman, hilang jika cache browser dihapus atau buka di browser lain

**Filter dan download:**
- Filter berdasarkan jenis event atau severity (INFO / WARNING / ERROR)
- Download laporan sebagai `audit_trail.json` atau `audit_trail.txt`
- Tombol **🗑️ Hapus Semua Event** untuk membersihkan log dari session state dan localStorage

---

### D. Skenario Pengujian Kegagalan

#### Dokumen yang Diubah (Tampering)

1. Buat signature dari dokumen asli (ikuti Langkah 1–2 alur A).
2. Ubah isi dokumen (tambah/hapus karakter, atau gunakan script `tamper_file.py`).
3. Di tab **✅ Verify Document**, upload dokumen yang sudah diubah beserta signature JSON dan public key dari dokumen asli.
4. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan:
```
INVALID — Hash dokumen berbeda. Dokumen telah diubah atau bukan dokumen yang ditandatangani.
```

#### Public Key yang Salah

1. Generate pasangan key baru yang berbeda dari key yang digunakan saat signing.
2. Di tab **✅ Verify Document**, upload dokumen asli dan signature JSON yang benar, tetapi gunakan **public key baru** (yang salah).
3. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan:
```
INVALID — Signature tidak cocok dengan public key. Gunakan public key yang benar.
```

#### QR Code dari Dokumen Lain

1. Upload dokumen dan signature JSON yang benar.
2. Upload QR Code dari dokumen atau sesi signing yang berbeda.
3. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan:
```
QR TIDAK COCOK — Hash di QR Code tidak cocok dengan dokumen yang diunggah.
```

---

### E. Memahami Hasil Verifikasi

| Hasil | Artinya |
|---|---|
| **VALID** | Hash dokumen cocok dan signature berhasil diverifikasi dengan public key |
| **INVALID — Hash berbeda** | Dokumen telah berubah sejak ditandatangani |
| **INVALID — Signature tidak cocok** | Public key yang digunakan salah atau signature rusak |
| **QR VALID** | Hash di QR Code cocok dengan dokumen yang diunggah |
| **QR TIDAK COCOK** | Hash di QR berbeda dari dokumen yang diunggah |
| **QR TIDAK TERBACA** | File QR tidak dapat dibaca — gunakan file PNG asli hasil download, bukan screenshot |

> Jika hasil tidak sesuai, pastikan semua file berasal dari satu proses signing yang sama. Membuka dan menyimpan ulang PDF dapat mengubah byte file dan membuat hash berbeda.

---

## Format Signature JSON

**Single-signature (versi 1.1):**

```json
{
  "app_name": "eSignGuard",
  "signature_version": "1.1",
  "algorithm": "Ed25519",
  "hash_algorithm": "SHA-256",
  "document_name": "nama_dokumen.pdf",
  "document_sha256": "<hash-hex>",
  "signature_base64": "<ed25519-signature>",
  "signature_size_bytes": 64,
  "metadata": {
    "signer_name": "Nama Penandatangan",
    "signer_role": "Jabatan",
    "institution": "Institusi",
    "signed_at_utc": "2026-09-29T..."
  }
}
```

**Multi-signature (versi 1.2):**

```json
{
  "app_name": "eSignGuard",
  "signature_version": "1.2",
  "signature_type": "multi-signature",
  "hash_algorithm": "SHA-256",
  "document_name": "nama_dokumen.pdf",
  "document_sha256": "<hash-hex>",
  "signatures": [
    {
      "algorithm": "Ed25519",
      "signature_base64": "<ed25519-signature>",
      "signature_size_bytes": 64,
      "metadata": { "signer_name": "...", "signed_at_utc": "..." }
    },
    {
      "algorithm": "Ed25519",
      "signature_base64": "<ed25519-signature>",
      "signature_size_bytes": 64,
      "metadata": { "signer_name": "...", "signed_at_utc": "..." }
    }
  ]
}
```

---

## Keamanan

- Private key dienkripsi dengan **AES-256** (PKCS8) menggunakan password
- Input user disanitasi untuk mencegah XSS
- Password divalidasi: minimal 8 karakter, mengandung huruf dan angka
- `app_secure.py` menambahkan **password strength indicator** (lemah / sedang / kuat)

⚠️ **PENTING:**
- **Jangan unggah private key atau file `.pem` ke GitHub**
- **Jangan unggah dokumen sensitif ke repository**
- Simpan private key dan password di tempat yang aman
- Backup private key — jika hilang, dokumen tidak bisa diverifikasi ulang

---

## Benchmark & Testing

Hasil benchmark (30 iterasi, dokumen ~5KB):

| Operasi | Rata-rata | Min | Maks |
|---|---|---|---|
| Generate key pair | 4.88 ms | — | — |
| Signing | 0.61 ms | 0.55 ms | 1.07 ms |
| Verifikasi | 0.14 ms | 0.12 ms | 0.25 ms |
| Ukuran signature (base64) | 88 karakter | — | — |
| Ukuran public key (PEM) | 113 byte | — | — |

Reproduksi benchmark dan unit test:

```bash
# Benchmark performa
python benchmark.py

# Unit test (5 test case)
python -m pytest tests/

# Uji baca QR Code (butuh file di folder demo_berhasil/)
python test_qr_read.py
```

---

## 👥 Tim Pengembang

Kelompok eSignGuard — Universitas Siliwangi

| Nama | NIM | Role |
|------|-----|------|
| Ismatul Ilmi | 247006111137 | Backend Developer |
| Nabila Rohmatul Aulia | 247006111143 | Developer |
| Refa Adinda | 247006111197 | QA & Documentation |

### Kontak

- **Ismatul Ilmi**: [Instagram](https://instagram.com/Ilmysma) · [GitHub](https://github.com/Ismatul724)
- **Nabila Rohmatul Aulia**: [Instagram](https://instagram.com/nabilaara_) · [GitHub](https://github.com/NABILAARA)
- **Refa Adinda**: [Instagram](https://www.instagram.com/refaadiindaa) · [GitHub](https://github.com/247006111197-web)

---

## Lisensi

Proyek ini dibuat untuk tujuan edukasi — UTS Keamanan Informasi, Universitas Siliwangi.
