<template>
  <div class="min-h-full pb-6" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Top banner -->
    <div class="relative overflow-hidden px-4 pt-6 pb-4"
      style="background: linear-gradient(160deg, #bbf7d0, #6ee7b7); border-radius: 0 0 32px 32px; border-bottom: 4px solid #34d399">
      <div class="flex items-end justify-between">
        <div>
          <p class="text-xs font-black text-emerald-700 uppercase tracking-widest">Hey {{ userName }}!</p>
          <h1 class="text-3xl font-black text-emerald-900 leading-tight mt-1">
            Ready for<br>today's hunt?
          </h1>
          <div class="mt-3 inline-flex items-center gap-1 bg-white/60 rounded-full px-3 py-1">
            <PhSun v-if="weather.desc === 'Clear sky'" :size="16" weight="duotone" color="#f59e0b" />
            <PhCloud v-else-if="weather.desc === 'Cloudy' || weather.desc === 'Partly cloudy'" :size="16" weight="duotone" color="#94a3b8" />
            <PhCloudRain v-else-if="weather.desc === 'Rainy'" :size="16" weight="duotone" color="#60a5fa" />
            <PhSun v-else :size="16" weight="duotone" color="#f59e0b" />
            <span class="text-xs font-black text-emerald-800">
              <template v-if="weather.loading">Loading weather...</template>
              <template v-else>{{ weather.temp }}°C · {{ weather.desc }} · {{ weather.suburb }}</template>
            </span>
          </div>
        </div>
        <div class="w-24 h-24 flex-shrink-0 rounded-3xl flex items-center justify-center"
          style="background: white; border: 3px solid #34d399; border-bottom: 5px solid #16a34a">
          <PhPawPrint :size="52" weight="duotone" color="#16a34a" />
        </div>
      </div>
      <div class="absolute top-3 right-32 w-3 h-3 rounded-full bg-white opacity-40"></div>
      <div class="absolute top-8 right-24 w-2 h-2 rounded-full bg-white opacity-30"></div>
      <div class="absolute bottom-6 left-8 w-2 h-2 rounded-full bg-white opacity-30"></div>
    </div>

    <div class="px-4 flex flex-col gap-4 mt-4">

      <!-- XP / Level bar -->
      <div class="card-game">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center font-black text-white text-base"
              style="background: linear-gradient(135deg, #f59e0b, #ef4444); border-bottom: 3px solid #b45309">
              {{ progressStore.level }}
            </div>
            <div>
              <p class="text-xs font-black text-gray-500 uppercase tracking-wide">Level</p>
              <div class="flex items-center gap-1">
                <PhCompass :size="14" weight="duotone" color="#10b981" />
                <p class="text-sm font-black text-gray-800">{{ progressStore.levelTitle }}</p>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <PhLightning :size="14" weight="duotone" color="#f59e0b" />
            <p class="text-xs font-black text-amber-500">
              {{ progressStore.xpInCurrentLevel }} / {{ progressStore.xpNeededForLevel }} XP
            </p>
          </div>
        </div>
        <div class="h-4 rounded-full overflow-hidden border-2 border-gray-200" style="background: #f1f5f9">
          <div class="h-full rounded-full relative transition-all duration-500"
            :style="`width: ${progressStore.xpPercent}%; background: linear-gradient(to right, #fbbf24, #f59e0b)`">
            <div v-if="progressStore.xpPercent >= 15" class="absolute right-2 top-0 h-full flex items-center">
              <span class="text-white text-xs font-black">{{ progressStore.xpPercent }}%</span>
            </div>
          </div>
        </div>
        <p class="text-xs font-semibold text-gray-400 mt-1.5">
          {{ progressStore.xpNeededForLevel - progressStore.xpInCurrentLevel }} XP to next level
        </p>
      </div>

      <!-- Mode toggle + series dropdown -->
      <div class="relative">
        <div class="flex gap-2">
          <button
            class="flex-1 py-3 rounded-2xl font-black text-sm flex items-center justify-center gap-2 transition-all"
            :style="mode === 'random'
              ? 'background: #10b981; color: white; border: 2px solid #059669; border-bottom: 4px solid #047857'
              : 'background: white; color: #94a3b8; border: 2px solid #e2e8f0; border-bottom: 4px solid #cbd5e1'"
            @click="switchMode('random')">
            <PhShuffle :size="16" weight="duotone" :color="mode === 'random' ? 'white' : '#94a3b8'" />
            Random
          </button>
          <button
            class="flex-1 py-3 rounded-2xl font-black text-sm flex items-center justify-center gap-2 transition-all"
            :style="mode === 'series'
              ? 'background: #10b981; color: white; border: 2px solid #059669; border-bottom: 4px solid #047857'
              : 'background: white; color: #94a3b8; border: 2px solid #e2e8f0; border-bottom: 4px solid #cbd5e1'"
            @click="switchMode('series')">
            <PhStarFour :size="16" weight="duotone" :color="mode === 'series' ? 'white' : '#94a3b8'" />
            Series
            <PhCaretDown :size="14" weight="bold" :color="mode === 'series' ? 'white' : '#94a3b8'" />
          </button>
        </div>

        <!-- Series dropdown -->
        <div v-if="mode === 'series' && showSeriesDropdown"
          class="absolute right-0 top-14 z-20 w-1/2 rounded-2xl overflow-hidden"
          style="background: white; border: 2px solid #e2e8f0; border-bottom: 4px solid #cbd5e1">
          <div v-for="series in seriesList" :key="series.id"
            class="flex items-center gap-3 px-3 py-3 cursor-pointer transition-all"
            :style="selectedSeriesId === series.id ? `background: ${series.iconBg}` : 'background: white'"
            @click="selectSeries(series.id)">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
              :style="`background: ${series.iconBg}; border: 2px solid ${series.borderColor}; border-bottom: 2px solid ${series.borderBottomColor}`">
              <component :is="series.icon" :size="18" weight="duotone" :color="series.color" />
            </div>
            <p class="text-sm font-black flex-1"
              :style="`color: ${selectedSeriesId === series.id ? series.color : '#374151'}`">
              {{ series.name }}
            </p>
            <PhCheck v-if="selectedSeriesId === series.id" :size="14" weight="bold" :color="series.color" />
          </div>
        </div>
      </div>

      <!-- Random task card -->
      <template v-if="!selectedSeriesId">
        <div class="card-game" style="border-color: #bbf7d0; border-bottom-color: #34d399">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-1.5">
              <PhTarget :size="18" weight="duotone" color="#10b981" />
              <p class="text-base font-black text-gray-800">Today's Mission</p>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs font-black text-emerald-700 bg-emerald-100 rounded-xl px-2 py-1">
                {{ completedRandomCount }} / {{ randomTasks.length }}
              </span>
              <button @click="handleRefresh"
                class="w-7 h-7 rounded-xl flex items-center justify-center relative"
                :style="progressStore.refreshesLeftToday > 0
                  ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac'
                  : 'background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1; opacity: 0.5'"
                :disabled="progressStore.refreshesLeftToday <= 0">
                <PhArrowsClockwise :size="14" weight="duotone"
                  :color="progressStore.refreshesLeftToday > 0 ? '#16a34a' : '#94a3b8'" />
              </button>
              <span class="text-xs font-bold text-gray-400">{{ progressStore.refreshesLeftToday }}/3</span>
            </div>
          </div>
          <div v-if="loadingTasks" class="flex items-center justify-center py-6 gap-2">
            <PhSpinner :size="20" weight="duotone" color="#10b981" class="animate-spin" />
            <span class="text-sm font-bold text-gray-400">Loading tasks...</span>
          </div>
          <div v-else class="flex flex-col gap-2">
            <div v-for="task in randomTasks" :key="task.taskId"
              class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all"
              :style="task.done
                ? 'background: #f0fdf4; border: 2px solid #bbf7d0'
                : 'background: #f8fafc; border: 2px solid #e2e8f0'"
              @click="openConfirm(task)">
              <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
                :style="task.done ? 'background: #dcfce7' : 'background: #f1f5f9'">
                <PhCamera :size="18" weight="duotone" :color="task.done ? '#16a34a' : '#94a3b8'" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-bold"
                  :style="task.done ? 'color: #16a34a; text-decoration: line-through' : 'color: #374151'">
                  {{ task.taskName }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5">{{ task.taskDescription }}</p>
              </div>
              <div v-if="!task.done" class="flex items-center gap-1.5 flex-shrink-0">
                <div class="flex items-center gap-0.5">
                  <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                  <span class="text-xs font-black text-amber-500">+{{ task.rewardPoint }}</span>
                </div>
                <button v-if="task.latitude != null"
                  class="w-7 h-7 rounded-lg flex items-center justify-center"
                  style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-bottom: 2px solid #93c5fd"
                  @click.stop="goNavigate(task)">
                  <PhNavigationArrow :size="13" weight="duotone" color="#3b82f6" />
                </button>
              </div>
              <PhCheckCircle v-else :size="18" weight="duotone" color="#16a34a" />
            </div>
          </div>
        </div>
    </template>

      <!-- Series task card -->
      <template v-else>
        <div class="card-game"
          :style="`border-color: ${currentSeries?.borderColor}; border-bottom-color: ${currentSeries?.borderBottomColor}`">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <component :is="currentSeries?.icon" :size="18" weight="duotone" :color="currentSeries?.color" />
              <p class="text-base font-black text-gray-800">{{ currentSeries?.name }} Tasks</p>
            </div>
            <div class="flex items-center gap-2">
              <button @click="handleSeriesRefresh"
                class="w-7 h-7 rounded-xl flex items-center justify-center"
                :style="progressStore.refreshesLeftToday > 0
                  ? `background: ${currentSeries?.iconBg}; border: 2px solid ${currentSeries?.borderColor}; border-bottom: 3px solid ${currentSeries?.borderBottomColor}`
                  : 'background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1; opacity: 0.5'"
                :disabled="progressStore.refreshesLeftToday <= 0">
                <PhArrowsClockwise :size="14" weight="duotone"
                  :color="progressStore.refreshesLeftToday > 0 ? currentSeries?.color : '#94a3b8'" />
              </button>
              <span class="text-xs font-bold text-gray-400">{{ progressStore.refreshesLeftToday }}/3</span>
              <button @click="clearSeries"
                class="w-7 h-7 rounded-xl flex items-center justify-center"
                style="background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 2px solid #cbd5e1">
                <PhX :size="14" weight="bold" color="#94a3b8" />
              </button>
            </div>
          </div>
          <div v-if="loadingSeriesTasks" class="flex items-center justify-center py-6 gap-2">
            <PhSpinner :size="20" weight="duotone" :color="currentSeries?.color" class="animate-spin" />
            <span class="text-sm font-bold text-gray-400">Loading tasks...</span>
          </div>
          <div v-else class="flex flex-col gap-2">
            <div v-for="task in seriesTasks" :key="task.taskId"
              class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all"
              :style="task.done
                ? `background: ${currentSeries?.iconBg}; border: 2px solid ${currentSeries?.borderColor}`
                : 'background: #f8fafc; border: 2px solid #e2e8f0'"
              @click="openConfirm(task)">
              <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
                :style="task.done ? `background: ${currentSeries?.iconBg}` : 'background: #f1f5f9'">
                <PhCamera :size="18" weight="duotone"
                  :color="task.done ? currentSeries?.color : '#94a3b8'" />
              </div>
              <div class="flex-1">
                <p class="text-sm font-bold"
                  :style="task.done
                    ? `color: ${currentSeries?.color}; text-decoration: line-through`
                    : 'color: #374151'">
                  {{ task.taskName }}
                </p>
                <p class="text-xs text-gray-400 mt-0.5">{{ task.taskDescription }}</p>
              </div>
              <div v-if="!task.done" class="flex items-center gap-1.5 flex-shrink-0">
                <div class="flex items-center gap-0.5">
                  <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                  <span class="text-xs font-black text-amber-500">+{{ task.rewardPoint }}</span>
                </div>
                <button v-if="task.latitude != null"
                  class="w-7 h-7 rounded-lg flex items-center justify-center"
                  style="background: #eff6ff; border: 1.5px solid #bfdbfe; border-bottom: 2px solid #93c5fd"
                  @click.stop="goNavigate(task)">
                  <PhNavigationArrow :size="13" weight="duotone" color="#3b82f6" />
                </button>
              </div>
              <PhCheckCircle v-else :size="18" weight="duotone" :color="currentSeries?.color" />
            </div>
          </div>
        </div>
      </template>

    </div>

    <!-- Hidden file input -->
    <input ref="fileInput" type="file" accept="image/*" capture="environment"
      class="hidden" @change="handlePhotoCapture" />

    <!-- Confirm modal -->
    <div v-if="showModal"
      class="fixed inset-0 flex items-end justify-center z-50"
      style="background: rgba(0,0,0,0.4)"
      @click.self="closeConfirm">
      <div class="w-full max-w-md bg-white rounded-t-3xl p-6 flex flex-col gap-4"
        style="border-top: 4px solid #34d399">
        <div class="flex items-center gap-3">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center"
            style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac">
            <PhCamera :size="28" weight="duotone" color="#16a34a" />
          </div>
          <div>
            <p class="text-lg font-black text-gray-800">{{ selectedTask?.taskName }}</p>
            <p class="text-xs font-semibold text-gray-400">{{ selectedTask?.taskDescription }}</p>
          </div>
        </div>
        <div v-if="capturedPhoto"
          class="w-full rounded-2xl overflow-hidden"
          style="border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399">
          <img :src="capturedPhoto" class="w-full object-cover" style="max-height: 200px" />
        </div>
        <div v-if="evaluating" class="flex items-center justify-center gap-2 py-2">
          <PhSpinner :size="20" weight="duotone" color="#10b981" class="animate-spin" />
          <span class="text-sm font-bold text-gray-400">Checking your photo...</span>
        </div>
        <div v-if="evalResult" class="rounded-2xl p-3"
          :style="evalResult.matched
            ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399'
            : 'background: #fef2f2; border: 2px solid #fecaca; border-bottom: 3px solid #f87171'">
          <div class="flex items-center gap-2 mb-1">
            <PhCheckCircle v-if="evalResult.matched" :size="18" weight="duotone" color="#16a34a" />
            <PhXCircle v-else :size="18" weight="duotone" color="#ef4444" />
            <p class="text-sm font-black"
              :style="evalResult.matched ? 'color: #16a34a' : 'color: #ef4444'">
              {{ evalResult.matched ? 'Task complete!' : 'Not quite right...' }}
            </p>
          </div>
          <p class="text-xs font-semibold text-gray-500">{{ evalResult.reason }}</p>
        </div>
        <div class="bg-amber-50 rounded-2xl p-3 flex items-center gap-2"
          style="border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24">
          <PhLightning :size="20" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-amber-700">
            Complete this task to earn +{{ selectedTask?.rewardPoint }} XP!
          </p>
        </div>
        <!-- Location status banner -->
        <div v-if="selectedTask?.latitude != null" class="rounded-2xl p-3 flex items-center gap-2"
          :style="locationStatus === 'in_range'
            ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399'
            : locationStatus === 'checking'
              ? 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'
              : 'background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74'">
          <PhSpinner v-if="locationStatus === 'checking'" :size="16" weight="duotone" color="#94a3b8" class="animate-spin" />
          <PhMapPin v-else-if="locationStatus === 'in_range'" :size="16" weight="duotone" color="#16a34a" />
          <PhWarning v-else :size="16" weight="duotone" color="#f59e0b" />
          <p class="text-xs font-bold" :style="locationStatus === 'in_range' ? 'color: #16a34a' : locationStatus === 'checking' ? 'color: #94a3b8' : 'color: #ea580c'">
            {{ locationMessage }}
          </p>
        </div>
        <!-- Navigate to task location -->
        <button v-if="selectedTask?.latitude != null && !evalResult?.matched && locationStatus !== 'in_range'"
          class="flex items-center justify-center gap-2 py-3 rounded-2xl font-black text-sm transition-all"
          style="background: #eff6ff; color: #2563eb; border: 2px solid #bfdbfe; border-bottom: 4px solid #93c5fd"
          @click="goNavigate(selectedTask)">
          <PhNavigationArrow :size="18" weight="duotone" color="#3b82f6" />
          Navigate to Location
        </button>
        <button v-if="!evalResult?.matched"
          class="btn-game text-base font-black flex items-center justify-center gap-2"
          :style="canTakePhoto ? '' : 'opacity: 0.4; pointer-events: none'"
          :disabled="!canTakePhoto"
          @click="triggerCamera">
          <PhCamera :size="20" weight="duotone" color="white" />
          {{ capturedPhoto ? 'Retake Photo' : 'Take a Photo!' }}
        </button>
        <button v-if="evalResult?.matched"
          class="btn-game text-base font-black flex items-center justify-center gap-2"
          @click="handleCompleteTask">
          <PhCheckCircle :size="20" weight="duotone" color="white" />
          Awesome! Claim XP!
        </button>
        <button class="text-sm font-bold text-gray-400 py-2" @click="closeConfirm">
          Not yet
        </button>
      </div>
    </div>

    <!-- Backdrop -->
    <div v-if="showSeriesDropdown" class="fixed inset-0 z-10" @click="showSeriesDropdown = false" />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useWeatherStore } from '../stores/weather'
