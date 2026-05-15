<template>
  <div class="explore-root" style="font-family: var(--font-game)">

    <!-- Top bar -->
    <div class="explore-topbar">
      <button class="topbar-back" @click="handleExit">
        <PhArrowLeft :size="18" weight="bold" color="#16a34a" />
      </button>
      <div class="topbar-story">
        <p class="topbar-title">{{ storyData.title }}</p>
        <p class="topbar-park">{{ storyData.parkName }}</p>
      </div>
      <div class="topbar-progress" @click="mockSuccess" title="Debug: skip task">
        <span class="topbar-progress-text">{{ completedCount }}/{{ storyData.tasks.length }}</span>
      </div>
    </div>

    <!-- Progress dots -->
    <div class="progress-dots">
      <template v-for="(task, i) in storyData.tasks" :key="task.id">
        <div class="progress-dot" :class="{
          'dot-completed': task.completed,
          'dot-active': i === currentTaskIndex && !allCompleted,
          'dot-locked': i > currentTaskIndex && !task.completed
        }" @click="jumpToTask(i)">
          <PhCheck v-if="task.completed" :size="10" weight="bold" color="white" />
          <PhLock v-else-if="i > currentTaskIndex" :size="8" weight="bold" color="#cbd5e1" />
          <span v-else class="dot-num">{{ i + 1 }}</span>
        </div>
        <div v-if="i < storyData.tasks.length - 1" class="progress-line" :class="{ 'line-done': task.completed }" />
      </template>
    </div>

    <!-- Main stage: owl + task name -->
    <div class="explore-main-stage">

      <!-- Eye rest overlay (inside stage) -->
      <div v-if="showEyeRest" class="eye-rest-stage">
        <div class="eye-rest-ring">
          <svg viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#e2e8f0" stroke-width="8" />
            <circle cx="60" cy="60" r="52" fill="none" stroke="#10b981" stroke-width="8" stroke-linecap="round"
              :stroke-dasharray="2 * Math.PI * 52" :stroke-dashoffset="2 * Math.PI * 52 * (1 - eyeRestProgress)"
              style="transition: stroke-dashoffset 1s linear; transform: rotate(-90deg); transform-origin: center" />
          </svg>
          <div class="eye-rest-number">{{ eyeRestSeconds }}</div>
        </div>
        <PhEye :size="22" weight="duotone" color="#10b981" />
        <p class="eye-rest-label">Look at the farthest tree!</p>
      </div>

      <!-- Celebration state -->
      <div v-else-if="allCompleted && isExploring" class="celebration-stage">
        <div class="confetti-wrap">
          <div v-for="n in 20" :key="n" class="confetti-piece"
            :style="`left:${Math.random() * 100}%;animation-delay:${Math.random() * 2}s;background:${['#f59e0b', '#16a34a', '#7c3aed', '#ef4444', '#3b82f6'][n % 5]}`" />
        </div>
        <PhTrophy :size="48" weight="duotone" color="#f59e0b" />
        <p class="celebration-title">Amazing, {{ userName }}!</p>
        <p class="celebration-sub">You found all {{ storyData.tasks.length }} Time Fragments!</p>
        <div class="celebration-xp">
          <PhLightning :size="16" weight="duotone" color="#f59e0b" />
          <span>+{{ totalXp }} XP earned</span>
        </div>
        <button class="btn-game celebration-btn" @click="handleExit">
          <PhArrowLeft :size="14" weight="bold" color="white" />
          <span>Back to Map</span>
        </button>
      </div>

      <!-- Owl (normal state) -->
      <template v-else>
        <div class="owl-celebration" :class="{ 'speaking': isOwlTalking, 'listening': isListening && !isOwlTalking }">
          <div class="owl-body-big">
            <div class="owl-ears">
              <div class="owl-ear left" />
              <div class="owl-ear right" />
            </div>
            <div class="owl-eyes-big">
              <div class="owl-eye-big">
                <div class="owl-pupil-big" />
              </div>
              <div class="owl-eye-big">
                <div class="owl-pupil-big" />
              </div>
            </div>
            <div class="owl-beak-big" :class="{ 'beak-open': isOwlTalking }" />
          </div>
          <!-- Listening pulse rings -->
          <div v-if="isListening && !isOwlTalking" class="listen-rings">
            <div class="listen-ring r1" />
            <div class="listen-ring r2" />
            <div class="listen-ring r3" />
          </div>
        </div>
        <!-- Current task label -->
        <div v-if="isExploring && !allCompleted" class="task-label-pill">
          <PhMapPin :size="12" weight="duotone" color="#16a34a" />
          <span>{{ currentTask?.name }}</span>
        </div>
      </template>
    </div>

    <!-- Transcript area -->
    <div class="transcript-area">
      <p class="transcript-text" v-if="currentTranscript">{{ currentTranscript }}</p>
      <p class="transcript-placeholder" v-else-if="isExploring">Ollie is listening...</p>
      <p class="transcript-placeholder" v-else>Tap "Start Exploring" to begin!</p>
    </div>

    <!-- Education drawer (bottom swipe) -->
    <div v-if="currentTask && isExploring && !allCompleted && !showEyeRest" class="education-drawer"
      :class="{ 'drawer-open': isDrawerOpen }">
      <div class="drawer-handle" @click="toggleDrawer">
        <div class="drawer-handle-bar" />
        <span>{{ isDrawerOpen ? 'Tap to hide' : 'Need a hint? Swipe up' }}</span>
      </div>
      <div class="drawer-content">
        <!-- Reference photo -->
        <div v-if="currentTask.refPhotoUrl" class="drawer-photo" @click="expandedPhoto = currentTask.refPhotoUrl">
          <img :src="currentTask.refPhotoUrl" :alt="currentTask.name" />
          <div class="drawer-photo-label">
            <PhMagnifyingGlass :size="10" weight="bold" color="white" />
            <span>{{ currentTask.refPhoto }}</span>
          </div>
        </div>
        <!-- Edu cards scroll -->
        <div v-if="currentTask.eduCards?.length" class="drawer-edu-scroll">
          <div v-for="card in currentTask.eduCards" :key="card.id" class="drawer-edu-card"
            :style="`border-color: ${card.color}25; background: ${card.color}08`">
            <p class="drawer-edu-title" :style="`color: ${card.color}`">{{ card.title }}</p>
            <p class="drawer-edu-desc">{{ card.desc }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Audio bar -->
    <div class="audio-bar">
      <div class="audio-left-section">
        <div class="audio-dot" :class="wsState" />
        <span class="audio-label">{{ wsStatusText }}</span>
      </div>

      <!-- Start button (before exploring) -->
      <button v-if="!isExploring" class="btn-game start-btn" @click="startExploring">
        <PhPlay :size="14" weight="fill" color="white" />
        <span>Start Exploring</span>
      </button>

      <!-- Mic button + waveform (while exploring) -->
      <div v-else class="mic-section">
        <!-- Audio waveform visualizer -->
        <div class="waveform" v-if="isListening || isOwlTalking">
          <div v-for="n in 7" :key="n" class="wave-bar" :class="{ 'wave-active': isListening || isOwlTalking }"
            :style="`animation-delay: ${n * 0.08}s; background: ${isOwlTalking ? '#f59e0b' : '#16a34a'}`" />
        </div>
        <button class="audio-mic-btn" :class="{ 'mic-active': isListening }" @click="toggleMic">
          <PhMicrophone v-if="isListening" :size="20" weight="duotone" color="white" />
          <PhMicrophoneSlash v-else :size="20" weight="duotone" color="#94a3b8" />
        </button>
      </div>
    </div>

    <!-- Expanded photo modal -->
    <Transition name="fade">
      <div v-if="expandedPhoto" class="photo-modal" @click="expandedPhoto = null">
        <img :src="expandedPhoto" class="photo-modal-img" />
        <p class="photo-modal-hint">Tap anywhere to close</p>
      </div>
    </Transition>

  </div>

  <!-- Onboarding -->
  <Teleport to="body">
    <div v-if="showOb" class="fixed inset-0 z-[999]" @click="nextOb">
      <div class="absolute inset-0 bg-black/50"></div>
      <div v-if="obStep === 0" class="ob-card-explore" style="top: 14%; left: 50%; transform: translateX(-50%);">
        <div class="flex items-center gap-2 mb-2">
          <PhCastleTurret :size="20" weight="duotone" color="#7c3aed" />
          <p class="text-base font-black text-gray-800">Epic Park Story</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Welcome to an Epic Park! The owl guide will tell you a story and ask quiz questions. Answer correctly to earn
          bonus XP and unlock Epic Park badges.
        </p>
        <div class="ob-arrow-down-e"></div>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">1 / 2</span>
          <button class="ob-next-e" @click.stop="nextOb">Next</button>
        </div>
      </div>
      <div v-if="obStep === 1" class="ob-card-explore" style="bottom: 20%; left: 50%; transform: translateX(-50%);">
        <div class="flex items-center gap-2 mb-2">
          <PhMicrophone :size="20" weight="duotone" color="#10b981" />
          <p class="text-base font-black text-gray-800">Talk to the Owl</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Tap the answer buttons or use the microphone to speak your answers. Between questions, take an eye rest break
          by
          looking into the distance!
        </p>
        <div class="ob-arrow-down-e"></div>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">2 / 2</span>
          <button class="ob-next-e" @click.stop="nextOb">Let's go!</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProgressStore } from '../stores/progress'
import { trackEvent } from '../services/analytics'
import { GeminiLive } from '../services/geminiLive'
import {
  PhArrowLeft, PhArrowRight, PhCheck, PhLock, PhMicrophone, PhMicrophoneSlash,
  PhImage, PhMapPin, PhMagnifyingGlass, PhPlay, PhEye,
  PhTrophy, PhLightning, PhScroll, PhPaintBrush, PhPlus, PhBird, PhCastleTurret
} from '@phosphor-icons/vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const progressStore = useProgressStore()

const EXPLORE_KEY = 'snaphunter_epic_progress'
const userName = computed(() => authStore.user?.nickname || 'Explorer')

// ─── Park ID → Badge ID mapping ────────────────────────────
// Maps the numeric parkId from the API to the badge id in progress store
const PARK_TO_BADGE = {
  1: 'epic_flinders',
  2: 'epic_fitzroy',
  3: 'epic_greatoceanroad',
}

// ─── Story Data ──────────────────────────────────────────────
// Future: fetch from API by parkId
const storyData = ref({
  parkId: 2,
  parkName: 'Fitzroy Gardens',
  title: 'The Time Fragments',
  tasks: [
    {
      id: 'scar-tree',
      name: 'Secret of the Ancient Tree',
      refPhoto: 'Scarred Tree Trunk',
      refPhotoUrl: 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=400&h=200&fit=crop',
      xp: 30,
      eyeRestSec: 20,
      completed: false,
      eduCards: [
        { id: 'history', color: '#b45309', title: 'Aboriginal Heritage', desc: 'Indigenous Australians used bark from trees to build canoes and shelters for thousands of years.' },
        { id: 'shape', color: '#7c3aed', title: 'Shape Hunt', desc: 'The scar is long and oval-shaped, just like the canoe it became!' },
      ],
    },
    {
      id: 'tudor-village',
      name: 'Counting in Tiny Town',
      refPhoto: 'Model Tudor Village',
      refPhotoUrl: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=200&fit=crop',
      xp: 35,
      eyeRestSec: 20,
      completed: false,
      eduCards: [
        { id: 'colors', color: '#dc2626', title: 'Color Guide', desc: 'RED roofs look bright and warm. Can you tell red apart from brown and orange?' },
        { id: 'math', color: '#2563eb', title: 'Math Challenge', desc: '5 red roofs + 3 brown roofs = 8 roofs total!' },
        { id: 'history', color: '#b45309', title: 'History', desc: 'This tiny village was a gift to Melbourne after World War II, built brick by tiny brick!' },
      ],
    },
    {
      id: 'fairies-tree',
      name: 'The Animal Party',
      refPhoto: "Fairies' Tree Carvings",
      refPhotoUrl: 'https://images.unsplash.com/photo-1518882460567-78ef8e3e7e32?w=400&h=200&fit=crop',
      xp: 30,
      eyeRestSec: 20,
      completed: false,
      eduCards: [
        { id: 'animals', color: '#16a34a', title: 'Aussie Animals', desc: 'Look for koalas, possums, kookaburras, and fairy wrens carved into the bark!' },
        { id: 'art', color: '#7c3aed', title: 'Art Fact', desc: 'Sculptor Ola Cohn carved these figures in the 1930s on a 300-year-old tree stump.' },
      ],
    },
    {
      id: 'cooks-cottage',
      name: 'The Travelling House',
      refPhoto: "Captain Cook's Cottage",
      refPhotoUrl: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=200&fit=crop',
      xp: 35,
      eyeRestSec: 20,
      completed: false,
      eduCards: [
        { id: 'geo', color: '#2563eb', title: 'Geography', desc: 'England is over 16,000 km from Melbourne! The bricks traveled by ship for months.' },
        { id: 'math', color: '#16a34a', title: 'Big Numbers', desc: '253 crates × 50 kg each = 12,650 kg total! That is heavier than 2 elephants!' },
      ],
    },
  ],
})

// ─── State ───────────────────────────────────────────────────
const currentTaskIndex = ref(0)
const isExploring = ref(false)

// Onboarding
const OB_KEY = 'snaphunter_explore_onboarded'
const showOb = ref(false)
const obStep = ref(0)
function nextOb() {
  if (obStep.value < 1) { obStep.value++ } else { showOb.value = false; localStorage.setItem(OB_KEY, 'true') }
}
const isOwlTalking = ref(false)
const isListening = ref(false)
const isDrawerOpen = ref(false)
const wsState = ref('disconnected')
const currentTranscript = ref('')
const expandedPhoto = ref(null)

// Eye rest
const showEyeRest = ref(false)
const eyeRestSeconds = ref(20)
const eyeRestProgress = ref(0)
let eyeRestTimer = null
let gemini = null
let hasGreeted = false

// Track whether epic badge has already been awarded this session
// to prevent duplicate awards if celebration triggers multiple times
let epicBadgeAwarded = false

// ─── Computed ────────────────────────────────────────────────
const currentTask = computed(() => storyData.value.tasks[currentTaskIndex.value])
const completedCount = computed(() => storyData.value.tasks.filter(t => t.completed).length)
const allCompleted = computed(() => storyData.value.tasks.every(t => t.completed))
const totalXp = computed(() => storyData.value.tasks.reduce((sum, t) => sum + t.xp, 0))

const wsStatusText = computed(() => {
  if (wsState.value === 'connecting') return 'Connecting to Ollie...'
  if (wsState.value === 'connected') return isOwlTalking.value ? 'Ollie is talking' : isListening.value ? 'Listening...' : 'Mic off'
  return 'Ready to explore'
})

// ─── Persistence ─────────────────────────────────────────────
function loadProgress() {
  try {
    const saved = JSON.parse(localStorage.getItem(`${EXPLORE_KEY}_${storyData.value.parkId}`) || 'null')
    if (saved?.completedTasks) {
      const doneSet = new Set(saved.completedTasks)
      storyData.value.tasks.forEach(t => {
        if (doneSet.has(t.id)) t.completed = true
      })
      const firstIncomplete = storyData.value.tasks.findIndex(t => !t.completed)
      currentTaskIndex.value = firstIncomplete >= 0 ? firstIncomplete : storyData.value.tasks.length - 1
    }
  } catch { /* ignore */ }
}

function saveProgress() {
  const completedTasks = storyData.value.tasks.filter(t => t.completed).map(t => t.id)
  localStorage.setItem(`${EXPLORE_KEY}_${storyData.value.parkId}`, JSON.stringify({ completedTasks }))
}

// ─── System Prompt Builder ───────────────────────────────────

function buildSystemPrompt() {
  const tasksJson = storyData.value.tasks.map(t => ({
    id: t.id,
    name: t.name,
    completed: t.completed,
    eduCards: t.eduCards?.map(c => c.desc) || [],
  }))

  return `You are Ollie the Owl, a friendly and enthusiastic voice guide for children aged 5-12.
You are leading a child named "${userName.value}" through an outdoor scavenger hunt called "The Time Fragments" at ${storyData.value.parkName}.

RULES:
- Speak in short, simple sentences (2-3 at a time), then wait for the child to respond
- Be warm, encouraging, and playful like a fun teacher
- For each task, describe what the child should look for, then ask the question
- When the child answers CORRECTLY, call update_task_progress with the taskId and nextAction "eye_rest"
- If the child answers WRONG, give a gentle hint and let them try again (max 3 hints, then reveal answer)
- Never reveal the answer on the first wrong attempt
- For the LAST task (${storyData.value.tasks[storyData.value.tasks.length - 1].id}), use nextAction "celebration" instead of "eye_rest"
- After eye rest, the app automatically advances. Then introduce the next task naturally.
- Do NOT talk about screen time, myopia, or health. Focus on fun exploration and learning.
- If the child goes off topic, gently guide them back

TASKS (complete them in order):
${JSON.stringify(tasksJson, null, 2)}

Current task index: ${currentTaskIndex.value}

Start by greeting ${userName.value} warmly and introducing the first uncompleted task.`
}

// ─── Logic ───────────────────────────────────────────────────

function startExploring() {
  isExploring.value = true
  hasGreeted = false

  gemini = new GeminiLive({
    onStateChange: (state) => {
      if (state === 'connecting') {
        wsState.value = 'connecting'
      } else if (state === 'listening') {
        wsState.value = 'connected'
        isOwlTalking.value = false

        if (!hasGreeted && gemini) {
          hasGreeted = true
          isListening.value = false
          currentTranscript.value = 'Ollie is getting ready...'
          gemini.triggerGreeting()
        } else {
          isListening.value = true
          gemini.setMicMuted(false)
        }
      } else if (state === 'speaking') {
        wsState.value = 'connected'
        isOwlTalking.value = true
        isListening.value = false
        if (gemini) gemini.setMicMuted(true)
      } else if (state === 'disconnected') {
        wsState.value = 'disconnected'
        isOwlTalking.value = false
        isListening.value = false
      }
    },
    onTranscript: (text) => {
      currentTranscript.value = text
    },
    onFunctionCall: (payload) => {
      handleGeminiFunctionCall(payload)
    },
    onError: (error) => {
      console.error('[Explore] Gemini error:', error)
      currentTranscript.value = 'Connection lost. Tap the mic to reconnect.'
      wsState.value = 'disconnected'
    },
  })

  gemini.connect(buildSystemPrompt())

  trackEvent('explore_start', { parkId: storyData.value.parkId, parkName: storyData.value.parkName })
}

function toggleMic() {
  if (!gemini) return
  isListening.value = !isListening.value
  gemini.setMicMuted(!isListening.value)
}

function toggleDrawer() {
  isDrawerOpen.value = !isDrawerOpen.value
}

// ─── Gemini function call handler ────────────────────────────
function handleGeminiFunctionCall(payload) {
  if (payload.name === 'update_task_progress') {
    const taskId = payload.args.taskId
    const nextAction = payload.args.nextAction

    const task = storyData.value.tasks.find(t => t.id === taskId)
    if (task) {
      task.completed = true
      progressStore.addXp(task.xp || 30)
      trackEvent('explore_task_complete', { parkId: storyData.value.parkId, taskId })
    }

    saveProgress()

    if (nextAction === 'eye_rest') {
      startEyeRest()
    } else if (nextAction === 'next_task') {
      advanceToNextTask()
    } else if (nextAction === 'celebration') {
      // All tasks completed - show celebration UI
      currentTranscript.value = `Amazing ${userName.value}! You found all the Time Fragments!`
      isOwlTalking.value = true
      setTimeout(() => { isOwlTalking.value = false }, 3000)

      // Award epic park badge (only once per session to prevent duplicates)
      if (!epicBadgeAwarded) {
        epicBadgeAwarded = true
        const badgeId = PARK_TO_BADGE[storyData.value.parkId]
        if (badgeId) {
          // Pass 0 XP because XP was already awarded per-task via addXp above
          progressStore.completeEpicPark(badgeId, 0)
        }
      }

      trackEvent('explore_complete', { parkId: storyData.value.parkId })
    }
  }
}

function advanceToNextTask() {
  if (currentTaskIndex.value < storyData.value.tasks.length - 1) {
    currentTaskIndex.value++
    isDrawerOpen.value = false
    currentTranscript.value = `Great job! Now let's head to ${currentTask.value.name}.`
    isOwlTalking.value = true
    setTimeout(() => { isOwlTalking.value = false }, 3000)
  }
}

function startEyeRest() {
  const secs = currentTask.value?.eyeRestSec || 20
  eyeRestSeconds.value = secs
  eyeRestProgress.value = 0
  showEyeRest.value = true
  currentTranscript.value = 'Look at the farthest thing you can see and let your eyes rest!'

  let elapsed = 0
  eyeRestTimer = setInterval(() => {
    elapsed++
    eyeRestProgress.value = elapsed / secs
    eyeRestSeconds.value = secs - elapsed
    if (elapsed >= secs) {
      clearInterval(eyeRestTimer)
      showEyeRest.value = false
      advanceToNextTask()
    }
  }, 1000)
}

// Debug shortcut
function mockSuccess() {
  handleGeminiFunctionCall({
    name: 'update_task_progress',
    args: {
      taskId: currentTask.value.id,
      nextAction: currentTaskIndex.value >= storyData.value.tasks.length - 1 ? 'celebration' : 'eye_rest',
    },
  })
}

function handleExit() {
  if (gemini) { gemini.disconnect(); gemini = null }
  router.push('/map')
}

function jumpToTask(index) {
  if (index > currentTaskIndex.value && !storyData.value.tasks[index].completed) return
  currentTaskIndex.value = index
  isDrawerOpen.value = false
}

// ─── Lifecycle ───────────────────────────────────────────────
onMounted(() => {
  progressStore.init()
  loadProgress()
  if (!localStorage.getItem(OB_KEY)) { showOb.value = true; obStep.value = 0 }
})

onUnmounted(() => {
  if (eyeRestTimer) clearInterval(eyeRestTimer)
  if (gemini) { gemini.disconnect(); gemini = null }
})
</script>

<style scoped>
/* ─── Root ─── */
.explore-root {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: linear-gradient(180deg, #ecfdf5 0%, #f0fdf4 100%);
  overflow: hidden;
  overscroll-behavior: none;
}

/* ─── Top bar ─── */
.explore-topbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: white;
  border-bottom: 3px solid #bbf7d0;
  flex-shrink: 0;
  z-index: 10;
}

.topbar-back {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0fdf4;
  border: 2px solid #bbf7d0;
  border-bottom: 3px solid #34d399;
  flex-shrink: 0;
  cursor: pointer;
}

.topbar-back:active {
  transform: scale(0.9);
}

.topbar-story {
  flex: 1;
  min-width: 0;
}

.topbar-title {
  font-size: 14px;
  font-weight: 900;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}

.topbar-park {
  font-size: 11px;
  font-weight: 700;
  color: #6b7280;
  margin: 0;
}

.topbar-progress {
  padding: 4px 10px;
  border-radius: 10px;
  background: #f0fdf4;
  border: 2px solid #bbf7d0;
  flex-shrink: 0;
  cursor: pointer;
}

.topbar-progress:active {
  transform: scale(0.9);
}

.topbar-progress-text {
  font-size: 12px;
  font-weight: 900;
  color: #16a34a;
}

/* ─── Progress dots ─── */
.progress-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px 24px;
  flex-shrink: 0;
}

