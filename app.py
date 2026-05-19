"""
Academic Literature Analysis System
Streamlit Cloud Deployment — v2.1
Bahasa Indonesia Ilmiah (PUEBI) + Italic Istilah Asing
"""

import streamlit as st
import re
import os

# ─── Konfigurasi halaman ───────────────────────────────────────────
st.set_page_config(
    page_title="Sistem Analisis Literatur Akademik",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': (
            "Sistem Analisis Literatur Akademik\n"
            "Core Layer v2.1 — 11 Modul (M0–M9)\n"
            "Bahasa Indonesia Ilmiah sesuai PUEBI"
        )
    }
)

# ─── Daftar istilah asing (wajib italic sesuai PUEBI) ─────────────
ISTILAH_ASING = sorted([
    "systematic literature review", "scoping review", "narrative review",
    "literature review", "mixed methods", "grounded theory", "action research",
    "case study", "quasi-experiment", "randomized controlled trial",
    "meta-analysis", "sampling", "purposive sampling", "snowball sampling",
    "convenience sampling", "triangulation", "validity", "reliability",
    "inter-rater reliability", "construct validity", "content validity",
    "machine learning", "deep learning", "neural network", "artificial intelligence",
    "natural language processing", "large language model", "generative ai",
    "computer vision", "transfer learning", "fine-tuning", "pre-training",
    "dataset", "training", "testing", "validation", "preprocessing",
    "feature extraction", "feature engineering", "dimensionality reduction",
    "clustering", "classification", "reinforcement learning",
    "supervised learning", "unsupervised learning", "semi-supervised learning",
    "embedding", "tokenizer", "tokenization", "inference", "deployment",
    "accuracy", "precision", "recall", "f1-score", "confusion matrix",
    "hyperparameter", "overfitting", "underfitting", "dropout", "batch size",
    "epoch", "learning rate", "optimizer", "loss function", "backpropagation",
    "convolutional neural network", "recurrent neural network", "transformer",
    "attention mechanism", "encoder", "decoder", "autoencoder",
    "random forest", "support vector machine", "naive bayes", "k-means",
    "gradient boosting", "xgboost", "principal component analysis",
    "gap", "novelty", "framework", "state of the art", "best practice",
    "benchmark", "baseline", "finding", "stakeholder", "review",
    "feedback", "insight", "outcome", "impact", "deliverable",
    "proof of concept", "use case", "user story",
    "workflow", "pipeline", "dashboard", "interface", "platform",
    "database", "repository", "cluster", "module", "plugin",
    "software", "hardware", "firmware", "middleware", "backend", "frontend",
    "cloud computing", "edge computing", "internet of things",
    "application programming interface", "user interface", "user experience",
    "open source", "agile", "scrum", "devops",
    "open access", "peer review", "preprint", "abstract", "keywords",
    "doi", "citation", "impact factor", "h-index", "quartile",
    "upload", "download", "input", "output", "template", "prompt",
    "link", "online", "offline", "real-time", "update", "setting",
    "mean", "median", "standard deviation", "variance", "t-test",
    "chi-square", "anova", "regression", "correlation", "p-value",
    "confidence interval", "effect size", "odds ratio",
], key=len, reverse=True)

KATA_SERAPAN = {
    "analisis", "metode", "metodologi", "data", "sistem", "model",
    "program", "komputer", "internet", "digital", "teknologi", "informasi",
    "komunikasi", "jaringan", "basis", "format", "standar", "prosedur",
    "teknik", "instrumen", "instruksi", "parameter", "variabel", "faktor",
    "proses", "produk", "proyek", "aktivitas", "strategi", "evaluasi",
    "implementasi", "integrasi", "optimasi", "simulasi", "visualisasi",
    "dokumentasi", "publikasi", "presentasi", "demonstrasi", "eksperimen",
    "observasi", "survei", "wawancara", "kuesioner", "sampel", "populasi",
    "hipotesis", "teori", "konsep", "definisi", "kriteria", "indikator",
    "dimensi", "aspek", "komponen", "elemen", "struktur", "fungsi",
    "efektivitas", "efisiensi", "kualitas", "kuantitas", "kapasitas",
}


