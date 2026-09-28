# eSignGuard

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

Aplikasi web tanda tangan digital dokumen berbasis Python dan Streamlit.

## 🚀 Live Demo

Aplikasi ini sudah di-deploy dan bisa diakses di:

👉 [https://esignguard.streamlit.app/](https://esignguard.streamlit.app/)

## Fitur

- Generate pasangan key Ed25519 (single atau multi-signature)
- Private key disimpan dalam format PEM terenkripsi password
- Tanda tangan dokumen menggunakan hash SHA-256
- Dukungan multi-signature (lebih dari satu penandatangan)
- Pembuatan signature dalam format JSON
- QR Code verifikasi yang menyegel seluruh penandatangan
- Verifikasi dokumen asli (single maupun multi-signature)
- Deteksi perubahan/tampering dokumen
- Deteksi public key yang salah


## Teknologi

- **Python 3.8+**
- **Streamlit** - Framework aplikasi web
- **cryptography** - Library kriptografi
- **Ed25519** - Algoritma tanda tangan digital
- **SHA-256** - Fungsi hash kriptografis
- **qrcode** - Generator QR Code
- **Pillow** - Pemrosesan gambar

## Struktur Folder

- app.py - Aplikasi Streamlit utama
- crypto_utils.py - Fungsi kriptografi (generate key, sign, verify)
- qr_utils.py - Generator QR Code
- qr_verify.py - Verifikasi QR Code
- benchmark.py - Script benchmark performa
- assets/ - Foto tim
- tests/test_crypto.py - Unit test
- data/benchmark_results.json - Hasil benchmark
- requirements.txt - Dependensi Python
- .gitignore - File yang di-ignore Git
- README.md - Dokumentasi ini


## Instalasi

### Linux atau macOS

```bash
git clone <URL_REPOSITORI>
cd esignguard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows

```powershell
git clone <URL_REPOSITORI>
cd esignguard
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```


## Menjalankan Aplikasi

```bash
python -m streamlit run app.py
```

Buka aplikasi di:

```text
http://localhost:8501
```


## Alur Penggunaan Lengkap

---

### A. Tanda Tangan Tunggal (Single Signature)

Digunakan ketika dokumen hanya ditandatangani oleh satu orang.

#### 1. Generate Key

1. Buka tab **🔑 Generate Key**.
2. Masukkan password minimal 8 karakter (harus mengandung huruf dan angka).
3. Masukkan password yang sama pada kolom konfirmasi.
4. Pastikan checkbox **"Aktifkan multi-signature"** tidak dicentang.
5. Klik **Generate Key Pair**.
6. Download dua file yang dihasilkan:
   - `private_key_encrypted.pem`
   - `public_key.pem`

Simpan private key dan password dengan aman. **Jangan mengunggah private key ke GitHub.**

#### 2. Menandatangani Dokumen

1. Buka tab **✍️ Sign Document**.
2. Upload dokumen yang akan ditandatangani.
3. Upload `private_key_encrypted.pem`.
4. Masukkan password private key.
5. Isi nama, jabatan, dan institusi penandatangan.
6. Klik **Tandatangani Dokumen**.
7. Download dua file hasil:
   - `nama_dokumen.signature.json` — berisi hash, signature, dan metadata
   - `nama_dokumen.qrcode.png` — QR Code verifikasi

Simpan dokumen asli, signature JSON, QR Code, dan `public_key.pem` sebagai satu paket.

#### 3. Verifikasi Dokumen

1. Buka tab **✅ Verify Document**.
2. Upload dokumen asli.
3. Upload file `signature.json`.
4. Upload `public_key.pem`.
5. Upload QR Code (opsional).
6. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan:

```
VALID — Dokumen autentik dan tidak berubah.
QR VALID — Hash QR Code cocok dengan dokumen yang diunggah.
```

---

### B. Multi-Signature (Dua Penandatangan)

Digunakan ketika dokumen harus ditandatangani oleh dua orang.

#### 1. Generate 2 Key Pair

1. Buka tab **🔑 Generate Key**.
2. Masukkan password untuk **Penandatangan 1** dan konfirmasinya.
3. Centang checkbox **"Aktifkan multi-signature (generate key untuk 2 penandatangan)"**.
4. Muncul form password untuk **Penandatangan 2** — isi dan konfirmasi.
5. Klik **Generate 2 Key Pair**.
6. Download empat file yang dihasilkan:
   - `private_key_1_encrypted.pem` dan `public_key_1.pem` — untuk Penandatangan 1
   - `private_key_2_encrypted.pem` dan `public_key_2.pem` — untuk Penandatangan 2

#### 2. Penandatangan Pertama Menandatangani

1. Buka tab **✍️ Sign Document**.
2. Muncul info biru: *"Mode multi-signature aktif"*.
3. Upload dokumen yang akan ditandatangani.
4. Upload `private_key_1_encrypted.pem`.
5. Masukkan password Penandatangan 1.
6. Isi nama, jabatan, dan institusi Penandatangan 1.
7. Klik **Tandatangani Dokumen**.
8. Download `nama_dokumen.signature.json` (belum ada QR Code pada tahap ini).

#### 3. Penandatangan Kedua Menambahkan Tanda Tangan

1. Buka tab **➕ Tambah Tanda Tangan**.
2. Upload dokumen yang **sama persis** dengan dokumen di langkah sebelumnya.
3. Upload `nama_dokumen.signature.json` dari langkah sebelumnya.
4. Upload `private_key_2_encrypted.pem`.
5. Masukkan password Penandatangan 2.
6. Isi nama, jabatan, dan institusi Penandatangan 2.
7. Klik **Tambahkan Tanda Tangan**.
8. Download dua file hasil:
   - `nama_dokumen.multisignature.json` — berisi tanda tangan kedua penandatangan
   - `nama_dokumen.multisignature.qrcode.png` — QR Code yang menyegel keduanya

> QR Code hanya tergenerate setelah penandatangan kedua selesai karena QR menyegel seluruh tanda tangan.

#### 4. Verifikasi Multi-Signature

1. Buka tab **✅ Verify Document**.
2. Upload dokumen asli.
3. Upload `nama_dokumen.multisignature.json` — aplikasi otomatis mendeteksi multi-signature dan meminta 2 public key.
4. Upload `public_key_1.pem` untuk Penandatangan 1.
5. Upload `public_key_2.pem` untuk Penandatangan 2.
6. Upload QR Code (opsional).
7. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan:

```
VALID — Dokumen autentik dan seluruh tanda tangan valid.
1. Penandatangan 1 — VALID
2. Penandatangan 2 — VALID
```

---

### C. Menguji Skenario Kegagalan

#### Dokumen yang Diubah (Tampering)

1. Ubah satu karakter pada dokumen asli.
2. Upload dokumen yang sudah diubah di tab **Verify Document**.
3. Gunakan signature JSON dan public key dari dokumen asli.
4. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan: `INVALID — Hash dokumen berbeda.`

#### Public Key yang Salah

1. Generate pasangan key baru.
2. Gunakan public key baru untuk memverifikasi dokumen yang ditandatangani dengan key lama.
3. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan: `INVALID — Signature tidak cocok dengan public key.`

#### QR Code Palsu atau dari Dokumen Lain

1. Upload dokumen dan signature JSON yang benar.
2. Upload QR Code dari dokumen berbeda.
3. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan: `QR TIDAK COCOK — Hash di QR Code tidak cocok dengan dokumen.`

---

### D. Memahami Hasil Verifikasi

| Hasil | Artinya |
|---|---|
| **VALID** | Hash dokumen cocok dan signature berhasil diverifikasi dengan public key |
| **INVALID** | Dokumen berubah, signature rusak, atau public key tidak cocok |
| **QR VALID** | Hash di QR Code cocok dengan dokumen yang diunggah |
| **QR TIDAK COCOK** | Hash di QR berbeda dari dokumen yang diunggah |
| **QR TIDAK TERBACA** | File QR tidak dapat dibaca atau bukan dari eSignGuard |

> Jika hasil tidak sesuai, pastikan semua file berasal dari satu proses signing yang sama. Membuka dan menyimpan ulang PDF dapat mengubah byte file dan membuat hash berbeda.


## Keamanan

- ⚠️ **Jangan unggah private key, password, atau file `.pem` ke GitHub.**
- ⚠️ **Jangan unggah dokumen sensitif ke repository.**
- Private key dibuat dalam format terenkripsi menggunakan password (AES-256).


## Benchmark & Testing

Aplikasi ini telah diuji dengan:

- **Unit test**: 5 test cases (key generation, signing, verification, tampering detection)
- **Benchmark**: 30 iterasi signing dan verification untuk mengukur performa

Hasil benchmark dan test dapat direproduksi dengan menjalankan:

```bash
python benchmark.py
python -m pytest tests/
```

## 👥 Tim Pengembang

| Nama | NIM | Role |
|------|-----|------|
| Ismatul Ilmi | 247006111137 | Backend Developer |
| Nabila Rohmatul Aulia | 247006111143 | Developer |
| Refa Adinda | 247006111197 | QA & Documentation |

### 🌐 Kontak

- **Ismatul Ilmi**: [Instagram](https://instagram.com/Ilmysma) · [GitHub](https://github.com/Ismatul724)
- **Nabila Rohmatul Aulia**: [Instagram](https://instagram.com/nabilaara_) · [GitHub](https://github.com/NABILAARA)
- **Refa Adinda**: [Instagram](https://www.instagram.com/refaadiindaa) · [GitHub](https://github.com/247006111197-web)


## Lisensi

Proyek ini dibuat untuk tujuan edukasi.
