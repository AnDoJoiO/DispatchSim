<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useHistoryStore } from '@/stores/history'
import { useUiStore }      from '@/stores/ui'
import { fmtDate, fmtDuration } from '@/utils'
import { useI18n } from '@/i18n'
import { Search, RefreshCw, Trash2, Eye, MapPin, Clock, BookOpen, Loader2 } from 'lucide-vue-next'

const history = useHistoryStore()
const ui      = useUiStore()
const { t: tr, plural } = useI18n()

const selected    = ref<Set<number>>(new Set())
const selectAllEl = ref<HTMLInputElement | null>(null)
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
  return history.items.filter((inc: any) => {
    if (history.filterPriority !== null && inc.priority !== history.filterPriority) return false
    if (q && !`${inc.type} ${inc.location} ${inc.scenario_title || ''}`.toLowerCase().includes(q)) return false
    return true
  })
})

const hasItems = computed(() => filtered.value.length > 0)

watch(filtered, (nf) => {
  const ids = new Set(nf.map((i: any) => i.id))
  const cleaned = new Set([...selected.value].filter(id => ids.has(id)))
  if (cleaned.size !== selected.value.size) selected.value = cleaned
})

watch([() => selected.value.size, () => filtered.value.length], async () => {
  await nextTick()
  if (!selectAllEl.value) return
  const total = filtered.value.length
  const sel   = selected.value.size
  selectAllEl.value.indeterminate = sel > 0 && sel < total
  selectAllEl.value.checked       = sel === total && total > 0
})

function setFilter(p: number | null) { history.filterPriority = p; selected.value = new Set() }
function toggleItem(id: number, checked: boolean) { const s = new Set(selected.value); checked ? s.add(id) : s.delete(id); selected.value = s }
function toggleAll(checked: boolean) { selected.value = checked ? new Set(filtered.value.map((i: any) => i.id)) : new Set() }

async function deleteOne(id: number) {
  if (!confirm(tr('hp.confirm_del_one', { id }))) return
  try { await history.deleteOne(id) } catch { alert(tr('hp.alert_error')); return }
  const s = new Set(selected.value); s.delete(id); selected.value = s
}
async function deleteSelected() {
  const ids = [...selected.value]
  if (!ids.length) return
  if (!confirm(tr('hp.confirm_del_sel', { n: ids.length, s: plural(ids.length) }))) return
  try { await history.deleteMany(ids); selected.value = new Set() } catch { alert(tr('hp.alert_error')) }
}
async function deleteAll() {
  const total = filtered.value.length
  if (!total) return
  if (!confirm(tr('hp.confirm_del_all', { n: total, s: plural(total) }))) return
  try { await history.deleteAll(); selected.value = new Set() } catch { alert(tr('hp.alert_error')) }
}
</script>

