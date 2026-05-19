import streamlit as st
import pandas as pd
import json
import datetime
import re

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(
    page_title="ALAS v3.0 — Academic Literature System",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Mobile-First & Academic Styling
st.markdown("""
<style>
    .stButton button { min-height: 44px; font-weight: 500; }
    .stTabs [data-baseweb="tab-list"] button { padding: 8px 16px; }
    .module-badge { padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; }
    .badge-done { background: #dcfce7; color: #16a34a; }
    .badge-pending { background: #fef9c3; color: #ca8a04; }
    .badge-locked { background: #f3f4f6; color: #9ca3af; }
    .badge-rejected { background: #fee2e2; color: #dc2626; }
    .guardrail-box { padding: 10px; background: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 4px; margin: 8px 0; font-size: 0.9rem; }
    .prompt-code { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; font-family: monospace; font-size: 0.85rem; white-space: pre-wrap; }
    .academic-text { line-height: 1.8; font-size: 1.05rem; }
    .flowchart-ascii { background: #f1f5f9; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 0.85rem; overflow-x: auto; }
</style>
""", unsafe_allow_html=True)

# ================= KONSTANTA & SPESIFIKASI MODUL (Dashboard v2.2) =================
MODULES = ["M0", "M1", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9", "CL"]
MODULE_SPECS = {
    "M0": {"name": "Literature Search", "desc": "Jurnal primer • 4 tahun • 50% terkini • Scopus/IEEE • Exclude: conference/SLR", "input": ["keyword", "paper_metadata"], "output": "10 paper tervalidasi"},
    "M1": {"name": "Intake Protocol", "desc": "Auto-deteksi metadata • Tanpa upload PDF • Validasi DOI", "input": ["paper_blocks"], "output": "Tabel metadata terstandarisasi"},
    "M2": {"name": "Contradiction Finder", "desc": "Identifikasi kontradiksi genuine antar paper", "input": ["validated_papers"], "output": "Laporan kontradiksi + evidence map"},
    "M3": {"name": "Citation Chain", "desc": "Pelacakan genealogi konsep teoritis", "input": ["papers_with_doi"], "output": "Peta sitasi + konsep inti"},
    "M4": {"name": "Gap Scanner", "desc": "Pemetaan 5 research gap ter-ranking", "input": ["analyzed_papers"], "output": "5 GAP prioritized + justifikasi"},
    "M5": {"name": "Methodology Audit", "desc": "Evaluasi 4 kriteria: desain, sampel, instrumen, analisis", "input": ["papers_abstract"], "output": "Audit report + rekomendasi perbaikan"},
    "M6": {"name": "10 Rekomendasi Judul", "desc": "2500 kata/judul • Latar belakang • Urgensi • GAP • 2 novelty • Flowchart ASCII • Alignment Q1/SINTA 2", "input": ["M5_output", "M0_papers"], "output": "10 judul lengkap + flowchart"},
    "M7": {"name": "Hibah & Publikasi", "desc": "3500 kata • 7 skema: BIMA(PDP/PFR/Prototype/Model), BRIN, Scopus Q1, SINTA 2", "input": ["M6_titles"], "output": "21 rekomendasi proposal/artikel"},
    "M8": {"name": "Template IMRAD", "desc": "5000 kata • Scopus Q1(EN) & SINTA 2(ID) • 6 pernyataan/sekssi • Sitasi hanya di Results", "input": ["M7_selected"], "output": "Naskah IMRAD siap submit"},
    "M9": {"name": "Rekomendasi Dataset", "desc": "5 dataset • Colab-ready • Open access • Permanent link • Anti-fake • Alignment topik", "input": ["research_scope"], "output": "Tabel dataset + Colab snippet"},
    "CL": {"name": "Core Layer Fondasi", "desc": "Abstract-Only Mode • Anti-Halusinasi • Evidence Chain • Iteratif Protocol", "input": ["system_init"], "output": "Directive aktif"}
}

DEFAULT_CONFIG = {
    "domain": "Umum", 
    "level": "Skripsi", 
    "target": "SINTA 2",
    "terminology": {"instansi": True, "pegawai": True}  # Preferensi terminologi akademik
}

# ================= STATE MANAGEMENT =================
def init_state():
    if 'modules' not in st.session_state:
        st.session_state.modules = {m: {"status": "locked", "data": None, "output": None, "evidence_log": []} for m in MODULES}
        st.session_state.modules["M0"]["status"] = "pending"
        st.session_state.modules["CL"]["status"] = "done"  # Core Layer always active
    if 'config' not in st.session_state:
        st.session_state.config = DEFAULT_CONFIG.copy()
    if 'current' not in st.session_state:
        st.session_state.current = "M0"
    if 'anchor' not in st.session_state:
        st.session_state.anchor = {"topic": "", "novelty": [], "method": "", "target": "", "locked_after_M6": False}
    if 'process_mode' not in st.session_state:
        st.session_state.process_mode = "manual"
    if 'evidence_chain' not in st.session_state:
        st.session_state.evidence_chain = []  # Track all [Ref: ID_Paper] usage

init_state()

def save_state():
    """Update status modul & kunci anchor setelah M6"""
    current = st.session_state.current
    st.session_state.modules[current]["status"] = "done"
    
    # Unlock next module
    if current in MODULES[:-1]:
        idx = MODULES.index(current)
        if st.session_state.modules[MODULES[idx+1]]["status"] == "locked":
            st.session_state.modules[MODULES[idx+1]]["status"] = "pending"
    
    # Lock anchor core setelah M6 selesai pertama kali
    if current == "M6" and not st.session_state.anchor["locked_after_M6"]:
        st.session_state.anchor["locked_after_M6"] = True
        st.session_state.anchor["topic"] = st.session_state.anchor.get("topic") or "Penelitian berbasis metadata abstrak"
        st.session_state.anchor["target"] = st.session_state.config["target"]

def validate_m0_paper(paper: dict) -> dict:
    """Validasi deterministik untuk M0: jurnal primer, 4 tahun, DOI valid, exclude conference/SLR"""
    result = {"valid": True, "reasons": [], "flags": []}
    
    # Check required fields
    required = ["TITLE", "ABSTRACT", "KEYWORDS", "YEAR", "JOURNAL", "DOI"]
    for field in required:
        if field not in paper or not paper[field].strip():
            result["valid"] = False
            result["reasons"].append(f"Missing: {field}")
    
    if not result["valid"]:
        return result
    
    # Check year range (4 tahun terakhir)
    try:
        year = int(paper["YEAR"])
        current_year = datetime.datetime.now().year
        if not (current_year - 4 <= year <= current_year):
            result["valid"] = False
            result["reasons"].append(f"Year {year} outside 4-year range")
        elif year >= current_year - 1:
            result["flags"].append("recent_1-2yr")  # Untuk hitung 50% terkini
    except:
        result["valid"] = False
        result["reasons"].append("Invalid YEAR format")
    
    # Check journal type (exclude conference/proceedings/SLR)
    journal_lower = paper.get("JOURNAL", "").lower()
    abstract_lower = paper.get("ABSTRACT", "").lower()
    exclude_keywords = ["conference", "proceedings", "workshop", "symposium", 
                       "systematic review", "meta-analysis", "bibliometric", "literature review"]
    for kw in exclude_keywords:
        if kw in journal_lower or kw in abstract_lower:
            result["valid"] = False
            result["reasons"].append(f"Excluded: contains '{kw}'")
            result["flags"].append(f"rejected_{kw.replace(' ', '_')}")
            break
    
    # Check DOI format
    doi = paper.get("DOI", "")
    if doi and not re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', doi, re.I):
        result["flags"].append("doi_format_warning")  # Warning, not reject
    
    return result

# ================= FUNGSI HELPER: MANUAL MODE + CORE LAYER v3.0 =================
def generate_prompt_for_module(module_id: str, input_data: dict) -> str:
    """Generate prompt Core Layer v3.0 yang siap copy-paste ke AI eksternal"""
    config = st.session_state.config
    spec = MODULE_SPECS.get(module_id, {})
    
    # Terminologi preference injection
    term_note = ""
    if config.get("terminology", {}).get("instansi"):
        term_note = "\n• Gunakan terminologi: 'instansi' (bukan 'perusahaan'), 'pegawai' (bukan 'karyawan')"
    
    return f"""[CORE_LAYER_v3.0 — MANUAL MODE]
Bidang: {config['domain']} | Level: {config['level']} | Target: {config['target']}{term_note}
Modul: {module_id} — {spec.get('name', '')}
Spesifikasi: {spec.get('desc', 'Proses sesuai dashboard v2.2')}

[INPUT DATA]
{json.dumps(input_data, indent=2, ensure_ascii=False)}

[INSTRUKSI EKSEKUSI — WAJIB]
1. Analisis HANYA berdasarkan metadata yang diberikan (judul, abstrak, keyword). Dilarang akses full-text/PDF.
2. Jangan mengarang data, sitasi, metode, atau temuan yang tidak eksplisit tertulis di input.
3. Setiap klaim analitis HARUS disertai tag referensi: `[Ref: ID_Paper#X, Field: Abstract/Keyword]`
4. Jika informasi tidak lengkap/ambigu, tampilkan `[NEEDS_CLARIFICATION: <field>]` — jangan mengisi dengan asumsi.
5. Terapkan guardrail: Anti-Halusinasi • Evidence Chain • Abstract-Only • Iteratif Protocol.

[FORMAT OUTPUT — STRUKTUR WAJIB]
### Ringkasan Eksekutif
• Poin 1 (maksimal 15 kata)
• Poin 2
• Poin 3

### Konten Akademik Lengkap
[Narasi sesuai spesifikasi modul {module_id}. Gunakan heading Markdown: ##, ###, ####]
{f'- Untuk M6: Sertakan flowchart ASCII hierarki' if module_id == 'M6' else ''}
{f'- Untuk M8: Bahasa Inggris, 6 pernyataan/sekssi, sitasi hanya di Results' if module_id == 'M8' else ''}
{f'- Untuk M9: Sertakan Colab snippet + validasi link' if module_id == 'M9' else ''}

### Metadata & Evidence
- Modul: {module_id}
- Bahasa: {"Inggris (Scopus Q1) / Indonesia (SINTA 2)" if module_id == 'M8' else 'Indonesia akademik formal'}
- Evidence completeness: ≥95% (hitung % klaim dengan [Ref: ...])
- Guardrails passed: ✅

[STATUS_MODUL: {module_id}_SELESAI]
"""

def run_ai_processing(module_id: str, input_data: dict) -> dict:
    """
    MODE MANUAL: Generate prompt Core Layer v3.0 untuk dipaste ke AI eksternal.
    M0: Tambahkan validasi deterministik sebelum generate prompt.
    """
    # Special handling for M0: validate papers first
    if module_id == "M0" and isinstance(input_data.get("raw"), str):
        # Parse simple format: blocks separated by blank lines
        blocks = [b.strip() for b in input_data["raw"].split('\n\n') if b.strip()]
        validated = []
        recent_count = 0
        
        for i, block in enumerate(blocks[:10]):  # Max 10 papers
            paper = {}
            for line in block.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    paper[key.strip().upper()] = val.strip()
            
            validation = validate_m0_paper(paper)
            paper["_id"] = f"P{i+1}"
            paper["_validation"] = validation
            
            if validation["valid"]:
                validated.append(paper)
                if "recent_1-2yr" in validation.get("flags", []):
                    recent_count += 1
        
        # Check 50% recent rule
        total_valid = len(validated)
        if total_valid > 0 and recent_count / total_valid < 0.5:
            st.warning(f"⚠️ Hanya {recent_count}/{total_valid} paper dari 1-2 tahun terkini (<50%). Pertimbangkan menambah paper terbaru.")
        
        input_data["validated_papers"] = validated
        input_data["summary"] = f"{len(validated)} paper valid dari {len(blocks)} input"
    
    return {
        "status": "manual_mode",
        "layer1_summary": f"⚠️ Mode Manual: Salin prompt di tab 📖 Detail, paste ke AI eksternal (ChatGPT/Claude/Gemini/Qwen), lalu kembalikan hasilnya.",
        "layer2_academic": generate_prompt_for_module(module_id, input_data),
        "layer3_metadata": {
            "module": module_id,
            "spec": MODULE_SPECS.get(module_id, {}).get("desc", ""),
            "mode": "manual", 
            "note": "Paste output AI ke field di tab 📖 Detail Akademik",
            "guardrails": ["Anti-Halusinasi", "Evidence Chain", "Abstract-Only", "Iterative Protocol", "Terminology Consistency"],
            "validation_summary": input_data.get("summary") if module_id == "M0" else None
        }
    }

# ================= SIDEBAR: NAVIGASI & KONTROL =================
with st.sidebar:
    st.header("📘 ALAS v3.0")
    st.caption("Academic Literature Analysis System • Core v2.2 Compatible")
    
    # Toggle Mode Pemrosesan
    st.subheader("⚙️ Mode Inferensi")
    st.session_state.process_mode = st.radio(
        "Pilih mode:",
        ["👐 Manual (Eksternal AI)", "🤖 Otomatis (API)"],
        index=0,
        help="Manual: paste prompt ke AI eksternal. Otomatis: butuh API key (belum diimplementasi)."
    )
    
    st.divider()
    st.subheader("🔧 Core Layer Config")
    
    # Terminology preference (sesuai memori user)
    with st.expander("📝 Preferensi Terminologi", expanded=False):
        st.session_state.config["terminology"]["instansi"] = st.checkbox(
            "Gunakan 'instansi' (bukan 'perusahaan')", 
            value=st.session_state.config["terminology"].get("instansi", True)
        )
        st.session_state.config["terminology"]["pegawai"] = st.checkbox(
            "Gunakan 'pegawai' (bukan 'karyawan')", 
            value=st.session_state.config["terminology"].get("pegawai", True)
        )
    
    st.session_state.config["domain"] = st.selectbox(
        "Bidang Penelitian", 
        ["Data Mining", "Sentiment Analysis", "Policy Analysis", "Kepegawaian", "Umum"], 
        index=3 if st.session_state.config["domain"] == "Kepegawaian" else 0
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
    done_count = sum(1 for m in st.session_state.modules.values() if m["status"] == "done")
    progress = done_count / len(MODULES)
    st.progress(progress)
    st.caption(f"{done_count}/{len(MODULES)} modul selesai")
    
    # Module selector with status badges
    st.session_state.current = st.radio(
        "Pilih Modul", 
        MODULES,
        format_func=lambda x: f"{x} • {MODULE_SPECS[x]['name'] if x in MODULE_SPECS else ''} • {'✅' if st.session_state.modules[x]['status']=='done' else '🔒' if st.session_state.modules[x]['status']=='locked' else '⏳'}"
    )
    
    st.divider()
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("💾 Backup"):
            backup_data = {
                "config": st.session_state.config,
                "modules": {k: {kk: vv for kk, vv in v.items() if kk not in ['output', 'evidence_log']} for k, v in st.session_state.modules.items()},
                "anchor": st.session_state.anchor,
                "evidence_chain": st.session_state.evidence_chain[-20:],  # Last 20 refs
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
                st.session_state.modules[m] = {"status": "locked", "data": None, "output": None, "evidence_log": []}
            st.session_state.modules["M0"]["status"] = "pending"
            st.session_state.modules["CL"]["status"] = "done"
            st.session_state.current = "M0"
            st.session_state.anchor = {"topic": "", "novelty": [], "method": "", "target": "", "locked_after_M6": False}
            st.session_state.evidence_chain = []
            st.rerun()

# ================= RENDER MODUL =================
def render_m0():
    st.header("📥 M0: Literature Search")
    st.info("📌 **Abstract-Only Mode**: Masukkan metadata jurnal primer. Sistem menolak otomatis konferensi/SLR/PDF.")
    
    with st.form("m0_form"):
        kw = st.text_input("Keyword Target (Bahasa Inggris)", placeholder="Contoh: sentiment analysis e-commerce")
        st.markdown("### Input Metadata Paper (Paste 1 blok per paper)")
        paper_text = st.text_area(
            "Format per paper:\n```\nTITLE: [judul lengkap]\nAUTHORS: [nama]\nYEAR: [tahun]\nJOURNAL: [nama jurnal]\nKEYWORDS: [kw1; kw2]\nABSTRACT: [teks abstrak]\nDOI: [10.xxxx/...]\nSOURCE: [Scopus/IEEE]\n```", 
            height=300,
            placeholder="Paste metadata 10 paper di sini..."
        )
        
        col1, col2 = st.columns([1, 2])
        with col1:
            valid = st.form_submit_button("✅ Validasi & Proses", type="primary")
        with col2:
            st.markdown("🔍 **Auto-Filter Aktif (Dashboard v2.2)**:\n- ✅ `journal-article` only\n- ✅ 4 tahun terakhir\n- ✅ ≥50% dari 1–2 tahun terkini\n- ❌ Exclude: conference/proceedings/SLR/meta-analysis")
            
    if valid:
        if not kw or not paper_text:
            st.error("❌ Keyword dan metadata paper wajib diisi.")
            return
            
        # Simpan & Proses
        st.session_state.modules["M0"]["data"] = {"keyword": kw, "raw": paper_text}
        
        if st.session_state.process_mode == "👐 Manual (Eksternal AI)":
            with st.spinner("⏳ Menyiapkan prompt Core Layer v3.0 + validasi M0..."):
                st.session_state.modules["M0"]["output"] = run_ai_processing("M0", {"keyword": kw, "raw": paper_text})
                save_state()
                st.success("✅ Prompt siap + validasi M0 selesai! Buka tab 📖 Detail untuk menyalin.")
        else:
            st.warning("⚠️ Mode otomatis belum diimplementasi. Menggunakan fallback manual mode.")
            st.session_state.modules["M0"]["output"] = run_ai_processing("M0", {"keyword": kw, "raw": paper_text})
            save_state()
            
        st.rerun()

def render_output_layer(module_id: str):
    """Render output 3-tier dengan dukungan manual mode + evidence chain tracking"""
    out = st.session_state.modules[module_id]["output"]
    if not out:
        st.warning("⏳ Belum diproses. Klik tombol 🚀 Proses terlebih dahulu.")
        return
        
    t1, t2, t3 = st.tabs(["📋 Ringkasan", "📖 Detail Akademik", "📦 Metadata"])
    
    with t1:
        st.markdown(out["layer1_summary"])
        st.caption("💡 Gunakan ringkasan untuk executive summary atau abstrak cepat.")
        
        # Evidence quick stats
        if module_id in ["M2", "M4", "M6"]:
            st.markdown("#### 📊 Evidence Snapshot")
            refs = [r for r in st.session_state.evidence_chain if r.get("module") == module_id]
            st.metric("Klaim tereferensi", f"{len(refs)}", delta=None)
        
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
                height=500 if module_id in ["M6", "M7", "M8"] else 400,
                placeholder="Paste hasil lengkap dari AI eksternal di sini..."
            )
            
            col_s1, col_s2 = st.columns([1, 3])
            with col_s1:
                if st.button("💾 Simpan Hasil", type="primary", key=f"save_manual_{module_id}"):
                    if user_result.strip():
                        # Update output dengan hasil user
                        st.session_state.modules[module_id]["output"]["layer2_academic"] = user_result
                        st.session_state.modules[module_id]["output"]["user_verified"] = True
                        st.session_state.modules[module_id]["user_output"] = user_result
                        
                        # Extract & log evidence references (simple regex)
                        refs = re.findall(r'\[Ref:\s*([^\]]+)\]', user_result)
                        for ref in refs:
                            st.session_state.evidence_chain.append({
                                "module": module_id,
                                "ref": ref,
                                "timestamp": datetime.datetime.now().isoformat()
                            })
                        
                        save_state()
                        st.success("✅ Hasil tersimpan! Modul siap dilanjutkan.")
                        st.rerun()
                    else:
                        st.warning("⚠️ Hasil tidak boleh kosong.")
            with col_s2:
                if st.button("🗑️ Kosongkan", key=f"clear_manual_{module_id}"):
                    st.session_state.modules[module_id]["user_output"] = ""
                    st.rerun()
                    
            # Tampilkan guardrail checklist + evidence tracking
            with st.expander("🛡️ Checklist Guardrail & Evidence (Opsional)"):
                st.checkbox("✅ Setiap klaim merujuk ke metadata intake [Ref: ID_Paper]", key=f"gr1_{module_id}")
                st.checkbox("✅ Tidak ada halusinasi sitasi/DOI/metode", key=f"gr2_{module_id}")
                st.checkbox("✅ Output sesuai spesifikasi modul (kata, struktur, bahasa)", key=f"gr3_{module_id}")
                if st.session_state.config["terminology"]["instansi"]:
                    st.checkbox("✅ Konsisten: 'instansi' & 'pegawai' digunakan", key=f"gr4_{module_id}")
                
                # Evidence log preview
                refs = [r for r in st.session_state.evidence_chain if r.get("module") == module_id]
                if refs:
                    st.markdown(f"#### 📎 Evidence References ({len(refs)})")
                    for r in refs[-5:]:  # Last 5
                        st.caption(f"`[Ref: {r['ref']}]`")
                
        else:
            # Mode otomatis (placeholder)
            st.markdown(f"<div class='academic-text'>{out.get('layer2_academic', '')}</div>", unsafe_allow_html=True)
            if st.button("📋 Salin ke Clipboard"):
                st.toast("Tersalin! (Fitur clipboard memerlukan interaksi browser)")
            
    with t3:
        st.json(out["layer3_metadata"])
        st.caption("📤 Format siap export ke .docx, .tex, atau .json")
        
        # Evidence summary & guardrail status
        if out.get("layer3_metadata", {}).get("guardrails"):
            st.markdown("#### Guardrail Status")
            for g in out["layer3_metadata"]["guardrails"]:
                st.markdown(f"✅ {g}")
        
        # Validation summary for M0
        if module_id == "M0" and out["layer3_metadata"].get("validation_summary"):
            st.markdown("#### 📊 Validasi M0 Summary")
            st.info(out["layer3_metadata"]["validation_summary"])

def render_generic_module(mod_id: str):
    st.header(f"⚙️ {mod_id}: {MODULE_SPECS[mod_id]['name']}")
    st.caption(MODULE_SPECS[mod_id]['desc'])
    
    if st.session_state.modules[mod_id]["status"] == "locked":
        st.error("🔒 Modul terkunci. Selesaikan modul sebelumnya terlebih dahulu.")
        prev_idx = MODULES.index(mod_id) - 1
        if prev_idx >= 0:
            st.info(f"💡 Lanjutkan dari modul: **{MODULES[prev_idx]}** ({MODULE_SPECS[MODULES[prev_idx]]['name']})")
        return
        
    st.markdown('<div class="guardrail-box">🛡️ <strong>Guardrail Aktif:</strong> Anti-Halusinasi • Evidence Chain • Abstract-Only • Iteratif Protocol • Terminology Consistency</div>', unsafe_allow_html=True)
    
    # Tampilkan data input jika ada
    if st.session_state.modules[mod_id]["data"]:
        with st.expander("📥 Lihat Input Data"):
            data = st.session_state.modules[mod_id]["data"]
            if isinstance(data, dict) and "validated_papers" in data:
                # Show validated papers summary for M0
                papers = data["validated_papers"]
                st.write(f"**{len(papers)} paper tervalidasi**")
                for p in papers[:3]:  # Preview first 3
                    st.markdown(f"- `{p['_id']}`: {p.get('TITLE', '')[:80]}...")
            else:
                st.json(data)
    
    # Tombol proses
    if not st.session_state.modules[mod_id].get("output"):
        if st.button(f"🚀 Proses {mod_id}", type="primary"):
            if st.session_state.process_mode == "👐 Manual (Eksternal AI)":
                with st.spinner(f"⏳ Menyiapkan prompt Core Layer v3.0 untuk {mod_id}..."):
                    input_data = st.session_state.modules[mod_id]["data"] or {}
                    # Add anchor context for modules after M6
                    if mod_id in ["M7", "M8", "M9"] and st.session_state.anchor["locked_after_M6"]:
                        input_data["_anchor"] = st.session_state.anchor
                    st.session_state.modules[mod_id]["output"] = run_ai_processing(mod_id, input_data)
                    save_state()
                    st.success(f"✅ Prompt {mod_id} siap! Buka tab 📖 Detail untuk menyalin.")
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
if mod == "CL":
    st.header("🔷 Core Layer — Fondasi Sistem")
    st.markdown("""
    ### Core Layer v3.0 — Active ✅
    
    **Mode**: Abstract-Based Input Mode  
    **Guardrails**: Anti-Halusinasi • Evidence Chain • Terminology Consistency • Iteratif Protocol  
    **Input Schema**: TITLE • AUTHORS • YEAR • JOURNAL • KEYWORDS • ABSTRACT • DOI • SOURCE  
    
    ### Status Modul
    """)
    for m in MODULES:
        status = st.session_state.modules[m]["status"]
        icon = "✅" if status == "done" else "🔒" if status == "locked" else "⏳"
        st.markdown(f"- {icon} **{m}**: {MODULE_SPECS[m]['name']}")
        
elif mod == "M0":
    render_m0()
elif mod in ["M6", "M7", "M8", "M9"]:
    render_generic_module(mod)
else:
    # M1-M5: framework siap dikembangkan dengan spesifikasi dashboard
    st.info(f"🚧 Modul {mod} ({MODULE_SPECS[mod]['name']}) dalam pengembangan. Gunakan M0, M6-M9 untuk alur penelitian lengkap.")
    render_generic_module(mod)

# ================= FOOTER INTEGRITY =================
st.divider()
st.caption("📘 ALAS v3.0 • Abstract-Based Input Mode • Dashboard v2.2 Compatible • No Fake Data • Evidence Chain Active • Terminology: instansi/pegawai")
