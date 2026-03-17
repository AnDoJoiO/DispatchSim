import { watch, onUnmounted } from 'vue'
import { useCallStore }  from '@/stores/call'
import { useChatStore }  from '@/stores/chat'
import { useI18n }       from '@/i18n'
import { useMicrophone } from './useMicrophone'
import { useTTS }        from './useTTS'
import { SILENCE_DELAY, MIC_GRACE_PERIOD, TTS_RESUME_DELAY, MIN_REAL_WORDS, WORD_RE } from '@/config'

export function useAudioController() {
  const call  = useCallStore()
  const chat  = useChatStore()
  const { lang } = useI18n()

  const {
    active: micActive, recording: micRecording, transcribing,
    supported: micSupported, start: startMic, stop: stopMic,
    suspend: suspendMic, resume: resumeMic,
  } = useMicrophone()

  const { speaking, speak, stop: stopTTS, cleanup: cleanupTTS } = useTTS()

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
      graceTimer = setTimeout(() => {
        startMic(async (text) => {
          const realWords = text.match(WORD_RE) || []
          if (realWords.length < MIN_REAL_WORDS) return
          await chat.sendMessage(text)
        }, lang.value)
      }, MIC_GRACE_PERIOD)
    } else {
      stopMic()
    }
  }, { immediate: true })

  watch(() => call.callEnded, (ended) => {
    if (ended) { stopMic(); clearSilenceTimer() }
    // No cridem stopTTS() aquí — si la IA està parlant (últim missatge amb [FI]),
    // deixem que acabi. El onEnd del speak ja fa resumeMic/resetSilenceTimer
    // que seran no-ops perquè callEnded és true.
  })

  // ── Reacció a nous missatges ─────────────────────────────
  watch(() => chat.messages.length, () => {
    const last = chat.messages[chat.messages.length - 1]
    if (last?.role === 'alertant') {
      clearSilenceTimer()
      suspendMic()
      speak(last.content, last.voice || 'nova', {
        onEnd: () => {
          setTimeout(() => resumeMic(), TTS_RESUME_DELAY)
          resetSilenceTimer()
        },
      })
    } else if (last?.role === 'operator') {
      clearSilenceTimer()
      suspendMic() // apagar micro mentre la IA pensa — evita capturar soroll ambient
    }
  })

  onUnmounted(() => { stopMic(); cleanupTTS(); clearSilenceTimer(); if (graceTimer) clearTimeout(graceTimer) })

  return { micActive, micRecording, transcribing, micSupported, speaking, resetSilenceTimer }
}
