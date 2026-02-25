'use strict';

// ════════════════════════════════════════
// THEME
// ════════════════════════════════════════

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  document.getElementById('icon-moon').style.display = theme === 'light' ? '' : 'none';
  document.getElementById('icon-sun').style.display  = theme === 'dark'  ? '' : 'none';
  localStorage.setItem('dispatch_theme', theme);
}
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme');
  applyTheme(current === 'dark' ? 'light' : 'dark');
}
applyTheme(localStorage.getItem('dispatch_theme') || 'light');

// ════════════════════════════════════════
// AUTH STATE
// ════════════════════════════════════════

let authToken   = localStorage.getItem('dispatch_token');
let currentUser = JSON.parse(localStorage.getItem('dispatch_user') || 'null');

// ════════════════════════════════════════
// APP STATE
// ════════════════════════════════════════

let currentIncidentId  = null;
let selectedPriority   = 1;
let scenariosCache     = [];
let usersCache         = [];
let editUserId         = null;
let historyData        = [];
let activeHistoryPriority = null;
const sessionIncidents = [];

// ════════════════════════════════════════
// CHRONOMETER
// ════════════════════════════════════════

let chronometerInterval = null;
let callStartTime       = null;

function startChronometer() {
  callStartTime = new Date();
  const controls = document.getElementById('call-controls');
  controls.classList.remove('hidden');
  controls.classList.add('flex');
  if (chronometerInterval) clearInterval(chronometerInterval);
  chronometerInterval = setInterval(tickChronometer, 1000);
  tickChronometer();
}
function tickChronometer() {
  const elapsed = Math.floor((Date.now() - callStartTime.getTime()) / 1000);
  const m = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const s = String(elapsed % 60).padStart(2, '0');
  document.getElementById('chronometer').textContent = `${m}:${s}`;
}
function stopChronometer() {
  if (chronometerInterval) {
    clearInterval(chronometerInterval);
    chronometerInterval = null;
  }
  const badge = document.getElementById('call-status-badge');
  badge.textContent = 'Finalitzada';
  badge.style.cssText = 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5;font-size:11px;padding:3px 12px;border-radius:9999px;font-weight:700;letter-spacing:.05em;text-transform:uppercase';
  document.getElementById('chronometer').style.color = '#dc2626';
  const btn = document.getElementById('end-call-btn');
  btn.disabled = true;
  btn.textContent = '✓ Trucada finalitzada';
}
async function endCall() {
  if (!currentIncidentId) return;
  const btn = document.getElementById('end-call-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Finalitzant...';
  const res = await apiFetch(`/api/v1/incidents/${currentIncidentId}/call`, { method: 'PATCH' });
  if (!res || !res.ok) {
    btn.disabled = false;
    btn.textContent = 'Finalitzar Trucada';
    addSystemMessage('Error finalitzant la trucada');
    return;
  }
  stopChronometer();
  document.getElementById('msg-input').disabled = true;
  document.getElementById('send-btn').disabled  = true;
  addSystemMessage('Trucada finalitzada · Omple la fitxa i guarda la intervenció');
}

// ════════════════════════════════════════
// LIVE CLOCK
// ════════════════════════════════════════

function tickClock() {
  document.getElementById('live-clock').textContent =
    new Date().toLocaleTimeString('ca-AD', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
}
setInterval(tickClock, 1000);
tickClock();

// ════════════════════════════════════════
// BOOT
// ════════════════════════════════════════

window.addEventListener('DOMContentLoaded', () => {
  if (authToken && currentUser) onAuthReady();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeDebriefing(); closeEditUser(); }
});

function onAuthReady() {
  document.getElementById('login-modal').classList.add('hidden');
  document.getElementById('user-label').textContent = `${currentUser.username} · ${currentUser.role}`;
  if (['formador', 'admin'].includes(currentUser.role)) {
    document.getElementById('nav-scenarios').classList.remove('hidden');
    document.getElementById('nav-users').classList.remove('hidden');
    document.getElementById('nav-history').classList.remove('hidden');
  }
  if (currentUser.role !== 'admin') {
    document.getElementById('usr-role-formador').classList.add('hidden');
    document.getElementById('usr-role-admin').classList.add('hidden');
  }
  toggleExpiryField();
  setPriority(1);
  loadScenarios();
}

// ════════════════════════════════════════
// LOGIN / LOGOUT
// ════════════════════════════════════════

async function doLogin() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl    = document.getElementById('login-error');
  errEl.classList.add('hidden');
  try {
    const res = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      errEl.textContent = (await res.json()).detail || 'Error';
      errEl.classList.remove('hidden');
      return;
    }
    const data = await res.json();
    authToken   = data.access_token;
    currentUser = data.user;
    localStorage.setItem('dispatch_token', authToken);
    localStorage.setItem('dispatch_user', JSON.stringify(currentUser));
    onAuthReady();
  } catch {
    errEl.textContent = 'Error de connexió';
    errEl.classList.remove('hidden');
  }
}
function doLogout() {
  authToken   = null;
  currentUser = null;
  localStorage.removeItem('dispatch_token');
  localStorage.removeItem('dispatch_user');
  location.reload();
}

