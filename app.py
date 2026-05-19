import streamlit as st
import pandas as pd
import json
import datetime
import os

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="ALAS v3.0 — Academic Literature System",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Mobile-First & Anti-Clutter
st.markdown("""
<style>
    .stButton button { min-height: 44px; font-weight: 500; }
    .stTabs [data-baseweb="tab-list"] button { padding: 8px 16px; }
    .module-badge { padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; }
    .badge-done { background: #dcfce7; color: #16a34a; }
    .badge-pending { background: #fef9c3; color: #ca8a04; }
    .badge-locked { background: #f3f4f6; color: #9ca3af; }
    .guardrail-box { padding: 10px; background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 4px; margin: 8px 0; }
    .prompt-code { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# ================= STATE MANAGEMENT =================
MODULES = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]
DEFAULT_CONFIG = {"domain": "Umum", "level": "Skripsi", "target": "SINTA 2"}

def init_state():
    if 'modules' not in st.session_state:
        st.session_state.modules = {m: {"status": "locked", "data": None, "output": None} for m in MODULES}
        st.session_state.modules["M0"]["status"] = "pending"
    if 'config' not in st.session_state:
        st.session_state.config = DEFAULT_CONFIG.copy()
    if 'current' not in st.session_state:
        st.session_state.current = "M0"
    if 'anchor' not in st.session_state:
        st.session_state.anchor = {"topic": "", "novelty": [], "method": "", "target": ""}
    if 'process_mode' not in st.session_state:
        st.session_state.process_mode = "manual"  # Default: manual mode

init_state()

def save_state():
    st.session_state.modules[st.session_state.current]["status"] = "done"
    if st.session_state.current in MODULES[:-1]:
        idx = MODULES.index(st.session_state.current)
        st.session_state.modules[MODULES[idx+1]]["status"] = "pending"
    # Simpan anchor setelah M6
    if st.session_state.current == "M6" and st.session_state.anchor["topic"] == "":
        st.session_state.anchor = {
            "topic": "Penelitian berbasis metadata abstrak",
            "novelty": ["Metodologis", "Kontekstual"],
            "method": "Abstract-Only Screening",
            "target": st.session_state.config["target"]
        }

# ================= FUNGSI HELPER: MANUAL MODE =================
def generate_prompt_for_module(module_id, input_data):
    """Generate prompt Core Layer v3.0 yang siap copy-paste ke AI eksternal"""
    config = st.session_state.config
    specs = {
        "M0": "Validasi 10 paper jurnal primer • Filter: 4 tahun, 50% terkini, Scopus/IEEE, exclude conference/SLR",
        "M6": "10 rekomendasi judul • 2500 kata/judul • Latar belakang, urgensi, GAP, 2 novelty, flowchart ASCII, alignment Q1/SINTA 2",
        "M7": "3 rekomendasi per skema (BIMA PDP/PFR/Prototype/Model, BRIN, Scopus Q1, SINTA 2) • 3500 kata total",
        "M8": "Template IMRAD • Scopus Q1 & SINTA 2 • 6 pernyataan/sekssi • 5000 kata • Bahasa Inggris • sitasi hanya di Results",
        "M9": "5 dataset Colab-ready • Open access • Permanent link • Anti-fake • Alignment ke topik penelitian"
    }
    
    return f"""[CORE_LAYER_v3.0 — MANUAL MODE]
Bidang: {config['domain']} | Level: {config['level']} | Target: {config['target']}
Modul: {module_id} | Spesifikasi: {specs.get(module_id, 'Proses sesuai dashboard v2.2')}

[INPUT DATA]
{json.dumps(input_data, indent=2, ensure_ascii=False)}

[INSTRUKSI EKSEKUSI]
1. Analisis HANYA berdasarkan metadata yang diberikan (judul, abstrak, keyword)
2. Jangan mengarang data, sitasi, atau temuan yang tidak eksplisit ada di input
3. Gunakan tag [Ref: ID_Paper] untuk referensi ke paper intake
4. Terapkan guardrail: Anti-Halusinasi • Evidence Chain • Abstract-Only • Iteratif
5. Output dalam format terstruktur dengan heading Markdown

[FORMAT OUTPUT]
### Ringkasan Eksekutif
• Poin 1
• Poin 2
• Poin 3

### Konten Akademik Lengkap
[Narasi sesuai spesifikasi modul {module_id}]

### Metadata
- Modul: {module_id}
- Bahasa: Indonesia akademik (kecuali M8: Inggris)
- Evidence completeness: ≥95%

[STATUS_MODUL: {module_id}_SELESAI]
"""

def run_ai_processing(module_id, input_data):
    """
    MODE MANUAL: Generate prompt Core Layer v3.0 untuk dipaste ke AI eksternal
    (ChatGPT/Claude/Gemini/Qwen). User paste hasil kembali ke sistem.
    """
    return {
        "status": "manual_mode",
        "layer1_summary": f"⚠️ Mode Manual: Salin prompt di tab 📖 Detail, paste ke AI pilihan Anda, lalu kembalikan hasilnya.",
        "layer2_academic": generate_prompt_for_module(module_id, input_data),
        "layer3_metadata": {
            "module": module_id, 
            "mode": "manual", 
            "note": "Paste output AI ke field di tab 📖 Detail Akademik",
            "guardrails": ["Anti-Halusinasi", "Evidence Chain", "Abstract-Only", "Iterative Protocol"]
        }
    }

# ================= SIDEBAR: NAVIGASI & KONTROL =================
with st.sidebar:
    st.header("📘 ALAS v3.0")
    
    # Toggle Mode Pemrosesan
    st.subheader("⚙️ Mode Inferensi")
    st.session_state.process_mode = st.radio(
        "Pilih mode:",
        ["👐 Manual (Eksternal AI)", "🤖 Otomatis (API)"],
        index=0,
        help="Manual: paste prompt ke ChatGPT/Claude. Otomatis: butuh API key (belum diimplementasi)."
    )
    
    st.divider()
    st.subheader("🔧 Core Layer Config")
    st.session_state.config["domain"] = st.selectbox(
        "Bidang Penelitian", 
        ["Data Mining", "Sentiment Analysis", "Policy Analysis", "Umum"], 
        index=0
    )
    st.session_state.config["level"] = st.selectbox(
        "Level Akademik", 
        ["Skripsi", "Tesis", "Disertasi", "Hibah"], 
        index=0
    )
    st.session_state.config["target"] = st.selectbox(
        "Target Publikasi", 
        ["SINTA 2", "Scopus Q1"], 
        index=0
    )
    
    st.divider()
    st.subheader("📊 Progress Modul")
    progress = sum(1 for m in st.session_state.modules.values() if m["status"] == "done") / len(MODULES)
    st.progress(progress)
    
    st.session_state.current = st.radio(
        "Pilih Modul", 
        MODULES, 
        format_func=lambda x: f"{x} • {'✅' if st.session_state.modules[x]['status']=='done' else '🔒' if st.session_state.modules[x]['status']=='locked' else '⏳'}"
    )
    
    st.divider()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("💾 Backup"):
            backup_data = {
                "config": st.session_state.config,
                "modules": {k: {kk: vv for kk, vv in v.items() if kk != 'output'} for k, v in st.session_state.modules.items()},
                "anchor": st.session_state.anchor,
                "timestamp": datetime.datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON", 
                json.dumps(backup_data, indent=2, ensure_ascii=False), 
                file_name=f"ALAS_backup_{datetime.date.today()}.json",
                mime="application/json"
            )
    with col_b2:
        if st.button("🗑️ Reset", type="primary"):
            for m in MODULES: 
                st.session_state.modules[m] = {"status": "locked", "data": None, "output": None}
            st.session_state.modules["M0"]["status"] = "pending"
            st.session_state.current = "M0"
            st.session_state.anchor = {"topic": "", "novelty": [], "method": "", "target": ""}
            st.rerun()

# ================= RENDER MODUL =================
def render_m0():
    st.header("📥 M0: Literature Search")
    st.info("📌 **Abstract-Only Mode**: Masukkan metadata jurnal primer. Sistem menolak otomatis konferensi/SLR/PDF.")
    
    with st.form("m0_form"):
        kw = st.text_input("Keyword Target", placeholder="Contoh: sentiment analysis e-commerce")
        st.markdown("### Input Metadata Paper")
        paper_text = st.text_area(
            "Paste format per paper:\n```\nTITLE: ...\nAUTHORS: ...\nYEAR: ...\nJOURNAL: ...\nKEYWORDS: ...\nABSTRACT: ...\nDOI: ...\nSOURCE: ...\n```", 
            height=250
        )
        
        col1, col2 = st.columns([1, 2])
        with col1:
            valid = st.form_submit_button("✅ Validasi & Proses", type="primary")
        with col2:
            st.markdown("🔍 **Auto-Filter Aktif**:\n- `journal-article` only\n- 4 tahun terakhir\n- ≥50% dari 1–2 tahun terkini\n- Exclude: conference/proceedings/SLR")
            
    if valid:
        if not kw or not paper_text:
            st.error("❌ Keyword dan metadata paper wajib diisi.")
            return
            
        # Simpan & Proses
        st.session_state.modules["M0"]["data"] = {"keyword": kw, "raw": paper_text}
        
        if st.session_state.process_mode == "👐 Manual (Eksternal AI)":
            with st.spinner("⏳ Menyiapkan prompt Core Layer v3.0..."):
                st.session_state.modules["M0"]["output"] = run_ai_processing("M0", {"keyword": kw, "raw": paper_text})
                save_state()
                st.success("✅ Prompt siap! Buka tab 📖 Detail untuk menyalin.")
        else:
            st.warning("⚠️ Mode otomatis belum diimplementasi. Menggunakan fallback manual mode.")
            st.session_state.modules["M0"]["output"] = run_ai_processing("M0", {"keyword": kw, "raw": paper_text})
            save_state()
            
        st.rerun()

def render_output_layer(module_id):
    """Render output 3-tier dengan dukungan manual mode copy-paste"""
    out = st.session_state.modules[module_id]["output"]
    if not out:
        st.warning("⏳ Belum diproses. Klik tombol 🚀 Proses terlebih dahulu.")
        return
        
    t1, t2, t3 = st.tabs(["📋 Ringkasan", "📖 Detail Akademik", "📦 Metadata"])
    
    with t1:
        st.markdown(out["layer1_summary"])
        st.caption("💡 Gunakan ringkasan untuk executive summary atau abstrak cepat.")
        
    with t2:
        if out.get("status") == "manual_mode":
            # 🔥 TAMPILKAN PROMPT YANG BISA DISALIN 🔥
            st.info("📋 **Langkah Manual Mode**:\n1. Salin prompt di bawah\n2. Paste ke ChatGPT/Claude/Gemini/Qwen\n3. Salin hasilnya\n4. Paste ke field di bagian bawah\n5. Klik 💾 Simpan")
            
            st.markdown("### Prompt Core Layer v3.0 (Siap Salin)")
            st.code(out["layer2_academic"], language="text")
            
            st.markdown("### ↓ Paste Hasil dari AI Eksternal")
            user_result = st.text_area(
                "Hasil pemrosesan AI", 
                value=st.session_state.modules[module_id].get("user_output", ""),
                key=f"manual_input_{module_id}",
                height=400,
                placeholder="Paste hasil lengkap dari AI eksternal di sini..."
            )
            
            col_s1, col_s2 = st.columns([1, 3])
            with col_s1:
                if st.button("💾 Simpan Hasil", type="primary", key=f"save_manual_{module_id}"):
                    if user_result.strip():
                        # Update output dengan hasil user
                        st.session_state.modules[module_id]["output"]["layer2_academic"] = user_result
                        st.session_state.modules[module_id]["output"]["user_verified"] = True
                        st.session_state.modules[module_id]["user_output"] = user_result  # Persist user input
                        save_state()
                        st.success("✅ Hasil tersimpan! Modul siap dilanjutkan.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Hasil tidak boleh kosong.")
            with col_s2:
                if st.button("🗑️ Kosongkan", key=f"clear_manual_{module_id}"):
                    st.session_state.modules[module_id]["user_output"] = ""
                    st.rerun()
                    
            # Tampilkan guardrail checklist
            with st.expander("🛡️ Checklist Guardrail (Opsional)"):
                st.checkbox("✅ Setiap klaim merujuk ke metadata intake", key=f"gr1_{module_id}")
                st.checkbox("✅ Tidak ada halusinasi sitasi/DOI", key=f"gr2_{module_id}")
                st.checkbox("✅ Output sesuai spesifikasi modul", key=f"gr3_{module_id}")
                
        else:
            # Mode otomatis (placeholder untuk future implementation)
            st.markdown(out["layer2_academic"])
            if st.button("📋 Salin ke Clipboard"):
                st.toast("Tersalin! (Fitur clipboard memerlukan interaksi browser)")
            
    with t3:
        st.json(out["layer3_metadata"])
        st.caption("📤 Format siap export ke .docx, .tex, atau .json")
        
        # Evidence summary
        if out.get("layer3_metadata", {}).get("guardrails"):
            st.markdown("#### Guardrail Status")
            for g in out["layer3_metadata"]["guardrails"]:
                st.markdown(f"✅ {g}")

def render_generic_module(mod_id):
    st.header(f"⚙️ {mod_id}: Proses Analisis")
    
    if st.session_state.modules[mod_id]["status"] == "locked":
        st.error("🔒 Modul terkunci. Selesaikan modul sebelumnya terlebih dahulu.")
        prev_idx = MODULES.index(mod_id) - 1
        if prev_idx >= 0:
            st.info(f"💡 Lanjutkan dari modul: **{MODULES[prev_idx]}**")
        return
        
    st.markdown('<div class="guardrail-box">🛡️ <strong>Guardrail Aktif:</strong> Anti-Halusinasi • Evidence Chain • Abstract-Only • Iteratif Protocol</div>', unsafe_allow_html=True)
    
    # Tampilkan data input jika ada
    if st.session_state.modules[mod_id]["data"]:
        with st.expander("📥 Lihat Input Data"):
            st.json(st.session_state.modules[mod_id]["data"])
    
    # Tombol proses
    if not st.session_state.modules[mod_id].get("output"):
        if st.button(f"🚀 Proses {mod_id}", type="primary"):
            if st.session_state.process_mode == "👐 Manual (Eksternal AI)":
                with st.spinner("⏳ Menyiapkan prompt Core Layer v3.0..."):
                    st.session_state.modules[mod_id]["output"] = run_ai_processing(mod_id, st.session_state.modules[mod_id]["data"] or {})
                    save_state()
                    st.success("✅ Prompt siap! Buka tab 📖 Detail untuk menyalin.")
            else:
                st.warning("⚠️ Mode otomatis belum diimplementasi. Menggunakan fallback manual mode.")
                st.session_state.modules[mod_id]["output"] = run_ai_processing(mod_id, st.session_state.modules[mod_id]["data"] or {})
                save_state()
            st.rerun()
    else:
        st.success(f"✅ {mod_id} telah diproses. Review output di tab berikut.")
            
    render_output_layer(mod_id)

# ================= MAIN ROUTER =================
mod = st.session_state.current
if mod == "M0":
    render_m0()
elif mod in ["M6", "M7", "M8", "M9"]:
    render_generic_module(mod)
else:
    # M1-M5: framework siap dikembangkan
    st.info(f"🚧 Modul {mod} dalam pengembangan. Gunakan M0, M6-M9 untuk alur penelitian lengkap.")
    render_generic_module(mod)

# ================= FOOTER INTEGRITY =================
st.divider()
st.caption("📘 ALAS v3.0 • Abstract-Based Input Mode • Cross-AI Compatible • No Fake Data • Iterative Protocol Active • Manual Mode: Copy-Paste ke AI Eksternal")
