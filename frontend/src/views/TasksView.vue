<template>
  <div class="min-h-full pb-6" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Header -->
    <div class="relative overflow-hidden px-4 pt-6 pb-5"
      style="background: linear-gradient(160deg, #bbf7d0, #6ee7b7); border-radius: 0 0 32px 32px; border-bottom: 4px solid #34d399">
      <h1 class="text-2xl font-black text-emerald-900">Series Gallery</h1>
      <p class="text-xs font-bold text-emerald-700 mt-1">Complete a series to unlock a badge!</p>
    </div>

    <div class="px-4 flex flex-col gap-4 mt-4 pb-4">

      <div v-if="loadingTasks" class="flex items-center justify-center py-12 gap-2">
        <PhSpinner :size="24" weight="duotone" color="#10b981" class="animate-spin" />
        <span class="text-sm font-bold text-gray-400">Loading series...</span>
      </div>

      <!-- Series cards (stamp style) -->
      <div v-else v-for="series in seriesList" :key="series.id"
        class="rounded-3xl overflow-hidden"
        :style="`border: 2.5px solid ${series.borderColor}; border-bottom: 5px solid ${series.borderBottomColor}`">

        <!-- Card header -->
        <div class="px-4 pt-4 pb-3 flex items-center justify-between"
          :style="`background: ${series.iconBg}`">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center"
              style="background: white; border-bottom: 3px solid"
              :style="`border-color: ${series.borderColor}; border-bottom-color: ${series.borderBottomColor}`">
              <component :is="series.icon" :size="26" weight="duotone" :color="series.color" />
            </div>
            <div>
              <div class="flex items-center gap-1.5">
                <p class="text-base font-black" :style="`color: ${series.color}`">{{ series.name }}</p>
                <PhSeal v-if="seriesCompleted(series.id)" :size="16" weight="duotone" color="#f59e0b" />
              </div>
              <p class="text-xs font-semibold text-gray-500">{{ series.description }}</p>
            </div>
          </div>
          <div class="flex flex-col items-end gap-0.5">
            <span class="text-sm font-black" :style="`color: ${series.color}`">
              {{ seriesCompletedCount(series.id) }}/{{ getSeriesTasks(series.id).length }}
            </span>
          </div>
        </div>

        <!-- Progress bar -->
        <div class="px-4 py-2" :style="`background: ${series.iconBg}`">
          <div class="h-2.5 rounded-full overflow-hidden"
            style="background: rgba(255,255,255,0.6)">
            <div class="h-full rounded-full transition-all duration-500"
              :style="`width: ${seriesProgress(series.id)}%; background: ${series.color}`">
            </div>
          </div>
        </div>

        <!-- Dashed separator (stamp perforation effect) -->
        <div class="flex items-center px-2" :style="`background: ${series.iconBg}`">
          <div class="flex-1 border-t-2 border-dashed" :style="`border-color: ${series.borderColor}`"></div>
          <div class="mx-2">
            <PhMedal :size="18" weight="duotone"
              :color="seriesCompleted(series.id) ? '#f59e0b' : series.borderColor" />
          </div>
          <div class="flex-1 border-t-2 border-dashed" :style="`border-color: ${series.borderColor}`"></div>
        </div>

        <!-- Task cards horizontal scroll -->
        <div class="bg-white px-4 pt-3 pb-4">
          <div v-if="!getSeriesTasks(series.id).length"
            class="flex items-center justify-center py-6 text-xs font-semibold text-gray-400">
            No tasks loaded yet
          </div>
          <div v-else class="flex gap-3 overflow-x-auto pb-1"
            style="scrollbar-width: none; -ms-overflow-style: none;">

            <div v-for="task in getSeriesTasks(series.id)" :key="task.taskId"
              class="flex-shrink-0 flex flex-col rounded-2xl cursor-pointer active:scale-95 transition-all overflow-hidden"
              style="width: 140px; height: 160px;"
              :style="task.done
                ? `background: ${series.iconBg}; border: 2px solid ${series.borderColor}; border-bottom: 3px solid ${series.borderBottomColor}`
                : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'"
              @click="openConfirm(task, series)">

              <!-- Icon area -->
              <div class="flex items-center justify-center pt-3 pb-2">
                <div class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                  :style="task.done
                    ? `background: white; border: 2px solid ${series.borderColor}`
                    : 'background: white; border: 2px solid #e2e8f0'">
                  <PhCamera :size="20" weight="duotone"
                    :color="task.done ? series.color : '#94a3b8'" />
                </div>
              </div>

              <!-- Task name -->
              <div class="px-3 flex-1 flex flex-col justify-between pb-3">
                <div>
                  <p class="text-xs font-black leading-tight overflow-hidden"
                    style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;"
                    :style="task.done ? `color: ${series.color}` : 'color: #1f2937'">
                    {{ task.taskName }}
                  </p>
                  <p class="text-xs font-semibold text-gray-400 mt-1 overflow-hidden"
                    style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;">
                    {{ task.taskDescription }}
                  </p>
                </div>
                <div class="flex items-center justify-between mt-2">
                  <div class="flex items-center gap-0.5">
                    <PhLightning :size="11" weight="duotone" color="#f59e0b" />
                    <span class="text-xs font-black text-amber-500">+{{ task.rewardPoint }}</span>
                  </div>
                  <PhCheckCircle v-if="task.done" :size="16" weight="duotone" :color="series.color" />
                  <PhCamera v-else :size="14" weight="duotone" color="#cbd5e1" />
                </div>
              </div>
            </div>

            <!-- Badge unlock card -->
            <div class="flex-shrink-0 flex flex-col items-center justify-center gap-2 rounded-2xl"
              style="width: 100px; height: 160px; border: 2px dashed #e2e8f0; background: #f8fafc">
              <PhMedal :size="28" weight="duotone"
                :color="seriesCompleted(series.id) ? '#f59e0b' : '#cbd5e1'" />
              <p class="text-xs font-black text-center px-2 leading-tight"
                :style="seriesCompleted(series.id) ? 'color: #f59e0b' : 'color: #94a3b8'">
                {{ seriesCompleted(series.id) ? 'Badge unlocked!' : 'Complete all!' }}
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- Hidden file input -->
    <input ref="fileInput" type="file" accept="image/*" capture="environment"
      class="hidden" @change="handlePhotoCapture" />

    <!-- Task detail + confirm modal -->
    <div v-if="showModal"
      class="fixed inset-0 flex items-end justify-center z-50"
      style="background: rgba(0,0,0,0.4)"
      @click.self="closeConfirm">
      <div class="w-full max-w-md bg-white rounded-t-3xl p-6 flex flex-col gap-4"
        :style="`border-top: 4px solid ${selectedSeries?.borderBottomColor || '#34d399'}`">

        <div class="flex items-start gap-3">
          <div class="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0"
            :style="`background: ${selectedSeries?.iconBg}; border: 2px solid ${selectedSeries?.borderColor}; border-bottom: 3px solid ${selectedSeries?.borderBottomColor}`">
            <PhCamera :size="28" weight="duotone" :color="selectedSeries?.color || '#16a34a'" />
          </div>
          <div class="flex-1">
            <p class="text-lg font-black text-gray-800">{{ selectedTask?.taskName }}</p>
            <p class="text-xs font-semibold text-gray-400 mt-0.5 leading-relaxed">{{ selectedTask?.taskDescription }}</p>
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

        <button v-if="!evalResult?.matched"
          class="btn-game text-base font-black flex items-center justify-center gap-2"
          @click="triggerCamera">
          <PhCamera :size="20" weight="duotone" color="white" />
          {{ capturedPhoto ? 'Retake Photo' : 'Take a Photo!' }}
        </button>

        <button v-if="evalResult?.matched"
          class="btn-game text-base font-black flex items-center justify-center gap-2"
          @click="completeTask">
          <PhCheckCircle :size="20" weight="duotone" color="white" />
          Awesome! Claim XP!
        </button>

        <button class="text-sm font-bold text-gray-400 py-2" @click="closeConfirm">
          Not yet
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import {
  PhLightning, PhCheckCircle, PhXCircle, PhSpinner,
  PhCamera, PhMedal, PhSeal, PhTree, PhBuildings, PhPaintBrush
} from '@phosphor-icons/vue'