// ════════════════════════════════════════
// API FETCH WRAPPER
// ════════════════════════════════════════

async function apiFetch(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (authToken) headers['Authorization'] = `Bearer ${authToken}`;
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) { doLogout(); return null; }
  return res;
}

// ════════════════════════════════════════
// TABS
// ════════════════════════════════════════

function showTab(tab) {
  ['emergency', 'scenarios', 'users', 'history'].forEach(t => {
    document.getElementById(`panel-${t}`).classList.toggle('hidden', t !== tab);
    document.getElementById(`panel-${t}`).classList.toggle('flex',   t === tab);
    const btn = document.getElementById(`nav-${t}`);
    if (btn) btn.classList.toggle('active', t === tab);
  });
  if (tab === 'scenarios') loadScenarios();
  if (tab === 'users')     loadUsers();
  if (tab === 'history')   loadHistory();
}

// ════════════════════════════════════════
// SCENARIOS
// ════════════════════════════════════════

async function loadScenarios() {
  const res = await apiFetch('/api/v1/scenarios');
  if (!res || !res.ok) return;
  scenariosCache = await res.json();
  const sel = document.getElementById('scenario-select');
  sel.innerHTML = '<option value="">— Emergència lliure —</option>';
  scenariosCache.forEach(s => {
    sel.innerHTML += `<option value="${s.id}">[${s.incident_type}] ${s.title}</option>`;
  });
  renderScenarioList();
}
function renderScenarioList() {
  const ul = document.getElementById('scenario-list');
  if (!ul) return;
  ul.innerHTML = !scenariosCache.length
    ? `<li class="text-xs px-4 py-3" style="color:var(--text3)">Cap escenari creat</li>`
    : scenariosCache.map(s => `
        <li class="scenario-li flex items-center justify-between px-4 py-3 hover:bg-blue-50 transition"
            style="border-color:var(--border2);border-bottom-width:1px;border-bottom-style:solid">
          <div class="min-w-0 mr-2">
            <p class="text-xs font-semibold truncate" style="color:var(--text)">${escapeHtml(s.title)}</p>
            <p class="text-xs" style="color:var(--text3)">${s.incident_type} · ${escapeHtml(s.base_location)}</p>
          </div>
          <button onclick="deleteScenario(${s.id})" class="text-xs flex-shrink-0 transition" style="color:var(--text3)">✕</button>
        </li>`).join('');
}
async function createScenario() {
  const payload = {
    title:               document.getElementById('sc-title').value.trim(),
    incident_type:       document.getElementById('sc-type').value,
    base_location:       document.getElementById('sc-location').value.trim(),
    initial_description: document.getElementById('sc-desc').value.trim(),
    instructions_ia:     document.getElementById('sc-instructions').value.trim(),
  };
  if (!payload.title || !payload.base_location || !payload.initial_description || !payload.instructions_ia) {
    alert('Omple tots els camps');
    return;
  }
  const res = await apiFetch('/api/v1/scenarios', { method: 'POST', body: JSON.stringify(payload) });
  if (!res || !res.ok) { alert("Error creant l'escenari"); return; }
  ['sc-title', 'sc-location', 'sc-desc', 'sc-instructions'].forEach(id => {
    document.getElementById(id).value = '';
  });
  await loadScenarios();
}
async function deleteScenario(id) {
  if (!confirm('Eliminar aquest escenari?')) return;
  const res = await apiFetch(`/api/v1/scenarios/${id}`, { method: 'DELETE' });
  if (res && (res.ok || res.status === 204)) await loadScenarios();
}
function onScenarioChange() {
  const id = document.getElementById('scenario-select').value;
  if (!id) { setFieldsLocked(false); return; }
  const scenario = scenariosCache.find(x => x.id === +id);
  if (!scenario) return;
  [...document.getElementById('incident-type').options].forEach(o => {
    if (o.value === scenario.incident_type) o.selected = true;
  });
  document.getElementById('incident-location').value = scenario.base_location;
  document.getElementById('incident-desc').value     = scenario.initial_description;
  setFieldsLocked(true);
}
function setFieldsLocked(locked) {
  ['incident-type', 'incident-location', 'incident-desc'].forEach(id => {
    document.getElementById(id).disabled = locked;
  });
}

// ════════════════════════════════════════
// PRIORITY
// ════════════════════════════════════════

function setPriority(p) {
  selectedPriority = p;
  document.querySelectorAll('.prio').forEach(b => b.classList.toggle('sel', +b.dataset.p === p));
}

// ════════════════════════════════════════
// START INCIDENT
// ════════════════════════════════════════

