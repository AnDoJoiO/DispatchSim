<script setup>
import { ref, onMounted } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import { INCIDENT_TYPES, escapeHtml } from '@/utils'

const emergency = useEmergencyStore()

const title        = ref('')
const type         = ref('Incendio')
const location     = ref('')
const description  = ref('')
const instructions = ref('')
const creating     = ref(false)
const error        = ref('')

onMounted(() => emergency.loadScenarios())

async function createScenario() {
  error.value = ''
  if (!title.value.trim() || !location.value.trim() || !description.value.trim() || !instructions.value.trim()) {
    error.value = 'Omple tots els camps'
    return
  }
  creating.value = true
  try {
    await emergency.createScenario({
      title:               title.value.trim(),
      incident_type:       type.value,
      base_location:       location.value.trim(),
      initial_description: description.value.trim(),
      instructions_ia:     instructions.value.trim(),
    })
    title.value = location.value = description.value = instructions.value = ''
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
  <div class="flex flex-col gap-3 overflow-y-auto flex-1 pb-1 pr-0.5">

    <!-- Info banner -->
    <div
      class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium"
      style="background:#fefce8;border:1px solid #fef08a;color:#854d0e"
    >
      🔒 Zona del formador · Les instruccions IA no les veu l'operador
    </div>

    <!-- New scenario form -->
    <div class="panel">
      <div class="panel-hd">Nou escenari</div>
      <div class="panel-body flex flex-col gap-3">
        <div>
          <label class="fl">Títol</label>
          <input v-model="title" type="text" placeholder="Títol de l'escenari" class="fc" />
        </div>
        <div>
          <label class="fl">Tipus</label>
          <select v-model="type" class="fc">
            <option v-for="t in INCIDENT_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select>
        </div>
        <div>
          <label class="fl">Localització base</label>
          <input v-model="location" type="text" placeholder="Localització base" class="fc" />
        </div>
        <div>
          <label class="fl">Descripció inicial (visible al professional)</label>
          <textarea v-model="description" rows="2" placeholder="Descripció que veurà l'operador..." class="fc"></textarea>
        </div>
        <div>
          <label class="fl" style="color:#b45309">🔒 Instruccions secretes per a la IA</label>
          <textarea
            v-model="instructions"
            rows="3"
            placeholder="Ex: La víctima és un home de 65 anys..."
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

    <!-- Existing scenarios -->
    <div class="panel">
      <div class="panel-hd">Escenaris existents</div>
      <ul class="flex flex-col divide-y max-h-60 overflow-y-auto" style="border-color:var(--border2)">
        <li
          v-if="!emergency.scenariosCache.length"
          class="text-xs px-4 py-3"
          style="color:var(--text3)"
        >Cap escenari creat</li>
        <li
          v-for="s in emergency.scenariosCache"
          :key="s.id"
          class="scenario-li flex items-center justify-between px-4 py-3 hover:bg-blue-50 transition"
          style="border-bottom:1px solid var(--border2)"
        >
          <div class="min-w-0 mr-2">
            <p class="text-xs font-semibold truncate" style="color:var(--text)">{{ s.title }}</p>
            <p class="text-xs" style="color:var(--text3)">{{ s.incident_type }} · {{ s.base_location }}</p>
          </div>
          <button @click="deleteScenario(s.id)" class="text-xs flex-shrink-0 transition" style="color:var(--text3)">✕</button>
        </li>
      </ul>
    </div>

  </div>
</template>
