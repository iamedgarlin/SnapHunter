import axios from 'axios'

const API_BASE = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'
const ANALYTICS_KEY = 'snaphunter_analytics'
const SESSION_KEY = 'snaphunter_session'

/**
 * Get current user uid from localStorage
 */
function getUserId() {
  try {
    const user = JSON.parse(localStorage.getItem('snaphunter_user') || 'null')
    return user?.uid || null
  } catch {
    return null
  }
}

/**
 * Get stored analytics events
 */
function getStoredEvents() {
  try {
    return JSON.parse(localStorage.getItem(ANALYTICS_KEY) || '[]')
  } catch {
    return []
  }
}

/**
 * Save analytics events to localStorage
 */
function saveEvents(events) {
  // Keep max 500 events to avoid localStorage overflow
  const trimmed = events.slice(-500)
  localStorage.setItem(ANALYTICS_KEY, JSON.stringify(trimmed))
}

// ─── Session tracking ───────────────────────────────────────

/**
 * Start a new app session (call on app mount / page visible)
 */
export function startSession() {
  const session = {
    startedAt: new Date().toISOString(),
    userId: getUserId(),
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

/**
 * End the current session and record duration
 * (call on page hide / beforeunload)
 */
export function endSession() {
  try {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null')
    if (!session?.startedAt) return

    const durationMs = Date.now() - new Date(session.startedAt).getTime()
    const durationSec = Math.round(durationMs / 1000)

    // Only record sessions longer than 3 seconds
    if (durationSec > 3) {
      trackEvent('session_end', {
        startedAt: session.startedAt,
        endedAt: new Date().toISOString(),
        durationSec,
      })
    }

    localStorage.removeItem(SESSION_KEY)
  } catch {
    // ignore
  }
}

// ─── Event tracking ─────────────────────────────────────────

/**
 * Track a single analytics event
 * @param {'task_start'|'task_complete'|'session_end'|'photo_taken'|'page_view'} eventType
 * @param {object} data - event-specific data
 */
export function trackEvent(eventType, data = {}) {
  const userId = getUserId()
  if (!userId) return

  const event = {
    userId,
    eventType,
    timestamp: new Date().toISOString(),
    ...data,
  }

  const events = getStoredEvents()
  events.push(event)
  saveEvents(events)
}

// ─── Sync to backend ────────────────────────────────────────

/**
 * Flush all stored events to backend API
 * Call this periodically or on key moments (task complete, session end)
 */
export async function syncToBackend() {
  const events = getStoredEvents()
  if (events.length === 0) return

  const userId = getUserId()
  if (!userId) return

  try {
    await axios.post(`${API_BASE}/api/analytics/events`, {
      userId,
      events,
    })

    // Clear synced events on success
    localStorage.removeItem(ANALYTICS_KEY)
    console.log(`[Analytics] Synced ${events.length} events`)
  } catch (error) {
    // Keep events in localStorage, will retry next time
    console.warn('[Analytics] Sync failed, will retry later', error.message)
  }
}

/**
 * Sync user profile to backend (call on first login)
 */
export async function syncUserProfile() {
  const userId = getUserId()
  if (!userId) return

  try {
    const user = JSON.parse(localStorage.getItem('snaphunter_user') || 'null')
    if (!user) return

    await axios.post(`${API_BASE}/api/analytics/user`, {
      userId: user.uid,
      nickname: user.nickname,
      createdAt: user.createdAt,
    })

    console.log('[Analytics] User profile synced')
  } catch (error) {
    console.warn('[Analytics] User sync failed', error.message)
  }
}