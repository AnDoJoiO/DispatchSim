<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import { formatMessage, fmtElapsed } from '@/utils'
import { useAuthStore } from '@/stores/auth'

const emergency = useEmergencyStore()
const auth      = useAuthStore()

const messagesEl = ref(null)
const msgInput   = ref('')
const sending    = ref(false)
const endingCall = ref(false)

// Scroll to bottom when new messages arrive or typing indicator changes
watch([() => emergency.messages.length, () => emergency.isTyping], async () => {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
})

const elapsedDisplay = computed(() => fmtElapsed(emergency.elapsed))

async function sendMessage() {
  const text = msgInput.value.trim()
  if (!text || !emergency.inputEnabled || sending.value) return
  msgInput.value = ''
  sending.value  = true
  try { await emergency.sendMessage(text) }
  finally { sending.value = false }
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
}

async function endCall() {
  endingCall.value = true
  try { await emergency.endCall() }
  finally { endingCall.value = false }
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
            emergency.currentIncident
              ? `Incident #${emergency.currentIncidentId} — ${emergency.currentIncident.type}`
              : 'Selecciona o crea un incident'
          }}
        </p>
        <p class="text-xs truncate" style="color:var(--text3)">
          {{
            emergency.currentIncident
              ? `📍 ${emergency.currentIncident.location}`
              : "L'alertant respondrà les teves preguntes"
          }}
        </p>
      </div>

      <!-- Call controls: visible while call active or ended, hidden after saving fitxa -->
      <div
        v-if="(emergency.callActive || emergency.callEnded) && !emergency.interventionSaved"
        class="flex items-center gap-3 flex-shrink-0"
      >
        <span
          class="call-status-ok text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wider"
          :style="emergency.callEnded
            ? 'background:#fee2e2;color:#dc2626;border:1px solid #fca5a5'
            : 'background:#dcfce7;color:#15803d;border:1px solid #86efac'"
        >
          {{ emergency.callEnded ? 'Finalitzada' : 'En curs' }}
        </span>

        <span
          class="font-mono text-xl font-bold tabular-nums w-16 text-center"
          :class="emergency.callEnded ? 'text-red-600' : 'text-green-700'"
        >
          {{ elapsedDisplay }}
        </span>

        <button
          v-if="!emergency.callEnded"
          @click="endCall"
          :disabled="endingCall"
          class="end-call-btn text-xs font-bold px-3 py-2 rounded-lg transition"
          style="background:#fef2f2;border:1px solid #fecaca;color:#dc2626"
        >
          {{ endingCall ? '⏳ Finalitzant...' : 'Finalitzar Trucada' }}
        </button>
        <span
          v-else
          class="text-xs font-bold px-3 py-2 rounded-lg"
          style="background:#fee2e2;color:#dc2626;opacity:.6"
        >✓ Trucada finalitzada</span>
      </div>
    </div>

    <!-- Messages area -->
    <div
      ref="messagesEl"
      class="chat-msg-area flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-3"
      style="background:var(--chat-bg)"
    >
      <!-- Placeholder -->
      <div
        v-if="!emergency.messages.length && !emergency.isTyping"
        class="m-auto text-center"
        style="color:var(--text3)"
      >
        <p class="text-5xl mb-3">🎙️</p>
        <p class="text-sm">Inicia una nova emergència per<br>començar la simulació</p>
      </div>

      <!-- Messages -->
      <template v-for="msg in emergency.messages" :key="msg.id">
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
              {{ msg.role === 'operator' ? `👮 ${auth.user?.username || 'Operador'}` : '📞 Alertant' }}
            </p>
          </div>
        </div>
      </template>

      <!-- Typing indicator -->
      <div v-if="emergency.isTyping" class="flex justify-start">
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
        id="msg-input"
        v-model="msgInput"
        rows="1"
        :disabled="!emergency.inputEnabled || sending"
        placeholder="Escriu el missatge de l'operador..."
        @keydown="handleKey"
        class="flex-1 rounded-xl px-4 py-2.5 text-sm max-h-28 outline-none transition"
        style="background:var(--in-bg2);border:1px solid var(--border);color:var(--text)"
      ></textarea>
      <button
        @click="sendMessage"
        :disabled="!emergency.inputEnabled || sending"
        class="text-white rounded-xl px-5 py-2.5 font-bold text-sm transition flex-shrink-0"
        style="background:var(--accent)"
      >Enviar ↩</button>
    </div>

  </div>
</template>