import { useProgressStore, loadDailyTasks, saveDailyTasks, loadDailySeriesTasks, saveDailySeriesTasks } from '../stores/progress'
import { trackEvent } from '../services/analytics'
import {
  PhSun, PhCloud, PhCloudRain, PhPawPrint, PhCompass, PhLightning,
  PhTarget, PhCheckCircle, PhXCircle, PhNavigationArrow,
  PhCamera, PhShuffle, PhStarFour, PhArrowsClockwise, PhSpinner,
  PhTree, PhBuildings, PhPaintBrush, PhCheck, PhCaretDown, PhX,
  PhMapPin, PhWarning
} from '@phosphor-icons/vue'

const BASE_URL = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'

const authStore = useAuthStore()
const weather = useWeatherStore()
const progressStore = useProgressStore()
const router = useRouter()
const userName = authStore.user?.nickname || 'Explorer'

const mode = ref('random')
const showSeriesDropdown = ref(false)
const selectedSeriesId = ref(null)
const randomTasks = ref([])
const seriesTasks = ref([])
const loadingTasks = ref(false)
const loadingSeriesTasks = ref(false)
const showModal = ref(false)
const selectedTask = ref(null)
const fileInput = ref(null)
const capturedPhoto = ref(null)
const evaluating = ref(false)
const evalResult = ref(null)

