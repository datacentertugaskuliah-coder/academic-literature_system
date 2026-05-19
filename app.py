"""
Academic Literature Analysis System
Streamlit Cloud Deployment
"""

import streamlit as st
import os

# ─── Konfigurasi halaman ───────────────────────────────────────────
st.set_page_config(
    page_title="Academic Literature Analysis System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "Academic Literature Analysis System — Core Layer v2.1 — 11 Modul (M0–M9)"
    }
)

# ─── Hilangkan padding default Streamlit agar dashboard full-width ──
st.markdown("""
<style>
    /* Hapus semua padding default Streamlit */
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    /* Sembunyikan header dan footer Streamlit */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    footer {
        display: none !important;
    }
    /* Pastikan iframe full width */
    iframe {
        width: 100% !important;
        border: none !important;
    }
    /* Hilangkan scrollbar luar */
    .main {
        overflow: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# ─── Baca file HTML dashboard ──────────────────────────────────────
HTML_FILE = os.path.join(os.path.dirname(__file__), "dashboard.html")

def load_dashboard():
    """Load HTML dashboard dari file."""
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

html_content = load_dashboard()

if html_content is None:
    st.error(
        "File dashboard.html tidak ditemukan. "
        "Pastikan file dashboard.html ada di folder yang sama dengan app.py."
    )
    st.stop()

# ─── Render dashboard HTML ─────────────────────────────────────────
# Gunakan tinggi layar penuh dengan JavaScript untuk deteksi
# dan scrolling=False agar dashboard mengontrol scroll sendiri
st.components.v1.html(
    html_content,
    height=920,        # Cukup untuk sebagian besar layar laptop
    scrolling=False    # Dashboard punya internal scroll per panel
)

# ─── Deteksi layar kecil dan tampilkan scrolling ──────────────────
# Untuk perangkat mobile, tambahkan scrolling
st.markdown("""
<script>
// Sesuaikan tinggi iframe dengan layar
(function() {
    var iframes = document.querySelectorAll('iframe');
    iframes.forEach(function(iframe) {
        var h = window.innerHeight;
        if (h > 0) {
            iframe.style.height = h + 'px';
        }
    });
    window.addEventListener('resize', function() {
        var iframes = document.querySelectorAll('iframe');
        iframes.forEach(function(iframe) {
            iframe.style.height = window.innerHeight + 'px';
        });
    });
})();
</script>
""", unsafe_allow_html=True)
