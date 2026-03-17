import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const VOICE_THRESHOLD = 30   // RMS mínimo para detectar voz (0-255) — filtra ecos TTS y ruido
const SILENCE_MS      = 1200 // ms de silencio antes de parar la grabación
const MIN_DURATION_MS = 1000 // grabaciones más cortas se descartan (evita alucinaciones Whisper)
const MIN_BLOB_BYTES  = 3000 // blobs muy pequeños son silencio

export function useMicrophone() {
  const active       = ref(false)
  const recording    = ref(false)
  const transcribing = ref(false)
  const supported    = ref(!!navigator.mediaDevices?.getUserMedia)

  let stream        = null
  let audioCtx      = null
  let analyser      = null
  let animFrame     = null
  let mediaRecorder = null
  let chunks        = []
  let silenceTimer  = null
  let recordingStart = null
  let onResultCb    = null
  let currentLang   = 'ca'

  function getRMS(data) {
    let sum = 0
    for (let i = 0; i < data.length; i++) sum += data[i] ** 2
    return Math.sqrt(sum / data.length)
  }

  function startRecording() {
    if (recording.value || transcribing.value || !stream) return
    chunks         = []
    recordingStart = Date.now()
    mediaRecorder  = new MediaRecorder(stream)
    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data) }
    mediaRecorder.onstop = handleStop
    mediaRecorder.start()
    recording.value = true
  }

  async function handleStop() {
    recording.value = false
    const duration = Date.now() - (recordingStart ?? 0)
    const blob     = new Blob(chunks, { type: 'audio/webm' })

    // Descartar si es demasiado corto o pequeño (silencio / ruido / alucinación Whisper)
    if (duration < MIN_DURATION_MS || blob.size < MIN_BLOB_BYTES) return

    transcribing.value = true
    try {
      const auth = useAuthStore()
      const fd   = new FormData()
      fd.append('audio', blob, 'audio.webm')
      const res = await fetch(`/api/v1/voice/transcribe?lang=${currentLang}`, {
        method:  'POST',
        headers: { Authorization: `Bearer ${auth.token}` },
        body:    fd,
      })
      if (res.ok) {
        const { text } = await res.json()
        if (text?.trim()) onResultCb?.(text.trim())
      }
    } finally {
      transcribing.value = false
    }
  }

  function stopRecording() {
    if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null }
    if (mediaRecorder?.state !== 'inactive') mediaRecorder.stop()
  }

  function tick() {
    if (!analyser) return
    const data = new Uint8Array(analyser.frequencyBinCount)
    analyser.getByteFrequencyData(data)
    const rms = getRMS(data)

    if (rms > VOICE_THRESHOLD) {
      if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null }
      if (!recording.value && !transcribing.value) startRecording()
    } else if (recording.value && !silenceTimer) {
      silenceTimer = setTimeout(stopRecording, SILENCE_MS)
    }

    animFrame = requestAnimationFrame(tick)
  }

  async function start(onResult, lang = 'ca') {
    if (!supported.value || active.value) return
    onResultCb  = onResult
    currentLang = lang
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      supported.value = false
      return
    }
    audioCtx = new AudioContext()
    analyser = audioCtx.createAnalyser()
    analyser.fftSize = 512
    audioCtx.createMediaStreamSource(stream).connect(analyser)
    active.value = true
    tick()
  }

  function suspend() {
    if (animFrame)    { cancelAnimationFrame(animFrame); animFrame = null }
    if (silenceTimer) { clearTimeout(silenceTimer); silenceTimer = null }
    if (mediaRecorder?.state !== 'inactive') mediaRecorder?.stop()
    recording.value = false
  }

  function resume() {
    if (!active.value || !analyser) return
    tick()
  }

  function stop() {
    if (animFrame)    cancelAnimationFrame(animFrame)
    if (silenceTimer) clearTimeout(silenceTimer)
    if (mediaRecorder?.state !== 'inactive') mediaRecorder?.stop()
    stream?.getTracks().forEach(t => t.stop())
    audioCtx?.close()
    active.value    = false
    recording.value = false
    analyser  = null
    stream    = null
    audioCtx  = null
    animFrame = null
  }

  return { active, recording, transcribing, supported, start, stop, suspend, resume }
}