// Location verification state
const PROXIMITY_RADIUS = 200 // meters
const locationStatus = ref('checking') // 'checking' | 'in_range' | 'out_of_range' | 'error'
const locationMessage = ref('Checking your location...')

const canTakePhoto = computed(() => {
  if (selectedTask.value?.latitude == null) return true
  return locationStatus.value === 'in_range'
})

const completedRandomCount = computed(() =>
  randomTasks.value.filter(t => t.done).length
)

const seriesList = [
  {
    id: 1,
    name: 'Nature Series',
    description: 'Explore the natural world',
    icon: PhTree,
    color: '#16a34a',
    iconBg: '#f0fdf4',
    borderColor: '#bbf7d0',
    borderBottomColor: '#34d399',
  },
  {
    id: 2,
    name: 'Urban Series',
    description: 'Discover your city',
    icon: PhBuildings,
    color: '#3b82f6',
    iconBg: '#eff6ff',
    borderColor: '#bfdbfe',
    borderBottomColor: '#93c5fd',
  },
  {
    id: 3,
    name: 'Art Series',
    description: 'Find beauty everywhere',
    icon: PhPaintBrush,
    color: '#a855f7',
    iconBg: '#faf5ff',
    borderColor: '#e9d5ff',
    borderBottomColor: '#d8b4fe',
  },
]

