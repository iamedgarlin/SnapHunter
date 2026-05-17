import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const PROGRESS_KEY = 'snaphunter_progress'
const DAILY_TASKS_KEY = 'snaphunter_daily_tasks'
const DAILY_SERIES_KEY = 'snaphunter_daily_series'
const DAILY_PARKS_KEY = 'snaphunter_daily_parks'
const ADVENTURE_PROGRESS_KEY = 'snaphunter_adventure_progress'

// ─── Level thresholds ──────────────────────────────────────
// Level 1 = 0 XP, Level 2 = 100 XP, etc.
const LEVEL_THRESHOLDS = [
  0,    // Level 1
  100,  // Level 2
  250,  // Level 3
  450,  // Level 4
  700,  // Level 5
  1000, // Level 6
  1400, // Level 7
  1900, // Level 8
  2500, // Level 9
  3200, // Level 10
]

// ─── Badge / Achievement definitions ───────────────────────
const BADGE_DEFINITIONS = {
  // Series badges
  nature: {
    id: 'nature', type: 'series', name: 'Nature Explorer',
    description: 'Complete all Nature Series tasks in one day',
    howToGet: 'Complete all 5 Nature Series tasks in a single day to earn this badge.',
  },
  urban: {
    id: 'urban', type: 'series', name: 'City Hunter',
    description: 'Complete all Urban Series tasks in one day',
    howToGet: 'Complete all 5 Urban Series tasks in a single day to earn this badge.',
  },
  art: {
    id: 'art', type: 'series', name: 'Art Spotter',
    description: 'Complete all Art Series tasks in one day',
    howToGet: 'Complete all 5 Art Series tasks in a single day to earn this badge.',
  },
  // Epic Park badges
  epic_flinders: {
    id: 'epic_flinders', type: 'epic_park', name: 'Flinders St Station',
    description: 'Complete the Flinders Street Station epic park',
    howToGet: 'Visit and complete all tasks at Flinders Street Station to unlock this badge.',
  },
  epic_fitzroy: {
    id: 'epic_fitzroy', type: 'epic_park', name: 'Fitzroy Garden',
    description: 'Complete the Fitzroy Garden epic park',
    howToGet: 'Visit and complete all tasks at Fitzroy Garden to unlock this badge.',
  },
  epic_greatoceanroad: {
    id: 'epic_greatoceanroad', type: 'epic_park', name: 'Great Ocean Road',
    description: 'Complete the Great Ocean Road epic park',
    howToGet: 'Visit and complete all tasks at Great Ocean Road to unlock this badge.',
  },
  epic_master: {
    id: 'epic_master', type: 'epic_park', name: 'Melbourne Epic Explorer',
    description: 'Complete all Epic Parks to become a true Melbourne explorer!',
    howToGet: 'Unlock all three Epic Park badges (Flinders St Station, Fitzroy Garden, and Great Ocean Road) to earn this ultimate badge.',
  },
  // Achievement badges
  first_step: {
    id: 'first_step', type: 'achievement', name: 'First Step',
    description: 'Complete your very first task',
    howToGet: 'Complete any task for the first time.',
  },
  on_fire: {
    id: 'on_fire', type: 'achievement', name: 'On Fire!',
    description: '3-day streak',
    howToGet: 'Complete at least one task per day for 3 days in a row.',
  },
  snap_happy: {
    id: 'snap_happy', type: 'achievement', name: 'Snap Happy',
    description: 'Submit 10 photos',
    howToGet: 'Take and submit 10 verified photos across any tasks.',
  },
  park_pioneer: {
    id: 'park_pioneer', type: 'achievement', name: 'Park Pioneer',
    description: 'Visit your first park',
    howToGet: 'Navigate to and arrive at any park location on the map.',
  },
  week_warrior: {
    id: 'week_warrior', type: 'achievement', name: 'Week Warrior',
    description: '7-day streak',
    howToGet: 'Complete at least one task per day for 7 days in a row.',
  },
  sun_chaser: {
    id: 'sun_chaser', type: 'achievement', name: 'Sun Chaser',
    description: 'Complete a task on a sunny day',
    howToGet: 'Complete any outdoor task when the weather is sunny (Clear sky).',
  },
}