async function startIncident() {
  const sid = document.getElementById('scenario-select').value;
  const btn = document.getElementById('new-incident-btn');
  btn.disabled = true;
  btn.innerHTML = '⏳ Creant...';
  try {
    const body = sid
      ? { scenario_id: +sid, priority: selectedPriority }
      : {
          type:        document.getElementById('incident-type').value,
          location:    document.getElementById('incident-location').value.trim() || 'Desconeguda',
          description: document.getElementById('incident-desc').value.trim()     || 'Sense descripció',
          priority:    selectedPriority,
        };
    const res = await apiFetch('/api/v1/incidents', { method: 'POST', body: JSON.stringify(body) });
    if (!res || !res.ok) { addSystemMessage("Error creant l'incident"); return; }
    const inc = await res.json();
    currentIncidentId = inc.id;
    sessionIncidents.push(inc);
    document.getElementById('badge-id').textContent            = inc.id;
    document.getElementById('badge-type').textContent          = inc.type;
    document.getElementById('incident-badge').classList.remove('hidden');
    document.getElementById('chat-title').textContent          = `Incident #${inc.id} — ${inc.type}`;
    document.getElementById('chat-subtitle').textContent       = `📍 ${inc.location}`;
    const ph = document.getElementById('chat-placeholder');
    if (ph) ph.remove();
    const scLabel = sid
      ? ` · Escenari: ${scenariosCache.find(s => s.id === +sid)?.title || '#' + sid}`
      : '';
    addSystemMessage(`Incident #${inc.id} obert · ${inc.type} · ${inc.location}${scLabel}`);
    document.getElementById('msg-input').disabled = false;
    document.getElementById('send-btn').disabled  = false;
    document.getElementById('msg-input').focus();
    enableFitxa();
    startChronometer();
    setFieldsLocked(false);
    document.getElementById('scenario-select').value = '';
    renderIncidentList();
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🚨 Iniciar Nova Emergència';
  }
}

// ════════════════════════════════════════
// SEND MESSAGE
// ════════════════════════════════════════

async function sendMessage() {
  const input = document.getElementById('msg-input');
  const text  = input.value.trim();
  if (!text || !currentIncidentId) return;
  input.value = '';
  input.disabled = true;
  document.getElementById('send-btn').disabled = true;
  appendBubble('operator', text);
  const typing = appendTyping();
  try {
    const res = await apiFetch('/api/v1/simulate/chat', {
      method: 'POST',
      body: JSON.stringify({ incident_id: currentIncidentId, operator_message: text }),
    });
    typing.remove();
    if (!res || !res.ok) { addSystemMessage('Error de comunicació'); return; }
    appendBubble('alertant', (await res.json()).content);
  } catch (e) {
    typing.remove();
    addSystemMessage('Error: ' + e.message);
  } finally {
    input.disabled = false;
    document.getElementById('send-btn').disabled = false;
    input.focus();
  }
}
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
}

// ════════════════════════════════════════
// DOM HELPERS
// ════════════════════════════════════════

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
function appendBubble(who, text) {
  const isOp = who === 'operator';
  const wrap  = document.createElement('div');
  wrap.className = isOp ? 'flex justify-end' : 'flex justify-start';
  const bubble = document.createElement('div');
  bubble.className = `max-w-[70%] px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${isOp ? 'bop' : 'bal'}`;
  bubble.innerHTML = escapeHtml(text).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  const label = document.createElement('p');
  label.className = `text-xs mt-1 ${isOp ? 'text-right' : ''}`;
  label.style.color = 'var(--text3)';
  label.textContent = isOp ? `👮 ${currentUser?.username || 'Operador'}` : '📞 Alertant';
  const inner = document.createElement('div');
  inner.className = isOp ? 'flex flex-col items-end' : 'flex flex-col items-start';
  inner.appendChild(bubble);
  inner.appendChild(label);
  wrap.appendChild(inner);
  document.getElementById('chat-messages').appendChild(wrap);
  wrap.scrollIntoView({ behavior: 'smooth' });
  return wrap;
}
function appendTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'flex justify-start';
  wrap.innerHTML = `
    <div class="bal px-4 py-3 flex gap-1 items-center">
      <span class="typing-dot w-2 h-2 rounded-full animate-bounce" style="animation-delay:0ms"></span>
      <span class="typing-dot w-2 h-2 rounded-full animate-bounce" style="animation-delay:150ms"></span>
      <span class="typing-dot w-2 h-2 rounded-full animate-bounce" style="animation-delay:300ms"></span>
    </div>`;
  document.getElementById('chat-messages').appendChild(wrap);
  wrap.scrollIntoView({ behavior: 'smooth' });
  return wrap;
}
function addSystemMessage(text) {
  const el = document.createElement('div');
  el.className = 'sys-msg text-center text-xs py-1.5 px-4 mx-auto rounded-full';
  el.style.maxWidth = '90%';
  el.textContent = text;
  document.getElementById('chat-messages').appendChild(el);
  el.scrollIntoView({ behavior: 'smooth' });
}
function renderIncidentList() {
  document.getElementById('incident-list').innerHTML = sessionIncidents.map(inc => `
    <li class="incident-row cursor-pointer text-xs transition py-1.5 px-4 rounded"
        style="color:var(--text2)"
        onmouseenter="this.style.color='var(--accent)'"
        onmouseleave="this.style.color='var(--text2)'"
        onclick="switchIncident(${inc.id},'${escapeHtml(inc.type)}','${escapeHtml(inc.location)}')">
      <span class="font-mono font-bold mr-1" style="color:var(--text3)">#${inc.id}</span>${inc.type}
    </li>`).join('');
}
function switchIncident(id, type, location) {
  currentIncidentId = id;
  document.getElementById('badge-id').textContent            = id;
  document.getElementById('badge-type').textContent          = type;
  document.getElementById('incident-badge').classList.remove('hidden');
  document.getElementById('chat-title').textContent          = `Incident #${id} — ${type}`;
  document.getElementById('chat-subtitle').textContent       = `📍 ${location}`;
  document.getElementById('chat-messages').innerHTML         = '';
  addSystemMessage(`Canviat a Incident #${id}`);
  document.getElementById('msg-input').disabled = false;
  document.getElementById('send-btn').disabled  = false;
  enableFitxa();
}

