// ================= STATE MANAGEMENT =================
const DEFAULT_STATE = {
  config: { domain: '', level: '', target: '' },
  currentModule: 'M0',
  modules: {
    M0: { status: 'pending', data: [], papers: [] },
    M1: { status: 'locked', data: {} },
    M2: { status: 'locked', data: {} },
    M3: { status: 'locked', data: {} },
    M4: { status: 'locked', data: {} },
    M5: { status: 'locked', data: {} },
    M6: { status: 'locked', data: {} },
    M7: { status: 'locked', data: {} },
    M8: { status: 'locked', data: {} },
    M9: { status: 'locked', data: {} }
  },
  anchorCore: null,
  lastSaved: new Date().toISOString()
};

let state = JSON.parse(localStorage.getItem('ALAS_v3_state')) || JSON.parse(JSON.stringify(DEFAULT_STATE));

function saveState() {
  state.lastSaved = new Date().toISOString();
  localStorage.setItem('ALAS_v3_state', JSON.stringify(state));
}

function updateState(path, value) {
  const keys = path.split('.');
  let target = state;
  for (let i = 0; i < keys.length - 1; i++) target = target[keys[i]];
  target[keys[keys.length - 1]] = value;
  saveState();
}

// ================= UI RENDERING =================
function renderProgress() {
  const steps = Object.keys(state.modules);
  const container = document.getElementById('module-steps');
  container.innerHTML = '';
  
  let doneCount = 0;
  steps.forEach(mod => {
    const status = state.modules[mod].status;
    const el = document.createElement('div');
    el.className = `step ${status}`;
    el.textContent = mod;
    el.onclick = () => switchModule(mod);
    container.appendChild(el);
    if (status === 'done') doneCount++;
  });

  const pct = (doneCount / steps.length) * 100;
  document.getElementById('progress-bar').style.width = `${pct}%`;
}

function renderContent(view = 'input') {
  const area = document.getElementById('content-area');
  area.innerHTML = '';

  if (view === 'input') renderM0Input(area);
  else if (view === 'process') renderProcessView(area);
  else if (view === 'output') renderOutputView(area);
}

function renderM0Input(container) {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <h3>📥 Modul 0: Literature Search</h3>
    <div class="form-group">
      <label>Keyword Target</label>
      <input type="text" id="m0-keyword" class="form-input" placeholder="Contoh: sentiment analysis e-commerce">
    </div>
    <div id="paper-list"></div>
    <button class="btn btn-primary" id="btn-add-paper">+ Tambah Paper</button>
    <button class="btn btn-secondary" id="btn-validate-m0" style="margin-left:8px">Validasi & Proses</button>
  `;
  container.appendChild(card);

  // Event: Add Paper
  document.getElementById('btn-add-paper').onclick = () => addPaperForm();
  
  // Event: Validate
  document.getElementById('btn-validate-m0').onclick = () => processM0();
  
  renderPaperList();
}

let paperForms = [];
function addPaperForm() {
  const id = Date.now();
  const div = document.createElement('div');
  div.className = 'card';
  div.dataset.id = id;
  div.innerHTML = `
    <h4>Paper #${paperForms.length + 1}</h4>
    <div class="form-group"><label>Title</label><input type="text" class="form-input" data-field="TITLE"></div>
    <div class="form-group"><label>Authors</label><input type="text" class="form-input" data-field="AUTHORS"></div>
    <div class="form-group"><label>Year</label><input type="number" class="form-input" data-field="YEAR"></div>
    <div class="form-group"><label>Journal</label><input type="text" class="form-input" data-field="JOURNAL"></div>
    <div class="form-group"><label>Keywords</label><input type="text" class="form-input" data-field="KEYWORDS" placeholder="kw1; kw2; kw3"></div>
    <div class="form-group"><label>Abstract</label><textarea class="form-textarea" data-field="ABSTRACT"></textarea></div>
    <div class="form-group"><label>DOI</label><input type="text" class="form-input" data-field="DOI"></div>
    <div class="form-group"><label>Source</label>
      <select class="form-select" data-field="SOURCE">
        <option>Scopus</option><option>IEEE</option><option>Crossref</option>
      </select>
    </div>
    <button class="btn btn-danger btn-sm" onclick="removePaper(${id})">Hapus</button>
  `;
  document.getElementById('paper-list').appendChild(div);
  paperForms.push(id);
}

window.removePaper = (id) => {
  document.querySelector(`.card[data-id="${id}"]`).remove();
  paperForms = paperForms.filter(p => p !== id);
};

function renderPaperList() {
  document.getElementById('paper-list').innerHTML = '';
  paperForms = [];
  state.modules.M0.papers.forEach((p, i) => {
    const div = document.createElement('div');
    div.className = 'card';
    div.innerHTML = `<strong>Paper #${i+1}:</strong> ${p.TITLE}<br><span class="badge badge-success">✅ Tersimpan</span>`;
    document.getElementById('paper-list').appendChild(div);
  });
}