// All three individual epic park badge ids
const EPIC_PARK_IDS = ['epic_flinders', 'epic_fitzroy', 'epic_greatoceanroad']

// ─── Title definitions ─────────────────────────────────────
const TITLE_DEFINITIONS = [
  { id: 'first_timer', name: 'First Timer', requirement: 'Complete first task', unlockBadge: 'first_step' },
  { id: 'nature_explorer', name: 'Nature Explorer', requirement: 'Earn Nature Explorer badge', unlockBadge: 'nature' },
  { id: 'city_scout', name: 'City Scout', requirement: 'Earn City Hunter badge', unlockBadge: 'urban' },
  { id: 'week_warrior', name: 'Week Warrior', requirement: '7-day streak', unlockBadge: 'week_warrior' },
  { id: 'epic_explorer', name: 'Epic Explorer', requirement: 'Complete all Epic Parks', unlockBadge: 'epic_master' },
]

function getTodayKey() {
  return new Date().toISOString().slice(0, 10) // "2026-04-24"
}

function getDefaultProgress() {
  return {
    xp: 0,
    totalTasksCompleted: 0,
    totalPhotos: 0,
    parksVisited: [],        // array of unique park ids (deduplicated)
    visitedParkRecords: [],  // array of { parkId, parkName, latitude, longitude, visitedAt }
    earnedBadges: [],       // array of badge ids
    activeTitle: null,       // title id or null
    // Streak
    currentStreak: 0,
    bestStreak: 0,
    lastActiveDate: null,    // "2026-04-24"
    streakDays: [],          // last 7 days of activity ["2026-04-23", "2026-04-24"]
    // Daily refresh
    refreshesUsedToday: 0,
    lastRefreshDate: null,
  }
}

