import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const PROGRESS_KEY = 'snaphunter_progress'
const DAILY_TASKS_KEY = 'snaphunter_daily_tasks'
const DAILY_SERIES_KEY = 'snaphunter_daily_series'

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

// ─── Title definitions ─────────────────────────────────────
const TITLE_DEFINITIONS = [
  { id: 'first_timer', name: 'First Timer', requirement: 'Complete first task', unlockBadge: 'first_step' },
  { id: 'nature_explorer', name: 'Nature Explorer', requirement: 'Earn Nature Explorer badge', unlockBadge: 'nature' },
  { id: 'city_scout', name: 'City Scout', requirement: 'Earn City Hunter badge', unlockBadge: 'urban' },
  { id: 'week_warrior', name: 'Week Warrior', requirement: '7-day streak', unlockBadge: 'week_warrior' },
]

function getTodayKey() {
  return new Date().toISOString().slice(0, 10) // "2026-04-24"
}

function getDefaultProgress() {
  return {
    xp: 0,
    totalTasksCompleted: 0,
    totalPhotos: 0,
    parksVisited: 0,
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

  function visitPark() {
    progress.value.parksVisited += 1
    if (progress.value.parksVisited >= 1) earnBadge('park_pioneer')
    save()
  }

  function completeSunnyTask() {
    earnBadge('sun_chaser')
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
  }

  return {
    progress,
    // Computed
    level, xpPercent, xpInCurrentLevel, xpNeededForLevel,
    currentLevelXp, nextLevelXp, levelTitle,
    earnedBadgeSet, unlockedTitles, activeTitle,
    refreshesLeftToday, weekStreakDisplay,
    // Actions
    init, save, addXp, completeTask, addPhoto, visitPark,
    completeSunnyTask, earnBadge, setActiveTitle, useRefresh, resetAll,
    // Constants (export for other views)
    BADGE_DEFINITIONS, TITLE_DEFINITIONS,
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

export function loadDailySeriesTasks(seriesId) {
  try {
    const saved = JSON.parse(localStorage.getItem(DAILY_SERIES_KEY) || 'null')
    if (saved && saved.date === getTodayKey() && saved.seriesId === seriesId) {
      return saved.tasks
    }
  } catch { /* ignore */ }
  return null
}

export function saveDailySeriesTasks(seriesId, tasks) {
  localStorage.setItem(DAILY_SERIES_KEY, JSON.stringify({
    date: getTodayKey(),
    seriesId,
    tasks,
  }))
}