// ================= PROCESS & AI SIMULATION =================
function processM0() {
  const keyword = document.getElementById('m0-keyword').value.trim();
  const forms = document.querySelectorAll('.card[data-id]');
  const papers = [];

  forms.forEach(form => {
    const data = {};
    form.querySelectorAll('input, textarea, select').forEach(el => {
      if (el.dataset.field) data[el.dataset.field] = el.value.trim();
    });
    if (data.TITLE && data.ABSTRACT) papers.push(data);
  });

  if (papers.length < 1) return alert('Masukkan minimal 1 paper valid.');
  if (!keyword) return alert('Keyword wajib diisi.');

  updateState('currentModule', 'M0');
  updateState('modules.M0.data', { keyword, papers });
  state.modules.M0.status = 'running';
  renderProgress();
  simulateAI('M0', 'Processing metadata & applying journal-primary filter...');
}

function simulateAI(moduleId, message) {
  const area = document.getElementById('content-area');
  area.innerHTML = `
    <div class="card" style="text-align:center">
      <div class="loading-spinner"></div>
      <p>${message}</p>
      <span class="badge badge-warning">⏳ Abstract-Only Mode | Anti-Halusinasi Aktif</span>
    </div>
  `;

  // 🔌 INTEGRASI AI API: Ganti setTimeout ini dengan fetch() ke endpoint AI Anda
  // Kirim prompt Core Layer v3.0 + data input, stream response, parse output
  setTimeout(() => {
    state.modules[moduleId].status = 'done';
    state.modules[moduleId].data.result = '✅ Analisis selesai. Evidence chain: 100% terverifikasi.';
    
    // Unlock next module
    const mods = Object.keys(state.modules);
    const idx = mods.indexOf(moduleId);
    if (idx >= 0 && idx < mods.length - 1) {
      state.modules[mods[idx + 1]].status = 'pending';
    }
    
    saveState();
    renderProgress();
    renderContent('output');
  }, 2500);
}

// ================= OUTPUT VIEW (3-TIER) =================
function renderOutputView(container) {
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `
    <h3>📤 Output Layer</h3>
    <div class="tab-group">
      <button class="tab-btn active" onclick="switchTab('summary')">📋 Ringkasan</button>
      <button class="tab-btn" onclick="switchTab('academic')">📖 Detail</button>
      <button class="tab-btn" onclick="switchTab('meta')">📦 Metadata</button>
    </div>
    <div id="layer-summary" class="output-layer active">
      <ul><li>10 paper tervalidasi</li><li>Filter: Jurnal Primer | 4 Tahun | 50% Terkini</li><li>Status: Siap ke M1/M6</li></ul>
    </div>
    <div id="layer-academic" class="output-layer">
      <p>Konten akademik lengkap akan muncul di sini setelah pemrosesan AI. Format Markdown terstruktur, siap salin ke .docx/.md</p>
    </div>
    <div id="layer-meta" class="output-layer">
      <pre style="background:#f3f4f6;padding:10px;border-radius:8px;overflow:auto;font-size:0.85rem">${JSON.stringify(state.modules.M0.data, null, 2)}</pre>
    </div>
  `;
  container.appendChild(card);
}

window.switchTab = (layer) => {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.output-layer').forEach(l => l.classList.remove('active'));
  document.querySelector(`.tab-btn:nth-child(${['summary','academic','meta'].indexOf(layer)+1})`).classList.add('active');
  document.getElementById(`layer-${layer}`).classList.add('active');
};

// ================= NAVIGATION & CONTROLS =================
function switchModule(mod) {
  if (state.modules[mod].status === 'locked') return alert('Modul terkunci. Selesaikan modul sebelumnya.');
  state.currentModule = mod;
  saveState();
  renderProgress();
  renderContent('input');
}

document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    renderContent(btn.dataset.view);
  };
});

// Settings Modal
const modal = document.getElementById('settings-modal');
document.getElementById('btn-settings').onclick = () => {
  document.getElementById('cfg-domain').value = state.config.domain;
  document.getElementById('cfg-level').value = state.config.level;
  document.getElementById('cfg-target').value = state.config.target;
  modal.showModal();
};
document.getElementById('btn-close-modal').onclick = () => modal.close();
document.getElementById('config-form').onsubmit = (e) => {
  e.preventDefault();
  state.config.domain = document.getElementById('cfg-domain').value;
  state.config.level = document.getElementById('cfg-level').value;
  state.config.target = document.getElementById('cfg-target').value;
  saveState();
  modal.close();
  alert('✅ Core Layer config tersimpan.');
};

// Export State
document.getElementById('btn-export').onclick = () => {
  const blob = new Blob([JSON.stringify(state, null, 2)], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `ALAS_backup_${new Date().toISOString().slice(0,10)}.json`;
  a.click();
};

// ================= INIT =================
document.addEventListener('DOMContentLoaded', () => {
  renderProgress();
  renderContent('input');
});
