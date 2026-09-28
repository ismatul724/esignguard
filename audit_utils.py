
import json
import os
from datetime import datetime, timezone
import hashlib

class AuditTrail:
    """Modul untuk mengelola audit trail aplikasi eSignGuard"""

    def __init__(self, audit_file_path="audit_trail.json"):
        self.audit_file_path = audit_file_path
        self.ensure_audit_file_exists()

    def ensure_audit_file_exists(self):
        """Memastikan file audit trail ada, jika tidak buat file baru"""
        if not os.path.exists(self.audit_file_path):
            with open(self.audit_file_path, "w") as f:
                json.dump([], f)

    def add_audit_event(self, event_type, user_id=None, document_id=None, details=None, severity="INFO"):
        """
        Menambahkan event ke audit trail

        Args:
            event_type (str): Jenis event (misal: SIGN_DOCUMENT, VERIFY_DOCUMENT, LOGIN)
            user_id (str): ID pengguna yang melakukan aktivitas
            document_id (str): ID dokumen yang terkait
            details (dict): Detail tambahan tentang event
            severity (str): Tingkat keparahan (INFO, WARNING, ERROR, CRITICAL)
        """
        audit_event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "document_id": document_id,
            "details": details or {},
            "severity": severity,
            "ip_address": "UNKNOWN"  # Dalam implementasi sebenarnya, dapat diambil dari request
        }

        # Baca existing audit events
        with open(self.audit_file_path, "r") as f:
            audit_events = json.load(f)

        # Tambahkan event baru
        audit_events.append(audit_event)

        # Simpan kembali ke file
        with open(self.audit_file_path, "w") as f:
            json.dump(audit_events, f, indent=2)

    def get_audit_events(self, event_type=None, user_id=None, document_id=None, start_date=None, end_date=None, limit=100):
        """
        Mengambil event audit berdasarkan filter tertentu

        Args:
            event_type (str): Filter berdasarkan jenis event
            user_id (str): Filter berdasarkan ID pengguna
            document_id (str): Filter berdasarkan ID dokumen
            start_date (datetime): Filter dari tanggal tertentu
            end_date (datetime): Filter hingga tanggal tertentu
            limit (int): Jumlah maksimum event yang dikembalikan

        Returns:
            list: List of audit events
        """
        with open(self.audit_file_path, "r") as f:
            audit_events = json.load(f)

        # Filter events
        filtered_events = []

        for event in audit_events:
            # Filter by event type
            if event_type and event["event_type"] != event_type:
                continue

            # Filter by user ID
            if user_id and event["user_id"] != user_id:
                continue

            # Filter by document ID
            if document_id and event["document_id"] != document_id:
                continue

            # Filter by date range
            event_date = datetime.fromisoformat(event["timestamp"])

            if start_date and event_date < start_date:
                continue

            if end_date and event_date > end_date:
                continue

            filtered_events.append(event)

        # Urutkan berdasarkan timestamp terbaru
        filtered_events.sort(key=lambda x: x["timestamp"], reverse=True)

        # Batasi jumlah hasil
        return filtered_events[:limit]

    def generate_audit_report(self, start_date=None, end_date=None, format="json"):
        """
        Mengenerate laporan audit dalam format yang dipilih

        Args:
            start_date (datetime): Tanggal mulai laporan
            end_date (datetime): Tanggal akhir laporan
            format (str): Format laporan (json, csv, txt)

        Returns:
            str: Laporan dalam format yang dipilih
        """
        events = self.get_audit_events(start_date=start_date, end_date=end_date)

        if format == "json":
            return json.dumps(events, indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=events[0].keys() if events else [])
            writer.writeheader()
            writer.writerows(events)

            return output.getvalue()

        elif format == "txt":
            report_lines = []

            if start_date and end_date:
                report_lines.append(f"Laporan Audit: {start_date.date()} - {end_date.date()}")
            else:
                report_lines.append("Laporan Audit: Semua Data")

            report_lines.append("=" * 50)

            for event in events:
                report_lines.append(f"Timestamp: {event['timestamp']}")
                report_lines.append(f"Event: {event['event_type']}")
                report_lines.append(f"User: {event['user_id']}")
                report_lines.append(f"Document: {event['document_id']}")
                report_lines.append(f"Severity: {event['severity']}")
                report_lines.append("Details:")

                for key, value in event['details'].items():
                    report_lines.append(f"  {key}: {value}")

                report_lines.append("-" * 30)

            return "\n".join(report_lines)

        else:
            raise ValueError(f"Format laporan tidak dikenal: {format}")

    def get_audit_summary(self, start_date=None, end_date=None):
        """
        Mengenerate ringkasan aktivitas audit

        Args:
            start_date (datetime): Tanggal mulai analisis
            end_date (datetime): Tanggal akhir analisis

        Returns:
            dict: Ringkasan statistik audit
        """
        events = self.get_audit_events(start_date=start_date, end_date=end_date)

        # Hitung berdasarkan jenis event
        event_counts = {}
        for event in events:
            event_type = event["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Hitung berdasarkan tingkat keparahan
        severity_counts = {}
        for event in events:
            severity = event["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Hitung berdasarkan pengguna
        user_counts = {}
        for event in events:
            user_id = event["user_id"]
            user_counts[user_id] = user_counts.get(user_id, 0) + 1

        return {
            "total_events": len(events),
            "event_type_counts": event_counts,
            "severity_counts": severity_counts,
            "user_counts": user_counts,
            "date_range": {
                "start": min([e["timestamp"] for e in events]) if events else None,
                "end": max([e["timestamp"] for e in events]) if events else None
            }
        }

# Fungsi untuk membuat hash dokumen (digunakan untuk ID dokumen)
def create_document_id(document_content):
    """Menggunakan hash SHA-256 sebagai ID dokumen"""
    return hashlib.sha256(document_content).hexdigest()

# Fungsi untuk membuat ID pengguna (jika tidak tersedia)
def create_user_id():
    """Menggunakan timestamp dan random string untuk membuat ID pengguna unik"""
    import uuid
    return f"user_{uuid.uuid4().hex[:8]}"
