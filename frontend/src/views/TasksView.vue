<template>
  <div class="min-h-full pb-6" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Header -->
    <div class="relative overflow-hidden px-4 pt-6 pb-4"
      style="background: linear-gradient(160deg, #bbf7d0, #6ee7b7); border-radius: 0 0 32px 32px; border-bottom: 4px solid #34d399">
      <h1 class="text-2xl font-black text-emerald-900">Today's Missions</h1>

      <div class="mt-3 flex items-center gap-2 flex-wrap">
        <div v-if="weather.loading" class="flex items-center gap-1">
          <PhSpinner :size="14" weight="duotone" color="#065f46" class="animate-spin" />
          <span class="text-xs font-bold text-emerald-700">Loading weather...</span>
        </div>
        <div v-else class="flex items-center gap-2 flex-wrap">

          <!-- Temp -->
          <div class="inline-flex items-center gap-1.5 bg-white/60 rounded-full px-3 py-1.5">
            <PhSun v-if="weather.desc === 'Clear sky'" :size="16" weight="duotone" color="#f59e0b" />
            <PhCloud v-else-if="weather.desc === 'Cloudy' || weather.desc === 'Partly cloudy'" :size="16" weight="duotone" color="#94a3b8" />
            <PhCloudRain v-else :size="16" weight="duotone" color="#60a5fa" />
            <span class="text-xs font-black text-emerald-900">{{ weather.temp }}°C</span>
          </div>

          <!-- UV -->
          <div class="inline-flex items-center gap-1.5 bg-white/60 rounded-full px-3 py-1.5">
            <PhSunHorizon :size="16" weight="duotone" :color="weather.getUvLabel(weather.uvIndex).color" />
            <span class="text-xs font-black text-emerald-900">
              UV {{ weather.uvIndex }} ·
              <span :style="`color: ${weather.getUvLabel(weather.uvIndex).color}`">
                {{ weather.getUvLabel(weather.uvIndex).label }}
              </span>
            </span>
          </div>

          <!-- Outdoor status -->
          <div class="inline-flex items-center gap-1 rounded-full px-3 py-1.5"
            :style="weather.isGoodWeather ? 'background: #dcfce7' : 'background: #fef9c3'">
            <span class="text-xs font-black"
              :style="weather.isGoodWeather ? 'color: #16a34a' : 'color: #854d0e'">
              {{ weather.isGoodWeather ? 'Outdoor unlocked!' : 'Indoor day!' }}
            </span>
          </div>

        </div>
      </div>
    </div>

    <div class="px-4 flex flex-col gap-4 mt-4">

      <!-- Progress -->
      <div class="card-game flex flex-col gap-2">
        <div class="flex justify-between items-center">
          <p class="text-sm font-black text-gray-700">Today's progress</p>
          <span class="text-xs font-black text-emerald-600">{{ completedCount }} / {{ totalCount }} done</span>
        </div>
        <div class="h-4 bg-gray-100 rounded-full overflow-hidden border-2 border-gray-200">
          <div class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
            :style="`width: ${progressPercent}%; background: linear-gradient(to right, #34d399, #10b981)`">
            <span v-if="progressPercent > 20" class="text-white text-xs font-black">
              {{ progressPercent }}%
            </span>
          </div>
        </div>
        <p class="text-xs font-semibold text-gray-400">
          <template v-if="completedCount === totalCount">
            All done! You earned {{ totalXp }} XP today!
          </template>
          <template v-else>
            {{ totalCount - completedCount }} more task{{ totalCount - completedCount > 1 ? 's' : '' }} to go · +{{ remainingXp }} XP remaining
          </template>
        </p>
      </div>

      <!-- Outdoor tasks -->
      <div v-if="weather.isGoodWeather">
        <div class="flex items-center gap-1.5 mb-2">
          <PhTree :size="16" weight="duotone" color="#16a34a" />
          <p class="text-sm font-black text-gray-700">Outdoor Tasks</p>
        </div>
        <div class="flex flex-col gap-2">
          <div v-for="task in outdoorTasks" :key="task.id"
            class="card-game flex items-center gap-3 cursor-pointer active:scale-95 transition-all"
            :style="task.done ? 'border-color: #bbf7d0; border-bottom-color: #34d399; opacity: 0.8' : ''"
            @click="openConfirm(task)">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
              :style="task.done
                ? 'background: #dcfce7; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac'
                : 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac'">
              <component :is="task.icon" :size="24" weight="duotone"
                :color="task.done ? '#16a34a' : '#34d399'" />
            </div>
            <div class="flex-1">
              <p class="text-sm font-black"
                :style="task.done ? 'color: #16a34a; text-decoration: line-through' : 'color: #1f2937'">
                {{ task.name }}
              </p>
              <p class="text-xs font-semibold text-gray-400 mt-0.5">{{ task.description }}</p>
            </div>
            <div class="flex flex-col items-end gap-1">
              <div v-if="!task.done" class="flex items-center gap-0.5">
                <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                <span class="text-xs font-black text-amber-500">+{{ task.xp }} XP</span>
              </div>
              <PhCheckCircle v-else :size="20" weight="duotone" color="#16a34a" />
            </div>
          </div>
        </div>
      </div>

      <!-- Indoor tasks -->
      <div>
        <div class="flex items-center gap-1.5 mb-2">
          <PhHouse :size="16" weight="duotone" color="#6366f1" />
          <p class="text-sm font-black text-gray-700">Indoor Tasks</p>
        </div>
        <div class="flex flex-col gap-2">
          <div v-for="task in indoorTasks" :key="task.id"
            class="card-game flex items-center gap-3 cursor-pointer active:scale-95 transition-all"
            :style="task.done ? 'border-color: #e0e7ff; border-bottom-color: #a5b4fc; opacity: 0.8' : ''"
            @click="openConfirm(task)">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
              :style="task.done
                ? 'background: #e0e7ff; border: 2px solid #c7d2fe; border-bottom: 3px solid #a5b4fc'
                : 'background: #f5f3ff; border: 2px solid #e0e7ff; border-bottom: 3px solid #c7d2fe'">
              <component :is="task.icon" :size="24" weight="duotone"
                :color="task.done ? '#6366f1' : '#818cf8'" />
            </div>
            <div class="flex-1">
              <p class="text-sm font-black"
                :style="task.done ? 'color: #6366f1; text-decoration: line-through' : 'color: #1f2937'">
                {{ task.name }}
              </p>
              <p class="text-xs font-semibold text-gray-400 mt-0.5">{{ task.description }}</p>
            </div>
            <div class="flex flex-col items-end gap-1">
              <div v-if="!task.done" class="flex items-center gap-0.5">
                <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                <span class="text-xs font-black text-amber-500">+{{ task.xp }} XP</span>
              </div>
              <PhCheckCircle v-else :size="20" weight="duotone" color="#6366f1" />
            </div>
          </div>
        </div>
      </div>

      <!-- Rainy day message -->
      <div v-if="!weather.isGoodWeather" class="card-game text-center py-6"
        style="border-color: #fde68a; border-bottom-color: #fbbf24">
        <PhCloudRain :size="48" weight="duotone" color="#f59e0b" class="mx-auto mb-3" />
        <p class="text-sm font-black text-amber-800">Rainy day!</p>
        <p class="text-xs font-semibold text-amber-600 mt-1">
          Outdoor tasks are locked today. Complete indoor tasks to keep your streak!
        </p>
      </div>

    </div>

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
            <component :is="selectedTask?.icon" :size="28" weight="duotone" color="#16a34a" />
          </div>
          <div>
            <p class="text-lg font-black text-gray-800">{{ selectedTask?.name }}</p>
            <p class="text-xs font-semibold text-gray-400">{{ selectedTask?.description }}</p>
          </div>
        </div>
        <div class="bg-amber-50 rounded-2xl p-3 flex items-center gap-2"
          style="border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24">
          <PhLightning :size="20" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-amber-700">
            Complete this task to earn +{{ selectedTask?.xp }} XP!
          </p>
        </div>
        <p class="text-sm font-semibold text-gray-500 text-center">
          Did you complete this task?
        </p>
        <button class="btn-game text-base font-black flex items-center justify-center gap-2"
          @click="completeTask">
          <PhCheckCircle :size="20" weight="duotone" color="white" />
          Yes, I did it!
        </button>
        <button class="text-sm font-bold text-gray-400 py-2" @click="closeConfirm">
          Not yet
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWeatherStore } from '../stores/weather'
import {
  PhTree, PhHouse, PhLightning, PhCheckCircle,
  PhSpinner, PhCloudRain, PhSun, PhCloud, PhSunHorizon,
  PhFlower, PhSneaker, PhBinoculars,
  PhPencil, PhBookOpen, PhPuzzlePiece
} from '@phosphor-icons/vue'

