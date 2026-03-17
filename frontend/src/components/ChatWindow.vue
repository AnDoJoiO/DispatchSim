<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { formatMessage, fmtElapsed } from '@/utils'
import { useI18n }          from '@/i18n'
import { useChatStore }     from '@/stores/chat'
import { useCallStore }     from '@/stores/call'
import { useAuthStore }     from '@/stores/auth'
import CallTimer            from '@/components/CallTimer.vue'
import { Send, Mic, MicOff, Loader2, MapPin, Radio } from 'lucide-vue-next'

const props = defineProps({
  micActive:    { type: Boolean, default: false },
  micRecording: { type: Boolean, default: false },
  transcribing: { type: Boolean, default: false },
  micSupported: { type: Boolean, default: false },
})

const emit = defineEmits(['send', 'end-call', 'typing'])

const chat = useChatStore()
const call = useCallStore()
const auth = useAuthStore()
const { t: tr } = useI18n()

const messagesEl = ref<HTMLElement | null>(null)
const inputEl    = ref<HTMLTextAreaElement | null>(null)
const msgInput   = ref('')

const operatorName = computed(() => auth.user?.username || 'OPR')

// Scroll to bottom on new messages or typing
watch([() => chat.messages.length, () => chat.isTyping], async () => {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
})

// Auto-focus input when AI finishes responding
watch(() => chat.isTyping, (typing, wasTyping) => {
  if (wasTyping && !typing && chat.inputEnabled) {
    nextTick(() => inputEl.value?.focus())
  }
})

function sendMessage() {
  const text = msgInput.value.trim()
  if (!text || !chat.inputEnabled || chat.isTyping) return
  msgInput.value = ''
  emit('send', text)
}

function handleKey(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  else emit('typing')
}
</script>

<template>
  <div class="cw">

    <!-- Header -->
    <div class="cw-hd">
      <div class="cw-hd-info">
        <p class="cw-hd-title" v-if="call.currentIncident">
          <span class="cw-hd-id">#{{ call.currentIncidentId }}</span>
          {{ call.currentIncident.type }}
        </p>
        <p class="cw-hd-title cw-hd-title--empty" v-else>{{ tr('chat.no_incident') }}</p>
        <p class="cw-hd-loc" v-if="call.currentIncident">
          <MapPin :size="12" />
          {{ call.currentIncident.location || '—' }}
        </p>
      </div>

      <CallTimer
        :callActive="call.callActive"
        :callEnded="call.callEnded"
        :interventionSaved="call.interventionSaved"
        :elapsed="call.elapsed"
        @end-call="emit('end-call')"
      />
    </div>

    <!-- Transcript area -->
    <div ref="messagesEl" class="cw-transcript">

      <!-- Empty state -->
      <div v-if="!chat.messages.length && !chat.isTyping" class="cw-empty">
        <Radio :size="32" />
        <p>{{ tr('chat.empty') }}</p>
      </div>

      <!-- Messages -->
      <template v-for="msg in chat.messages" :key="msg.id">

        <!-- System -->
        <div v-if="msg.role === 'system'" class="cw-sys">
          <span>{{ msg.content }}</span>
        </div>

        <!-- Operator / Caller log entry -->
        <div v-else class="cw-entry" :class="msg.role === 'operator' ? 'cw-entry--opr' : 'cw-entry--alt'">
          <span class="cw-tag">{{ msg.role === 'operator' ? 'OPR' : 'ALT' }}</span>
          <span class="cw-body" v-html="formatMessage(msg.content)"></span>
        </div>
      </template>

      <!-- Typing indicator -->
      <div v-if="chat.isTyping" class="cw-entry cw-entry--alt">
        <span class="cw-tag">ALT</span>
        <span class="cw-typing">
          <Loader2 :size="14" class="animate-spin" />
        </span>
      </div>
    </div>

    <!-- Input area -->
    <div class="cw-input">
      <div class="cw-input-wrap">
        <textarea
          ref="inputEl"
          v-model="msgInput"
          rows="1"
          :disabled="!chat.inputEnabled || chat.isTyping"
          :placeholder="tr('chat.input_ph')"
          @keydown="handleKey"
          class="cw-textarea"
        ></textarea>

        <!-- Mic indicator -->
        <div v-if="micSupported && call.callActive" class="cw-mic" :title="transcribing ? tr('chat.mic_transcribing') : micRecording ? tr('chat.mic_stop') : tr('chat.mic_start')">
          <Loader2 v-if="transcribing" :size="14" class="animate-spin" style="color:var(--warning)" />
          <Mic v-else-if="micRecording" :size="14" class="cw-mic-rec" />
          <Mic v-else-if="micActive" :size="14" style="color:var(--success)" />
          <MicOff v-else :size="14" style="color:var(--text-muted)" />
        </div>
      </div>

      <button
        @click="sendMessage"
        :disabled="!chat.inputEnabled || chat.isTyping"
        class="cw-send"
        :aria-label="tr('chat.send')"
      >
        <Send :size="16" />
      </button>
    </div>

  </div>
