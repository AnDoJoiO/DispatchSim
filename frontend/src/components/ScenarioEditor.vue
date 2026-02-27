<script setup>
import { ref } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import { useI18n } from '@/i18n'

const emit = defineEmits(['created'])

const emergency = useEmergencyStore()
const { t: tr, incidentTypes } = useI18n()

const title          = ref('')
const incidentType   = ref('Incendio')
const baseLocation   = ref('')
const locationExact  = ref('')
const victimStatus   = ref('Consciente')
const initialEmotion = ref('Calma')
const instructions   = ref('')
const creating       = ref(false)
const error          = ref('')
const success        = ref(false)

const VICTIM_STATUSES  = ['Consciente', 'Inconsciente', 'GASP']
const INITIAL_EMOTIONS = ['Calma', 'Pánico', 'Agresión']

function reset() {
  title.value = baseLocation.value = locationExact.value = instructions.value = ''
  incidentType.value   = 'Incendio'
  victimStatus.value   = 'Consciente'
  initialEmotion.value = 'Calma'
  error.value          = ''
}

async function submit() {
  error.value   = ''
  success.value = false
  if (!title.value.trim() || !baseLocation.value.trim() || !locationExact.value.trim() || !instructions.value.trim()) {
    error.value = tr('se.error_required')
    return
  }
  creating.value = true
  try {
    await emergency.createScenario({
      title:           title.value.trim(),
      incident_type:   incidentType.value,
      base_location:   baseLocation.value.trim(),
      location_exact:  locationExact.value.trim(),
      victim_status:   victimStatus.value,
      initial_emotion: initialEmotion.value,
      instructions_ia: instructions.value.trim(),
    })
    reset()
    success.value = true
    setTimeout(() => { success.value = false }, 3000)
    emit('created')
  } catch (e) {
    error.value = e.message
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <div class="flex-1 overflow-y-auto">
    <div class="max-w-2xl mx-auto py-6 px-6">

      <!-- Capçalera -->
      <div class="mb-5">
        <h2 class="text-base font-bold" style="color:var(--text)">{{ tr('se.title') }}</h2>
        <p class="text-xs mt-1" style="color:var(--text3)">{{ tr('se.subtitle') }}</p>
      </div>

      <!-- Banner zona formador -->
      <div
        class="flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium mb-5"
        style="background:#fefce8;border:1px solid #fef08a;color:#854d0e"
      >
        {{ tr('se.banner') }}
      </div>

      <!-- Formulari -->
      <div class="flex flex-col gap-4">

        <!-- Títol -->
        <div>
          <label class="fl">{{ tr('se.title_label') }}</label>
          <input
            v-model="title"
            type="text"
            :placeholder="tr('se.title_ph')"
            class="fc"
          />
        </div>

        <!-- Tipus + Localització base -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="fl">{{ tr('se.inc_type') }}</label>
            <select v-model="incidentType" class="fc">
              <option v-for="t in incidentTypes()" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
          <div>
            <label class="fl">{{ tr('se.base_loc') }}</label>
            <input
              v-model="baseLocation"
              type="text"
              :placeholder="tr('se.base_loc_ph')"
              class="fc"
            />
          </div>
        </div>

        <!-- Adreça exacta -->
        <div>
          <label class="fl">{{ tr('se.exact_addr') }}</label>
          <input
            v-model="locationExact"
            type="text"
            :placeholder="tr('se.exact_addr_ph')"
            class="fc"
          />
        </div>

        <!-- Estat víctima + Emoció inicial -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="fl">{{ tr('se.victim') }}</label>
            <select v-model="victimStatus" class="fc">
              <option v-for="s in VICTIM_STATUSES" :key="s" :value="s">{{ tr('vs.' + s) }}</option>
            </select>
            <!-- Indicador visual de gravetat -->
            <p class="text-xs mt-1" style="color:var(--text3)">
              <span v-if="victimStatus === 'Consciente'"   style="color:#16a34a">{{ tr('se.victim_stable') }}</span>
              <span v-else-if="victimStatus === 'Inconsciente'" style="color:#dc2626">{{ tr('se.victim_critical') }}</span>
              <span v-else-if="victimStatus === 'GASP'"    style="color:#dc2626">{{ tr('se.victim_gasp') }}</span>
            </p>
          </div>
          <div>
            <label class="fl">{{ tr('se.emotion') }}</label>
            <select v-model="initialEmotion" class="fc">
              <option v-for="e in INITIAL_EMOTIONS" :key="e" :value="e">{{ tr('ie.' + e) }}</option>
            </select>
            <p class="text-xs mt-1" style="color:var(--text3)">
              <span v-if="initialEmotion === 'Calma'"    style="color:#16a34a">{{ tr('se.emotion_calm') }}</span>
              <span v-else-if="initialEmotion === 'Pánico'"   style="color:#ca8a04">{{ tr('se.emotion_panic') }}</span>
              <span v-else-if="initialEmotion === 'Agresión'" style="color:#dc2626">{{ tr('se.emotion_aggr') }}</span>
            </p>
          </div>
        </div>

        <!-- Instruccions secretes -->
        <div>
          <label class="fl" style="color:#b45309">{{ tr('se.instructions') }}</label>
          <textarea
            v-model="instructions"
            rows="5"
            :placeholder="tr('se.instructions_ph')"
            class="fc"
            style="border-color:#fde68a;background:#fffbeb;color:#78350f;resize:vertical"
          ></textarea>
          <p class="text-xs mt-1" style="color:#b45309">{{ tr('se.instructions_hint') }}</p>
        </div>

        <!-- Error / Èxit -->
        <p v-if="error"   class="text-xs text-red-500">{{ error }}</p>
        <p v-if="success" class="text-xs font-medium" style="color:#16a34a">{{ tr('se.success') }}</p>

        <!-- Accions -->
        <div class="flex gap-2 pt-1">
          <button
            @click="submit"
            :disabled="creating"
            class="flex-1 py-2.5 rounded-lg font-bold text-sm text-white transition"
            style="background:var(--accent)"
          >
            {{ creating ? tr('se.creating') : tr('se.create_btn') }}
          </button>
          <button
            @click="reset"
            class="px-4 py-2.5 rounded-lg text-sm font-medium transition"
            style="border:1px solid var(--border);color:var(--text2)"
          >
            {{ tr('se.clear_btn') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
