import json
import time
from pathlib import Path

import matplotlib.pyplot as plt

from crypto_utils import (
    generate_key_pair,
    create_signature_data,
    verify_document_signature,
    signature_json_bytes,
)


def create_performance_chart(signing_times, verification_times, output_file):
    """Membuat grafik waktu signing dan verification per iterasi."""
    iterations = list(range(1, len(signing_times) + 1))
    signing_ms = [value * 1000 for value in signing_times]
    verification_ms = [value * 1000 for value in verification_times]

    avg_signing_ms = sum(signing_ms) / len(signing_ms)
    avg_verification_ms = sum(verification_ms) / len(verification_ms)

    plt.figure(figsize=(12, 6))
    plt.plot(
        iterations,
        signing_ms,
        marker="o",
        markersize=4,
        linewidth=1.5,
        color="#2563EB",
        label="Signing",
    )
    plt.plot(
        iterations,
        verification_ms,
        marker="o",
        markersize=4,
        linewidth=1.5,
        color="#16A34A",
        label="Verification",
    )
    plt.axhline(
        avg_signing_ms,
        color="#2563EB",
        linestyle="--",
        linewidth=1.2,
        label=f"Rata-rata Signing ({avg_signing_ms:.3f} ms)",
    )
    plt.axhline(
        avg_verification_ms,
        color="#16A34A",
        linestyle="--",
        linewidth=1.2,
        label=f"Rata-rata Verification ({avg_verification_ms:.3f} ms)",
    )

    plt.title("Benchmark Performa eSignGuard - 30 Iterasi", fontweight="bold")
    plt.xlabel("Percobaan ke-")
    plt.ylabel("Waktu Eksekusi (milidetik / ms)")
    plt.xticks(iterations)
    plt.grid(True, linestyle="--", alpha=0.35)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()


def run_benchmark(num_iterations=30):
    """Jalankan benchmark signing dan verifikasi."""
    password = "benchmarkpassword123"
    document_bytes = b"Test document content for benchmark timing analysis." * 100
    document_name = "benchmark_document.txt"
    signer_name = "Benchmark User"
    signer_role = "Tester"
    institution = "Test Institution"

    print(f"Running benchmark dengan {num_iterations} iterasi...\n")

    print("1. Generate key pair...")
    start = time.perf_counter()
    private_pem, public_pem = generate_key_pair(password)
    keygen_time = time.perf_counter() - start
    print(f"   Waktu generate key: {keygen_time:.4f} detik\n")

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
        print(f"   Signing iterasi {i + 1:02d}: {elapsed * 1000:.4f} ms")

    avg_signing_time = sum(signing_times) / len(signing_times)
    min_signing_time = min(signing_times)
    max_signing_time = max(signing_times)

    print(f"\n   Rata-rata waktu signing: {avg_signing_time:.6f} detik")
    print(f"   Minimum: {min_signing_time:.6f} detik")
    print(f"   Maksimum: {max_signing_time:.6f} detik\n")

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
        print(f"   Verification iterasi {i + 1:02d}: {elapsed * 1000:.4f} ms")

    avg_verification_time = sum(verification_times) / len(verification_times)
    min_verification_time = min(verification_times)
    max_verification_time = max(verification_times)

    print(f"\n   Rata-rata waktu verifikasi: {avg_verification_time:.6f} detik")
    print(f"   Minimum: {min_verification_time:.6f} detik")
    print(f"   Maksimum: {max_verification_time:.6f} detik\n")

    signature_size = len(signature_data["signature_base64"])
    public_key_size = len(public_pem)

    print("4. Ukuran signature dan key:")
    print(f"   Ukuran signature (base64): {signature_size} karakter")
    print(f"   Ukuran public key (PEM): {public_key_size} byte\n")

    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)

    results = {
        "iterations": num_iterations,
        "key_generation_time_sec": keygen_time,
        "signing": {
            "times_sec": signing_times,
            "avg_sec": avg_signing_time,
            "min_sec": min_signing_time,
            "max_sec": max_signing_time,
        },
        "verification": {
            "times_sec": verification_times,
            "avg_sec": avg_verification_time,
            "min_sec": min_verification_time,
            "max_sec": max_verification_time,
        },
        "signature_size_base64_chars": signature_size,
        "public_key_size_bytes": public_key_size,
    }

    json_output_file = output_dir / "benchmark_results.json"
    with open(json_output_file, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2)

    chart_output_file = output_dir / "benchmark_performance_chart.png"
    create_performance_chart(
        signing_times,
        verification_times,
        chart_output_file,
    )

    print(f"5. Hasil JSON disimpan ke: {json_output_file}")
    print(f"6. Grafik benchmark disimpan ke: {chart_output_file}")
    print("\n=== BENCHMARK SELESAI ===\n")

    return results


if __name__ == "__main__":
    run_benchmark(num_iterations=30)