const BASE_URL = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'

const allTasks = ref([])
const loadingTasks = ref(false)
const showModal = ref(false)
const selectedTask = ref(null)
const selectedSeries = ref(null)
const fileInput = ref(null)
const capturedPhoto = ref(null)
const evaluating = ref(false)
const evalResult = ref(null)

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

async function fetchAllTasks() {
  loadingTasks.value = true
  try {
    const res = await axios.get(`${BASE_URL}/api/tasks/random`)
    allTasks.value = res.data.map(t => ({ ...t, done: false }))
  } catch (e) {
    console.error('Failed to fetch tasks:', e)
  } finally {
    loadingTasks.value = false
  }
}

function getSeriesTasks(seriesId) {
  return allTasks.value.filter(t => t.seriesId === seriesId)
}

function seriesCompletedCount(seriesId) {
  return getSeriesTasks(seriesId).filter(t => t.done).length
}

function seriesProgress(seriesId) {
  const tasks = getSeriesTasks(seriesId)
  if (!tasks.length) return 0
  return Math.round((seriesCompletedCount(seriesId) / tasks.length) * 100)
}

function seriesCompleted(seriesId) {
  const tasks = getSeriesTasks(seriesId)
  return tasks.length > 0 && tasks.every(t => t.done)
}

function openConfirm(task, series) {
  if (task.done) return
  selectedTask.value = task
  selectedSeries.value = series
  capturedPhoto.value = null
  evalResult.value = null
  showModal.value = true
}

function closeConfirm() {
  showModal.value = false
  selectedTask.value = null
  selectedSeries.value = null
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

function completeTask() {
  const task = allTasks.value.find(t => t.taskId === selectedTask.value.taskId)
  if (task) task.done = true
  closeConfirm()
}

onMounted(() => {
  fetchAllTasks()
})
</script>