<template>
  <div class="hp">

    <!-- Filters -->
    <div class="hp-section">
      <div class="hp-filters">
        <button
          @click="setFilter(null)"
          class="hp-pf"
          :class="{ 'hp-pf--active': history.filterPriority === null }"
        >{{ tr('hp.all') }}</button>
        <button
          v-for="p in [1,2,3,4,5]" :key="p"
          @click="setFilter(p)"
          class="hp-pf"
          :class="[`hp-pf--p${p}`, { 'hp-pf--active': history.filterPriority === p }]"
        >P{{ p }}</button>
      </div>
      <div class="hp-search-wrap">
        <Search :size="14" />
        <input
          v-model="history.searchQuery"
          type="text"
          :placeholder="tr('hp.search_ph')"
          class="hp-search"
        />
      </div>
    </div>

    <!-- Toolbar -->
    <div v-if="hasItems" class="hp-toolbar">
      <label class="hp-sel-label">
        <input ref="selectAllEl" type="checkbox" @change="toggleAll(($event.target as HTMLInputElement).checked)" />
        <span>{{ selected.size }} / {{ filtered.length }}</span>
      </label>
      <div class="hp-toolbar-actions">
        <button @click="deleteSelected" :disabled="!selected.size" class="hp-action hp-action--danger">
          <Trash2 :size="12" />
          {{ selected.size > 0 ? tr('hp.delete_sel', { n: selected.size }) : tr('hp.delete_sel_empty') }}
        </button>
        <button @click="deleteAll" class="hp-action">{{ tr('hp.delete_all') }}</button>
        <button @click="loadHistory" class="hp-icon-btn" :title="tr('title.refresh')">
          <RefreshCw :size="13" />
        </button>
      </div>
    </div>

    <!-- States -->
    <div v-if="loading" class="hp-state">
      <Loader2 :size="18" class="animate-spin" />
      {{ tr('hp.loading') }}
    </div>
    <div v-else-if="loadError" class="hp-state hp-state--err">{{ tr('hp.error') }}</div>
    <div v-else-if="!hasItems" class="hp-state">{{ tr('hp.empty') }}</div>

    <!-- Table -->
    <div v-else class="hp-table-wrap">
      <table class="hp-table">
        <thead>
          <tr>
            <th class="hp-th hp-th--chk"></th>
            <th class="hp-th hp-th--id">#</th>
            <th class="hp-th hp-th--type">{{ tr('hp.col_type') || 'Tipus' }}</th>
            <th class="hp-th hp-th--loc">{{ tr('hp.col_location') || 'Ubicació' }}</th>
            <th class="hp-th hp-th--p">P</th>
            <th class="hp-th hp-th--dur">{{ tr('hp.col_duration') || 'Duració' }}</th>
            <th class="hp-th hp-th--date">{{ tr('hp.col_date') || 'Data' }}</th>
            <th class="hp-th hp-th--act"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="inc in filtered"
            :key="inc.id"
            class="hp-row"
            :class="{ 'hp-row--sel': selected.has(inc.id) }"
          >
            <td class="hp-td hp-td--chk">
              <input type="checkbox" :checked="selected.has(inc.id)" @change="toggleItem(inc.id, ($event.target as HTMLInputElement).checked)" />
            </td>
            <td class="hp-td hp-td--id">{{ inc.id }}</td>
            <td class="hp-td hp-td--type">
              {{ tr(`type.${inc.type}`) }}
              <span v-if="inc.scenario_title" class="hp-scenario">{{ inc.scenario_title }}</span>
            </td>
            <td class="hp-td hp-td--loc">{{ inc.location }}</td>
            <td class="hp-td hp-td--p">
              <span class="hp-pbadge" :class="`hp-pbadge--${inc.priority}`">P{{ inc.priority }}</span>
            </td>
            <td class="hp-td hp-td--dur">{{ fmtDuration(inc.duration_seconds) }}</td>
            <td class="hp-td hp-td--date">{{ fmtDate(inc.call_end_at) }}</td>
            <td class="hp-td hp-td--act">
              <button class="hp-icon-btn" @click="ui.openDebriefing(inc.id)" :title="tr('hp.open_debriefing')">
                <Eye :size="14" />
              </button>
              <button class="hp-icon-btn hp-icon-btn--danger" @click="deleteOne(inc.id)">
                <Trash2 :size="14" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.hp {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow: hidden;
  flex: 1;
}

/* ── Filters ── */
.hp-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex-shrink: 0;
}
.hp-filters { display: flex; gap: 4px; flex-wrap: wrap; }
.hp-pf {
  font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 4px;
  cursor: pointer; border: 1px solid var(--border); background: transparent;
  color: var(--text-muted); font-family: inherit; transition: all .15s;
}
.hp-pf:hover { color: var(--text); }
.hp-pf--active { background: var(--accent); color: white; border-color: var(--accent); }
.hp-pf--p1.hp-pf--active { background: var(--p1); border-color: var(--p1); }
.hp-pf--p2.hp-pf--active { background: var(--p2); border-color: var(--p2); }
.hp-pf--p3.hp-pf--active { background: var(--p3); border-color: var(--p3); }
.hp-pf--p4.hp-pf--active { background: var(--p4); border-color: var(--p4); }
.hp-pf--p5.hp-pf--active { background: var(--p5); border-color: var(--p5); }