def format_puebi(teks: str) -> str:
    """Format teks sesuai PUEBI: italic istilah asing, ejaan baku."""
    if not teks or not teks.strip():
        return teks

    pelindung = {}
    n = [0]

    def lindungi(m):
        k = f"__PELINDUNG_{n[0]}__"
        pelindung[k] = m.group(0)
        n[0] += 1
        return k

    # Lindungi konten yang tidak boleh diubah
    t = re.sub(r'```[\s\S]*?```', lindungi, teks)
    t = re.sub(r'`[^`]+`', lindungi, t)
    t = re.sub(r'\*[^*\n]+\*', lindungi, t)       # sudah italic
    t = re.sub(r'\[.*?\]\(.*?\)', lindungi, t)
    t = re.sub(r'https?://\S+', lindungi, t)
    t = re.sub(r'\[[A-Z][^\]]{0,60}\]', lindungi, t)  # marker epistemic

    # Terapkan italic istilah asing
    for istilah in ISTILAH_ASING:
        if istilah.lower() in KATA_SERAPAN:
            continue
        pola = r'(?<!\*)\b(' + re.escape(istilah) + r')\b(?!\*)'
        t = re.sub(pola, r'*\1*', t, flags=re.IGNORECASE)

    # Koreksi PUEBI dasar
    koreksi = [
        (r'\bdikarenakan\b', 'karena'),
        (r'\bdipersilahkan\b', 'dipersilakan'),
        (r'\bmerubah\b', 'mengubah'),
        (r'\bterdiri dari\b', 'terdiri atas'),
        (r'\bdidalam\b', 'di dalam'),
        (r'\bdiluar\b', 'di luar'),
        (r'\bdiatas\b', 'di atas'),
        (r'\bdibawah\b', 'di bawah'),
        (r'\bdisamping\b', 'di samping'),
        (r'\bdibelakang\b', 'di belakang'),
        (r'\bdidepan\b', 'di depan'),
        (r'([,;:])([^\s\*])', r'\1 \2'),
        (r'  +', ' '),
    ]
    for pola, ganti in koreksi:
        t = re.sub(pola, ganti, t)

    # Kembalikan konten yang dilindungi
    for k, v in pelindung.items():
        t = t.replace(k, v)

    return t


def hitung_statistik(asli: str, hasil: str) -> dict:
    return {
        'kata': len(asli.split()),
        'italic': len(re.findall(r'\*[^*]+\*', hasil)),
        'paragraf': asli.count('\n\n') + 1,
        'karakter': len(asli),
    }