</template>

<style scoped>
.cw {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
}

/* ── Header ── */
.cw-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  background: var(--surface-raised);
  flex-shrink: 0;
  gap: 12px;
}
.cw-hd-info { min-width: 0; }
.cw-hd-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}
.cw-hd-title--empty { color: var(--text-muted); }
.cw-hd-id {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 12px;
  color: var(--text-muted);
  margin-right: 6px;
}
.cw-hd-loc {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
  margin: 2px 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ── Transcript ── */
.cw-transcript {
  flex: 1;
  overflow-y: auto;
  padding: 12px 0;
  background: var(--bg);
}

.cw-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 12px;
  color: var(--text-muted);
  font-size: 13px;
  text-align: center;
  padding: 24px;
}

/* ── Log entries ── */
.cw-entry {
  display: flex;
  gap: 0;
  padding: 6px 16px;
  font-size: 13px;
  line-height: 1.5;
  transition: background .1s;
}
.cw-entry:hover { background: var(--surface-raised); }
.cw-entry--opr { }
.cw-entry--alt { background: rgba(0,0,0,.015); }
[data-theme="dark"] .cw-entry--alt { background: rgba(255,255,255,.02); }

.cw-tag {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 11px;
  font-weight: 700;
  width: 36px;
  flex-shrink: 0;
  padding-top: 1px;
}
.cw-entry--opr .cw-tag { color: var(--accent); }
.cw-entry--alt .cw-tag { color: var(--warning); }

.cw-body {
  flex: 1;
  color: var(--text);
  white-space: pre-wrap;
  word-break: break-word;
}

.cw-typing {
  display: flex;
  align-items: center;
  color: var(--text-muted);
}

/* ── System messages ── */
.cw-sys {
  display: flex;
  justify-content: center;
  padding: 4px 16px;
}
.cw-sys span {
  font-size: 11px;
  color: var(--text-muted);
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 3px 12px;
  border-radius: 4px;
}

/* ── Input ── */
.cw-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 12px;
  border-top: 1px solid var(--border);
  background: var(--surface);
  flex-shrink: 0;
}
.cw-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--input-bg-alt);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0 12px;
  transition: border-color .15s, box-shadow .15s;
}
.cw-input-wrap:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}
.cw-textarea {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  padding: 8px 0;
  font-size: 13px;
  font-family: inherit;
  color: var(--text);
  resize: none;
  max-height: 112px;
  line-height: 1.5;
}
.cw-textarea::placeholder { color: var(--placeholder); }
.cw-textarea:disabled { cursor: default; }

/* ── Mic indicator ── */
.cw-mic {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}
.cw-mic-rec {
  color: var(--danger);
  animation: mic-pulse 1s ease infinite;
}
@keyframes mic-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: .3; }
}

/* ── Send button ── */
.cw-send {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: none;
  background: var(--accent);
  color: white;
  transition: all .15s;
  flex-shrink: 0;
}
.cw-send:hover:not(:disabled) { filter: brightness(1.1); }
</style>
