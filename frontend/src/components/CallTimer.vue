<script setup lang="ts">
import { ref, computed } from 'vue'
import { fmtElapsed }   from '@/utils'
import { useI18n }      from '@/i18n'

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
    class="flex items-center gap-3 flex-shrink-0"
  >
    <span
      class="call-status-ok text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider"
      :style="callEnded
        ? 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5'
        : 'background:#dcfce7;color:#15803d;border:1px solid #86efac'"
    >
      {{ callEnded ? tr('chat.call_ended') : tr('chat.call_active') }}
    </span>

    <span
      class="font-mono text-xl font-bold tabular-nums w-16 text-center"
      :class="callEnded ? 'text-red-600' : 'text-green-700'"
    >
      {{ display }}
    </span>

    <button
      v-if="!callEnded"
      @click="handleEndCall"
      :disabled="ending"
      class="end-call-btn text-xs font-bold px-3 py-2 rounded-lg transition"
      style="background:#fef2f2;border:1px solid #fecaca;color:#dc2626"
    >
      {{ ending ? tr('chat.ending') : tr('chat.end_call') }}
    </button>
    <span
      v-else
      class="text-xs font-bold px-3 py-2 rounded-lg"
      style="background:#fee2e2;color:#dc2626;opacity:.6"
    >{{ tr('chat.call_finished') }}</span>
  </div>
</template>
