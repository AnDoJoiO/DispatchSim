<script setup lang="ts">
import { ref, computed } from 'vue'
import { useScenarioStore } from '@/stores/scenarios'
import { useCallStore }     from '@/stores/call'
import { useI18n } from '@/i18n'
import { Play, Loader2, BookOpen, MapPin, FileText, Gauge, List } from 'lucide-vue-next'

const scenarios = useScenarioStore()
const call      = useCallStore()
const { t: tr, incidentTypes } = useI18n()

const scenarioId   = ref('')
const incType      = ref('Incendio')
const incLocation  = ref('')
const incDesc      = ref('')
const fieldsLocked = ref(false)
const starting     = ref(false)

const PRIO_LABELS: Record<number, string> = {
  1: 'P1', 2: 'P2', 3: 'P3', 4: 'P4', 5: 'P5',
}

const selectedScenario = computed(() =>
  scenarios.scenariosCache.find((s: any) => s.id === +scenarioId.value) ?? null
)

function onScenarioChange() {
  const sc = selectedScenario.value
  if (!sc) { fieldsLocked.value = false; return }
  incType.value     = sc.incident_type
  incLocation.value = sc.base_location
  const parts: string[] = []
  if (sc.location_exact)  parts.push(sc.location_exact)
  if (sc.victim_status)   parts.push(`${tr('ep.victim_prefix')}: ${tr('vs.' + sc.victim_status)}`)
  if (sc.initial_emotion) parts.push(`${tr('ep.emotion_prefix')}: ${tr('ie.' + sc.initial_emotion)}`)
  incDesc.value     = parts.join(' · ')
  fieldsLocked.value = true
}

async function startIncident() {
  starting.value = true
  try {
    const body = scenarioId.value
      ? { scenario_id: +scenarioId.value, priority: call.selectedPriority }
      : {
          type:        incType.value,
          location:    incLocation.value.trim(),
          description: incDesc.value.trim(),
          priority:    call.selectedPriority,
        }
    await call.startIncident(body)
    fieldsLocked.value = false
    scenarioId.value   = ''
    incLocation.value  = ''
    incDesc.value      = ''
  } finally {
    starting.value = false
  }
}
</script>

<template>
  <div class="ep">

    <!-- Scenario selector -->
    <div class="ep-section">
      <div class="ep-section-hd">
        <BookOpen :size="13" />
        {{ tr('ep.scenario') }}
      </div>
      <div class="ep-section-body">
        <select v-model="scenarioId" @change="onScenarioChange" class="fc">
          <option value="">{{ tr('ep.free') }}</option>
          <option v-for="s in scenarios.scenariosCache" :key="s.id" :value="s.id">
            {{ s.title }}
          </option>
        </select>
        <!-- Scenario preview -->
        <div v-if="selectedScenario" class="ep-preview">
          <span class="ep-preview-tag">{{ tr(`type.${selectedScenario.incident_type}`) }}</span>
          <span class="ep-preview-loc">{{ selectedScenario.base_location }}</span>
        </div>
      </div>
    </div>

    <!-- Incident details -->
    <div class="ep-section">
      <div class="ep-section-hd">
        <FileText :size="13" />
        {{ tr('ep.details') }}
      </div>
      <div class="ep-section-body">
        <div class="ep-field">
          <label for="ep-type" class="fp-label">{{ tr('ep.type') }}</label>
          <select id="ep-type" v-model="incType" :disabled="fieldsLocked" class="fc">
            <option v-for="t in incidentTypes()" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
        <div class="ep-field">
          <label for="ep-location" class="fp-label">{{ tr('ep.location') }}</label>
          <input id="ep-location" v-model="incLocation" :disabled="fieldsLocked" type="text" :placeholder="tr('ep.location_ph')" class="fc" />
        </div>
        <div class="ep-field">
          <label for="ep-desc" class="fp-label">{{ tr('ep.description') }}</label>
          <textarea id="ep-desc" v-model="incDesc" :disabled="fieldsLocked" rows="2" :placeholder="tr('ep.desc_ph')" class="fc"></textarea>
        </div>
      </div>
    </div>

    <!-- Priority -->
    <div class="ep-section">
      <div class="ep-section-hd">
        <Gauge :size="13" />
        {{ tr('ep.priority') }}
      </div>
      <div class="ep-section-body">
        <div class="ep-prio-row">
          <button
            v-for="p in [1, 2, 3, 4, 5]"
            :key="p"
            class="ep-prio"
            :class="[`ep-prio--${p}`, { 'ep-prio--sel': call.selectedPriority === p }]"
            @click="call.setPriority(p)"
          >{{ PRIO_LABELS[p] }}</button>
        </div>
      </div>
    </div>

    <!-- Start button -->
    <button
      @click="startIncident"
      :disabled="starting"
      class="ep-start"
    >
      <Loader2 v-if="starting" :size="16" class="animate-spin" />
      <Play v-else :size="16" />
      {{ starting ? tr('ep.starting') : tr('ep.start') }}
    </button>

    <!-- Session incidents -->
    <div v-if="call.sessionIncidents.length" class="ep-section">
      <div class="ep-section-hd">
        <List :size="13" />
        {{ tr('ep.session') }}
      </div>
      <ul class="ep-session">
        <li
          v-for="inc in call.sessionIncidents"
          :key="inc.id"
          class="ep-session-item"
          :class="{ 'ep-session-item--active': inc.id === call.currentIncidentId }"
          @click="call.switchIncident(inc)"
        >
          <span class="ep-session-id">#{{ inc.id }}</span>
          <span class="ep-session-type">{{ tr(`type.${inc.type}`) }}</span>
          <span class="ep-session-status" :class="inc.call_status === 'finalitzada' ? 'ep-session-status--done' : ''">
            {{ inc.call_status === 'en_curs' ? 'EN CURS' : 'FI' }}
          </span>
        </li>
      </ul>
    </div>

  </div>