const weather = useWeatherStore()

onMounted(() => {
  if (!weather.temp) weather.fetchWeather()
})

const showModal = ref(false)
const selectedTask = ref(null)

const tasks = ref([
  { id: 1, name: 'Find a flower',   description: 'Spot any flower outside',         icon: PhFlower,      xp: 20, type: 'outdoor', done: false },
  { id: 2, name: 'Spot 3 trees',    description: 'Find 3 different types of trees',  icon: PhTree,        xp: 20, type: 'outdoor', done: false },
  { id: 3, name: 'Walk 10 mins',    description: 'Go for a walk around the block',   icon: PhSneaker,     xp: 30, type: 'outdoor', done: false },
  { id: 4, name: 'Nature watch',    description: 'Spot a bird or insect outside',    icon: PhBinoculars,  xp: 25, type: 'outdoor', done: false },
  { id: 5, name: 'Draw outside',    description: 'Draw what you see from a window',  icon: PhPencil,      xp: 15, type: 'indoor',  done: false },
  { id: 6, name: 'Read 15 mins',    description: 'Read a book instead of a screen',  icon: PhBookOpen,    xp: 15, type: 'indoor',  done: false },
  { id: 7, name: 'Puzzle time',     description: 'Complete a puzzle or board game',  icon: PhPuzzlePiece, xp: 15, type: 'indoor',  done: false },
])

const outdoorTasks    = computed(() => tasks.value.filter(t => t.type === 'outdoor'))
const indoorTasks     = computed(() => tasks.value.filter(t => t.type === 'indoor'))
const completedCount  = computed(() => tasks.value.filter(t => t.done).length)
const totalCount      = computed(() => tasks.value.length)
const progressPercent = computed(() => Math.round((completedCount.value / totalCount.value) * 100))
const totalXp         = computed(() => tasks.value.filter(t => t.done).reduce((sum, t) => sum + t.xp, 0))
const remainingXp     = computed(() => tasks.value.filter(t => !t.done).reduce((sum, t) => sum + t.xp, 0))

function openConfirm(task) {
  if (task.done) return
  selectedTask.value = task
  showModal.value = true
}

function closeConfirm() {
  showModal.value = false
  selectedTask.value = null
}

function completeTask() {
  const task = tasks.value.find(t => t.id === selectedTask.value.id)
  if (task) task.done = true
  closeConfirm()
}
</script>