// ════════════════════════════════════════
// HISTORY — FORMATTERS
// ════════════════════════════════════════

function fmtDuration(secs) {
  if (secs == null) return '—';
  return `${String(Math.floor(secs / 60)).padStart(2, '0')}:${String(secs % 60).padStart(2, '0')}`;
}
function fmtDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z');
  return d.toLocaleString('ca-AD', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}
function fmtTime(iso) {
  if (!iso) return '';
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z');
  return d.toLocaleTimeString('ca-AD', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

const PRIORITY_STYLES = {
  1: { pill: 'background:#dcfce7;color:#16a34a;border:1px solid #86efac',  large: 'color:#16a34a' },
  2: { pill: 'background:#fef9c3;color:#ca8a04;border:1px solid #fde047',  large: 'color:#ca8a04' },
  3: { pill: 'background:#ffedd5;color:#ea580c;border:1px solid #fed7aa',  large: 'color:#ea580c' },
  4: { pill: 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5',  large: 'color:#dc2626' },
  5: { pill: 'background:#fef2f2;color:#991b1b;border:1px solid #fca5a5',  large: 'color:#991b1b' },
};
function pStyle(p) {
  return PRIORITY_STYLES[p] || {
    pill:  'background:var(--surface2);color:var(--text3);border:1px solid var(--border)',
    large: 'color:var(--text3)',
  };
}

// ════════════════════════════════════════
// HISTORY — LOAD / FILTER / RENDER
// ════════════════════════════════════════

async function loadHistory() {
  const el = document.getElementById('history-list');
  el.innerHTML = `<p class="text-xs animate-pulse" style="color:var(--text3)">Carregant...</p>`;
  const res = await apiFetch('/api/v1/history');
  if (!res || !res.ok) { el.innerHTML = `<p class="text-xs text-red-500">Error</p>`; return; }
  historyData = await res.json();
  renderHistoryTable();
}
function filterHistory(priority) {
  activeHistoryPriority = priority;
  const accentStyle   = 'background:var(--accent);color:#fff;border:1px solid var(--accent)';
  const inactiveStyle = 'background:transparent;color:var(--text3);border:1px solid var(--border)';
  document.getElementById('hf-all').style.cssText = priority === null ? accentStyle : inactiveStyle;
  document.querySelectorAll('.hf-p').forEach(btn => {
    const p = +btn.dataset.p;
    btn.style.cssText = priority === p ? pStyle(p).pill : inactiveStyle;
  });
  renderHistoryTable();
}
function renderHistoryTable() {
  const el      = document.getElementById('history-list');
  const toolbar = document.getElementById('history-toolbar');
  const search  = (document.getElementById('hf-search')?.value || '').toLowerCase();
  const filtered = historyData.filter(inc => {
    if (activeHistoryPriority !== null && inc.priority !== activeHistoryPriority) return false;
    if (search && !`${inc.type} ${inc.location} ${inc.scenario_title || ''}`.toLowerCase().includes(search)) return false;
    return true;
  });
  if (!filtered.length) {
    el.innerHTML = `<p class="text-xs" style="color:var(--text3)">Cap intervenció trobada</p>`;
    toolbar.classList.add('hidden');
    return;
  }
  toolbar.classList.remove('hidden');
  el.innerHTML = filtered.map(inc => {
    const st = pStyle(inc.priority);
    return `
      <div class="history-card rounded-xl overflow-hidden transition" style="background:var(--surface);border:1px solid var(--border)">
        <div class="history-card-hd flex items-center justify-between px-3 py-2"
             style="background:var(--surface2);border-bottom:1px solid var(--border2)">
          <div class="flex items-center gap-2">
            <input type="checkbox" class="h-cb" data-id="${inc.id}" onchange="updateHistorySelection()"
                   style="accent-color:var(--accent);cursor:pointer">
            <span class="text-xs font-mono" style="color:var(--text3)">#${inc.id}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-bold px-2 py-0.5 rounded-full" style="${st.pill}">P${inc.priority}</span>
            <button onclick="deleteHistoryItem(${inc.id})"
              class="text-xs w-5 h-5 flex items-center justify-center rounded-md transition"
              style="color:var(--text3);border:1px solid var(--border)" title="Eliminar">✕</button>
          </div>
        </div>
        <div class="px-3 py-2.5 cursor-pointer"
             onclick="openDebriefing(${inc.id})"
             onmouseenter="this.closest('.history-card').style.borderColor='var(--accent)'"
             onmouseleave="this.closest('.history-card').style.borderColor=this.closest('.history-card').querySelector('.h-cb').checked?'var(--accent)':'var(--border)'">
          <p class="text-xs font-bold truncate" style="color:var(--text)">${escapeHtml(inc.type)}</p>
          <p class="text-xs truncate mt-0.5" style="color:var(--text3)">📍 ${escapeHtml(inc.location)}</p>
          <div class="flex justify-between items-center mt-2">
            <span class="text-xs" style="color:var(--text3)">${fmtDate(inc.call_end_at)}</span>
            <span class="font-mono text-xs font-bold text-indigo-500">${fmtDuration(inc.duration_seconds)}</span>
          </div>
          ${inc.scenario_title ? `<p class="text-xs text-amber-500 truncate mt-1">🎓 ${escapeHtml(inc.scenario_title)}</p>` : ''}
        </div>
        <div class="px-3 pb-3">
          <button onclick="openDebriefing(${inc.id})"
            class="w-full text-xs font-semibold py-1.5 rounded-lg transition"
            style="background:var(--accent-bg);border:1px solid var(--accent-br);color:var(--accent)">
            📊 Obrir debriefing
          </button>
        </div>
      </div>`;
  }).join('');
  updateHistorySelection();
}

// ════════════════════════════════════════
// HISTORY — SELECTION & DELETE
// ════════════════════════════════════════

function toggleSelectAll() {
  const checked = document.getElementById('hf-select-all').checked;
  document.querySelectorAll('.h-cb').forEach(cb => {
    cb.checked = checked;
    const card = cb.closest('.history-card');
    if (card) card.style.borderColor = checked ? 'var(--accent)' : 'var(--border)';
  });
  updateHistorySelection();
}
function updateHistorySelection() {
  const cbs = [...document.querySelectorAll('.h-cb')];
  const sel = cbs.filter(c => c.checked);
  const saEl = document.getElementById('hf-select-all');
  if (saEl) {
    saEl.checked       = sel.length === cbs.length && cbs.length > 0;
    saEl.indeterminate = sel.length > 0 && sel.length < cbs.length;
  }
  const countEl = document.getElementById('hf-sel-count');
  if (countEl) countEl.textContent = `${sel.length} / ${cbs.length}`;
  const delBtn = document.getElementById('hf-del-sel');
  if (delBtn) {
    delBtn.disabled    = sel.length === 0;
    delBtn.textContent = sel.length > 0 ? `Eliminar sel. (${sel.length})` : 'Eliminar sel.';
  }
  cbs.forEach(cb => {
    const card = cb.closest('.history-card');
    if (card) card.style.borderColor = cb.checked ? 'var(--accent)' : 'var(--border)';
  });
}
async function deleteHistoryItem(id) {
  if (!confirm(`Eliminar l'historial #${id}?`)) return;
  const res = await apiFetch(`/api/v1/history/${id}`, { method: 'DELETE' });
  if (!res || !res.ok) { alert("Error eliminant l'historial"); return; }
  await loadHistory();
}
async function deleteSelected() {
  const ids = [...document.querySelectorAll('.h-cb:checked')].map(c => +c.dataset.id);
  if (!ids.length) return;
  if (!confirm(`Eliminar ${ids.length} historial${ids.length > 1 ? 's' : ''}?`)) return;
  const res = await apiFetch('/api/v1/history', { method: 'DELETE', body: JSON.stringify({ ids }) });
  if (!res || !res.ok) { alert("Error eliminant els historials"); return; }
  await loadHistory();
}
async function deleteAllHistory() {
  const total = document.querySelectorAll('.h-cb').length;
  if (!total) return;
  if (!confirm(`Eliminar tot l'historial (${total} entrada${total > 1 ? 's' : ''})?\nAquesta acció no es pot desfer.`)) return;
  const res = await apiFetch('/api/v1/history', { method: 'DELETE', body: JSON.stringify({}) });
  if (!res || !res.ok) { alert("Error eliminant l'historial"); return; }
  await loadHistory();
}

// ════════════════════════════════════════
// DEBRIEFING MODAL
// ════════════════════════════════════════

async function openDebriefing(callId) {
  const modal = document.getElementById('debriefing-modal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
  document.getElementById('db-title').textContent    = `Debriefing — Incident #${callId}`;
  document.getElementById('db-subtitle').textContent = '—';
  document.getElementById('db-transcript').innerHTML =
    `<div class="m-auto text-center" style="color:var(--text3)"><p class="text-3xl mb-2">⏳</p><p class="text-xs">Carregant...</p></div>`;
  document.getElementById('db-fitxa').innerHTML = '';

  const res = await apiFetch(`/api/v1/history/${callId}`);
  if (!res || !res.ok) {
    document.getElementById('db-transcript').innerHTML = `<p class="text-red-500 text-xs m-auto">Error</p>`;
    return;
  }
  const d  = await res.json();
  const ps = pStyle(d.priority);

  document.getElementById('db-title').textContent    = `Debriefing — Incident #${d.id} · ${d.type}`;
  document.getElementById('db-subtitle').textContent = `📍 ${d.location}`;
  const badge = document.getElementById('db-priority-badge');
  badge.textContent = `P${d.priority}`;
  badge.style.cssText = ps.pill + ';font-size:11px;padding:3px 12px;border-radius:9999px;font-weight:700';
  document.getElementById('db-duration').textContent  = fmtDuration(d.duration_seconds);
  document.getElementById('db-initial').textContent   = fmtDuration(d.initial_response_seconds);
  document.getElementById('db-msg-count').textContent = d.message_count;
  const lp = document.getElementById('db-priority-large');
  lp.textContent  = `P${d.priority}`;
  lp.style.cssText = ps.large;
  document.getElementById('db-start').textContent    = fmtDate(d.call_start_at);
  document.getElementById('db-scenario').textContent = d.scenario_title || '— Emergència lliure —';

  const tc = document.getElementById('db-transcript');
  tc.innerHTML = '';
  if (!d.transcript.length) {
    tc.innerHTML = `<p class="text-xs m-auto" style="color:var(--text3)">Sense missatges</p>`;
  } else {
    d.transcript.forEach(msg => {
      const isOp = msg.role === 'user';
      const wrap = document.createElement('div');
      wrap.className = isOp ? 'flex justify-end' : 'flex justify-start';
      wrap.innerHTML = `
        <div class="flex flex-col ${isOp ? 'items-end' : 'items-start'} max-w-[75%]">
          <div class="px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${isOp ? 'bop' : 'bal'}">
            ${escapeHtml(msg.content).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
          </div>
          <p class="text-xs mt-0.5" style="color:var(--text3)">
            ${isOp ? '👮 Operador' : '📞 Alertant'} · ${fmtTime(msg.timestamp)}
          </p>
        </div>`;
      tc.appendChild(wrap);
    });
    tc.scrollTop = tc.scrollHeight;
  }

  const fe = document.getElementById('db-fitxa');
  if (!d.intervention) {
    fe.innerHTML = `<div class="text-center p-4" style="color:var(--text3)"><p class="text-xl mb-1">📋</p><p class="text-xs">Sense fitxa</p></div>`;
  } else {
    const iv    = d.intervention;
    const risks = iv.additional_risks ? iv.additional_risks.split(',').filter(Boolean) : [];
    fe.innerHTML = `
      <div class="fitxa-row-odd flex justify-between items-start px-4 py-3"
           style="background:var(--surface2);border-bottom:1px solid var(--border2)">
        <span class="text-xs" style="color:var(--text3)">📍 Adreça</span>
        <span class="text-xs font-medium text-right ml-4" style="color:var(--text)">${escapeHtml(iv.exact_address) || '—'}</span>
      </div>
      <div class="fitxa-row-even flex justify-between items-center px-4 py-3"
           style="background:var(--surface);border-bottom:1px solid var(--border2)">
        <span class="text-xs" style="color:var(--text3)">📞 Telèfon</span>
        <span class="text-xs font-medium" style="color:var(--text)">${escapeHtml(iv.contact_phone) || '—'}</span>
      </div>
      <div class="fitxa-row-odd flex justify-between items-center px-4 py-3"
           style="background:var(--surface2);border-bottom:1px solid var(--border2)">
        <span class="text-xs" style="color:var(--text3)">🚑 Ferits</span>
        <span class="text-base font-bold font-mono ${iv.num_injured > 0 ? 'text-red-500' : ''}"
              ${iv.num_injured === 0 ? 'style="color:var(--text3)"' : ''}>
          ${iv.num_injured}
        </span>
      </div>
      ${risks.length ? `
      <div class="fitxa-row-even px-4 py-3" style="background:var(--surface);border-bottom:1px solid var(--border2)">
        <p class="text-xs mb-2" style="color:var(--text3)">⚠️ Riscos</p>
        <div class="flex flex-wrap gap-1">
          ${risks.map(r => `<span class="text-xs px-2 py-0.5 rounded-full"
            style="background:#ffedd5;color:#ea580c;border:1px solid #fed7aa">${escapeHtml(r)}</span>`).join('')}
        </div>
      </div>` : ''}
      ${iv.operator_notes ? `
      <div class="fitxa-row-odd px-4 py-3" style="background:var(--surface2);border-bottom:1px solid var(--border2)">
        <p class="text-xs mb-1.5" style="color:var(--text3)">📝 Notes</p>
        <p class="text-xs leading-relaxed" style="color:var(--text2)">${escapeHtml(iv.operator_notes)}</p>
      </div>` : ''}
      <div class="fitxa-db-foot px-4 py-2 text-right" style="background:var(--surface)">
        <p class="text-xs" style="color:var(--text3)">Guardat: ${fmtDate(iv.saved_at)}</p>
      </div>`;
  }
}
function closeDebriefing() {
  const m = document.getElementById('debriefing-modal');
  m.classList.add('hidden');
  m.classList.remove('flex');
}

// ════════════════════════════════════════
// USERS
// ════════════════════════════════════════

const ROLE_LABELS = { admin: '🔑 Admin', formador: '🎓 Formador', operador: '👮 Operador' };
const ROLE_STYLES = {
  admin:    'background:#f3e8ff;color:#7e22ce;border:1px solid #e9d5ff',
  formador: 'background:#fef9c3;color:#92400e;border:1px solid #fef08a',
  operador: 'background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe',
};

async function loadUsers() {
  const res = await apiFetch('/api/v1/users');
  if (!res || !res.ok) return;
  renderUsersTable(await res.json());
}
function renderUsersTable(users) {
  usersCache = users;
  const el = document.getElementById('users-table');
  if (!users.length) {
    el.innerHTML = `<p class="text-xs px-4 py-3" style="color:var(--text3)">Cap usuari</p>`;
    return;
  }
  const now = new Date();
  el.innerHTML = users.map(u => {
    const hasExpiry = u.role === 'operador' && u.expires_at;
    const expDate   = hasExpiry
      ? new Date(u.expires_at.endsWith('Z') || u.expires_at.includes('+') ? u.expires_at : u.expires_at + 'Z')
      : null;
    const isExpired = hasExpiry && expDate < now;
    const canEdit   = ['admin', 'formador'].includes(currentUser?.role) && u.role === 'operador';
    let expiryDisplay = '';
    if (hasExpiry) {
      const dateStr = expDate.toLocaleDateString('ca-AD', { day: '2-digit', month: '2-digit', year: '2-digit' });
      expiryDisplay = `<span class="text-xs" style="color:${isExpired ? '#dc2626' : 'var(--text3)'}">${dateStr}</span>`;
    }
    return `
      <div class="users-row flex items-center justify-between px-4 py-2.5 hover:bg-blue-50 transition"
           style="border-bottom:1px solid var(--border2)${isExpired ? ';background:#fff5f5' : ''}">
        <div class="flex items-center gap-2 min-w-0 flex-1">
          <span class="text-xs font-mono w-5 text-right flex-shrink-0" style="color:var(--text3)">${u.id}</span>
          <span class="text-sm font-medium truncate" style="color:var(--text)">${escapeHtml(u.username)}</span>
          ${isExpired ? '<span class="text-xs px-1.5 py-0.5 rounded font-bold flex-shrink-0" style="background:#fee2e2;color:#dc2626">Caducat</span>' : ''}
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          ${expiryDisplay}
          <span class="text-xs px-2 py-0.5 rounded-full font-semibold" style="${ROLE_STYLES[u.role] || ''}">${ROLE_LABELS[u.role] || u.role}</span>
          <span class="w-2 h-2 rounded-full ${u.is_active ? 'bg-emerald-400' : 'bg-red-400'} inline-block"></span>
          ${canEdit ? `<button onclick="openEditUser(${u.id})" class="text-xs px-2 py-0.5 rounded transition" style="color:var(--accent);border:1px solid var(--accent-br)">✎</button>` : ''}
        </div>
      </div>`;
  }).join('');
}
function toggleExpiryField() {
  const role = document.getElementById('usr-role').value;
  document.getElementById('usr-expiry-wrap').classList.toggle('hidden', role !== 'operador');
}
async function createUser() {
  const username  = document.getElementById('usr-username').value.trim();
  const password  = document.getElementById('usr-password').value;
  const role      = document.getElementById('usr-role').value;
  const expiryVal = document.getElementById('usr-expiry').value;
  const errEl     = document.getElementById('usr-error');
  errEl.classList.add('hidden');
  if (username.length < 3) { errEl.textContent = 'Mínim 3 caràcters'; errEl.classList.remove('hidden'); return; }
  if (password.length < 6) { errEl.textContent = 'Mínim 6 caràcters'; errEl.classList.remove('hidden'); return; }
  const body = { username, password, role };
  if (role === 'operador' && expiryVal) body.expires_at = expiryVal + 'T00:00:00';
  const res = await apiFetch('/api/v1/users', { method: 'POST', body: JSON.stringify(body) });
  if (!res) return;
  if (res.status === 409) { errEl.textContent = "El nom d'usuari ja existeix"; errEl.classList.remove('hidden'); return; }
  if (res.status === 403) { errEl.textContent = 'No tens permís'; errEl.classList.remove('hidden'); return; }
  if (!res.ok)            { errEl.textContent = "Error creant l'usuari"; errEl.classList.remove('hidden'); return; }
  document.getElementById('usr-username').value = '';
  document.getElementById('usr-password').value = '';
  document.getElementById('usr-expiry').value   = '';
  document.getElementById('usr-role').value     = 'operador';
  await loadUsers();
}

// ════════════════════════════════════════
// EDIT USER MODAL
// ════════════════════════════════════════

function openEditUser(id) {
  const u = usersCache.find(x => x.id === id);
  if (!u) return;
  editUserId = id;
  document.getElementById('edit-user-name').textContent   = u.username;
  document.getElementById('edit-user-active').value       = u.is_active ? 'true' : 'false';
  document.getElementById('edit-user-expiry').value       = u.expires_at ? u.expires_at.substring(0, 10) : '';
  document.getElementById('edit-user-error').classList.add('hidden');
  const modal = document.getElementById('edit-user-modal');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}
function closeEditUser() {
  const modal = document.getElementById('edit-user-modal');
  modal.classList.add('hidden');
  modal.classList.remove('flex');
  editUserId = null;
}
async function submitEditUser() {
  if (!editUserId) return;
  const isActive  = document.getElementById('edit-user-active').value === 'true';
  const expiryVal = document.getElementById('edit-user-expiry').value;
  const payload   = { is_active: isActive, expires_at: expiryVal ? expiryVal + 'T00:00:00' : null };
  const errEl     = document.getElementById('edit-user-error');
  errEl.classList.add('hidden');
  const res = await apiFetch(`/api/v1/users/${editUserId}`, { method: 'PATCH', body: JSON.stringify(payload) });
  if (!res) return;
  if (!res.ok) {
    const data = await res.json();
    errEl.textContent = data.detail || "Error actualitzant l'usuari";
    errEl.classList.remove('hidden');
    return;
  }
  closeEditUser();
  await loadUsers();
}

// ════════════════════════════════════════
// FITXA
// ════════════════════════════════════════

function enableFitxa() {
  document.getElementById('fi-save-btn').disabled = false;
}
async function saveIntervention() {
  if (!currentIncidentId) return;
  const risks   = [...document.querySelectorAll('.risk-cb:checked')].map(c => c.value).join(',');
  const payload = {
    incident_id:      currentIncidentId,
    exact_address:    document.getElementById('fi-address').value.trim(),
    contact_phone:    document.getElementById('fi-phone').value.trim(),
    num_injured:      parseInt(document.getElementById('fi-injured').value) || 0,
    additional_risks: risks,
    operator_notes:   document.getElementById('fi-notes').value.trim(),
  };
  const btn = document.getElementById('fi-save-btn');
  btn.disabled = true;
  btn.innerHTML = '⏳ Guardant...';
  const res       = await apiFetch('/api/v1/interventions', { method: 'POST', body: JSON.stringify(payload) });
  const statusEl  = document.getElementById('fi-status');
  if (res && (res.ok || res.status === 201)) {
    if (chronometerInterval !== null) {
      await apiFetch(`/api/v1/incidents/${currentIncidentId}/call`, { method: 'PATCH' });
      stopChronometer();
    }
    const ctrl = document.getElementById('call-controls');
    ctrl.classList.add('hidden');
    ctrl.classList.remove('flex');
    document.getElementById('msg-input').disabled = true;
    document.getElementById('send-btn').disabled  = true;
    statusEl.textContent  = '✓ Intervenció guardada correctament';
    statusEl.style.cssText = 'background:#dcfce7;color:#16a34a;border:1px solid #86efac';
    statusEl.classList.remove('hidden');
    addSystemMessage(`Fitxa guardada · Incident #${currentIncidentId}`);
  } else {
    statusEl.textContent  = '✗ Error en guardar la fitxa';
    statusEl.style.cssText = 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5';
    statusEl.classList.remove('hidden');
  }
  btn.disabled  = false;
  btn.innerHTML = '💾 Finalitzar i Guardar Intervenció';
  setTimeout(() => statusEl.classList.add('hidden'), 4000);
}