export const useProgressStore = defineStore('progress', () => {

  // ─── State ──────────────────────────────────────────────
  const progress = ref(getDefaultProgress())

  // ─── Computed ───────────────────────────────────────────
  const level = computed(() => {
    for (let i = LEVEL_THRESHOLDS.length - 1; i >= 0; i--) {
      if (progress.value.xp >= LEVEL_THRESHOLDS[i]) return i + 1
    }
    return 1
  })

  const currentLevelXp = computed(() => {
    const lvl = level.value
    return LEVEL_THRESHOLDS[lvl - 1] || 0
  })

  const nextLevelXp = computed(() => {
    const lvl = level.value
    if (lvl >= LEVEL_THRESHOLDS.length) return LEVEL_THRESHOLDS[LEVEL_THRESHOLDS.length - 1] + 500
    return LEVEL_THRESHOLDS[lvl]
  })

  const xpInCurrentLevel = computed(() =>
    progress.value.xp - currentLevelXp.value
  )

  const xpNeededForLevel = computed(() =>
    nextLevelXp.value - currentLevelXp.value
  )

  const xpPercent = computed(() => {
    if (xpNeededForLevel.value <= 0) return 100
    return Math.min(100, Math.round((xpInCurrentLevel.value / xpNeededForLevel.value) * 100))
  })

  const levelTitle = computed(() => {
    const lvl = level.value
    if (lvl <= 1) return 'Beginner'
    if (lvl <= 2) return 'Rookie'
    if (lvl <= 3) return 'Explorer'
    if (lvl <= 5) return 'Adventurer'
    if (lvl <= 7) return 'Hunter'
    if (lvl <= 9) return 'Master'
    return 'Legend'
  })

  const earnedBadgeSet = computed(() =>
    new Set(progress.value.earnedBadges)
  )

  const unlockedTitles = computed(() =>
    TITLE_DEFINITIONS.filter(t => earnedBadgeSet.value.has(t.unlockBadge))
  )

  const activeTitle = computed(() => {
    if (!progress.value.activeTitle) return null
    const t = TITLE_DEFINITIONS.find(d => d.id === progress.value.activeTitle)
    // Only show if actually unlocked
    if (t && earnedBadgeSet.value.has(t.unlockBadge)) return t
    return null
  })

  const refreshesLeftToday = computed(() => {
    if (progress.value.lastRefreshDate !== getTodayKey()) return 3
    return Math.max(0, 3 - progress.value.refreshesUsedToday)
  })

  const parksVisitedCount = computed(() => {
    // Handle legacy number format
    if (typeof progress.value.parksVisited === 'number') return progress.value.parksVisited
    return Array.isArray(progress.value.parksVisited) ? progress.value.parksVisited.length : 0
  })

  // All visited park records (rich objects), most recent first
  const visitedParkRecords = computed(() => {
    const recs = Array.isArray(progress.value.visitedParkRecords)
      ? progress.value.visitedParkRecords
      : []
    return [...recs].sort((a, b) => (b.visitedAt || 0) - (a.visitedAt || 0))
  })

  // Number of distinct parks visited today (used for "0/3 done" style chip)
  const parksVisitedTodayCount = computed(() => {
    const today = getTodayKey()
    const recs = Array.isArray(progress.value.visitedParkRecords)
      ? progress.value.visitedParkRecords
      : []
    const ids = new Set()
    for (const r of recs) {
      if (r.visitedAt && new Date(r.visitedAt).toISOString().slice(0, 10) === today) {
        ids.add(String(r.parkId))
      }
    }
    return ids.size
  })

  // ─── Week streak display ────────────────────────────────
  const weekStreakDisplay = computed(() => {
    const labels = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    const today = new Date()
    const dayOfWeek = today.getDay() // 0=Sun
    // Monday = index 0
    const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek
    const monday = new Date(today)
    monday.setDate(today.getDate() + mondayOffset)

    const activeDays = new Set(progress.value.streakDays || [])

    return labels.map((label, i) => {
      const d = new Date(monday)
      d.setDate(monday.getDate() + i)
      const key = d.toISOString().slice(0, 10)
      return { label, done: activeDays.has(key), dateKey: key }
    })
  })

  // ─── Actions ────────────────────────────────────────────

  function init() {
    const saved = localStorage.getItem(PROGRESS_KEY)
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        progress.value = { ...getDefaultProgress(), ...parsed }
      } catch {
        // corrupted data, start fresh
      }
    }
    // Migrate legacy parksVisited from number to array
    if (typeof progress.value.parksVisited === 'number') {
      progress.value.parksVisited = []
    }
    // Ensure visitedParkRecords exists (for users with older saved data)
    if (!Array.isArray(progress.value.visitedParkRecords)) {
      progress.value.visitedParkRecords = []
    }
    // Check if day changed and reset refresh counter
    if (progress.value.lastRefreshDate !== getTodayKey()) {
      progress.value.refreshesUsedToday = 0
      progress.value.lastRefreshDate = getTodayKey()
      save()
    }
  }

  function save() {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(progress.value))
  }

  function addXp(amount) {
    progress.value.xp += amount
    save()
  }

  function completeTask(xpReward = 10) {
    const today = getTodayKey()

    progress.value.xp += xpReward
    progress.value.totalTasksCompleted += 1

    // Update streak
    updateStreak(today)

    // Check for first_step badge
    if (progress.value.totalTasksCompleted === 1) {
      earnBadge('first_step')
    }

    // Check for streak badges
    if (progress.value.currentStreak >= 3) earnBadge('on_fire')
    if (progress.value.currentStreak >= 7) earnBadge('week_warrior')

    save()
  }

  function addPhoto() {
    progress.value.totalPhotos += 1
    if (progress.value.totalPhotos >= 10) earnBadge('snap_happy')
    save()
  }

  /**
   * Record a park visit. Deduplicates by parkId so the same park
   * only counts once no matter how many times the user visits.
   * @param {number|string} parkId - unique park identifier
   */
  function visitPark(parkId) {
    if (!parkId) return
    const id = String(parkId)
    // Migrate legacy number format to array
    if (!Array.isArray(progress.value.parksVisited)) {
      progress.value.parksVisited = []
    }
    if (progress.value.parksVisited.includes(id)) return // already counted
    progress.value.parksVisited.push(id)
    if (progress.value.parksVisited.length >= 1) earnBadge('park_pioneer')
    save()
  }

  /**
   * Record a REAL park visit (the user physically arrived, verified by
   * GPS proximity). This is the single source of truth for the "visited"
   * state shown in the Tasks "Parks Series", the map gray->green pins and
   * the Home "x/3 done" counter. Do NOT call this on Navigate / Start
   * Adventure taps — those are intent, not arrival.
   * Deduplicates by parkId — the same park keeps one record, but the
   * visitedAt timestamp refreshes on each real re-visit.
   * @param {{parkId:(number|string), parkName?:string, latitude?:number, longitude?:number}} park
   */
  function recordParkVisit(park) {
    if (!park || park.parkId == null) return
    const id = String(park.parkId)

    // Keep the lightweight id list + park_pioneer badge behaviour
    visitPark(id)

    if (!Array.isArray(progress.value.visitedParkRecords)) {
      progress.value.visitedParkRecords = []
    }
    const now = Date.now()
    const existing = progress.value.visitedParkRecords.find(r => String(r.parkId) === id)
    if (existing) {
      existing.visitedAt = now
      // Backfill any missing metadata on re-visit
      if (park.parkName) existing.parkName = park.parkName
      if (park.latitude != null) existing.latitude = park.latitude
      if (park.longitude != null) existing.longitude = park.longitude
    } else {
      progress.value.visitedParkRecords.push({
        parkId: id,
        parkName: park.parkName || 'Unknown Park',
        latitude: park.latitude ?? null,
        longitude: park.longitude ?? null,
        visitedAt: now,
      })
    }
    save()
  }

  function completeSunnyTask() {
    earnBadge('sun_chaser')
    save()
  }

  /**
   * Call when an epic park is completed.
   * @param {'epic_flinders' | 'epic_fitzroy' | 'epic_greatoceanroad'} epicParkId
   * @param {number} xpReward - XP to award (default 50)
   */
  function completeEpicPark(epicParkId, xpReward = 50) {
    // Award the individual epic park badge
    earnBadge(epicParkId)
    progress.value.xp += xpReward

    // Check if all three epic parks are now completed
    const allDone = EPIC_PARK_IDS.every(id =>
      progress.value.earnedBadges.includes(id)
    )
    if (allDone) {
      earnBadge('epic_master')
    }

    save()
  }

  function earnBadge(badgeId) {
    if (!progress.value.earnedBadges.includes(badgeId)) {
      progress.value.earnedBadges.push(badgeId)
      save()
    }
  }

  function setActiveTitle(titleId) {
    progress.value.activeTitle = titleId
    save()
  }

  function updateStreak(today) {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    const yesterdayKey = yesterday.toISOString().slice(0, 10)

    if (progress.value.lastActiveDate === today) {
      // Already active today, no streak change
    } else if (progress.value.lastActiveDate === yesterdayKey) {
      // Consecutive day
      progress.value.currentStreak += 1
    } else {
      // Streak broken or first day
      progress.value.currentStreak = 1
    }

    progress.value.lastActiveDate = today
    progress.value.bestStreak = Math.max(progress.value.bestStreak, progress.value.currentStreak)

    // Track last 7 active dates
    if (!progress.value.streakDays) progress.value.streakDays = []
    if (!progress.value.streakDays.includes(today)) {
      progress.value.streakDays.push(today)
    }
    // Keep only last 14 days
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - 14)
    const cutoffKey = cutoff.toISOString().slice(0, 10)
    progress.value.streakDays = progress.value.streakDays.filter(d => d >= cutoffKey)
  }

  function useRefresh() {
    const today = getTodayKey()
    if (progress.value.lastRefreshDate !== today) {
      progress.value.refreshesUsedToday = 0
      progress.value.lastRefreshDate = today
    }
    if (progress.value.refreshesUsedToday >= 3) return false
    progress.value.refreshesUsedToday += 1
    save()
    return true
  }

  function resetAll() {
    progress.value = getDefaultProgress()
    localStorage.removeItem(PROGRESS_KEY)
    localStorage.removeItem(DAILY_TASKS_KEY)
    localStorage.removeItem(DAILY_SERIES_KEY)
    localStorage.removeItem(DAILY_PARKS_KEY)
    localStorage.removeItem(ADVENTURE_PROGRESS_KEY)
    // Permanent completed-task set (COMPLETED_TASKS_KEY, defined at
    // module scope below — literal kept in sync with that constant).
    localStorage.removeItem('snaphunter_completed_tasks')
  }

  return {
    progress,
    // Computed
    level, xpPercent, xpInCurrentLevel, xpNeededForLevel,
    currentLevelXp, nextLevelXp, levelTitle,
    earnedBadgeSet, unlockedTitles, activeTitle,
    refreshesLeftToday, weekStreakDisplay, parksVisitedCount,
    visitedParkRecords, parksVisitedTodayCount,
    // Actions
    init, save, addXp, completeTask, addPhoto, visitPark, recordParkVisit,
    completeSunnyTask, completeEpicPark, earnBadge, setActiveTitle,
    useRefresh, resetAll,
    // Constants (export for other views)
    BADGE_DEFINITIONS, TITLE_DEFINITIONS, EPIC_PARK_IDS,
  }
})

