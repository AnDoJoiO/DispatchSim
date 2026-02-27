<script setup>
import { ref, onMounted } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import { INCIDENT_TYPES } from '@/utils'

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
            <textarea v-model="description" rows="3" placeholder="Descripció que veurà l'operador..." class="fc"></textarea>
          </div>
          <div>
            <label class="fl" style="color:#b45309">🔒 Instruccions secretes per a la IA</label>
            <textarea
              v-model="instructions"
              rows="4"
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
              <p v-if="s.initial_description" class="text-xs mt-1 line-clamp-2" style="color:var(--text2)">{{ s.initial_description }}</p>
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
