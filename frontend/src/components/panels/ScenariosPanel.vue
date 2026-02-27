<script setup>
import { ref, onMounted } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import { INCIDENT_TYPES } from '@/utils'

const emergency = useEmergencyStore()

const title          = ref('')
const type           = ref('Incendio')
const baseLocation   = ref('')
const locationExact  = ref('')
const victimStatus   = ref('Consciente')
const initialEmotion = ref('Calma')
const instructions   = ref('')
const creating       = ref(false)
const error          = ref('')

const VICTIM_STATUSES  = ['Consciente', 'Inconsciente', 'GASP']
const INITIAL_EMOTIONS = ['Calma', 'Pánico', 'Agresión']

onMounted(() => emergency.loadScenarios())

async function createScenario() {
  error.value = ''
  if (!title.value.trim() || !baseLocation.value.trim() || !locationExact.value.trim() || !instructions.value.trim()) {
    error.value = 'Omple tots els camps obligatoris'
    return
  }
  creating.value = true
  try {
    await emergency.createScenario({
      title:           title.value.trim(),
      incident_type:   type.value,
      base_location:   baseLocation.value.trim(),
      location_exact:  locationExact.value.trim(),
      victim_status:   victimStatus.value,
      initial_emotion: initialEmotion.value,
      instructions_ia: instructions.value.trim(),
    })
    title.value = baseLocation.value = locationExact.value = instructions.value = ''
    victimStatus.value   = 'Consciente'
    initialEmotion.value = 'Calma'
  } catch (e) {
    error.value = e.message
  } finally {
    creating.value = false
  }
}

async function deleteScenario(id) {
  if (!confirm('Eliminar aquest escenari?')) return
  await emergency.deleteScenario(id)
}
</script>

<template>
  <div class="w-full flex gap-4 overflow-hidden">

    <!-- Columna esquerra: formulari -->
    <div class="w-96 flex-shrink-0 flex flex-col gap-3 overflow-y-auto pb-1">

      <!-- Info banner -->
      <div
        class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium"
        style="background:#fefce8;border:1px solid #fef08a;color:#854d0e"
      >
        🔒 Zona del formador · Les instruccions IA no les veu l'operador
      </div>

      <!-- Formulari nou escenari -->
      <div class="panel">
        <div class="panel-hd">Nou escenari</div>
        <div class="panel-body flex flex-col gap-3">
          <div>
            <label class="fl">Títol</label>
            <input v-model="title" type="text" placeholder="Títol de l'escenari" class="fc" />
          </div>
          <div>
            <label class="fl">Tipus d'incident</label>
            <select v-model="type" class="fc">
              <option v-for="t in INCIDENT_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
          <div>
            <label class="fl">Localització base</label>
            <input v-model="baseLocation" type="text" placeholder="Ex: Andorra la Vella" class="fc" />
          </div>
          <div>
            <label class="fl">Localització exacta</label>
            <input v-model="locationExact" type="text" placeholder="Ex: Carrer Major 15, 2n pis" class="fc" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="fl">Estat de la víctima</label>
              <select v-model="victimStatus" class="fc">
                <option v-for="s in VICTIM_STATUSES" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div>
              <label class="fl">Emoció inicial</label>
              <select v-model="initialEmotion" class="fc">
                <option v-for="e in INITIAL_EMOTIONS" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="fl" style="color:#b45309">🔒 Instruccions secretes per a la IA</label>
            <textarea
              v-model="instructions"
              rows="4"
              placeholder="Ex: La víctima és un home de 65 anys amb antecedents cardíacs..."
              class="fc warn-textarea"
              style="border-color:#fde68a;background:#fffbeb;color:#78350f"
            ></textarea>
          </div>
          <p v-if="error" class="text-xs text-red-500 -mt-1">{{ error }}</p>
          <button
            @click="createScenario"
            :disabled="creating"
            class="w-full py-2 rounded-lg font-bold text-sm text-white transition"
            style="background:var(--accent)"
          >
            {{ creating ? 'Creant...' : '+ Crear Escenari' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Columna dreta: llista d'escenaris -->
    <div class="flex-1 flex flex-col gap-3 overflow-y-auto pb-1">
      <div class="panel flex-1 flex flex-col">
        <div class="panel-hd">Escenaris existents ({{ emergency.scenariosCache.length }})</div>
        <ul class="flex flex-col divide-y overflow-y-auto flex-1" style="border-color:var(--border2)">
          <li
            v-if="!emergency.scenariosCache.length"
            class="text-xs px-4 py-3"
            style="color:var(--text3)"
          >Cap escenari creat</li>
          <li
            v-for="s in emergency.scenariosCache"
            :key="s.id"
            class="flex items-start justify-between px-4 py-3 hover:bg-blue-50 transition gap-3"
            style="border-bottom:1px solid var(--border2)"
          >
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold" style="color:var(--text)">{{ s.title }}</p>
              <p class="text-xs mt-0.5" style="color:var(--text3)">{{ s.incident_type }} · {{ s.base_location }}</p>
              <div v-if="s.location_exact || s.victim_status || s.initial_emotion" class="flex flex-wrap gap-1.5 mt-1.5">
                <span v-if="s.location_exact" class="text-xs px-2 py-0.5 rounded-full" style="background:var(--surface2);color:var(--text2)">
                  📍 {{ s.location_exact }}
                </span>
                <span v-if="s.victim_status" class="text-xs px-2 py-0.5 rounded-full" style="background:#fef9c3;color:#854d0e">
                  {{ s.victim_status }}
                </span>
                <span v-if="s.initial_emotion" class="text-xs px-2 py-0.5 rounded-full" style="background:#ede9fe;color:#5b21b6">
                  {{ s.initial_emotion }}
                </span>
              </div>
            </div>
            <button
              @click="deleteScenario(s.id)"
              class="text-xs flex-shrink-0 transition px-2 py-0.5 rounded"
              style="color:var(--text3)"
            >✕</button>
          </li>
        </ul>
      </div>
    </div>

  </div>
</template>