// ─── Daily tasks persistence ────────────────────────────────

export function loadDailyTasks() {
  try {
    const saved = JSON.parse(localStorage.getItem(DAILY_TASKS_KEY) || 'null')
    if (saved && saved.date === getTodayKey()) {
      return saved.tasks
    }
  } catch { /* ignore */ }
  return null
}

export function saveDailyTasks(tasks) {
  localStorage.setItem(DAILY_TASKS_KEY, JSON.stringify({
    date: getTodayKey(),
    tasks,
  }))
}

// ─── Daily parks persistence (Today's Park) ─────────────────
// Same model as daily tasks: cached per day, auto-refreshes when
// the date key rolls over (i.e. at 00:00).

export function loadDailyParks() {
  try {
    const saved = JSON.parse(localStorage.getItem(DAILY_PARKS_KEY) || 'null')
    if (saved && saved.date === getTodayKey()) {
      return saved.parks
    }
  } catch { /* ignore */ }
  return null
}

export function saveDailyParks(parks) {
  localStorage.setItem(DAILY_PARKS_KEY, JSON.stringify({
    date: getTodayKey(),
    parks,
  }))
}

export function loadDailySeriesTasks(seriesId) {
  try {
    const key = `${DAILY_SERIES_KEY}_${seriesId}`
    const saved = JSON.parse(localStorage.getItem(key) || 'null')
    if (saved && saved.date === getTodayKey()) {
      return saved.tasks
    }
  } catch { /* ignore */ }
  return null
}

