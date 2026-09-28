"""
local_storage.py — Utilitas baca/tulis localStorage browser untuk Streamlit.

Menggunakan library streamlit-local-storage yang menangani komunikasi
browser↔server dengan benar via Streamlit component protocol.
"""

import json
from streamlit_local_storage import LocalStorage

STORAGE_KEY = "esignguard_audit"

# Inisialisasi satu instance (singleton per sesi)
_ls = LocalStorage()


def save_to_localstorage(events: list) -> None:
    """
    Tulis daftar event audit ke localStorage browser.
    Dipanggil setiap kali ada event baru ditambahkan.
    """
    try:
        _ls.setItem(STORAGE_KEY, json.dumps(events, ensure_ascii=False))
    except Exception:
        pass


def load_from_localstorage() -> list:
    """
    Baca daftar event audit dari localStorage browser.

    Returns:
        List event audit dari localStorage, atau [] jika kosong/error.
    """
    try:
        raw = _ls.getItem(STORAGE_KEY)
        if raw:
            events = json.loads(raw)
            if isinstance(events, list):
                return events
    except Exception:
        pass
    return []


def clear_localstorage() -> None:
    """Hapus data audit dari localStorage browser."""
    try:
        _ls.deleteItem(STORAGE_KEY)
    except Exception:
        pass
