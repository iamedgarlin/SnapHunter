import { ref, onUnmounted } from 'vue'

/**
 * useSensors - composable for motion-based task interactions
 *
 * Provides four sensor detectors:
 *   useShake()  - detect phone shaking via accelerometer
 *   useSpin()   - detect body rotation via gyroscope/compass
 *   useSky()    - detect phone held up toward the sky
 *   useStep()   - count walking steps via accelerometer peaks
 *
 * Each returns reactive state + start/stop controls.
 * All sensors auto-cleanup on component unmount.
 */

// ─── Permission helper (iOS 13+ requires explicit permission) ───

async function requestMotionPermission() {
  // iOS 13+ requires permission for DeviceMotion and DeviceOrientation
  if (
    typeof DeviceMotionEvent !== 'undefined' &&
    typeof DeviceMotionEvent.requestPermission === 'function'
  ) {
    try {
      const result = await DeviceMotionEvent.requestPermission()
      return result === 'granted'
    } catch {
      return false
    }
  }
  // Android / desktop - no permission needed
  return true
}

async function requestOrientationPermission() {
  if (
    typeof DeviceOrientationEvent !== 'undefined' &&
    typeof DeviceOrientationEvent.requestPermission === 'function'
  ) {
    try {
      const result = await DeviceOrientationEvent.requestPermission()
      return result === 'granted'
    } catch {
      return false
    }
  }
  return true
}

// ─── Shake Detector ─────────────────────────────────────────

/**
 * Detect phone shaking.
 * @param {number} targetShakes - how many shakes to complete the task
 * @param {Function} onComplete - called when target reached
 */
export function useShake(targetShakes = 3, onComplete = null) {
  const shakeCount = ref(0)
  const isActive = ref(false)
  const progress = ref(0)
  const completed = ref(false)

  const SHAKE_THRESHOLD = 15 // acceleration magnitude threshold
  const SHAKE_COOLDOWN = 400 // ms between counted shakes

  let lastShakeTime = 0
  let handler = null

  function onMotion(e) {
    if (completed.value) return
    const acc = e.accelerationIncludingGravity
    if (!acc) return

    const magnitude = Math.sqrt(acc.x ** 2 + acc.y ** 2 + acc.z ** 2)
    const now = Date.now()

    // Subtract gravity (~9.8) and check threshold
    if (magnitude > SHAKE_THRESHOLD && now - lastShakeTime > SHAKE_COOLDOWN) {
      lastShakeTime = now
      shakeCount.value++
      progress.value = Math.min(1, shakeCount.value / targetShakes)

      if (shakeCount.value >= targetShakes) {
        completed.value = true
        stop()
        onComplete?.()
      }
    }
  }

  async function start() {
    const granted = await requestMotionPermission()
    if (!granted) return false

    shakeCount.value = 0
    progress.value = 0
    completed.value = false
    isActive.value = true
    handler = onMotion
    window.addEventListener('devicemotion', handler)
    return true
  }

  function stop() {
    isActive.value = false
    if (handler) {
      window.removeEventListener('devicemotion', handler)
      handler = null
    }
  }

  function reset() {
    stop()
    shakeCount.value = 0
    progress.value = 0
    completed.value = false
  }

  onUnmounted(stop)

  return { shakeCount, isActive, progress, completed, start, stop, reset }
}

// ─── Spin Detector ──────────────────────────────────────────

/**
 * Detect body rotation (turning around).
 * @param {number} targetDegrees - total degrees to rotate (e.g. 360)
 * @param {Function} onComplete - called when target reached
 */
export function useSpin(targetDegrees = 360, onComplete = null) {
  const totalRotation = ref(0)
  const isActive = ref(false)
  const progress = ref(0)
  const completed = ref(false)

  let lastAlpha = null
  let handler = null

  function onOrientation(e) {
    if (completed.value) return
    if (e.alpha == null) return

    const alpha = e.alpha // 0-360 compass heading

    if (lastAlpha !== null) {
      let delta = alpha - lastAlpha

      // Handle wrap-around (e.g. 359 → 1 = +2, not -358)
      if (delta > 180) delta -= 360
      if (delta < -180) delta += 360

      totalRotation.value += Math.abs(delta)
      progress.value = Math.min(1, totalRotation.value / targetDegrees)

      if (totalRotation.value >= targetDegrees) {
        completed.value = true
        stop()
        onComplete?.()
      }
    }

    lastAlpha = alpha
  }

  async function start() {
    const granted = await requestOrientationPermission()
    if (!granted) return false

    totalRotation.value = 0
    progress.value = 0
    completed.value = false
    lastAlpha = null
    isActive.value = true
    handler = onOrientation
    window.addEventListener('deviceorientation', handler)
    return true
  }

  function stop() {
    isActive.value = false
    if (handler) {
      window.removeEventListener('deviceorientation', handler)
      handler = null
    }
  }

  function reset() {
    stop()
    totalRotation.value = 0
    progress.value = 0
    completed.value = false
    lastAlpha = null
  }

  onUnmounted(stop)

  return { totalRotation, isActive, progress, completed, start, stop, reset }
}

// ─── Sky Gazer Detector ─────────────────────────────────────

/**
 * Detect phone held up toward the sky.
 * Uses accelerometer z-axis: when phone faces up, z ≈ -9.8 (gravity pulling down).
 * Also checks beta angle (tilt forward/back) from orientation.
 *
 * @param {number} targetSeconds - how many seconds to hold phone up
 * @param {Function} onComplete - called when target reached
 */