export function saveDailySeriesTasks(seriesId, tasks) {
  const key = `${DAILY_SERIES_KEY}_${seriesId}`
  localStorage.setItem(key, JSON.stringify({
    date: getTodayKey(),
    seriesId,
    tasks,
  }))
}

// ─── Park Adventure progress persistence ────────────────────
// Persists in-progress trail state so the user can leave the
// Park Adventure view and come back without redoing waypoints.
// Keyed by `${parkId}-${routeId}` so different trails are independent.
// Not date-scoped — an adventure can legitimately span more than one day.

function adventureKey(parkId, routeId) {
  return `${parkId}::${routeId}`
}

/**
 * Save the current adventure state.
 * @param {number|string} parkId
 * @param {number|string} routeId
 * @param {object} state - { parkName, route, waypoints, pathSegments, currentWpIndex, earnedXp }
 */
export function saveAdventureProgress(parkId, routeId, state) {
  if (parkId == null || routeId == null) return
  let all = {}
  try {
    all = JSON.parse(localStorage.getItem(ADVENTURE_PROGRESS_KEY) || '{}') || {}
  } catch { all = {} }
  all[adventureKey(parkId, routeId)] = {
    parkId: String(parkId),
    routeId: String(routeId),
    savedAt: Date.now(),
    ...state,
  }
  localStorage.setItem(ADVENTURE_PROGRESS_KEY, JSON.stringify(all))
}

