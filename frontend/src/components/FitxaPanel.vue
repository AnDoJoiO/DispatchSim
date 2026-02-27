<script setup>
import { ref, watch } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import { useI18n } from '@/i18n'

const emergency = useEmergencyStore()
const { t: tr, risks } = useI18n()

const address  = ref('')
const phone    = ref('')
const injured  = ref(0)
const notes    = ref('')
const selected = ref([])  // array of selected risk values
const saving   = ref(false)
const status   = ref(null)  // null | 'ok' | 'error'

// Reset form when switching incidents
watch(() => emergency.currentIncidentId, () => {
  address.value = phone.value = notes.value = ''
  injured.value = 0
  selected.value = []
  status.value  = null
})

async function save() {
  if (!emergency.currentIncidentId) return
  saving.value = true
  status.value = null
  const ok = await emergency.saveIntervention({
    incident_id:      emergency.currentIncidentId,
    exact_address:    address.value.trim(),
    contact_phone:    phone.value.trim(),
    num_injured:      Math.max(0, parseInt(injured.value) || 0),
    additional_risks: selected.value.join(','),
    operator_notes:   notes.value.trim(),
  })
  status.value = ok ? 'ok' : 'error'
  saving.value = false
  if (ok) setTimeout(() => { status.value = null }, 4000)
}
</script>

<template>
  <div
    class="fitxa-wrap w-72 flex-shrink-0 flex flex-col panel overflow-hidden"
    style="background:var(--surface)"
  >
    <!-- Header -->
    <div
      class="fitxa-hd px-4 py-3 flex-shrink-0"
      style="background:var(--surface2);border-bottom:1px solid var(--border)"
    >
      <h2 class="text-xs font-bold uppercase tracking-widest" style="color:var(--text3)">{{ tr('fitxa.title') }}</h2>
      <p class="text-xs mt-0.5" style="color:var(--text3)">{{ tr('fitxa.subtitle') }}</p>
    </div>

    <!-- Form fields -->
    <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
      <div>
        <label class="fl">{{ tr('fitxa.address') }}</label>
        <input v-model="address" type="text" :placeholder="tr('fitxa.address_ph')" class="fc" />
      </div>
      <div>
        <label class="fl">{{ tr('fitxa.phone') }}</label>
        <input v-model="phone" type="tel" :placeholder="tr('fitxa.phone_ph')" class="fc" />
      </div>
      <div>
        <label class="fl">{{ tr('fitxa.injured') }}</label>
        <input v-model="injured" type="number" min="0" class="fc" />
      </div>
      <div>
        <label class="fl">{{ tr('fitxa.risks') }}</label>
        <div class="grid grid-cols-2 gap-1 mt-1">
          <label
            v-for="risk in risks()"
            :key="risk.value"
            class="flex items-center gap-2 cursor-pointer py-1"
          >
            <input type="checkbox" v-model="selected" :value="risk.value" :class="risk.accent" />
            <span class="text-xs" style="color:var(--text2)">{{ risk.label }}</span>
          </label>
        </div>
      </div>
      <div>
        <label class="fl">{{ tr('fitxa.notes') }}</label>
        <textarea v-model="notes" rows="4" :placeholder="tr('fitxa.notes_ph')" class="fc"></textarea>
      </div>

      <!-- Status message -->
      <div
        v-if="status"
        class="text-xs text-center py-2 rounded-lg"
        :style="status === 'ok'
          ? 'background:#dcfce7;color:#16a34a;border:1px solid #86efac'
          : 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5'"
      >
        {{ status === 'ok' ? tr('fitxa.saved') : tr('fitxa.error') }}
      </div>
    </div>

    <!-- Footer with save button -->
    <div
      class="fitxa-foot p-4 flex-shrink-0"
      style="background:var(--surface2);border-top:1px solid var(--border)"
    >
      <button
        @click="save"
        :disabled="!emergency.currentIncidentId || saving || emergency.interventionSaved"
        class="w-full py-2.5 rounded-lg font-bold text-sm text-white transition flex items-center justify-center gap-2"
        style="background:var(--accent)"
      >
        {{ saving ? tr('fitxa.saving') : tr('fitxa.save') }}
      </button>
    </div>
  </div>
</template>