.progress-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2.5px solid #e2e8f0;
  background: white;
  font-size: 11px;
  font-weight: 900;
  color: #94a3b8;
  flex-shrink: 0;
  transition: all 0.3s;
  cursor: pointer;
}

.dot-num {
  font-size: 11px;
}

.dot-completed {
  background: #16a34a;
  border-color: #059669;
}

.dot-active {
  border-color: #34d399;
  color: #16a34a;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15);
  animation: dot-pulse 2s ease-in-out infinite;
}

.dot-locked {
  background: #f8fafc;
  border-color: #e2e8f0;
  cursor: not-allowed;
}

@keyframes dot-pulse {

  0%,
  100% {
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.15);
  }

  50% {
    box-shadow: 0 0 0 8px rgba(16, 185, 129, 0.08);
  }
}

.progress-line {
  flex: 1;
  height: 3px;
  max-width: 40px;
  background: #e2e8f0;
  border-radius: 2px;
}

.line-done {
  background: #34d399;
}

/* ─── Main stage ─── */
.explore-main-stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px 20px;
  min-height: 0;
  position: relative;
}

/* ─── Owl ─── */
.owl-celebration {
  position: relative;
  transition: transform 0.3s;
}

.owl-celebration.speaking {
  animation: owl-bounce 0.6s ease-in-out infinite;
}

