import json
import time
from pathlib import Path

from crypto_utils import (
    generate_key_pair,
    create_signature_data,
    verify_document_signature,
    signature_json_bytes,
)


def run_benchmark(num_iterations=30):
    """Jalankan benchmark signing dan verifikasi."""
    password = "benchmarkpassword123"
    document_bytes = b"Test document content for benchmark timing analysis." * 100
    document_name = "benchmark_document.txt"
    signer_name = "Benchmark User"
    signer_role = "Tester"
    institution = "Test Institution"

    print(f"Running benchmark dengan {num_iterations} iterasi...\n")

    # Generate key pair
    print("1. Generate key pair...")
    start = time.perf_counter()
    private_pem, public_pem = generate_key_pair(password)
    keygen_time = time.perf_counter() - start
    print(f"   Waktu generate key: {keygen_time:.4f} detik\n")

    # Benchmark signing
    print("2. Benchmark signing...")
    signing_times = []
    signature_data_list = []

    for i in range(num_iterations):
        start = time.perf_counter()
        signature_data, document_hash = create_signature_data(
            document_bytes=document_bytes,
            document_name=document_name,
            private_key_pem=private_pem,
            password=password,
            signer_name=signer_name,
            signer_role=signer_role,
            institution=institution,
        )
        elapsed = time.perf_counter() - start
        signing_times.append(elapsed)
        signature_data_list.append(signature_data)

    avg_signing_time = sum(signing_times) / len(signing_times)
    min_signing_time = min(signing_times)
    max_signing_time = max(signing_times)

    print(f"   Rata-rata waktu signing: {avg_signing_time:.4f} detik")
    print(f"   Minimum: {min_signing_time:.4f} detik")
    print(f"   Maksimum: {max_signing_time:.4f} detik\n")

    # Benchmark verifikasi
    print("3. Benchmark verifikasi...")
    json_bytes = signature_json_bytes(signature_data)
    verification_times = []

    for i in range(num_iterations):
        start = time.perf_counter()
        result = verify_document_signature(
            document_bytes=document_bytes,
            signature_json_bytes=json_bytes,
            public_key_pem=public_pem,
        )
        elapsed = time.perf_counter() - start
        verification_times.append(elapsed)

    avg_verification_time = sum(verification_times) / len(verification_times)
    min_verification_time = min(verification_times)
    max_verification_time = max(verification_times)

    print(f"   Rata-rata waktu verifikasi: {avg_verification_time:.4f} detik")
    print(f"   Minimum: {min_verification_time:.4f} detik")
    print(f"   Maksimum: {max_verification_time:.4f} detik\n")

    # Ukuran signature dan public key
    signature_size = len(signature_data["signature_base64"])
    public_key_size = len(public_pem)

    print("4. Ukuran signature dan key:")
    print(f"   Ukuran signature (base64): {signature_size} karakter")
    print(f"   Ukuran public key (PEM): {public_key_size} byte\n")

    # Simpan hasil ke JSON
    results = {
        "iterations": num_iterations,
        "key_generation_time_sec": keygen_time,
        "signing": {
            "avg_sec": avg_signing_time,
            "min_sec": min_signing_time,
            "max_sec": max_signing_time,
        },
        "verification": {
            "avg_sec": avg_verification_time,
            "min_sec": min_verification_time,
            "max_sec": max_verification_time,
        },
        "signature_size_base64_chars": signature_size,
        "public_key_size_bytes": public_key_size,
    }

    output_file = Path("data/benchmark_results.json")
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"5. Hasil disimpan ke: {output_file}")
    print("\n=== BENCHMARK SELESAI ===\n")

    return results


if __name__ == "__main__":
    run_benchmark(num_iterations=30)