/**
 * Load a saved adventure for a given park+route, or null if none.
 */
export function loadAdventureProgress(parkId, routeId) {
  if (parkId == null || routeId == null) return null
  try {
    const all = JSON.parse(localStorage.getItem(ADVENTURE_PROGRESS_KEY) || '{}') || {}
    return all[adventureKey(parkId, routeId)] || null
  } catch {
    return null
  }
}

/**
 * Return the most recent unfinished saved adventure for a park
 * (any route), so we can offer "continue where you left off"
 * even before the user picks a route again. Null if none.
 */
export function loadLatestAdventureForPark(parkId) {
  if (parkId == null) return null
  try {
    const all = JSON.parse(localStorage.getItem(ADVENTURE_PROGRESS_KEY) || '{}') || {}
    const matches = Object.values(all)
      .filter(a => String(a.parkId) === String(parkId))
      .filter(a => Array.isArray(a.waypoints) && !a.waypoints.every(w => w.completed))
      .sort((a, b) => (b.savedAt || 0) - (a.savedAt || 0))
    return matches[0] || null
  } catch {
    return null
  }
}

/**
 * Clear a saved adventure (called when the trail is fully completed
 * or the user explicitly abandons it).
 */
export function clearAdventureProgress(parkId, routeId) {
  if (parkId == null || routeId == null) return
  try {
    const all = JSON.parse(localStorage.getItem(ADVENTURE_PROGRESS_KEY) || '{}') || {}
    delete all[adventureKey(parkId, routeId)]
    localStorage.setItem(ADVENTURE_PROGRESS_KEY, JSON.stringify(all))
  } catch { /* ignore */ }
}

// ─── Permanent completed-task set ───────────────────────────
// Single source of truth for which Series tasks are done. A task is
// the same backend entity wherever it's completed (Tasks page photo
// OR a Park Adventure route photo waypoint, since the waypoint's id
// IS the backend taskId), so completion is recorded here by taskId.
//
// Deliberately NOT date-scoped: a finished Series task stays finished
// forever, like a badge. This is independent of SERIES_TASKS_KEY,
// which only caches the task LIST for the day (saves a fetch) and
// gets its `done` flags overwritten from this set on read. Decoupling
// the two means completion survives the daily list refresh and does
// not depend on whether the route or the Tasks page ran first.

const COMPLETED_TASKS_KEY = 'snaphunter_completed_tasks'

/**
 * Return the set of completed task ids (as strings) for O(1) lookup.
 * @returns {Set<string>}
 */
export function loadCompletedTaskIds() {
  try {
    const arr = JSON.parse(localStorage.getItem(COMPLETED_TASKS_KEY) || '[]')
    return new Set(Array.isArray(arr) ? arr.map(String) : [])
  } catch {
    return new Set()
  }
}

/**
 * Mark a task as permanently completed. Idempotent — calling it again
 * for an already-completed task is a no-op. Returns true only the
 * first time a given task is recorded (useful for one-shot side
 * effects like awarding XP), false if it was already done.
 * @param {number|string} taskId
 * @returns {boolean} true if this call newly completed the task
 */
export function markTaskCompleted(taskId) {
  if (taskId == null) return false
  const id = String(taskId)
  const set = loadCompletedTaskIds()
  if (set.has(id)) return false
  set.add(id)
  try {
    localStorage.setItem(COMPLETED_TASKS_KEY, JSON.stringify([...set]))
  } catch { /* ignore */ }
  return true
}