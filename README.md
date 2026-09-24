# eSignGuard

Aplikasi web tanda tangan digital dokumen berbasis Python dan Streamlit.

## Fitur saat ini

- Generate pasangan key Ed25519
- Private key disimpan dalam format PEM terenkripsi password
- Tanda tangan dokumen menggunakan hash SHA-256
- Pembuatan signature dalam format JSON
- Pembuatan QR Code metadata verifikasi
- Verifikasi dokumen asli
- Deteksi perubahan/tampering dokumen
- Deteksi public key yang salah

## Teknologi

- Python
- Streamlit
- cryptography
- Ed25519
- SHA-256
- qrcode
- Pillow

## Instalasi

```bash
git clone <URL_REPOSITORI>
cd esignguard
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

## Menjalankan aplikasi

```bash
python -m streamlit run app.py
```

Buka aplikasi di:

```text
http://localhost:8501
```

## Keamanan

- Jangan unggah private key, password, atau file `.pem` ke GitHub.
- Jangan unggah dokumen sensitif ke repository.
- Private key dibuat dalam format terenkripsi menggunakan password.

## Anggota Kelompok

- Ismatul Ilmi — NPM
- Nabila Rohmatul Aulia — NPM
- Refa Adinda — NPM