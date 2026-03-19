import { ref } from 'vue'
import { MicVAD } from '@ricky0123/vad-web'
import { useAuthStore } from '@/stores/auth'
import { MIN_DURATION_MS, MIN_BLOB_BYTES } from '@/config'

export function useMicrophone() {
  const active       = ref(false)
  const recording    = ref(false)
  const transcribing = ref(false)
  const supported    = ref(!!navigator.mediaDevices?.getUserMedia)

  let vad: MicVAD | null = null
  let mediaRecorder: MediaRecorder | null     = null
  let chunks: Blob[]        = []
  let recordingStart: number | null = null
  let onResultCb: ((text: string) => void) | null = null
  let currentLang           = 'ca'
  let _discardNext          = false // true → handleStop discards audio (suspend active)
  let _stream: MediaStream | null = null

  function startRecording() {
    if (recording.value || transcribing.value || !_stream) return
    chunks         = []
    recordingStart = Date.now()
    mediaRecorder  = new MediaRecorder(_stream)
    mediaRecorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data) }
    mediaRecorder.onstop = handleStop
    mediaRecorder.start()
    recording.value = true
  }

  async function handleStop() {
    recording.value = false
    // If suspended (TTS playing), discard captured audio
    if (_discardNext) { _discardNext = false; return }

    const duration = Date.now() - (recordingStart ?? 0)
    const blob     = new Blob(chunks, { type: 'audio/webm' })

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
    if (mediaRecorder?.state !== 'inactive') mediaRecorder?.stop()
  }

  async function start(onResult: (text: string) => void, lang = 'ca') {
    if (!supported.value || active.value) return
    onResultCb  = onResult
    currentLang = lang

    try {
      // Determine base path for VAD static assets (ONNX model, worklet, WASM).
      // In dev Vite serves public/ at root; in prod everything is under /static/.
      const base = import.meta.env.BASE_URL || '/static/'

      vad = await MicVAD.new({
        baseAssetPath: base,
        onnxWASMBasePath: base,
        onSpeechStart: () => {
          startRecording()
        },
        onSpeechEnd: () => {
          stopRecording()
        },
      })

      // Grab the stream that MicVAD created internally so we can record from it
      _stream = (vad as any)._stream as MediaStream ?? null

      // If MicVAD doesn't expose the stream, get our own from the same mic
      if (!_stream) {
        _stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      }

      await vad.start()
      active.value = true
    } catch {
      supported.value = false
    }
  }

  function suspend() {
    if (mediaRecorder?.state !== 'inactive') {
      _discardNext = true // handleStop will discard this chunk
      mediaRecorder?.stop()
    }
    recording.value = false
    vad?.pause()
  }

  function resume() {
    if (!active.value || !vad) return
    vad.start()
  }

  function stop() {
    if (mediaRecorder?.state !== 'inactive') mediaRecorder?.stop()
    vad?.destroy()
    vad = null
    _stream?.getTracks().forEach(t => t.stop())
    _stream         = null
    active.value    = false
    recording.value = false
  }

  return { active, recording, transcribing, supported, start, stop, suspend, resume }
}