</template>

<style scoped>
.ep {
  display: flex;
  flex-direction: column;
  gap: 10px;
  overflow-y: auto;
  flex: 1;
  padding-bottom: 4px;
  padding-right: 2px;
}

/* ── Sections ── */
.ep-section {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}
.ep-section-hd {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--surface-raised);
  border-bottom: 1px solid var(--border);
}
.ep-section-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ep-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ── Scenario preview ── */
.ep-preview {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: var(--accent-bg);
  border: 1px solid var(--accent-border);
  border-radius: 6px;
  font-size: 12px;
}
.ep-preview-tag {
  font-weight: 600;
  color: var(--accent);
}
.ep-preview-loc {
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Priority ── */
.ep-prio-row { display: flex; gap: 6px; }
.ep-prio {
  flex: 1;
  padding: 6px 2px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  border: 1.5px solid;
  background: transparent;
  font-family: inherit;
  transition: all .15s;
}
.ep-prio--1 { border-color: var(--p1); color: var(--p1); }
.ep-prio--2 { border-color: var(--p2); color: var(--p2); }
.ep-prio--3 { border-color: var(--p3); color: var(--p3); }
.ep-prio--4 { border-color: var(--p4); color: var(--p4); }
.ep-prio--5 { border-color: var(--p5); color: var(--p5); }
.ep-prio--sel { color: white; }
.ep-prio--1.ep-prio--sel { background: var(--p1); }
.ep-prio--2.ep-prio--sel { background: var(--p2); }
.ep-prio--3.ep-prio--sel { background: var(--p3); }
.ep-prio--4.ep-prio--sel { background: var(--p4); }
.ep-prio--5.ep-prio--sel { background: var(--p5); }

/* ── Start button ── */
.ep-start {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  border: none;
  background: var(--danger);
  color: white;
  font-family: inherit;
  transition: all .15s;
  flex-shrink: 0;
}
.ep-start:hover:not(:disabled) { filter: brightness(1.1); }

/* ── Session list ── */
.ep-session {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 140px;
  overflow-y: auto;
}
.ep-session-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  font-size: 12px;
  cursor: pointer;
  transition: background .1s;
  border-bottom: 1px solid var(--border);
}
.ep-session-item:last-child { border-bottom: none; }
.ep-session-item:hover { background: var(--surface-raised); }
.ep-session-item--active { background: var(--accent-bg); }

.ep-session-id {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  width: 28px;
}
.ep-session-type {
  flex: 1;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ep-session-status {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 3px;
  background: var(--success-bg);
  color: var(--success);
}
.ep-session-status--done {
  background: var(--surface-raised);
  color: var(--text-muted);
}
</style>