const currentSeries = computed(() =>
  seriesList.find(s => s.id === selectedSeriesId.value)
)

// ─── Daily task persistence ─────────────────────────────────

async function fetchRandomTasks() {
  loadingTasks.value = true
  try {
    const res = await axios.get(`${BASE_URL}/api/tasks/random`)
    randomTasks.value = res.data.map(t => ({ ...t, done: false }))
    saveDailyTasks(randomTasks.value)
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  } finally {
    loadingTasks.value = false
  }
}

async function loadOrFetchRandomTasks() {
  const cached = loadDailyTasks()
  if (cached && cached.length > 0) {
    randomTasks.value = cached
  } else {
    await fetchRandomTasks()
  }
}

function handleRefresh() {
  if (!progressStore.useRefresh()) return
  fetchRandomTasks()
}

function handleSeriesRefresh() {
  if (!selectedSeriesId.value) return
  if (!progressStore.useRefresh()) return
  fetchSeriesTasks(selectedSeriesId.value)
}

async function fetchSeriesTasks(seriesId) {
  loadingSeriesTasks.value = true
  try {
    const res = await axios.get(`${BASE_URL}/api/tasks/series/random`, {
      params: { seriesId }
    })
    seriesTasks.value = res.data.map(t => ({ ...t, done: false }))
    saveDailySeriesTasks(seriesId, seriesTasks.value)
  } catch (e) {
    console.error('Failed to fetch series tasks:', e)
  } finally {
    loadingSeriesTasks.value = false
  }
}