export function useSky(targetSeconds = 3, onComplete = null) {
  const holdTime = ref(0)
  const isActive = ref(false)
  const isFacingUp = ref(false)
  const progress = ref(0)
  const completed = ref(false)

  // beta ≈ 0-30 means phone is fairly flat/facing up
  // z acceleration < -7 means gravity is pulling on back of phone (screen faces up)
  const BETA_THRESHOLD = 40 // degrees - less than this = facing up enough
  const Z_THRESHOLD = -6   // m/s² - more negative = more face-up

  let currentBeta = 90
  let currentZ = 0
  let countInterval = null
  let motionHandler = null
  let orientHandler = null

  function onMotion(e) {
    const acc = e.accelerationIncludingGravity
    if (acc) currentZ = acc.z
  }

  function onOrientation(e) {
    if (e.beta != null) currentBeta = Math.abs(e.beta)
  }

  function checkSky() {
    if (completed.value) return

    // Phone is facing up when beta is small AND z is very negative
    const facingUp = currentBeta < BETA_THRESHOLD && currentZ < Z_THRESHOLD
    isFacingUp.value = facingUp

    if (facingUp) {
      holdTime.value += 0.1
      progress.value = Math.min(1, holdTime.value / targetSeconds)

      if (holdTime.value >= targetSeconds) {
        completed.value = true
        stop()
        onComplete?.()
      }
    }
    // Don't reset holdTime - accumulated hold is more forgiving for kids
  }

  async function start() {
    const motionOk = await requestMotionPermission()
    const orientOk = await requestOrientationPermission()
    if (!motionOk || !orientOk) return false

    holdTime.value = 0
    progress.value = 0
    completed.value = false
    isFacingUp.value = false
    currentBeta = 90
    currentZ = 0
    isActive.value = true

    motionHandler = onMotion
    orientHandler = onOrientation
    window.addEventListener('devicemotion', motionHandler)
    window.addEventListener('deviceorientation', orientHandler)
    countInterval = setInterval(checkSky, 100) // check 10x per second
    return true
  }

  function stop() {
    isActive.value = false
    if (motionHandler) {
      window.removeEventListener('devicemotion', motionHandler)
      motionHandler = null
    }
    if (orientHandler) {
      window.removeEventListener('deviceorientation', orientHandler)
      orientHandler = null
    }
    if (countInterval) {
      clearInterval(countInterval)
      countInterval = null
    }
  }

  function reset() {
    stop()
    holdTime.value = 0
    progress.value = 0
    completed.value = false
    isFacingUp.value = false
  }

  onUnmounted(stop)

  return { holdTime, isFacingUp, isActive, progress, completed, start, stop, reset }
}

// ─── Step Counter ───────────────────────────────────────────

/**
 * Count walking steps using accelerometer peak detection.
 * Algorithm: detect peaks in acceleration magnitude that exceed a threshold,
 * with a minimum time gap between peaks to avoid double-counting.
 *
 * @param {number} targetSteps - steps needed to complete
 * @param {Function} onComplete - called when target reached
 */
export function useStep(targetSteps = 20, onComplete = null) {
  const stepCount = ref(0)
  const isActive = ref(false)
  const progress = ref(0)
  const completed = ref(false)

  const STEP_THRESHOLD = 12  // acceleration peak to count as a step
  const STEP_COOLDOWN = 300  // ms minimum between steps (walking cadence)
  const SMOOTHING = 0.3      // low-pass filter factor

  let smoothedMag = 9.8
  let lastStepTime = 0
  let wasAbove = false
  let handler = null

  function onMotion(e) {
    if (completed.value) return
    const acc = e.accelerationIncludingGravity
    if (!acc) return

    const rawMag = Math.sqrt(acc.x ** 2 + acc.y ** 2 + acc.z ** 2)

    // Low-pass filter to smooth out noise
    smoothedMag = smoothedMag * (1 - SMOOTHING) + rawMag * SMOOTHING

    const now = Date.now()

    // Peak detection: crossing above threshold, then back below
    if (smoothedMag > STEP_THRESHOLD) {
      if (!wasAbove && now - lastStepTime > STEP_COOLDOWN) {
        wasAbove = true
        lastStepTime = now
        stepCount.value++
        progress.value = Math.min(1, stepCount.value / targetSteps)

        if (stepCount.value >= targetSteps) {
          completed.value = true
          stop()
          onComplete?.()
        }
      }
    } else {
      wasAbove = false
    }
  }

  async function start() {
    const granted = await requestMotionPermission()
    if (!granted) return false

    stepCount.value = 0
    progress.value = 0
    completed.value = false
    smoothedMag = 9.8
    lastStepTime = 0
    wasAbove = false
    isActive.value = true
    handler = onMotion
    window.addEventListener('devicemotion', handler)
    return true
  }

  function stop() {
    isActive.value = false
    if (handler) {
      window.removeEventListener('devicemotion', handler)
      handler = null
    }
  }

  function reset() {
    stop()
    stepCount.value = 0
    progress.value = 0
    completed.value = false
    smoothedMag = 9.8
    wasAbove = false
  }

  onUnmounted(stop)

  return { stepCount, isActive, progress, completed, start, stop, reset }
}