.owl-celebration.listening {
  transform: scale(1.05);
}

@keyframes owl-bounce {

  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-6px);
  }
}

.owl-body-big {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid #d97706;
  position: relative;
  flex-direction: column;
  gap: 6px;
  box-shadow: 0 10px 25px -5px rgba(217, 119, 6, 0.4);
}

/* Owl ears */
.owl-ears {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  display: flex;
  justify-content: space-between;
}

.owl-ear {
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-bottom: 16px solid #d97706;
}

.owl-ear.left {
  transform: rotate(-15deg);
}

.owl-ear.right {
  transform: rotate(15deg);
}

.owl-eyes-big {
  display: flex;
  gap: 16px;
}

.owl-eye-big {
  width: 28px;
  height: 28px;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.owl-pupil-big {
  width: 14px;
  height: 14px;
  background: #1f2937;
  border-radius: 50%;
  animation: owl-look 6s ease-in-out infinite;
}

@keyframes owl-look {

  0%,
  80%,
  100% {
    transform: translateX(0);
  }

  40% {
    transform: translateX(3px);
  }

  60% {
    transform: translateX(-3px);
  }
}

.owl-beak-big {
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 14px solid #ea580c;
  transition: transform 0.15s;
  margin-top: 4px;
}

.beak-open {
  animation: beak-talk 0.3s ease-in-out infinite;
}

@keyframes beak-talk {

  0%,
  100% {
    transform: scaleY(1);
  }

  50% {
    transform: scaleY(1.6) translateY(2px);
  }
}

/* Listening pulse rings */
.listen-rings {
  position: absolute;
  inset: -20px;
  pointer-events: none;
}

.listen-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(16, 185, 129, 0.3);
  animation: ring-expand 2s ease-out infinite;
}

