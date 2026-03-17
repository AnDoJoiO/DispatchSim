import { watch, onUnmounted } from 'vue'
import { useCallStore }  from '@/stores/call'
import { useChatStore }  from '@/stores/chat'
import { useI18n }       from '@/i18n'
import { useMicrophone } from './useMicrophone'
import { useTTS }        from './useTTS'

const SILENCE_DELAY    = 15000 // ms sense resposta de l'operador
const MIC_GRACE_PERIOD = 2000  // ms d'espera abans d'activar VAD (evita capturar clic/soroll inicial)

export function useAudioController() {
  const call  = useCallStore()
  const chat  = useChatStore()
  const { lang } = useI18n()

  const {
    active: micActive, recording: micRecording, transcribing,
    supported: micSupported, start: startMic, stop: stopMic,
    suspend: suspendMic, resume: resumeMic,
  } = useMicrophone()

  const { speaking, speak, stop: stopTTS } = useTTS()

  let silenceTimer = null

  function clearSilenceTimer() {
    if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null }
  }

  function resetSilenceTimer() {
    clearSilenceTimer()
    if (!call.callActive || call.callEnded) return
    silenceTimer = setTimeout(() => {
      if (call.callActive && !call.callEnded && !chat.isTyping && !speaking.value) {
        chat.sendSilence()
      }
    }, SILENCE_DELAY)
  }

  // ── Cicle de vida de la trucada ──────────────────────────
  let graceTimer = null
  watch(() => call.callActive, (active) => {
    if (graceTimer) { clearTimeout(graceTimer); graceTimer = null }
    if (active && micSupported.value) {
      // Esperar grace period per evitar capturar clic i soroll inicial
      graceTimer = setTimeout(() => {
        startMic(async (text) => {
          await chat.sendMessage(text)
        }, lang.value)
      }, MIC_GRACE_PERIOD)
    } else {
      stopMic()
    }
  }, { immediate: true })

  watch(() => call.callEnded, (ended) => {
    if (ended) { stopMic(); stopTTS(); clearSilenceTimer() }
  })

  // ── Reacció a nous missatges ─────────────────────────────
  watch(() => chat.messages.length, () => {
    const last = chat.messages[chat.messages.length - 1]
    if (last?.role === 'alertant') {
      clearSilenceTimer()
      suspendMic() // apagar VAD immediatament, abans del fetch TTS
      speak(last.content, last.voice || 'nova', {
        onEnd: () => {
          setTimeout(() => resumeMic(), 600)
          resetSilenceTimer() // iniciar compte enrere un cop acabat el TTS
        },
      })
    } else if (last?.role === 'operator') {
      clearSilenceTimer() // l'operador ha respost, cancel·lar compte enrere
    }
  })

  onUnmounted(() => { stopMic(); stopTTS(); clearSilenceTimer(); if (graceTimer) clearTimeout(graceTimer) })

  return { micActive, micRecording, transcribing, micSupported, speaking, resetSilenceTimer }
}
