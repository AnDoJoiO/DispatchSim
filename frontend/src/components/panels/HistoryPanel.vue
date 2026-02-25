<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useHistoryStore } from '@/stores/history'
import { useUiStore }      from '@/stores/ui'
import { pStyle, fmtDate, fmtDuration } from '@/utils'

const history = useHistoryStore()
const ui      = useUiStore()

const selected    = ref(new Set())
const selectAllEl = ref(null)
const loading     = ref(false)
const loadError   = ref(false)

onMounted(loadHistory)

async function loadHistory() {
  loading.value   = true
  loadError.value = false
  selected.value  = new Set()
  try { await history.load() }
  catch { loadError.value = true }
  finally { loading.value = false }
}

const filtered = computed(() => {
  const q = history.searchQuery.toLowerCase()
  return history.items.filter(inc => {
    if (history.filterPriority !== null && inc.priority !== history.filterPriority) return false
    if (q && !`${inc.type} ${inc.location} ${inc.scenario_title || ''}`.toLowerCase().includes(q)) return false
    return true
  })
})

const hasItems = computed(() => filtered.value.length > 0)

// Sync select-all checkbox indeterminate state
watch(() => selected.value.size, async () => {
  await nextTick()
  if (!selectAllEl.value) return
  const total = filtered.value.length
  selectAllEl.value.indeterminate = selected.value.size > 0 && selected.value.size < total
  selectAllEl.value.checked = selected.value.size === total && total > 0
})

function setFilter(p) {
  history.filterPriority = p
  selected.value = new Set()
}

function toggleItem(id, checked) {
  const s = new Set(selected.value)
  checked ? s.add(id) : s.delete(id)
  selected.value = s
}

function toggleAll(checked) {
  selected.value = checked ? new Set(filtered.value.map(i => i.id)) : new Set()
}

async function deleteOne(id) {
  if (!confirm(`Eliminar l'historial #${id}?`)) return
  try { await history.deleteOne(id) }
  catch { alert("Error eliminant l'historial") }
  selected.value.delete(id)
}

async function deleteSelected() {
  const ids = [...selected.value]
  if (!ids.length) return
  if (!confirm(`Eliminar ${ids.length} historial${ids.length > 1 ? 's' : ''}?`)) return
  try { await history.deleteMany(ids); selected.value = new Set() }
  catch { alert("Error eliminant els historials") }
}

async function deleteAll() {
  const total = filtered.value.length
  if (!total) return
  if (!confirm(`Eliminar tot l'historial (${total} entrada${total > 1 ? 's' : ''})?\nAquesta acció no es pot desfer.`)) return
  try { await history.deleteAll(); selected.value = new Set() }
  catch { alert("Error eliminant l'historial") }
}

const PRIO_BORDER_COLORS = {
  1: '#16a34a', 2: '#ca8a04', 3: '#ea580c', 4: '#dc2626', 5: '#991b1b',
}
const PRIO_PILL_ACTIVE = {
  1: 'background:#dcfce7;color:#16a34a;border:1px solid #86efac',
  2: 'background:#fef9c3;color:#ca8a04;border:1px solid #fde047',
  3: 'background:#ffedd5;color:#ea580c;border:1px solid #fed7aa',
  4: 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5',
  5: 'background:#fef2f2;color:#991b1b;border:1px solid #fca5a5',
}
const inactiveStyle = 'background:transparent;color:var(--text3);border:1px solid var(--border)'
const accentStyle   = 'background:var(--accent);color:#fff;border:1px solid var(--accent)'
</script>

