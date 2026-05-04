import axios from 'axios'

const API_BASE = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'
const ANALYTICS_KEY = 'snaphunter_analytics'
const SESSION_KEY = 'snaphunter_session'
const CONSENT_KEY = 'snaphunter_parental_consent'

function hasParentalConsent() {
  return localStorage.getItem(CONSENT_KEY) === 'true'
}

function getUserId() {
  try {
    const user = JSON.parse(localStorage.getItem('snaphunter_user') || 'null')
    return user?.uid || null
  } catch {
    return null
  }
}

function getStoredEvents() {
  try {
    return JSON.parse(localStorage.getItem(ANALYTICS_KEY) || '[]')
  } catch {
    return []
  }
}

function saveEvents(events) {
  const trimmed = events.slice(-500)
  localStorage.setItem(ANALYTICS_KEY, JSON.stringify(trimmed))
}

export function startSession() {
  if (!hasParentalConsent()) return

  const session = {
    startedAt: new Date().toISOString(),
    userId: getUserId(),
  }
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function endSession() {
  if (!hasParentalConsent()) return

  try {
    const session = JSON.parse(localStorage.getItem(SESSION_KEY) || 'null')
    if (!session?.startedAt) return

    const durationMs = Date.now() - new Date(session.startedAt).getTime()
    const durationSec = Math.round(durationMs / 1000)

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

export function trackEvent(eventType, data = {}) {
  if (!hasParentalConsent()) return

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

export async function syncToBackend() {
  if (!hasParentalConsent()) return

  const events = getStoredEvents()
  if (events.length === 0) return

  const userId = getUserId()
  if (!userId) return

  try {
    await axios.post(`${API_BASE}/api/analytics/events`, {
      userId,
      events,
    })

    localStorage.removeItem(ANALYTICS_KEY)
    console.log(`[Analytics] Synced ${events.length} events`)
  } catch (error) {
    console.warn('[Analytics] Sync failed, will retry later', error.message)
  }
}

export async function syncUserProfile() {
  if (!hasParentalConsent()) return

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