.hp-search-wrap {
  display: flex; align-items: center; gap: 6px; padding: 0 10px;
  background: var(--input-bg-alt); border: 1px solid var(--border); border-radius: 6px;
  color: var(--text-muted);
}
.hp-search {
  flex: 1; border: none; outline: none; background: transparent; padding: 6px 0;
  font-size: 12px; font-family: inherit; color: var(--text);
}
.hp-search::placeholder { color: var(--placeholder); }

/* ── Toolbar ── */
.hp-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  flex-shrink: 0; gap: 8px;
}
.hp-sel-label {
  display: flex; align-items: center; gap: 6px; font-size: 12px;
  color: var(--text-muted); cursor: pointer;
  font-variant-numeric: tabular-nums;
}
.hp-sel-label input { accent-color: var(--accent); cursor: pointer; }
.hp-toolbar-actions { display: flex; align-items: center; gap: 4px; }
.hp-action {
  display: flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 500;
  padding: 4px 8px; border-radius: 4px; cursor: pointer;
  border: 1px solid var(--border); background: transparent; color: var(--text-muted);
  font-family: inherit; transition: all .15s;
}
.hp-action:hover { color: var(--text); }
.hp-action--danger { border-color: var(--danger-border); color: var(--danger); }
.hp-action--danger:hover { background: var(--danger-bg); }

.hp-icon-btn {
  width: 28px; height: 28px; border-radius: 5px; display: flex; align-items: center;
  justify-content: center; cursor: pointer; border: 1px solid var(--border);
  background: transparent; color: var(--text-muted); transition: all .15s;
}
.hp-icon-btn:hover { background: var(--surface-raised); color: var(--text); }
.hp-icon-btn--danger:hover { background: var(--danger-bg); color: var(--danger); border-color: var(--danger-border); }

/* ── States ── */
.hp-state {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  flex: 1; font-size: 13px; color: var(--text-muted);
}
.hp-state--err { color: var(--danger); }

/* ── Table ── */
.hp-table-wrap {
  flex: 1; overflow-y: auto; min-height: 0;
  background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
}
.hp-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.hp-th {
  text-align: left; padding: 8px 10px; font-size: 11px; font-weight: 600;
  color: var(--text-muted); background: var(--surface-raised);
  border-bottom: 1px solid var(--border); white-space: nowrap;
  position: sticky; top: 0; z-index: 1;
}
.hp-th--chk { width: 32px; text-align: center; }
.hp-th--id  { width: 40px; }
.hp-th--p   { width: 40px; text-align: center; }
.hp-th--dur { width: 70px; }
.hp-th--date { width: 130px; }
.hp-th--act { width: 70px; }

.hp-row { transition: background .1s; }
.hp-row:hover { background: var(--surface-raised); }
.hp-row--sel { background: var(--accent-bg); }
.hp-row:not(:last-child) .hp-td { border-bottom: 1px solid var(--border); }

.hp-td { padding: 8px 10px; vertical-align: middle; }
.hp-td--chk { text-align: center; }
.hp-td--chk input { accent-color: var(--accent); cursor: pointer; }
.hp-td--id { font-family: 'JetBrains Mono', ui-monospace, monospace; color: var(--text-muted); font-size: 11px; }
.hp-td--type { color: var(--text); font-weight: 500; }
.hp-td--loc { color: var(--text-secondary); max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.hp-td--dur { font-family: 'JetBrains Mono', ui-monospace, monospace; font-weight: 600; color: var(--accent); }
.hp-td--date { color: var(--text-muted); font-size: 11px; }
.hp-td--act { display: flex; gap: 4px; }

.hp-scenario { display: block; font-size: 11px; color: var(--warning); margin-top: 1px; }

.hp-pbadge {
  font-size: 10px; font-weight: 700; padding: 2px 6px; border-radius: 3px;
  display: inline-block; text-align: center;
}
.hp-pbadge--1 { background: var(--success-bg); color: var(--p1); }
.hp-pbadge--2 { background: var(--warning-bg); color: var(--p2); }
.hp-pbadge--3 { background: #fff7ed; color: var(--p3); }
.hp-pbadge--4 { background: var(--danger-bg); color: var(--p4); }
.hp-pbadge--5 { background: var(--danger-bg); color: var(--p5); }
</style>
