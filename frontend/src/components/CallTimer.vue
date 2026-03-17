<script setup lang="ts">
import { ref, computed } from 'vue'
import { fmtElapsed }   from '@/utils'
import { useI18n }      from '@/i18n'
import { PhoneOff, CheckCircle } from 'lucide-vue-next'

const props = defineProps({
  callActive:        { type: Boolean, required: true },
  callEnded:         { type: Boolean, required: true },
  interventionSaved: { type: Boolean, required: true },
  elapsed:           { type: Number,  required: true },
})

const emit = defineEmits(['end-call'])
const { t: tr } = useI18n()

const ending  = ref(false)
const display = computed(() => fmtElapsed(props.elapsed))

function handleEndCall() {
  if (ending.value) return
  ending.value = true
  emit('end-call')
}
</script>

<template>
  <div
    v-if="(callActive || callEnded) && !interventionSaved"
    class="ct"
  >
    <!-- Status badge -->
    <span class="ct-badge" :class="callEnded ? 'ct-badge--ended' : 'ct-badge--active'">
      {{ callEnded ? tr('chat.call_ended') : tr('chat.call_active') }}
    </span>

    <!-- Timer -->
    <span class="ct-time" :class="callEnded ? 'ct-time--ended' : ''">
      {{ display }}
    </span>

    <!-- End / Finished button -->
    <button
      v-if="!callEnded"
      @click="handleEndCall"
      :disabled="ending"
      class="ct-end-btn"
    >
      <PhoneOff :size="13" />
      {{ ending ? tr('chat.ending') : tr('chat.end_call') }}
    </button>
    <span v-else class="ct-finished">
      <CheckCircle :size="13" />
      {{ tr('chat.call_finished') }}
    </span>
  </div>
</template>

<style scoped>
.ct {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.ct-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: .04em;
}
.ct-badge--active {
  background: var(--success-bg);
  color: var(--success);
  border: 1px solid var(--success-border);
}
.ct-badge--ended {
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}

.ct-time {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 16px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--text);
  min-width: 52px;
  text-align: center;
}
.ct-time--ended { color: var(--danger); }

.ct-end-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--danger-border);
  background: var(--danger-bg);
  color: var(--danger);
  font-family: inherit;
  transition: all .15s;
}
.ct-end-btn:hover { background: var(--danger); color: white; border-color: var(--danger); }

.ct-finished {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}
</style>
