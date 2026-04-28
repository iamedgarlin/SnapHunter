/**
 * Gemini Live API Service - SnapHunter
 * 
 * Root cause fixes for "only static noise, no voice":
 *   1. Mic was unmuted before setupComplete → Gemini ignores/garbles pre-setup audio
 *   2. AudioContext sample rate mismatch (48kHz context vs 24kHz Gemini output)
 *   3. Tiny audio fragments played individually → pops and crackle
 *   4. Scheduling gap too large (200ms) → audible silence gaps
 */

const API_BASE = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'
const MODEL = 'gemini-3.1-flash-live-preview'

const PLAYBACK_SAMPLE_RATE = 24000  // Gemini always returns 24kHz PCM
const MIN_PLAYBACK_SAMPLES = 2400   // Buffer 100ms before playing (reduces boundary pops)

export class GeminiLive {
  constructor({ onStateChange, onTranscript, onFunctionCall, onError }) {
    this._onStateChange = onStateChange || (() => {})
    this._onTranscript = onTranscript || (() => {})
    this._onFunctionCall = onFunctionCall || (() => {})
    this._onError = onError || (() => {})

    this._ws = null
    this._playbackCtx = null   // 24kHz - for playing Gemini audio
    this._micCtx = null        // system default - for mic capture
    this._workletNode = null
    this._mediaStream = null
    this._micMuted = true
    this._state = 'disconnected'
    this._setupDone = false    // ★ track whether setup is complete
    
    this._nextStreamTime = 0 
    this._pcmDataBuffer = new Uint8Array(0)
  }

  get state() { return this._state }

  async connect(systemPrompt) {
    this._setState('connecting')
    this._setupDone = false

    try {
      // ★ FIX 1: Playback context at 24kHz to match Gemini output exactly
      // Eliminates browser resampling artifacts (the main source of static)
      this._playbackCtx = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: PLAYBACK_SAMPLE_RATE
      });

      const tokenRes = await fetch(`${API_BASE}/api/gemini/token`)
      if (!tokenRes.ok) throw new Error(`Token request failed: ${tokenRes.status}`)
      let { token, wsUrl } = await tokenRes.json()

      if (!wsUrl) throw new Error("No wsUrl received from backend");

      // Backend token is scoped to the Constrained endpoint — use it as-is.
      // NOTE: Constrained endpoint does NOT support clientContent (sendText).
      // To trigger Gemini's greeting, we send a brief silence after setup completes.
      let finalUrl = wsUrl
      if (!finalUrl.includes('Constrained')) {
        finalUrl = finalUrl.replace('BidiGenerateContent', 'BidiGenerateContentConstrained')
      }
      
      console.log("[GeminiLive] Connecting to:", finalUrl);
      this._ws = new WebSocket(`${finalUrl}?access_token=${encodeURIComponent(token)}`)

      this._ws.onopen = () => {
        console.log("[GeminiLive] WebSocket open, sending setup...");
        const setupMessage = {
          setup: {
            model: `models/${MODEL}`,
            systemInstruction: { parts: [{ text: systemPrompt }] },
            generationConfig: {
              responseModalities: ['AUDIO'],
              speechConfig: {
                voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Kore' } }
              }
            },
            // ★ Disable automatic VAD — we control turns manually via
            // activityStart/activityEnd signals. This lets us trigger
            // Gemini's greeting without requiring actual user speech.
            realtimeInputConfig: {
              automaticActivityDetection: {
                disabled: true
              }
            },
            tools: [{
              functionDeclarations: [{
                name: 'update_task_progress',
                description: 'Call this when the child has correctly answered the current task.',
                parameters: {
                  type: 'OBJECT',
                  properties: {
                    taskId: { type: 'STRING', description: 'The ID of the completed task' },
                    nextAction: {
                      type: 'STRING',
                      enum: ['eye_rest', 'next_task', 'celebration'],
                      description: 'eye_rest = 20s break, next_task = skip to next, celebration = all done'
                    }
                  },
                  required: ['taskId', 'nextAction']
                }
              }]
            }]
          }
        }
        this._ws.send(JSON.stringify(setupMessage))
      }