async function loadOrFetchSeriesTasks(seriesId) {
  const cached = loadDailySeriesTasks(seriesId)
  if (cached && cached.length > 0) {
    seriesTasks.value = cached
  } else {
    await fetchSeriesTasks(seriesId)
  }
}

// ─── Mode switching ─────────────────────────────────────────

function switchMode(newMode) {
  if (newMode === 'series') {
    if (mode.value === 'series') {
      showSeriesDropdown.value = !showSeriesDropdown.value
    } else {
      mode.value = 'series'
      showSeriesDropdown.value = true
    }
  } else {
    mode.value = 'random'
    showSeriesDropdown.value = false
    selectedSeriesId.value = null
    seriesTasks.value = []
  }
}

function selectSeries(id) {
  selectedSeriesId.value = id
  showSeriesDropdown.value = false
  loadOrFetchSeriesTasks(id)
}

function clearSeries() {
  selectedSeriesId.value = null
  seriesTasks.value = []
}

// ─── Location verification ─────────────────────────────────

function getDistanceMeters(lat1, lng1, lat2, lng2) {
  const R = 6371000
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180)
    * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function checkProximity() {
  if (selectedTask.value?.latitude == null) {
    locationStatus.value = 'in_range'
    locationMessage.value = 'No location required'
    return
  }
  locationStatus.value = 'checking'
  locationMessage.value = 'Checking your location...'
  if (!navigator.geolocation) {
    locationStatus.value = 'error'
    locationMessage.value = 'GPS not available on this device'
    return
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const dist = getDistanceMeters(
        pos.coords.latitude, pos.coords.longitude,
        selectedTask.value.latitude, selectedTask.value.longitude
      )
      if (dist <= PROXIMITY_RADIUS) {
        locationStatus.value = 'in_range'
        locationMessage.value = `You're at the task location (${Math.round(dist)}m away)`
      } else {
        locationStatus.value = 'out_of_range'
        const distKm = dist >= 1000 ? `${(dist / 1000).toFixed(1)}km` : `${Math.round(dist)}m`
        locationMessage.value = `You're ${distKm} away. Please go to the task location first!`
      }
    },
    (err) => {
      locationStatus.value = 'error'
      locationMessage.value = err.code === 1
        ? 'Location access denied. Please enable GPS to take photos.'
        : 'Could not get your location. Please try again.'
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
  )
}