.listen-ring.r2 {
  animation-delay: 0.5s;
}

.listen-ring.r3 {
  animation-delay: 1s;
}

@keyframes ring-expand {
  0% {
    transform: scale(1);
    opacity: 0.6;
  }

  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

/* Task label pill */
.task-label-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 14px;
  padding: 6px 14px;
  border-radius: 20px;
  background: white;
  border: 2px solid #bbf7d0;
  border-bottom: 3px solid #34d399;
  font-size: 12px;
  font-weight: 900;
  color: #16a34a;
}

/* ─── Eye rest ─── */
.eye-rest-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.eye-rest-ring {
  position: relative;
  width: 120px;
  height: 120px;
}

.eye-rest-ring svg {
  width: 100%;
  height: 100%;
}

.eye-rest-number {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: 900;
  color: #10b981;
}

.eye-rest-label {
  font-size: 14px;
  font-weight: 800;
  color: #065f46;
  margin: 0;
}

/* ─── Celebration ─── */
.celebration-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  position: relative;
  overflow: visible;
}

.celebration-title {
  font-size: 22px;
  font-weight: 900;
  color: #1f2937;
  margin: 4px 0 0;
}

.celebration-sub {
  font-size: 13px;
  font-weight: 700;
  color: #6b7280;
  margin: 0;
}