      this._ws.onmessage = (event) => this._handleMessage(event)
      this._ws.onerror = (err) => {
        console.error('[GeminiLive] WebSocket error:', err)
        this._onError(err)
      }
      this._ws.onclose = (event) => {
        console.log('[GeminiLive] WebSocket closed:', event.code, event.reason)
        this._setState('disconnected')
        this._cleanup()
      }

      // Setup mic with separate AudioContext
      await this._setupMic()

    } catch (error) {
      console.error('[GeminiLive] Connect failed:', error)
      this._onError(error)
      this._setState('disconnected')
    }
  }

  async _setupMic() {
    this._mediaStream = await navigator.mediaDevices.getUserMedia({
      audio: { sampleRate: 48000, channelCount: 1, echoCancellation: true }
    })

    // ★ FIX 2: Mic uses its own AudioContext at system sample rate
    // playbackCtx is 24kHz which would break mic capture/downsampling
    this._micCtx = new (window.AudioContext || window.webkitAudioContext)()
    
    await this._micCtx.audioWorklet.addModule('/pcm-worker.js')
    const source = this._micCtx.createMediaStreamSource(this._mediaStream)
    this._workletNode = new AudioWorkletNode(this._micCtx, 'pcm-processor')

    this._workletNode.port.onmessage = (event) => {
      // ★ FIX 3: CRITICAL - Don't send audio until setupComplete is received
      if (this._micMuted || !this._setupDone) return
      if (!this._ws || this._ws.readyState !== WebSocket.OPEN) return
      
      const pcm16 = new Uint8Array(event.data)
      const base64 = this._arrayBufferToBase64(pcm16)

      this._ws.send(JSON.stringify({
        realtimeInput: { audio: { mimeType: 'audio/pcm;rate=16000', data: base64 } }
      }))
    }

    // Connect worklet but don't output mic to speakers
    const silentGain = this._micCtx.createGain()
    silentGain.gain.value = 0
    source.connect(this._workletNode)
    this._workletNode.connect(silentGain)
    silentGain.connect(this._micCtx.destination)
  }

  _handleMessage(event) {
    // ★ FIX: Handle both text and binary WebSocket frames uniformly
    // Gemini may send JSON messages (including setupComplete) as binary frames
    if (event.data instanceof Blob) {
      event.data.arrayBuffer().then(buf => {
        // First, try to decode as JSON text — setupComplete and other control
        // messages sometimes arrive as binary frames instead of text frames
        try {
          const text = new TextDecoder().decode(buf)
          // Quick sanity check: JSON always starts with '{' or '['
          if (text.startsWith('{') || text.startsWith('[')) {
            const msg = JSON.parse(text)
            console.log('[GeminiLive] Decoded binary frame as JSON:', Object.keys(msg).join(', '))
            this._processJsonMessage(msg)
            return
          }
        } catch {
          // Not valid JSON — fall through to treat as audio
        }

        // It's actual audio PCM data
        if (buf.byteLength > 0) {
          console.log(`[GeminiLive] Received audio blob: ${buf.byteLength} bytes`)
          this._enqueueAudio(buf)
        }
      })
      return
    }

    // Text frame — standard JSON message
    let msg
    try { msg = JSON.parse(event.data) } catch { return }
    this._processJsonMessage(msg)
  }

  /** Process a parsed JSON message from Gemini (from either text or binary frame) */
  _processJsonMessage(msg) {
    if (msg.setupComplete) {
      console.log("[GeminiLive] ✓ Setup complete — ready for audio")
      this._setupDone = true
      this._setState('listening')
      return
    }

    if (msg.serverContent) {
      const sc = msg.serverContent
      if (sc.turnComplete) {
        console.log("[GeminiLive] Turn complete")
        // Flush any remaining buffered audio before going back to listening
        this._flushAudioBuffer()
        this._setState('listening')
      }

      if (sc.modelTurn?.parts) {
        for (const part of sc.modelTurn.parts) {
          if (part.inlineData?.mimeType?.startsWith('audio/')) {
            const audioBytes = this._base64ToArrayBuffer(part.inlineData.data)
            console.log(`[GeminiLive] Received inline audio: ${audioBytes.byteLength} bytes`)
            this._enqueueAudio(audioBytes)
          }
          if (part.text) {
            console.log(`[GeminiLive] Transcript: ${part.text}`)
            this._onTranscript(part.text)
          }
        }
      }
    }

    if (msg.toolCall) {
      for (const fc of msg.toolCall.functionCalls || []) {
        console.log(`[GeminiLive] Function call: ${fc.name}`, fc.args)
        this._onFunctionCall({ name: fc.name, args: fc.args || {} })
        if (this._ws && this._ws.readyState === WebSocket.OPEN) {
          this._ws.send(JSON.stringify({
            toolResponse: { functionResponses: [{ name: fc.name, id: fc.id, response: { result: 'ok' } }] }
          }))
        }
      }
    }
  }

  _enqueueAudio(pcmBuffer) {
    if (!this._playbackCtx || this._playbackCtx.state === 'closed') return
    if (this._playbackCtx.state === 'suspended') this._playbackCtx.resume()

    // Accumulate incoming bytes
    const newBytes = new Uint8Array(pcmBuffer)
    const totalLen = this._pcmDataBuffer.length + newBytes.length
    const combined = new Uint8Array(totalLen)
    combined.set(this._pcmDataBuffer)
    combined.set(newBytes, this._pcmDataBuffer.length)

    // Int16 alignment (2 bytes per sample)
    const safeLength = Math.floor(totalLen / 2) * 2
    const sampleCount = safeLength / 2

    // ★ FIX 5: Buffer at least 100ms before playing
    // Tiny fragments (like the 118-byte blob you saw) cause pops
    if (sampleCount < MIN_PLAYBACK_SAMPLES) {
      this._pcmDataBuffer = combined
      return
    }

    // Consume safeLength bytes, keep remainder for next chunk
    this._pcmDataBuffer = combined.slice(safeLength)

    const audioData = combined.slice(0, safeLength)
    const int16 = new Int16Array(audioData.buffer, audioData.byteOffset, sampleCount)
    const float32 = new Float32Array(sampleCount)

    for (let i = 0; i < sampleCount; i++) {
      float32[i] = int16[i] / 32768.0
    }

    // playbackCtx.sampleRate === 24000, so no resampling happens here
    const audioBuf = this._playbackCtx.createBuffer(1, float32.length, PLAYBACK_SAMPLE_RATE)
    audioBuf.getChannelData(0).set(float32)

    const source = this._playbackCtx.createBufferSource()
    source.buffer = audioBuf
    source.connect(this._playbackCtx.destination)

    const now = this._playbackCtx.currentTime

    // ★ FIX 6: Minimal scheduling gap (was 200ms → now 20ms)
    if (this._nextStreamTime < now) {
      this._nextStreamTime = now + 0.02
    }

    source.start(this._nextStreamTime)
    this._nextStreamTime += audioBuf.duration

    console.log(`[GeminiLive] ▶ Playing ${sampleCount} samples (${(sampleCount/PLAYBACK_SAMPLE_RATE*1000).toFixed(0)}ms)`)
    this._setState('speaking')
  }

  // ★ Also flush remaining buffer when turn completes
  _flushAudioBuffer() {
    if (this._pcmDataBuffer.length < 2) return
    
    const safeLength = Math.floor(this._pcmDataBuffer.length / 2) * 2
    if (safeLength === 0) return

    const audioData = this._pcmDataBuffer.slice(0, safeLength)
    this._pcmDataBuffer = this._pcmDataBuffer.slice(safeLength)

    const sampleCount = safeLength / 2
    const int16 = new Int16Array(audioData.buffer, audioData.byteOffset, sampleCount)
    const float32 = new Float32Array(sampleCount)
    for (let i = 0; i < sampleCount; i++) {
      float32[i] = int16[i] / 32768.0
    }

    const audioBuf = this._playbackCtx.createBuffer(1, float32.length, PLAYBACK_SAMPLE_RATE)
    audioBuf.getChannelData(0).set(float32)
    const source = this._playbackCtx.createBufferSource()
    source.buffer = audioBuf
    source.connect(this._playbackCtx.destination)

    const now = this._playbackCtx.currentTime
    if (this._nextStreamTime < now) this._nextStreamTime = now + 0.02
    source.start(this._nextStreamTime)
    this._nextStreamTime += audioBuf.duration
  }

  _arrayBufferToBase64(buffer) {
    let bin = ''
    const bytes = new Uint8Array(buffer)
    for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i])
    return btoa(bin)
  }

  _base64ToArrayBuffer(base64) {
    const bin = atob(base64)
    const bytes = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
    return bytes.buffer
  }

  _cleanup() {
    if (this._mediaStream) {
      this._mediaStream.getTracks().forEach(t => t.stop())
      this._mediaStream = null
    }
    if (this._micCtx && this._micCtx.state !== 'closed') {
      this._micCtx.close().catch(() => {})
      this._micCtx = null
    }
    if (this._playbackCtx && this._playbackCtx.state !== 'closed') {
      this._playbackCtx.close().catch(() => {})
      this._playbackCtx = null
    }
    this._ws = null
    this._setupDone = false
    this._nextStreamTime = 0
    this._pcmDataBuffer = new Uint8Array(0)
  }

  _setState(s) { this._state = s; this._onStateChange(s) }

  sendText(text) {
    if (!this._ws || this._ws.readyState !== WebSocket.OPEN || !this._setupDone) {
      console.warn('[GeminiLive] sendText blocked — ws not ready or setup not done')
      return false
    }
    try {
      console.log(`[GeminiLive] Sending text: "${text.substring(0, 60)}..."`)
      this._ws.send(JSON.stringify({
        clientContent: { turns: [{ role: 'user', parts: [{ text: text }] }], turnComplete: true }
      }))
      return true
    } catch (err) {
      console.error('[GeminiLive] sendText failed:', err)
      return false
    }
  }

  /**
   * Trigger Gemini's greeting without requiring user speech.
   * 
   * With automatic VAD disabled, we manually signal turn boundaries.
   * Send activityStart → tiny audio → activityEnd to create a
   * complete (empty) user turn, triggering Gemini to respond
   * per the system prompt's "Start by greeting..." instruction.
   */
  triggerGreeting() {
    if (!this._ws || this._ws.readyState !== WebSocket.OPEN || !this._setupDone) return
    console.log('[GeminiLive] Triggering greeting via manual activity signals...')

    // Signal: user turn started
    this._ws.send(JSON.stringify({ realtimeInput: { activityStart: {} } }))

    // Send minimal audio (50ms of near-silence at 16kHz)
    const samples = new Int16Array(800)
    for (let i = 0; i < samples.length; i++) {
      samples[i] = Math.floor((Math.random() - 0.5) * 100)
    }
    const base64 = this._arrayBufferToBase64(samples.buffer)
    this._ws.send(JSON.stringify({
      realtimeInput: { audio: { mimeType: 'audio/pcm;rate=16000', data: base64 } }
    }))

    // Signal: user turn ended → Gemini will now respond
    this._ws.send(JSON.stringify({ realtimeInput: { activityEnd: {} } }))
  }

  setMicMuted(muted) {
    const wasMuted = this._micMuted
    this._micMuted = muted
    
    if (!muted) {
      this._micCtx?.resume()
      this._playbackCtx?.resume()
      // Manual VAD: signal that user started speaking
      if (wasMuted && this._ws?.readyState === WebSocket.OPEN && this._setupDone) {
        console.log('[GeminiLive] activityStart (mic unmuted)')
        this._ws.send(JSON.stringify({ realtimeInput: { activityStart: {} } }))
      }
    } else {
      // Manual VAD: signal that user stopped speaking
      if (!wasMuted && this._ws?.readyState === WebSocket.OPEN && this._setupDone) {
        console.log('[GeminiLive] activityEnd (mic muted)')
        this._ws.send(JSON.stringify({ realtimeInput: { activityEnd: {} } }))
      }
    }
  }

  disconnect() {
    if (this._ws) this._ws.close()
    this._cleanup()
    this._setState('disconnected')
  }
}