# ─── CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 0 !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 100% !important;
}
header[data-testid="stHeader"] { display: none !important; }
footer { display: none !important; }
iframe { width: 100% !important; border: none !important; }
.stTabs [data-baseweb="tab-list"] {
    gap: 8px; background: #f8f7f4;
    padding: 8px; border-radius: 10px; margin-bottom: 1rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; padding: 8px 20px; font-weight: 500;
}
.stTabs [aria-selected="true"] {
    background: #3c3489 !important; color: white !important;
}
.stat-card {
    background: #f1efe8; border: 1px solid #e2e0d8;
    border-radius: 10px; padding: 14px; text-align: center;
}
.stat-val { font-size: 26px; font-weight: 700; color: #3c3489; }
.stat-lbl { font-size: 12px; color: #888780; margin-top: 2px; }
.puebi-note {
    background: #eeedfe; border: 1px solid #afa9ec;
    border-radius: 8px; padding: 10px 14px;
    font-size: 13px; color: #3c3489; margin-bottom: 1rem;
}
.istilah-tag {
    display: inline-block; background: #faeeda;
    border: 1px solid #fac775; border-radius: 4px;
    padding: 1px 6px; font-size: 11px; margin: 2px;
    color: #633806; font-style: italic;
}
</style>
""", unsafe_allow_html=True)

# ─── Tab utama ─────────────────────────────────────────────────────
tab1, tab2 = st.tabs([
    "📋  Dashboard Prompt",
    "🔤  Pemformat Keluaran PUEBI"
])

# ══════════════════════════════════════════════════════
# TAB 1 — Dashboard Prompt
# ══════════════════════════════════════════════════════
with tab1:
    HTML_FILE = os.path.join(os.path.dirname(__file__), "dashboard.html")

    def muat_dashboard():
        try:
            with open(HTML_FILE, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return None

    html_content = muat_dashboard()

    if html_content is None:
        st.error(
            "⚠️ Berkas dashboard.html tidak ditemukan. "
            "Pastikan berkas berada di folder yang sama dengan app.py."
        )
        st.stop()

    st.components.v1.html(html_content, height=920, scrolling=False)

    st.markdown("""
    <script>
    (function() {
        function sesuaikanTinggi() {
            var iframes = document.querySelectorAll('iframe');
            var h = window.innerHeight - 80;
            iframes.forEach(function(f) { f.style.height = h + 'px'; });
        }
        sesuaikanTinggi();
        window.addEventListener('resize', sesuaikanTinggi);
    })();
    </script>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 2 — Pemformat Keluaran PUEBI
# ══════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    <div class="puebi-note">
    📌 <strong>Cara penggunaan:</strong>
    Salin keluaran (<em>output</em>) dari AI (ChatGPT, Claude, Gemini, dsb.),
    tempel ke kolom di bawah, lalu klik <strong>Format Sesuai PUEBI</strong>.
    Sistem akan: (1) menerapkan ejaan baku sesuai PUEBI,
    (2) mencetak miring setiap istilah asing yang belum terserap sempurna ke dalam
    Bahasa Indonesia, dan (3) menyajikan hasil dalam format ilmiah siap gunakan.
    </div>
    """, unsafe_allow_html=True)

    kol_kiri, kol_kanan = st.columns([1, 1], gap="medium")

    with kol_kiri:
        st.markdown("#### ✏️ Tempel Keluaran AI di Sini")
        teks_masukan = st.text_area(
            label="Masukan",
            placeholder=(
                "Tempel teks keluaran dari AI di sini...\n\n"
                "Contoh: hasil analisis dari Modul 1, Modul 6, Modul 8, dsb."
            ),
            height=420,
            label_visibility="collapsed"
        )

        kol_btn1, kol_btn2 = st.columns([2, 1])
        with kol_btn1:
            tombol_format = st.button(
                "🔤 Format Sesuai PUEBI",
                type="primary",
                use_container_width=True
            )
        with kol_btn2:
            if st.button("🗑️ Hapus", use_container_width=True):
                st.rerun()

        # Tampilkan istilah yang terdeteksi
        if teks_masukan.strip():
            istilah_ditemukan = [
                i for i in ISTILAH_ASING
                if re.search(r'\b' + re.escape(i) + r'\b', teks_masukan, re.IGNORECASE)
                and i not in KATA_SERAPAN
            ]
            if istilah_ditemukan:
                st.markdown(
                    f"**Istilah asing terdeteksi** "
                    f"({len(istilah_ditemukan)} istilah akan dicetak miring):"
                )
                tags = " ".join(
                    f'<span class="istilah-tag">{i}</span>'
                    for i in istilah_ditemukan[:25]
                )
                if len(istilah_ditemukan) > 25:
                    tags += (
                        f' <span class="istilah-tag">'
                        f'+{len(istilah_ditemukan)-25} lainnya</span>'
                    )
                st.markdown(tags, unsafe_allow_html=True)

    with kol_kanan:
        st.markdown("#### ✅ Hasil Format PUEBI")

        if tombol_format and teks_masukan.strip():
            with st.spinner("Memformat teks sesuai PUEBI..."):
                teks_hasil = format_puebi(teks_masukan)
                stat = hitung_statistik(teks_masukan, teks_hasil)

            # Statistik ringkas
            s1, s2, s3, s4 = st.columns(4)
            for col, val, lbl in [
                (s1, stat['kata'], 'Kata'),
                (s2, stat['italic'], 'Istilah Miring'),
                (s3, stat['paragraf'], 'Paragraf'),
                (s4, stat['karakter'], 'Karakter'),
            ]:
                with col:
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<div class="stat-val">{val}</div>'
                        f'<div class="stat-lbl">{lbl}</div></div>',
                        unsafe_allow_html=True
                    )

            st.markdown("<br>", unsafe_allow_html=True)

            # Render hasil (markdown aktif agar italic tampil)
            with st.container():
                st.markdown(teks_hasil)

            st.markdown("<br>", unsafe_allow_html=True)

            # Teks salin
            st.markdown(
                "**Salin hasil** "
                "(tanda `*teks*` = italic — siap tempel ke Word/Google Docs):"
            )
            st.text_area(
                "Hasil",
                value=teks_hasil,
                height=280,
                label_visibility="collapsed"
            )

            st.success(
                f"✅ Pemformatan selesai — {stat['italic']} istilah asing "
                f"dicetak miring sesuai PUEBI."
            )

        elif tombol_format:
            st.warning(
                "⚠️ Kolom masukan masih kosong. "
                "Tempel teks keluaran AI terlebih dahulu."
            )
        else:
            st.markdown(
                '<div style="background:#f8f7f4;border:2px dashed #c8c6be;'
                'border-radius:10px;padding:60px 20px;text-align:center;'
                'color:#888780;font-size:14px;">'
                '← Tempel teks di kolom kiri<br>'
                'lalu klik <strong>Format Sesuai PUEBI</strong>'
                '</div>',
                unsafe_allow_html=True
            )

    # ─── Panduan PUEBI ────────────────────────────────────────────
    with st.expander("📖 Panduan PUEBI — Ketentuan Penulisan Istilah Asing"):
        st.markdown("""
**Berdasarkan Pedoman Umum Ejaan Bahasa Indonesia (PUEBI) Edisi Keempat:**

**1. Istilah Asing yang Dicetak Miring**
Kata atau ungkapan asing yang belum terserap ke dalam Bahasa Indonesia
wajib ditulis dengan huruf miring (*italic*).

> Penelitian ini menggunakan pendekatan *machine learning* untuk mengklasifikasikan
> data. Metode *deep learning* terbukti lebih efektif daripada metode konvensional
> dalam mengolah *dataset* berskala besar.

**2. Istilah yang Sudah Diserap (Tidak Perlu Miring)**
Kata serapan yang sudah masuk KBBI tidak perlu dicetak miring:
analisis, metode, data, sistem, model, teknologi, informasi, komunikasi,
jaringan, basis data, program, komputer, internet, digital.

**3. Penyebutan Singkatan Istilah Asing**
Perkenalkan padanan Indonesia terlebih dahulu, diikuti singkatan dalam kurung.

> Pembelajaran Mesin (*Machine Learning*/ML), Jaringan Saraf Tiruan
> (*Neural Network*/NN), Pemrosesan Bahasa Alami (*Natural Language Processing*/NLP).

**4. Penulisan Kata Depan**
"di", "ke", "dari" ditulis terpisah jika berfungsi sebagai kata depan tempat/arah.

> ✅ Benar: di dalam, di luar, di atas, di bawah, ke dalam, dari luar
> ❌ Salah: didalam, diluar, diatas, dibawah

**5. Pilihan Kata Baku**
- "karena" (bukan "dikarenakan")
- "dipersilakan" (bukan "dipersilahkan")
- "mengubah" (bukan "merubah")
- "terdiri atas" (bukan "terdiri dari")
        """)

    st.markdown("""
    ---
    <p style="text-align:center;color:#888780;font-size:12px;">
    Sistem Analisis Literatur Akademik — Core Layer v2.1 — 11 Modul (M0–M9)<br>
    Pemformat Keluaran sesuai PUEBI (Pedoman Umum Ejaan Bahasa Indonesia)
    </p>
    """, unsafe_allow_html=True)
