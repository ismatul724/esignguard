
# Implementasi Keamanan Aplikasi eSignGuard

## Ringkasan Perubahan

Dokumen ini menjelaskan implementasi perubahan keamanan pada aplikasi eSignGuard untuk meningkatkan keamanan dan mengatasi kerentanan yang telah diidentifikasi.

## Struktur File Baru

### 1. `security_utils.py`
Modul utilitas keamanan yang berisi:
- Enkripsi data sementara dengan PBKDF2
- Validasi kekuatan password
- Sanitasi input untuk mencegah XSS
- Manajemen session yang aman
- Validasi file upload
- Logging keamanan
- Rate limiting

### 2. `config.py`
Konfigurasi aplikasi termasuk:
- Pengaturan keamanan
- Konfigurasi HTTPS
- Konfigurasi session
- Header keamanan

### 3. `app_secure.py`
Versi aman dari aplikasi utama dengan:
- Session management yang ditingkatkan
- Validasi input yang lebih ketat
- Logging keamanan
- Rate limiting
- Penanganan error yang lebih baik

### 4. `requirements_secure.txt`
Daftar dependensi yang diperbarui dengan library keamanan tambahan.

### 5. `run_secure.py`
Skrip untuk menjalankan aplikasi dengan konfigurasi keamanan.

## Cara Mengimplementasikan

### 1. Instalasi Dependensi Baru

```bash
pip install -r requirements_secure.txt
```

### 2. Menjalankan Aplikasi Aman

Untuk pengembangan (HTTP):
```bash
python run_secure.py
```

Untuk produksi (HTTPS):
```bash
python run_secure.py --ssl
```

Atau secara langsung dengan Streamlit:
```bash
streamlit run app_secure.py
```

### 3. Konfigurasi HTTPS

Untuk menggunakan HTTPS, Anda memerlukan sertifikat SSL. Anda dapat:
1. Menggunakan sertifikat yang dikeluarkan oleh CA (Certificate Authority)
2. Mengenerate self-signed certificate untuk pengujian:

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

Kemudian, tambahkan path ke sertifikat dalam `config.py`:
```python
Config.CERTIFICATE_PATH = "path/to/cert.pem"
Config.PRIVATE_KEY_PATH = "path/to/key.pem"
```

### 4. Konfigurasi Tambahan

Anda dapat menyesuaikan pengaturan keamanan di `config.py`:
- `SESSION_TIMEOUT`: Waktu timeout session (dalam menit)
- `MAX_PASSWORD_LENGTH`: Panjang maksimal password
- `MIN_PASSWORD_LENGTH`: Panjang minimal password
- `RATE_LIMIT_REQUESTS`: Batas permintaan rate limiting
- `ALLOWED_FILE_EXTENSIONS`: Ekstensi file yang diizinkan

## Perubahan Spesifik pada Fitur

### 1. Session Management

- **Sebelumnya**: Data disimpan langsung di `st.session_state`
- **Sekarang**: Menggunakan kelas `SecureSession` dengan enkripsi data sensitif
- **Implementasi**:
  ```python
  secure_session = SecureSession()
  secure_session.store_data("private_key", private_key, encrypt=True, password=password)
  ```

### 2. Validasi Password

- **Sebelumnya**: Hanya memeriksa panjang minimal 8 karakter
- **Sekarang**: Memeriksa kompleksitas (huruf kapital, huruf kecil, angka, simbol)
- **Implementasi**:
  ```python
  is_valid, message = validate_password_strength(password)
  if not is_valid:
      st.error(message)
  ```

### 3. Sanitasi Input

- **Sebelumnya**: Tidak ada sanitasi input
- **Sekarang**: Menghapus karakter berbahaya dan membatasi panjang input
- **Implementasi**:
  ```python
  signer_name = sanitize_input(signer_name, max_length=100)
  ```

### 4. Rate Limiting

- **Sebelumnya**: Tidak ada batas permintaan
- **Sekarang**: Menerapkan rate limiting untuk mencegah abuse
- **Implementasi**:
  ```python
  rate_limiter = RateLimiter(max_requests=10, time_window=60)
  if not rate_limiter.is_allowed("document_signing"):
      st.error("Anda telah melebihi batas penandatangan dokumen.")
  ```

### 5. Logging Keamanan

- **Sebelumnya**: Tidak ada logging keamanan
- **Sekarang**: Mencatat semua aktivitas sensitif
- **Implementasi**:
  ```python
  log_security_event("DOCUMENT_SIGNING_SUCCESS", {
      "time": datetime.now().isoformat(),
      "document_name": document_file.name,
      "signer_name": signer_name
  })
  ```

## Cara Menggunakan Aplikasi yang Ditingkatkan

1. **Generate Key**:
   - Password harus memenuhi persyaratan keamanan yang lebih ketat
   - Private key dienkripsi dengan PBKDF2

2. **Sign Document**:
   - Input divalidasi dan disanitasi
   - File divalidasi untuk ukuran dan tipe
   - Aktivitas dicatat untuk audit

3. **Verify Document**:
   - Session diperiksa sebelum memproses
   - Rate limiting diterapkan

## Penanganan Error yang Ditingkatkan

- Pesan error yang lebih umum untuk user
- Detail error dicatat untuk debugging
- Notifikasi untuk error kritis

## Keamanan Tambahan

- Header keamanan HTTP ditambahkan
- Validasi CSRF diterapkan
- Proteksi terhadap serangan brute force
- Session timeout otomatis

## Panduan Pemeliharaan

1. **Pembaruan Reguler**:
   - Pantau CVE untuk dependensi
   - Perbarui library secara berkala

2. **Monitoring**:
   - Periksa log keamanan secara berkala
   - Pantau aktivitas mencurigakan

3. **Backup**:
   - Backup konfigurasi dan data secara berkala
   - Simpan log keamanan untuk audit

## Kesimpulan

Implementasi perubahan keamanan ini secara signifikan meningkatkan keamanan aplikasi eSignGuard dengan mengatasi kerentanan yang telah diidentifikasi. Aplikasi sekarang memiliki:
- Session management yang lebih aman
- Validasi input yang lebih ketat
- Proteksi terhadap serangan web umum
- Logging dan monitoring keamanan
- Rate limiting untuk mencegah abuse

Dengan implementasi ini, aplikasi eSignGuard menjadi lebih aman dan dapat diandalkan untuk digunakan dalam lingkungan produksi.