.celebration-xp {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
  font-weight: 900;
  color: #d97706;
  margin-top: 4px;
}

.celebration-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  margin-top: 8px;
  padding: 12px 28px;
  border-radius: 16px;
  font-size: 14px;
}

/* Confetti */
.confetti-wrap {
  position: absolute;
  top: -60px;
  left: -40px;
  right: -40px;
  height: 200px;
  pointer-events: none;
  overflow: hidden;
}

.confetti-piece {
  position: absolute;
  top: -10px;
  width: 8px;
  height: 8px;
  border-radius: 2px;
  animation: confetti-fall 3s ease-in-out infinite;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(-20px) rotate(0deg);
    opacity: 1;
  }

  100% {
    transform: translateY(200px) rotate(720deg);
    opacity: 0;
  }
}

/* ─── Transcript ─── */
.transcript-area {
  padding: 0 24px 12px;
  text-align: center;
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.transcript-text {
  font-size: 17px;
  font-weight: 800;
  color: #1f2937;
  line-height: 1.4;
  margin: 0;
}

.transcript-placeholder {
  font-size: 15px;
  font-weight: 700;
  color: #94a3b8;
  font-style: italic;
  margin: 0;
}

/* ─── Education Drawer ─── */
.education-drawer {
  background: white;
  border-top-left-radius: 24px;
  border-top-right-radius: 24px;
  border: 2px solid #e2e8f0;
  border-bottom: none;
  max-height: 44px;
  overflow: hidden;
  transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}

.education-drawer.drawer-open {
  max-height: 280px;
  overflow-y: auto;
}

.drawer-handle {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 16px 6px;
  cursor: pointer;
  font-size: 11px;
  font-weight: 800;
  color: #64748b;
  text-transform: uppercase;
}

.drawer-handle-bar {
  width: 32px;
  height: 4px;
  background: #cbd5e1;
  border-radius: 2px;
}

.drawer-content {
  padding: 8px 16px 16px;
}

.drawer-photo {
  position: relative;
  border-radius: 14px;
  overflow: hidden;
  border: 2px solid #e2e8f0;
  margin-bottom: 10px;
  cursor: pointer;
}

.drawer-photo:active {
  transform: scale(0.98);
}

.drawer-photo img {
  width: 100%;
  height: 120px;
  object-fit: cover;
  display: block;
}

.drawer-photo-label {
  position: absolute;
  bottom: 6px;
  left: 6px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.55);
  font-size: 10px;
  font-weight: 800;
  color: white;
}