// ─── Task interaction ───────────────────────────────────────

function openConfirm(task) {
  if (task.done) return
  selectedTask.value = task
  capturedPhoto.value = null
  evalResult.value = null
  locationStatus.value = 'checking'
  showModal.value = true
  trackEvent('task_start', { taskId: task.taskId, taskName: task.taskName })
  checkProximity()
}

function closeConfirm() {
  showModal.value = false
  selectedTask.value = null
  capturedPhoto.value = null
  evalResult.value = null
}

function triggerCamera() {
  capturedPhoto.value = null
  evalResult.value = null
  fileInput.value?.click()
}

async function handlePhotoCapture(event) {
  const file = event.target.files?.[0]
  if (!file) return
  capturedPhoto.value = URL.createObjectURL(file)
  evaluating.value = true
  evalResult.value = null
  progressStore.addPhoto()
  trackEvent('photo_taken', { taskId: selectedTask.value?.taskId, taskName: selectedTask.value?.taskName })
  try {
    const formData = new FormData()
    formData.append('taskId', selectedTask.value.taskId)
    formData.append('file', file)
    const res = await axios.post(`${BASE_URL}/api/tasks/evaluate`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    evalResult.value = res.data
  } catch (e) {
    evalResult.value = { matched: false, reason: 'Something went wrong. Please try again.' }
  } finally {
    evaluating.value = false
    event.target.value = ''
  }
}

function handleCompleteTask() {
  const task = randomTasks.value.find(t => t.taskId === selectedTask.value?.taskId)
    || seriesTasks.value.find(t => t.taskId === selectedTask.value?.taskId)
  if (task) {
    task.done = true

    // Update progress store
    progressStore.completeTask(task.rewardPoint || 10)

    // Check sunny day badge
    if (weather.desc === 'Clear sky') {
      progressStore.completeSunnyTask()
    }

    // Check series completion
    if (selectedSeriesId.value) {
      const allDone = seriesTasks.value.every(t => t.done)
      if (allDone) {
        const seriesKey = selectedSeriesId.value === 1 ? 'nature'
          : selectedSeriesId.value === 2 ? 'urban' : 'art'
        progressStore.earnBadge(seriesKey)
      }
      saveDailySeriesTasks(selectedSeriesId.value, seriesTasks.value)
    } else {
      saveDailyTasks(randomTasks.value)
    }

    trackEvent('task_complete', {
      taskId: task.taskId,
      taskName: task.taskName,
      xpEarned: task.rewardPoint || 10,
    })
  }
  closeConfirm()
}

function goNavigate(task) {
  if (task.latitude == null || task.longitude == null) return
  router.push({
    path: '/map',
    query: {
      navLat: String(task.latitude),
      navLng: String(task.longitude),
      navName: task.taskName,
      navId: `task-${task.taskId}`,
    }
  })
}

onMounted(() => {
  progressStore.init()
  if (!weather.temp) weather.fetchWeather()
  loadOrFetchRandomTasks()
})
</script>