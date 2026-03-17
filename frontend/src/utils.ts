'use strict'

export function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function formatMessage(content) {
  return escapeHtml(content).replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

export function fmtDuration(secs) {
  if (secs == null) return '—'
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = secs % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
}

function _locale() {
  const lang = localStorage.getItem('dispatch_lang') || 'ca'
  return { ca: 'ca-AD', es: 'es-ES', fr: 'fr-FR', en: 'en-GB' }[lang] || 'ca-AD'
}

export function fmtDate(iso) {
  if (!iso) return '—'
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z')
  return d.toLocaleString(_locale(), {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

export function fmtTime(iso) {
  if (!iso) return ''
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z')
  return d.toLocaleTimeString(_locale(), { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

export function fmtElapsed(secs) {
  const h = Math.floor(secs / 3600)
  const m = Math.floor((secs % 3600) / 60)
  const s = secs % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
}

export const PRIORITY_STYLES = {
  1: { pill: 'background:#dcfce7;color:#16a34a;border:1px solid #86efac',  large: 'color:#16a34a' },
  2: { pill: 'background:#fef9c3;color:#ca8a04;border:1px solid #fde047',  large: 'color:#ca8a04' },
  3: { pill: 'background:#ffedd5;color:#ea580c;border:1px solid #fed7aa',  large: 'color:#ea580c' },
  4: { pill: 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5',  large: 'color:#dc2626' },
  5: { pill: 'background:#fef2f2;color:#991b1b;border:1px solid #fca5a5',  large: 'color:#991b1b' },
}

export function pStyle(p) {
  return PRIORITY_STYLES[p] || {
    pill:  'background:var(--surface2);color:var(--text3);border:1px solid var(--border)',
    large: 'color:var(--text3)',
  }
}

export const ROLE_LABELS = { admin: '🔑 Admin', formador: '🎓 Formador', operador: '👮 Operador' }
export const ROLE_STYLES = {
  admin:    'background:#f3e8ff;color:#7e22ce;border:1px solid #e9d5ff',
  formador: 'background:#fef9c3;color:#92400e;border:1px solid #fef08a',
  operador: 'background:#eff6ff;color:#1e40af;border:1px solid #bfdbfe',
}

export const INCIDENT_TYPES = [
  { value: 'Incendio',            label: '🔥 Incendi' },
  { value: 'Incendi forestal',    label: '🌲 Incendi forestal' },
  { value: 'Accidente',           label: '🚗 Accident de trànsit' },
  { value: 'Inundació',           label: '💧 Inundació' },
  { value: 'Emergència mèdica',   label: '🏥 Emergència mèdica' },
  { value: 'Allau',               label: '❄️ Allau' },
]

export const RISKS = [
  { value: 'Gas',         label: '🔴 Gas',         accent: 'accent-orange-500' },
  { value: 'Electricitat',label: '⚡ Electricitat', accent: 'accent-yellow-500' },
  { value: 'Químics',     label: '☢️ Químics',      accent: 'accent-green-600'  },
  { value: 'Estructural', label: '🏗️ Estructural',  accent: 'accent-blue-500'   },
  { value: 'Explosius',   label: '💥 Explosius',    accent: 'accent-purple-500' },
  { value: 'Biohazard',   label: '🦠 Biohazard',    accent: 'accent-red-600'    },
]