.drawer-edu-scroll {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}

.drawer-edu-scroll::-webkit-scrollbar {
  display: none;
}

.drawer-edu-card {
  flex-shrink: 0;
  width: 180px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1.5px solid;
}

.drawer-edu-title {
  font-size: 11px;
  font-weight: 900;
  margin: 0 0 3px;
}

.drawer-edu-desc {
  font-size: 10px;
  font-weight: 600;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

/* ─── Audio bar ─── */
.audio-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  padding-bottom: max(12px, env(safe-area-inset-bottom, 12px));
  background: white;
  border-top: 3px solid #bbf7d0;
  flex-shrink: 0;
  z-index: 10;
}

.audio-left-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.audio-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.audio-dot.disconnected {
  background: #cbd5e1;
}

.audio-dot.connecting {
  background: #f59e0b;
  animation: pulse-dot 1s infinite;
}

.audio-dot.connected {
  background: #16a34a;
}

@keyframes pulse-dot {

  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }

  50% {
    opacity: 0.5;
    transform: scale(1.3);
  }
}

.audio-label {
  font-size: 13px;
  font-weight: 800;
  color: #6b7280;
}

/* Start button */
.start-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex: 1;
  padding: 14px 20px;
  margin-left: 12px;
  background: #16a34a;
  color: white;
  border: none;
  border-bottom: 4px solid #059669;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 900;
  cursor: pointer;
  font-family: inherit;
}

