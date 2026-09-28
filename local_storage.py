"""
local_storage.py — Utilitas baca/tulis localStorage browser untuk Streamlit.

Cara kerja:
- WRITE: inject JS yang menulis JSON ke localStorage["esignguard_audit"]
- READ : inject JS yang membaca localStorage dan mengirim nilai ke Streamlit
         via URL hash, lalu dibaca dari st.query_params
"""

import json
import streamlit as st
import streamlit.components.v1 as components


STORAGE_KEY = "esignguard_audit"


def save_to_localstorage(events: list) -> None:
    """
    Tulis daftar event audit ke localStorage browser.
    Dipanggil setiap kali ada event baru ditambahkan.
    """
    try:
        data_json = json.dumps(events, ensure_ascii=False)
        # Escape backtick dan backslash agar aman di dalam template literal JS
        data_json_escaped = data_json.replace("\\", "\\\\").replace("`", "\\`")

        js_code = f"""
        <script>
        (function() {{
            try {{
                localStorage.setItem("{STORAGE_KEY}", `{data_json_escaped}`);
            }} catch(e) {{
                console.warn("eSignGuard: gagal menyimpan audit ke localStorage", e);
            }}
        }})();
        </script>
        """
        components.html(js_code, height=0, scrolling=False)
    except Exception:
        pass


def load_from_localstorage() -> list:
    """
    Baca daftar event audit dari localStorage browser.

    Cara kerja:
    1. Inject JS yang membaca localStorage dan set query param "audit_data"
    2. Streamlit membaca query param tersebut
    3. Parse JSON dan kembalikan sebagai list

    Returns:
        List event audit dari localStorage, atau [] jika kosong/error.
    """
    try:
        # Baca query param yang di-set oleh JS di render sebelumnya
        params = st.query_params
        raw = params.get("audit_data", "")
        if raw and raw != "empty":
            events = json.loads(raw)
            if isinstance(events, list):
                return events
    except Exception:
        pass
    return []


def inject_localstorage_reader() -> None:
    """
    Inject JS yang membaca localStorage dan mengirim ke Streamlit
    via query param "audit_data".

    Harus dipanggil SEKALI di awal render app (sebelum session state diisi).
    Hasilnya baru tersedia di render BERIKUTNYA (karena Streamlit re-render
    setelah query param berubah).
    """
    js_code = f"""
    <script>
    (function() {{
        try {{
            var data = localStorage.getItem("{STORAGE_KEY}");
            if (data) {{
                // Kirim ke Streamlit via URL query param
                var url = new URL(window.location.href);
                var current = url.searchParams.get("audit_data");
                // Hanya update jika berbeda untuk menghindari loop
                var incoming = data.substring(0, 500); // cukup 500 char untuk cek
                if (!current || current.length < 10) {{
                    url.searchParams.set("audit_data", data);
                    window.history.replaceState(null, "", url.toString());
                    // Trigger Streamlit rerun via klik tombol tersembunyi
                    window.location.href = url.toString();
                }}
            }} else {{
                var url = new URL(window.location.href);
                url.searchParams.set("audit_data", "empty");
                window.history.replaceState(null, "", url.toString());
            }}
        }} catch(e) {{
            console.warn("eSignGuard: gagal membaca localStorage", e);
        }}
    }})();
    </script>
    """
    components.html(js_code, height=0, scrolling=False)


def clear_localstorage() -> None:
    """Hapus data audit dari localStorage browser."""
    try:
        js_code = f"""
        <script>
        (function() {{
            try {{
                localStorage.removeItem("{STORAGE_KEY}");
                var url = new URL(window.location.href);
                url.searchParams.delete("audit_data");
                window.history.replaceState(null, "", url.toString());
            }} catch(e) {{
                console.warn("eSignGuard: gagal menghapus localStorage", e);
            }}
        }})();
        </script>
        """
        components.html(js_code, height=0, scrolling=False)
        # Hapus query param di sisi Python juga
        if "audit_data" in st.query_params:
            del st.query_params["audit_data"]
    except Exception:
        pass
