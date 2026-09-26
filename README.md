# eSignGuard

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-green)

Aplikasi web tanda tangan digital dokumen berbasis Python dan Streamlit.

## 🚀 Live Demo

Aplikasi ini sudah di-deploy dan bisa diakses di:

👉 [https://esignguard.streamlit.app/](https://esignguard.streamlit.app/)

## Fitur

- Generate pasangan key Ed25519
- Private key disimpan dalam format PEM terenkripsi password
- Tanda tangan dokumen menggunakan hash SHA-256
- Pembuatan signature dalam format JSON
- Pembuatan QR Code metadata verifikasi
- Verifikasi dokumen asli
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

### 1. Membuat Pasangan Key

1. Buka tab **Generate Key**.
2. Masukkan password minimal 8 karakter.
3. Masukkan password yang sama pada kolom konfirmasi.
4. Klik **Generate Key Pair**.
5. Download dua file yang dihasilkan:
   - `private_key_encrypted.pem`
   - `public_key.pem`

Private key digunakan untuk membuat tanda tangan. Public key digunakan untuk memeriksa tanda tangan. Simpan private key dan password secara aman. **Jangan mengunggah private key atau password ke GitHub.**


### 2. Menandatangani Dokumen

1. Buka tab **Sign Document**.
2. Upload dokumen yang akan ditandatangani.
3. Upload `private_key_encrypted.pem` dari pasangan key yang dibuat.
4. Masukkan password private key.
5. Isi nama penandatangan.
6. Isi jabatan atau peran penandatangan.
7. Isi institusi.
8. Klik **Tandatangani Dokumen**.

Setelah proses berhasil, aplikasi menghitung hash SHA-256 dokumen dan membuat signature Ed25519. Aplikasi menampilkan hash dokumen serta menghasilkan dua file tambahan:

- `nama_dokumen.signature.json`, berisi hash, signature, algoritma, dan metadata.
- `nama_dokumen.qrcode.png`, berisi hash dan metadata verifikasi.

Simpan dokumen asli, signature JSON, QR Code, dan `public_key.pem` sebagai satu paket. Keempat file tersebut harus berasal dari proses signing yang sama.


### 3. Memverifikasi Dokumen Asli

1. Buka tab **Verify Document**.
2. Upload dokumen asli yang belum diubah.
3. Upload file signature JSON yang sesuai.
4. Upload `public_key.pem` pasangannya.
5. Upload QR Code yang sesuai jika ingin memeriksa QR.
6. Klik **Verifikasi Dokumen**.

Jika semua file cocok, hasilnya adalah:

```text
VALID - Dokumen autentik dan tidak berubah.
QR VALID - QR Code cocok dengan dokumen dan signature JSON.
```


### 4. Menguji Dokumen yang Diubah (Tampering)

Untuk demonstrasi tampering:

1. Buat salinan dokumen asli.
2. Ubah satu kata atau satu byte pada salinan tersebut.
3. Upload salinan yang sudah diubah pada tab **Verify Document**.
4. Gunakan signature JSON dan public key dari dokumen asli.
5. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan adalah `INVALID` karena hash dokumen baru berbeda dari hash yang tersimpan di signature JSON.

**Jangan menyimpan perubahan ke file asli yang ingin dipakai sebagai pembanding.**


### 5. Menguji Public Key yang Salah

1. Generate pasangan key baru pada tab **Generate Key**.
2. Jangan gunakan private key baru untuk menandatangani ulang dokumen lama.
3. Pada tab **Verify Document**, upload dokumen lama dan signature JSON lama.
4. Gunakan `public_key.pem` dari pasangan key baru.
5. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan adalah `INVALID` karena signature dibuat menggunakan private key yang berbeda dari public key yang digunakan untuk verifikasi.


### 6. Menguji QR Code Palsu

1. Gunakan dokumen, signature JSON, dan public key yang benar.
2. Upload QR Code yang berasal dari dokumen lain atau QR yang datanya telah diubah.
3. Klik **Verifikasi Dokumen**.

Hasil yang diharapkan adalah `QR INVALID` karena hash atau metadata pada QR tidak cocok dengan dokumen dan signature JSON yang sedang diverifikasi.


### 7. Memahami Hasil Verifikasi

Verifikasi dokumen dan verifikasi QR ditampilkan sebagai hasil terpisah:

- **VALID**: hash dokumen cocok dan signature Ed25519 dapat diverifikasi dengan public key yang diberikan.
- **INVALID**: dokumen berubah, signature rusak, atau public key tidak cocok.
- **QR VALID**: isi QR cocok dengan dokumen dan signature JSON.
- **QR INVALID**: QR tidak terbaca, berasal dari aplikasi lain, atau isinya tidak cocok dengan dokumen/signature JSON.

Jika hasilnya tidak sesuai, pastikan semua file diambil dari satu proses signing. Membuka lalu menyimpan ulang PDF juga dapat mengubah byte file dan membuat hash berbeda.


## Keamanan

- ⚠️ **Jangan unggah private key, password, atau file `.pem` ke GitHub.**
- ⚠️ **Jangan unggah dokumen sensitif ke repository.**
- Private key dibuat dalam format terenkripsi menggunakan password.


## Benchmark & Testing

Aplikasi ini telah diuji dengan:

- **Unit test**: 5 test cases (key generation, signing, verification, tampering detection)
- **Benchmark**: 30 iterasi signing dan verification untuk mengukur performa

Hasil benchmark dan test dapat direproduksi dengan menjalankan:

```bash
python benchmark.py
python -m pytest tests/
```


## Anggota Kelompok

| Nama | NIM |
|------|-----|
| Ismatul Ilmi | 247006111137 |
| Nabila Rohmatul Aulia | 247006111143 |
| Refa Adinda | 247006111197 |


## Lisensi

Proyek ini dibuat untuk tujuan edukasi.