<template>
  <div class="flex flex-col gap-3 overflow-hidden flex-1">

    <!-- Filters -->
    <div class="panel flex-shrink-0">
      <div class="panel-hd">Filtres</div>
      <div class="panel-body flex flex-col gap-2">
        <div class="flex gap-1.5 flex-wrap">
          <button
            @click="setFilter(null)"
            class="text-xs px-2.5 py-1 rounded-lg font-bold transition text-white"
            :style="history.filterPriority === null ? accentStyle : inactiveStyle"
          >Totes</button>
          <button
            v-for="p in [1,2,3,4,5]" :key="p"
            @click="setFilter(p)"
            class="text-xs px-2.5 py-1 rounded-lg font-bold border transition"
            :style="history.filterPriority === p
              ? PRIO_PILL_ACTIVE[p]
              : `border-color:${PRIO_BORDER_COLORS[p]};color:${PRIO_BORDER_COLORS[p]}`"
          >P{{ p }}</button>
        </div>
        <input
          v-model="history.searchQuery"
          type="text"
          placeholder="Cerca per tipus o escenari..."
          class="fc"
          style="font-size:12px;padding:6px 10px"
        />
      </div>
    </div>

    <!-- Toolbar (only when items exist) -->
    <div v-if="hasItems" class="flex items-center justify-between gap-2 flex-shrink-0">
      <label class="flex items-center gap-1.5 cursor-pointer">
        <input
          ref="selectAllEl"
          type="checkbox"
          @change="toggleAll($event.target.checked)"
          style="accent-color:var(--accent);cursor:pointer"
        />
        <span class="text-xs tabular-nums" style="color:var(--text3)">
          {{ selected.size }} / {{ filtered.length }}
        </span>
      </label>
      <div class="flex items-center gap-1.5">
        <button
          @click="deleteSelected"
          :disabled="!selected.size"
          class="text-xs px-2 py-1 rounded-lg font-medium transition"
          style="border:1px solid #fca5a5;color:#dc2626;background:transparent"
        >
          {{ selected.size > 0 ? `Eliminar sel. (${selected.size})` : 'Eliminar sel.' }}
        </button>
        <button
          @click="deleteAll"
          class="text-xs px-2 py-1 rounded-lg font-medium transition"
          style="border:1px solid var(--border);color:var(--text3);background:transparent"
        >Tot</button>
        <button @click="loadHistory" class="text-xs transition" style="color:var(--text3)" title="Actualitzar">↺</button>
      </div>
    </div>

    <!-- Loading / error / empty -->
    <div v-if="loading" class="flex flex-col gap-2 flex-1">
      <p class="text-xs animate-pulse" style="color:var(--text3)">Carregant...</p>
    </div>
    <div v-else-if="loadError" class="flex flex-col gap-2 flex-1">
      <p class="text-xs text-red-500">Error carregant l'historial</p>
    </div>
    <div v-else-if="!hasItems" class="flex flex-col gap-2 flex-1">
      <p class="text-xs" style="color:var(--text3)">Cap intervenció trobada</p>
    </div>

    <!-- Cards -->
    <div v-else class="flex flex-col gap-2 overflow-y-auto flex-1 min-h-0 pr-0.5">
      <div
        v-for="inc in filtered"
        :key="inc.id"
        class="history-card rounded-xl overflow-hidden transition"
        :style="`background:var(--surface);border:1px solid ${selected.has(inc.id) ? 'var(--accent)' : 'var(--border)'}`"
      >
        <!-- Card header -->
        <div
          class="history-card-hd flex items-center justify-between px-3 py-2"
          style="background:var(--surface2);border-bottom:1px solid var(--border2)"
        >
          <div class="flex items-center gap-2">
            <input
              type="checkbox"
              :checked="selected.has(inc.id)"
              @change="toggleItem(inc.id, $event.target.checked)"
              style="accent-color:var(--accent);cursor:pointer"
            />
            <span class="text-xs font-mono" style="color:var(--text3)">#{{ inc.id }}</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-xs font-bold px-2 py-0.5 rounded-full" :style="pStyle(inc.priority).pill">
              P{{ inc.priority }}
            </span>
            <button
              @click="deleteOne(inc.id)"
              class="text-xs w-5 h-5 flex items-center justify-center rounded-md transition"
              style="color:var(--text3);border:1px solid var(--border)"
              title="Eliminar"
            >✕</button>
          </div>
        </div>

        <!-- Card body -->
        <div class="px-3 py-2.5 cursor-pointer" @click="ui.openDebriefing(inc.id)">
          <p class="text-xs font-bold truncate" style="color:var(--text)">{{ inc.type }}</p>
          <p class="text-xs truncate mt-0.5" style="color:var(--text3)">📍 {{ inc.location }}</p>
          <div class="flex justify-between items-center mt-2">
            <span class="text-xs" style="color:var(--text3)">{{ fmtDate(inc.call_end_at) }}</span>
            <span class="font-mono text-xs font-bold text-indigo-500">{{ fmtDuration(inc.duration_seconds) }}</span>
          </div>
          <p v-if="inc.scenario_title" class="text-xs text-amber-500 truncate mt-1">
            🎓 {{ inc.scenario_title }}
          </p>
        </div>

        <!-- Card footer -->
        <div class="px-3 pb-3">
          <button
            @click="ui.openDebriefing(inc.id)"
            class="w-full text-xs font-semibold py-1.5 rounded-lg transition"
            style="background:var(--accent-bg);border:1px solid var(--accent-br);color:var(--accent)"
          >📊 Obrir debriefing</button>
        </div>
      </div>
    </div>

  </div>
</template>
