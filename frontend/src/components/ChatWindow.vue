<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import { formatMessage }    from '@/utils'
import { useI18n }          from '@/i18n'
import { useChatStore }     from '@/stores/chat'
import { useCallStore }     from '@/stores/call'
import { useAuthStore }     from '@/stores/auth'
import CallTimer            from '@/components/CallTimer.vue'

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

const messagesEl = ref(null)
const inputEl    = ref(null)
const msgInput   = ref('')

const operatorName = computed(() => auth.user?.username || '')

// Scroll to bottom when new messages arrive or typing indicator changes
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

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
  else emit('typing')
}
</script>

<template>
  <div class="chat-wrap flex-1 flex flex-col min-w-0 panel overflow-hidden">

    <!-- Chat header -->
    <div
      class="chat-hd flex items-center gap-3 px-5 py-3 flex-shrink-0"
      style="border-bottom:1px solid var(--border)"
    >
      <div
        class="w-9 h-9 rounded-xl flex items-center justify-center text-lg flex-shrink-0"
        style="background:#fef2f2;border:1px solid #fecaca"
      >📞</div>

      <div class="flex-1 min-w-0">
        <p class="text-sm font-bold truncate" style="color:var(--text)">
          {{
            call.currentIncident
              ? `Incident #${call.currentIncidentId} — ${call.currentIncident.type}`
              : tr('chat.no_incident')
          }}
        </p>
        <p class="text-xs truncate" style="color:var(--text3)">
          {{
            call.currentIncident
              ? `📍 ${call.currentIncident.location}`
              : tr('chat.no_incident_sub')
          }}
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

    <!-- Messages area -->
    <div
      ref="messagesEl"
      class="chat-msg-area flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-3"
      style="background:var(--chat-bg)"
    >
      <!-- Placeholder -->
      <div
        v-if="!chat.messages.length && !chat.isTyping"
        class="m-auto text-center"
        style="color:var(--text3)"
      >
        <p class="text-5xl mb-3">🎙️</p>
        <p class="text-sm" style="white-space:pre-line">{{ tr('chat.empty') }}</p>
      </div>

      <!-- Messages -->
      <template v-for="msg in chat.messages" :key="msg.id">
        <!-- System message -->
        <div
          v-if="msg.role === 'system'"
          class="sys-msg text-center text-xs py-1.5 px-4 mx-auto rounded-full"
          style="max-width:90%"
        >{{ msg.content }}</div>

        <!-- Operator / Alertant bubble -->
        <div
          v-else
          :class="msg.role === 'operator' ? 'flex justify-end' : 'flex justify-start'"
        >
          <div :class="msg.role === 'operator' ? 'flex flex-col items-end' : 'flex flex-col items-start'">
            <div
              class="max-w-[70%] px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap"
              :class="msg.role === 'operator' ? 'bop' : 'bal'"
              v-html="formatMessage(msg.content)"
            ></div>
            <p class="text-xs mt-1" :class="msg.role === 'operator' ? 'text-right' : ''" style="color:var(--text3)">
              {{ msg.role === 'operator' ? `👮 ${operatorName || tr('chat.operator_name')}` : tr('chat.caller_label') }}
            </p>
          </div>
        </div>
      </template>

      <!-- Typing indicator -->
      <div v-if="chat.isTyping" class="flex justify-start">
        <div class="bal px-4 py-3 flex gap-1 items-center">
          <span class="typing-dot w-2 h-2 rounded-full animate-bounce" style="animation-delay:0ms"></span>
          <span class="typing-dot w-2 h-2 rounded-full animate-bounce" style="animation-delay:150ms"></span>
          <span class="typing-dot w-2 h-2 rounded-full animate-bounce" style="animation-delay:300ms"></span>
        </div>
      </div>
    </div>

    <!-- Input area -->
    <div
      class="chat-input-area px-4 py-3 flex gap-3 items-end flex-shrink-0"
      style="background:var(--surface);border-top:1px solid var(--border)"
    >
      <textarea
        ref="inputEl"
        id="msg-input"
        v-model="msgInput"
        rows="1"
        :disabled="!chat.inputEnabled || chat.isTyping"
        :placeholder="tr('chat.input_ph')"
        @keydown="handleKey"
        class="flex-1 rounded-xl px-4 py-2.5 text-sm max-h-28 outline-none transition"
        style="background:var(--in-bg2);border:1px solid var(--border);color:var(--text)"
      ></textarea>
      <!-- Indicador d'estat del micròfon (no interactiu) -->
      <div
        v-if="micSupported && call.callActive"
        class="flex-shrink-0 flex items-center justify-center w-10 h-10"
        :title="transcribing ? tr('chat.mic_transcribing') : micRecording ? tr('chat.mic_stop') : tr('chat.mic_start')"
      >
        <span v-if="transcribing"          class="text-xl">⏳</span>
        <span v-else-if="micRecording"     class="text-xl animate-pulse">🔴</span>
        <span v-else-if="micActive"        class="block w-3 h-3 rounded-full animate-pulse" style="background:#22c55e"></span>
      </div>
      <button
        @click="sendMessage"
        :disabled="!chat.inputEnabled || chat.isTyping"
        class="text-white rounded-xl px-5 py-2.5 font-bold text-sm transition flex-shrink-0"
        style="background:var(--accent)"
      >{{ tr('chat.send') }}</button>
    </div>

  </div>
</template>