.start-btn:active {
  transform: translateY(2px);
  border-bottom-width: 2px;
}

/* Mic section */
.mic-section {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Waveform */
.waveform {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 28px;
}

.wave-bar {
  width: 3px;
  height: 6px;
  border-radius: 2px;
  transition: height 0.15s;
}

.wave-bar.wave-active {
  animation: wave-bounce 0.6s ease-in-out infinite alternate;
}

@keyframes wave-bounce {
  0% {
    height: 4px;
  }

  100% {
    height: 22px;
  }
}

.audio-mic-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f5f9;
  border: 2px solid #e2e8f0;
  border-bottom: 3px solid #cbd5e1;
  cursor: pointer;
  transition: all 0.2s;
}

.audio-mic-btn:active {
  transform: scale(0.9);
}

.mic-active {
  background: #16a34a !important;
  border-color: #059669 !important;
  border-bottom-color: #047857 !important;
  animation: mic-pulse 1.5s infinite;
}

@keyframes mic-pulse {

  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.3);
  }

  50% {
    box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
  }
}

/* ─── Photo modal ─── */
.photo-modal {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.85);
  padding: 24px;
}

.photo-modal-img {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 16px;
  object-fit: contain;
}

.photo-modal-hint {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 12px;
}

/* ─── Transitions ─── */
.fade-enter-active {
  animation: fade-in 0.3s ease;
}

.fade-leave-active {
  animation: fade-out 0.3s ease forwards;
}

@keyframes fade-in {
  from {
    opacity: 0;
  }

  to {
    opacity: 1;
  }
}

@keyframes fade-out {
  from {
    opacity: 1;
  }

  to {
    opacity: 0;
  }
}
</style>
<style>
.ob-card-explore {
  position: absolute;
  width: calc(100% - 32px);
  max-width: 360px;
  padding: 20px;
  border-radius: 24px;
  background: white;
  border: 2px solid #ddd6fe;
  border-bottom: 4px solid #8b5cf6;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  z-index: 1000;
  font-family: var(--font-game), system-ui, sans-serif
}

.ob-next-e {
  padding: 8px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  border-bottom: 3px solid #6d28d9;
  color: white;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
  font-family: var(--font-game), system-ui, sans-serif
}

.ob-arrow-down-e {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid white
}
</style>