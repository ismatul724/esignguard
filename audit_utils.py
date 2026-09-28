import hashlib
import json
import uuid
from datetime import datetime, timezone

import streamlit as st


class AuditTrail:
    """
    Modul audit trail eSignGuard.

    Event disimpan di st.session_state sehingga:
    - Persisten selama sesi browser aktif
    - Tidak bergantung pada file disk (aman di Streamlit Cloud)
    - Hilang saat user refresh/tutup browser (sesuai sifat Streamlit)
    """

    SESSION_KEY = "audit_events"

    def _get_events(self) -> list:
        """Ambil daftar event dari session state."""
        if self.SESSION_KEY not in st.session_state:
            st.session_state[self.SESSION_KEY] = []
        return st.session_state[self.SESSION_KEY]

    def add_audit_event(
        self,
        event_type: str,
        user_id: str = None,
        document_id: str = None,
        details: dict = None,
        severity: str = "INFO",
    ) -> None:
        """
        Tambahkan event baru ke audit trail.

        Args:
            event_type : Jenis event (DOCUMENT_SIGNED, DOCUMENT_VERIFIED, dll)
            user_id    : Nama penandatangan atau identifier user
            document_id: SHA-256 hash dokumen sebagai ID unik
            details    : Dict berisi detail tambahan event
            severity   : INFO | WARNING | ERROR | CRITICAL
        """
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id or "-",
            "document_id": document_id or "-",
            "details": details or {},
            "severity": severity,
        }
        events = self._get_events()
        events.append(event)
        st.session_state[self.SESSION_KEY] = events

    def get_audit_events(
        self,
        event_type: str = None,
        user_id: str = None,
        document_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 200,
    ) -> list:
        """Ambil event audit dengan filter opsional, diurutkan terbaru di atas."""
        events = self._get_events()
        filtered = []

        for event in events:
            if event_type and event["event_type"] != event_type:
                continue
            if user_id and user_id.lower() not in event["user_id"].lower():
                continue
            if document_id and event["document_id"] != document_id:
                continue
            if start_date or end_date:
                event_dt = datetime.fromisoformat(event["timestamp"])
                if start_date and event_dt < start_date:
                    continue
                if end_date and event_dt > end_date:
                    continue
            filtered.append(event)

        filtered.sort(key=lambda x: x["timestamp"], reverse=True)
        return filtered[:limit]

    def get_audit_summary(self) -> dict:
        """Ringkasan statistik audit trail sesi ini."""
        events = self.get_audit_events(limit=9999)

        event_counts: dict = {}
        severity_counts: dict = {}

        for event in events:
            event_counts[event["event_type"]] = (
                event_counts.get(event["event_type"], 0) + 1
            )
            severity_counts[event["severity"]] = (
                severity_counts.get(event["severity"], 0) + 1
            )

        return {
            "total_events": len(events),
            "event_type_counts": event_counts,
            "severity_counts": severity_counts,
        }

    def generate_audit_report(self, format: str = "json") -> str:
        """Generate laporan audit dalam format json atau txt."""
        events = self.get_audit_events(limit=9999)

        if format == "json":
            return json.dumps(events, indent=2, ensure_ascii=False)

        # format txt
        lines = ["LAPORAN AUDIT TRAIL — eSignGuard", "=" * 50]
        for event in events:
            lines.append(f"Timestamp  : {event['timestamp']}")
            lines.append(f"Event      : {event['event_type']}")
            lines.append(f"User       : {event['user_id']}")
            lines.append(f"Dokumen ID : {event['document_id']}")
            lines.append(f"Severity   : {event['severity']}")
            if event["details"]:
                lines.append("Detail     :")
                for k, v in event["details"].items():
                    lines.append(f"  {k}: {v}")
            lines.append("-" * 40)

        return "\n".join(lines)

    def clear(self) -> None:
        """Hapus semua event audit dari session state."""
        st.session_state[self.SESSION_KEY] = []


def create_document_id(document_bytes: bytes) -> str:
    """SHA-256 dokumen sebagai ID unik."""
    return hashlib.sha256(document_bytes).hexdigest()
