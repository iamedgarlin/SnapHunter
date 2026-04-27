class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    this._buffer = new Float32Array(0)
    this._targetChunkSize = 2048 
  }

  process(inputs) {
    const input = inputs[0]?.[0]
    if (!input) return true

    const newBuffer = new Float32Array(this._buffer.length + input.length)
    newBuffer.set(this._buffer)
    newBuffer.set(input, this._buffer.length)
    this._buffer = newBuffer

    const ratio = sampleRate / 16000
    const targetLen = Math.floor(this._buffer.length / ratio)

    if (targetLen >= this._targetChunkSize) {
      const pcm16 = new Int16Array(targetLen)
      for (let i = 0; i < targetLen; i++) {
        const srcIdx = Math.floor(i * ratio)
        const sample = this._buffer[srcIdx]
        const clamped = Math.max(-1, Math.min(1, sample))
        pcm16[i] = clamped < 0 ? clamped * 0x8000 : clamped * 0x7FFF
      }

      this.port.postMessage(pcm16.buffer, [pcm16.buffer])
      
      const consumed = Math.floor(targetLen * ratio)
      this._buffer = this._buffer.slice(consumed)
    }

    return true
  }
}
registerProcessor('pcm-processor', PCMProcessor)