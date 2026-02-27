<script setup>
import { ref, computed } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import { INCIDENT_TYPES } from '@/utils'

const emergency = useEmergencyStore()

const scenarioId   = ref('')
const incType      = ref('Incendio')
const incLocation  = ref('')
const incDesc      = ref('')
const fieldsLocked = ref(false)
const starting     = ref(false)

const PRIO_COLORS = {
  1: 'border-color:#16a34a;color:#16a34a',
  2: 'border-color:#ca8a04;color:#ca8a04',
  3: 'border-color:#ea580c;color:#ea580c',
  4: 'border-color:#dc2626;color:#dc2626',
  5: 'border-color:#991b1b;color:#991b1b',
}

const selectedScenario = computed(() =>
  emergency.scenariosCache.find(s => s.id === +scenarioId.value) ?? null
)

function onScenarioChange() {
  const sc = selectedScenario.value
  if (!sc) { fieldsLocked.value = false; return }
  incType.value     = sc.incident_type
  incLocation.value = sc.base_location
  const parts = []
  if (sc.location_exact)  parts.push(sc.location_exact)
  if (sc.victim_status)   parts.push(`Víctima: ${sc.victim_status}`)
  if (sc.initial_emotion) parts.push(`Emoció: ${sc.initial_emotion}`)
  incDesc.value     = parts.join(' · ')
  fieldsLocked.value = true
}

async function startIncident() {
  starting.value = true
  try {
    const body = scenarioId.value
      ? { scenario_id: +scenarioId.value, priority: emergency.selectedPriority }
      : {
          type:        incType.value,
          location:    incLocation.value.trim() || 'Desconeguda',
          description: incDesc.value.trim()     || 'Sense descripció',
          priority:    emergency.selectedPriority,
        }
    await emergency.startIncident(body)
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
  <div class="flex flex-col gap-3 overflow-y-auto flex-1 pb-1 pr-0.5">

    <!-- Scenario selector -->
    <div class="panel">
      <div class="panel-hd">Escenari base</div>
      <div class="panel-body">
        <select v-model="scenarioId" @change="onScenarioChange" class="fc">
          <option value="">— Emergència lliure —</option>
          <option v-for="s in emergency.scenariosCache" :key="s.id" :value="s.id">
            [{{ s.incident_type }}] {{ s.title }}
          </option>
        </select>
      </div>
    </div>

    <!-- Incident details -->
    <div class="panel">
      <div class="panel-hd">Detalls de l'incident</div>
      <div class="panel-body flex flex-col gap-3">
        <div>
          <label class="fl">Tipus d'incident</label>
          <select v-model="incType" :disabled="fieldsLocked" class="fc">
            <option v-for="t in INCIDENT_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
        <div>
          <label class="fl">Localització</label>
          <input v-model="incLocation" :disabled="fieldsLocked" type="text" placeholder="Carrer, municipi..." class="fc" />
        </div>
        <div>
          <label class="fl">Descripció breu</label>
          <textarea v-model="incDesc" :disabled="fieldsLocked" rows="2" placeholder="Detalls inicials..." class="fc"></textarea>
        </div>
      </div>
    </div>

    <!-- Priority -->
    <div class="panel">
      <div class="panel-hd">Prioritat</div>
      <div class="panel-body">
        <div class="flex gap-2">
          <button
            v-for="p in [1, 2, 3, 4, 5]"
            :key="p"
            class="prio"
            :class="{ sel: emergency.selectedPriority === p }"
            :style="PRIO_COLORS[p]"
            @click="emergency.setPriority(p)"
          >P{{ p }}</button>
        </div>
      </div>
    </div>

    <!-- Start incident button -->
    <button
      @click="startIncident"
      :disabled="starting"
      class="w-full py-3 rounded-xl font-bold text-sm text-white transition flex items-center justify-center gap-2 flex-shrink-0"
      style="background:#dc2626"
    >
      {{ starting ? '⏳ Creant...' : '🚨 Iniciar Nova Emergència' }}
    </button>

    <!-- Session incidents list -->
    <div class="panel">
      <div class="panel-hd">Incidents de la sessió</div>
      <ul class="flex flex-col max-h-36 overflow-y-auto py-1">
        <li
          v-for="inc in emergency.sessionIncidents"
          :key="inc.id"
          class="incident-row cursor-pointer text-xs transition py-1.5 px-4 rounded"
          style="color:var(--text2)"
          @click="emergency.switchIncident(inc)"
          @mouseenter="$event.currentTarget.style.color='var(--accent)'"
          @mouseleave="$event.currentTarget.style.color='var(--text2)'"
        >
          <span class="font-mono font-bold mr-1" style="color:var(--text3)">#{{ inc.id }}</span>
          {{ inc.type }}
        </li>
      </ul>
    </div>

  </div>
</template>
