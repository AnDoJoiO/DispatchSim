<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useCallStore } from '@/stores/call'
import { useI18n } from '@/i18n'
import { Save, CheckCircle, AlertCircle, MapPin, Phone, Users, ShieldAlert, FileText } from 'lucide-vue-next'

const call = useCallStore()
const { t: tr, risks } = useI18n()

const address  = ref('')
const phone    = ref('')
const injured  = ref(0)
const notes    = ref('')
const selected = ref<string[]>([])
const saving   = ref(false)
const status   = ref<null | 'ok' | 'error'>(null)

// Reset form when switching incidents
watch(() => call.currentIncidentId, () => {
  address.value = phone.value = notes.value = ''
  injured.value = 0
  selected.value = []
  status.value  = null
})

function toggleRisk(value: string) {
  const idx = selected.value.indexOf(value)
  if (idx >= 0) selected.value.splice(idx, 1)
  else selected.value.push(value)
}

async function save() {
  if (!call.currentIncidentId) return
  saving.value = true
  status.value = null
  const ok = await call.saveIntervention({
    incident_id:      call.currentIncidentId,
    exact_address:    address.value.trim(),
    contact_phone:    phone.value.trim(),
    num_injured:      Math.max(0, parseInt(String(injured.value)) || 0),
    additional_risks: selected.value.join(','),
    operator_notes:   notes.value.trim(),
  })
  status.value = ok ? 'ok' : 'error'
  saving.value = false
  if (ok) setTimeout(() => { status.value = null }, 4000)
}
</script>

<template>
  <div class="fp">

    <!-- Header -->
    <div class="fp-hd">
      <FileText :size="14" />
      <div>
        <h2 class="fp-title">{{ tr('fitxa.title') }}</h2>
        <p class="fp-subtitle">{{ tr('fitxa.subtitle') }}</p>
      </div>
    </div>

    <!-- Form -->
    <div class="fp-body">

      <!-- Address -->
      <div class="fp-field">
        <label for="fitxa-address" class="fp-label">
          <MapPin :size="12" />
          {{ tr('fitxa.address') }}
        </label>
        <input id="fitxa-address" v-model="address" type="text" :placeholder="tr('fitxa.address_ph')" class="fc" />
      </div>

      <!-- Phone -->
      <div class="fp-field">
        <label for="fitxa-phone" class="fp-label">
          <Phone :size="12" />
          {{ tr('fitxa.phone') }}
        </label>
        <input id="fitxa-phone" v-model="phone" type="tel" :placeholder="tr('fitxa.phone_ph')" class="fc" />
      </div>

      <!-- Injured -->
      <div class="fp-field">
        <label for="fitxa-injured" class="fp-label">
          <Users :size="12" />
          {{ tr('fitxa.injured') }}
        </label>
        <input id="fitxa-injured" v-model="injured" type="number" min="0" class="fc" />
      </div>

      <!-- Divider -->
      <div class="fp-divider"></div>

      <!-- Risks as chips -->
      <div class="fp-field">
        <label id="fitxa-risks-label" class="fp-label">
          <ShieldAlert :size="12" />
          {{ tr('fitxa.risks') }}
        </label>
        <div class="fp-chips" role="group" aria-labelledby="fitxa-risks-label">
          <button
            v-for="risk in risks()"
            :key="risk.value"
            type="button"
            class="fp-chip"
            :class="{ 'fp-chip--active': selected.includes(risk.value) }"
            @click="toggleRisk(risk.value)"
          >{{ risk.label }}</button>
        </div>
      </div>

      <!-- Divider -->
      <div class="fp-divider"></div>

      <!-- Notes -->
      <div class="fp-field">
        <label for="fitxa-notes" class="fp-label">{{ tr('fitxa.notes') }}</label>
        <textarea id="fitxa-notes" v-model="notes" rows="3" :placeholder="tr('fitxa.notes_ph')" class="fc"></textarea>
      </div>

      <!-- Status -->
      <div v-if="status" class="fp-status" :class="status === 'ok' ? 'fp-status--ok' : 'fp-status--err'">
        <CheckCircle v-if="status === 'ok'" :size="14" />
        <AlertCircle v-else :size="14" />
        {{ status === 'ok' ? tr('fitxa.saved') : tr('fitxa.error') }}
      </div>
    </div>

    <!-- Footer -->
    <div class="fp-foot">
      <button
        @click="save"
        :disabled="!call.currentIncidentId || saving || call.interventionSaved"
        :aria-label="tr('fitxa.save')"
        class="fp-save"
        :class="{ 'fp-save--saved': call.interventionSaved }"
      >
        <CheckCircle v-if="call.interventionSaved" :size="15" />
        <Save v-else :size="15" />
        {{ call.interventionSaved ? tr('fitxa.saved') : saving ? tr('fitxa.saving') : tr('fitxa.save') }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.fp {
  width: 340px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

/* ── Header ── */
.fp-hd {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 16px;
  background: var(--surface-raised);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
  color: var(--text-muted);
}
.fp-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}
.fp-subtitle {
  font-size: 11px;
  color: var(--text-muted);
  margin: 1px 0 0;
}

/* ── Body ── */
.fp-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ── Fields ── */
.fp-field { display: flex; flex-direction: column; gap: 4px; }

.fp-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.fp-divider {
  height: 1px;
  background: var(--border);
  margin: 2px 0;
}

/* ── Risk chips ── */
.fp-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.fp-chip {
  font-size: 11px;
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-secondary);
  font-family: inherit;
  transition: all .15s;
}
.fp-chip:hover {
  border-color: var(--accent-border);
  color: var(--accent);
}
.fp-chip--active {
  background: var(--accent-bg);
  border-color: var(--accent-border);
  color: var(--accent);
  font-weight: 600;
}

/* ── Status ── */
.fp-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
  padding: 8px;
  border-radius: 6px;
}
.fp-status--ok {
  background: var(--success-bg);
  color: var(--success);
  border: 1px solid var(--success-border);
}
.fp-status--err {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

/* ── Footer ── */
.fp-foot {
  padding: 12px 16px;
  border-top: 1px solid var(--border);
  background: var(--surface-raised);
  flex-shrink: 0;
}
.fp-save {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 9px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  background: var(--success);
  color: white;
  font-family: inherit;
  transition: all .15s;
}
.fp-save:hover:not(:disabled) { filter: brightness(1.1); }
.fp-save--saved {
  background: var(--surface-raised);
  color: var(--success);
  border: 1px solid var(--success-border);
  cursor: default;
}
</style>
