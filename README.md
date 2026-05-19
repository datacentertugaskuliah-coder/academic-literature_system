# Academic Literature Analysis System
**Core Layer v2.1 | 11 Modul (M0–M9)**

Custom prompting profesional untuk analisis literatur akademik — tanpa upload PDF, auto-deteksi paper, obfuskasi prompt aktif.

---

## Cara Deploy ke Streamlit Cloud

### Langkah 1 — Buat Repository GitHub

1. Buka [github.com](https://github.com) → Login
2. Klik **"New repository"** (tombol hijau kanan atas)
3. Isi:
   - **Repository name:** `academic-literature-system` (atau nama lain)
   - **Visibility:** Public ✓ (wajib untuk Streamlit Cloud gratis)
   - **Add README:** ✗ (jangan centang, kita upload sendiri)
4. Klik **"Create repository"**

### Langkah 2 — Upload File ke GitHub

Di halaman repository yang baru dibuat, klik **"uploading an existing file"**

Upload **semua file berikut sekaligus:**
```
app.py
dashboard.html
requirements.txt
```

Untuk folder `.streamlit/config.toml`:
- Klik **"Add file" → "Create new file"**
- Ketik nama: `.streamlit/config.toml`
- Copy-paste isi dari file config.toml
- Klik **"Commit new file"**

### Langkah 3 — Deploy ke Streamlit Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Login dengan akun GitHub Anda
3. Klik **"New app"**
4. Isi form:
   - **Repository:** `username/academic-literature-system`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Klik **"Deploy!"**
6. Tunggu 2–5 menit sampai deployment selesai
7. Anda akan mendapat URL seperti: `https://username-academic-literature-system.streamlit.app`

---

## Struktur File

```
repository/
├── app.py              ← Streamlit entry point (jangan ubah)
├── dashboard.html      ← Dashboard utama (semua prompt ada di sini)
├── requirements.txt    ← Dependencies (streamlit saja)
└── .streamlit/
    └── config.toml     ← Konfigurasi tampilan
```

---

## Catatan Penting

**Keamanan prompt:**
- Sistem obfuskasi aktif — setiap copy menghasilkan token unik `[SID:XXX-YYYY-ZZZZ]`
- Kode sesi 3 karakter di-generate random setiap buka dashboard

**Akses:**
- URL Streamlit Cloud bisa dibagikan ke tim
- Dashboard berjalan sepenuhnya di browser — tidak ada data yang dikirim ke server

**Update dashboard:**
- Edit file `dashboard.html` di GitHub
- Streamlit Cloud otomatis redeploy dalam beberapa menit

---

## Modul yang Tersedia

| Modul | Nama | Fungsi |
|-------|------|--------|
| CL | Core Layer v2.1 | Fondasi sistem — paste pertama |
| M0 | Literature Search | Cari jurnal (bukan konferensi/SLR) |
| M1 | Intake Protocol | Analisis abstrak — auto-deteksi |
| M2 | Contradiction Finder | Kontradiksi antar paper |
| M3 | Citation Chain | Genealogi konsep teoritis |
| M4 | Gap Scanner | 5 research gap terranking |
| M5 | Methodology Audit | Audit metodologi 4 kriteria |
| M6 | 10 Rekomendasi Judul | Judul + novelty + flowchart |
| M7 | Hibah & Publikasi | BIMA, BRIN, Scopus Q1, SINTA 2 |
| M8 | Template IMRAD | Draft artikel Scopus Q1/SINTA 2 |
| M9 | Rekomendasi Dataset | 5 dataset untuk Google Colab |
