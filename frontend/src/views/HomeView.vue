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

      <!-- Today's Mission (random tasks) -->
        <div class="card-game" style="border-color: #bbf7d0; border-bottom-color: #34d399">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-1.5">
              <PhTarget :size="18" weight="duotone" color="#10b981" />
              <p class="text-base font-black text-gray-800">Today's Mission</p>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-xs font-black text-emerald-700 bg-emerald-100 rounded-xl px-2 py-1">
                {{ completedRandomCount }}/{{ randomTasks.length }} done
              </span>
              <div class="flex items-center gap-1">
                <button @click="handleRefresh"
                  class="w-7 h-7 rounded-xl flex items-center justify-center relative"
                  :style="progressStore.refreshesLeftToday > 0
                    ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac'
                    : 'background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1; opacity: 0.5'"
                  :disabled="progressStore.refreshesLeftToday <= 0">
                  <PhArrowsClockwise :size="14" weight="duotone"
                    :color="progressStore.refreshesLeftToday > 0 ? '#16a34a' : '#94a3b8'" />
                </button>
                <span class="text-xs font-bold text-gray-400">{{ progressStore.refreshesLeftToday }}/3 rerolls</span>
              </div>
            </div>
          </div>
          <div v-if="loadingTasks" class="flex items-center justify-center py-6 gap-2">
            <PhSpinner :size="20" weight="duotone" color="#10b981" class="animate-spin" />
            <span class="text-sm font-bold text-gray-400">Loading tasks...</span>
          </div>
          <div v-else class="flex flex-col gap-2">
            <div v-for="task in sortedRandomTasks" :key="task.taskId"
              class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all"
              :style="task.done
                ? 'background: #f0fdf4; border: 2px solid #bbf7d0'
                : navStore.isActive(taskNavId(task))
                  ? (navStore.arrived
                      ? 'background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #34d399'
                      : 'background:#f0fdf4;border:2px solid #86efac;border-bottom:3px solid #34d399')
                  : 'background: #f8fafc; border: 2px solid #e2e8f0'"
              @click="navStore.isActive(taskNavId(task)) && !task.done ? null : openConfirm(task)">
              <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
                :style="task.done || navStore.isActive(taskNavId(task)) ? 'background: #dcfce7' : 'background: #f1f5f9'">
                <PhCamera :size="18" weight="duotone" :color="task.done || navStore.isActive(taskNavId(task)) ? '#16a34a' : '#94a3b8'" />
              </div>
              <div class="flex-1">
                <div class="flex items-center gap-1.5">
                  <p class="text-sm font-bold"
                    :style="task.done
                      ? 'color: #16a34a; text-decoration: line-through'
                      : navStore.isActive(taskNavId(task)) ? 'color:#15803d' : 'color: #374151'">
                    {{ task.taskName }}
                  </p>
                  <span v-if="!task.done && navStore.isActive(taskNavId(task))"
                    class="text-xs font-black px-1.5 py-0.5 rounded-md flex-shrink-0"
                    style="background:#dcfce7;color:#15803d">
                    {{ navStore.arrived ? 'Arrived' : 'Navigating' }}
                  </span>
                </div>
                <p class="text-xs text-gray-400 mt-0.5">{{ task.taskDescription }}</p>
              </div>
              <div v-if="!task.done" class="flex items-center gap-1.5 flex-shrink-0">
                <div class="flex items-center gap-0.5">
                  <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                  <span class="text-xs font-black text-amber-500">+{{ task.rewardPoint }}</span>
                </div>
                <!-- Active navigation: red X (or green check on arrival) to cancel -->
                <button v-if="navStore.isActive(taskNavId(task)) && !navStore.arrived"
                  class="w-7 h-7 rounded-lg flex items-center justify-center"
                  style="background:#fef2f2;border:1.5px solid #fecaca;border-bottom:2px solid #f87171"
                  @click.stop="cancelNavigation">
                  <PhX :size="13" weight="bold" color="#ef4444" />
                </button>
                <button v-else-if="navStore.isActive(taskNavId(task)) && navStore.arrived"
                  class="w-7 h-7 rounded-lg flex items-center justify-center"
                  style="background:#f0fdf4;border:1.5px solid #bbf7d0;border-bottom:2px solid #34d399"
                  @click.stop="cancelNavigation">
                  <PhCheck :size="13" weight="bold" color="#16a34a" />
                </button>
                <button v-else-if="task.latitude != null"
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

      <!-- ═══ Today's Park (no-route parks) ═══ -->
      <div class="card-game" style="border-color: #d1fae5; border-bottom-color: #6ee7b7">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-1.5">
            <PhTree :size="18" weight="duotone" color="#10b981" />
            <p class="text-base font-black text-gray-800">Today's Park</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="text-xs font-black text-emerald-700 bg-emerald-100 rounded-xl px-2 py-1">
              {{ progressStore.parksVisitedTodayCount }}/3 done
            </span>
            <div class="flex items-center gap-1">
              <button @click="handleRecParkRefresh"
                class="w-7 h-7 rounded-xl flex items-center justify-center relative"
                :style="progressStore.refreshesLeftToday > 0
                  ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac'
                  : 'background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1; opacity: 0.5'"
                :disabled="progressStore.refreshesLeftToday <= 0">
                <PhArrowsClockwise :size="14" weight="duotone"
                  :color="progressStore.refreshesLeftToday > 0 ? '#16a34a' : '#94a3b8'"
                  :class="recParksLoading ? 'animate-spin' : ''" />
              </button>
              <span class="text-xs font-bold text-gray-400">{{ progressStore.refreshesLeftToday }}/3 rerolls</span>
            </div>
          </div>
        </div>
        <div v-if="recParksLoading && !recParks.length" class="flex items-center justify-center py-6 gap-2">
          <PhSpinner :size="20" weight="duotone" color="#10b981" class="animate-spin" />
          <span class="text-sm font-bold text-gray-400">Finding nearby parks...</span>
        </div>
        <div v-else-if="!recParksLoading && !recParks.length" class="flex flex-col items-center gap-2 py-4">
          <PhTree :size="28" weight="duotone" color="#94a3b8" />
          <p class="text-xs font-black text-gray-500 text-center">No parks available right now</p>
        </div>
        <div v-else class="flex flex-col gap-2">
          <div v-for="rp in sortedRecParks" :key="rp.parkId"
            class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all"
            :style="navStore.isActive(parkNavId(rp))
              ? (navStore.arrived
                  ? 'background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #34d399'
                  : 'background:#f0fdf4;border:2px solid #86efac;border-bottom:3px solid #34d399')
              : 'background: #f8fafc; border: 2px solid #e2e8f0'"
            @click="navStore.isActive(parkNavId(rp)) ? null : goNavigatePark(rp)">
            <div class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0"
              style="background:#ecfdf5;border:2px solid #a7f3d0;border-bottom:3px solid #6ee7b7">
              <PhTree :size="20" weight="duotone" color="#059669" />
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-1.5">
                <p class="text-sm font-bold truncate"
                  :style="navStore.isActive(parkNavId(rp)) ? 'color:#15803d' : 'color:#1f2937'">{{ rp.parkName }}</p>
                <span v-if="navStore.isActive(parkNavId(rp))"
                  class="text-xs font-black px-1.5 py-0.5 rounded-md flex-shrink-0"
                  :style="navStore.arrived ? 'background:#dcfce7;color:#16a34a' : 'background:#dcfce7;color:#15803d'">
                  {{ navStore.arrived ? 'Arrived' : 'Navigating' }}
                </span>
              </div>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="text-xs font-semibold text-gray-400">{{ formatDistM(rp.distance) }}</span>
              </div>
              <div class="flex flex-wrap gap-1 mt-1.5">
                <span class="rec-park-tag" :style="sizeTagStyle(rp.parkHa)">
                  <PhMapPin :size="9" weight="bold" />
                  {{ rp.parkHa }}
                </span>
                <span class="rec-park-tag" :style="accessTagStyle(rp.transportAccessibility)">
                  <PhBus :size="9" weight="bold" />
                  {{ rp.transportAccessibility }}
                </span>
                <span class="rec-park-tag" :style="richnessTagStyle(rp.taskRichness)">
                  <PhFlower :size="9" weight="bold" />
                  {{ rp.taskRichness }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <div class="flex items-center gap-0.5">
                <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                <span class="text-xs font-black text-amber-500">+50</span>
              </div>
              <!-- Active: red X to cancel navigation; otherwise nav arrow -->
              <button v-if="navStore.isActive(parkNavId(rp)) && !navStore.arrived"
                class="w-8 h-8 rounded-xl flex items-center justify-center"
                style="background:#fef2f2;border:2px solid #fecaca;border-bottom:3px solid #f87171"
                @click.stop="cancelNavigation">
                <PhX :size="14" weight="bold" color="#ef4444" />
              </button>
              <button v-else-if="navStore.isActive(parkNavId(rp)) && navStore.arrived"
                class="w-8 h-8 rounded-xl flex items-center justify-center"
                style="background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #34d399"
                @click.stop="cancelNavigation">
                <PhCheck :size="14" weight="bold" color="#16a34a" />
              </button>
              <button v-else class="w-8 h-8 rounded-xl flex items-center justify-center"
                style="background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #86efac"
                @click.stop="goNavigatePark(rp)">
                <PhNavigationArrow :size="14" weight="duotone" color="#10b981" />
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Hidden file input -->
    <input ref="fileInput" type="file" accept="image/*" capture="environment"
      class="hidden" @change="handlePhotoCapture" />

    <!-- Onboarding overlay -->
    <Teleport to="body">
      <div v-if="showOnboarding" class="fixed inset-0 z-[999]" @click="nextOnboardingStep">
        <!-- Dim background -->
        <div class="absolute inset-0 bg-black/50"></div>

        <!-- Step 1: Today's Mission -->
        <div v-if="onboardingStep === 0" class="ob-card" style="top: 56%; left: 50%; transform: translateX(-50%);">
          <div class="ob-arrow-up"></div>
          <div class="flex items-center gap-2 mb-2">
            <PhTarget :size="20" weight="duotone" color="#10b981" />
            <p class="text-base font-black text-gray-800">Today's Mission</p>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed">
            Each day you get random photo tasks. Go to the location, take a photo, and our AI checks if it matches. Complete tasks to earn XP!
          </p>
          <p class="text-sm text-gray-600 leading-relaxed mt-2">
            Tap the refresh button to reroll tasks (3 times per day).
          </p>
          <div class="ob-footer">
            <span class="text-xs font-bold text-gray-400">1 / 3</span>
            <button class="ob-next-btn" @click.stop="nextOnboardingStep">Next</button>
          </div>
        </div>

        <!-- Step 2: Today's Park -->
        <div v-if="onboardingStep === 1" class="ob-card" style="bottom: 22%; left: 50%; transform: translateX(-50%);">
          <div class="flex items-center gap-2 mb-2">
            <PhTree :size="20" weight="duotone" color="#10b981" />
            <p class="text-base font-black text-gray-800">Today's Park</p>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed">
            Scroll down to find nearby parks. Tap a park to navigate there. Each park has tags showing useful info.
          </p>
          <div class="ob-arrow-down"></div>
          <div class="ob-footer">
            <span class="text-xs font-bold text-gray-400">2 / 3</span>
            <button class="ob-next-btn" @click.stop="nextOnboardingStep">Next</button>
          </div>
        </div>

        <!-- Step 3: Tag meanings -->
        <div v-if="onboardingStep === 2" class="ob-card" style="bottom: 16%; left: 50%; transform: translateX(-50%);">
          <div class="flex items-center gap-2 mb-2">
            <PhInfo :size="20" weight="duotone" color="#3b82f6" />
            <p class="text-base font-black text-gray-800">Understanding Park Tags</p>
          </div>
          <div class="flex flex-col gap-2.5 mt-1">
            <div class="flex items-start gap-2">
              <PhMapPin :size="16" weight="duotone" color="#4338ca" class="flex-shrink-0 mt-0.5" />
              <div>
                <p class="text-sm font-black text-gray-700">Park Size</p>
                <p class="text-xs text-gray-500">Small (&lt;1 ha): quick visits. Medium (1-5 ha): short exploration. Large (&gt;5 ha): longer walks and route adventures.</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <PhBus :size="16" weight="duotone" color="#15803d" class="flex-shrink-0 mt-0.5" />
              <div>
                <p class="text-sm font-black text-gray-700">Transport Access</p>
                <p class="text-xs text-gray-500">Easy to get to: nearby stops. Moderately easy: may need longer walk. Harder to reach: limited transport.</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <PhFlower :size="16" weight="duotone" color="#be185d" class="flex-shrink-0 mt-0.5" />
              <div>
                <p class="text-sm font-black text-gray-700">Activity Richness</p>
                <p class="text-xs text-gray-500">Lots to explore: many tasks. Some things: reasonable options. Limited: fewer exploration points.</p>
              </div>
            </div>
          </div>
          <div class="ob-footer">
            <span class="text-xs font-bold text-gray-400">3 / 3</span>
            <button class="ob-next-btn" @click.stop="nextOnboardingStep">Got it!</button>
          </div>
        </div>
      </div>
    </Teleport>
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

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useWeatherStore } from '../stores/weather'
import { useProgressStore, loadDailyTasks, saveDailyTasks, loadDailyParks, saveDailyParks } from '../stores/progress'
import { useNavigationStore } from '../stores/navigation'
import { trackEvent } from '../services/analytics'
import {
  PhSun, PhCloud, PhCloudRain, PhPawPrint, PhLightning,
  PhTarget, PhCheckCircle, PhXCircle, PhNavigationArrow,
  PhCamera, PhArrowsClockwise, PhSpinner,
  PhTree, PhMapPin, PhWarning, PhBus, PhFlower,
  PhInfo, PhX, PhCheck
} from '@phosphor-icons/vue'

const BASE_URL = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'

const authStore = useAuthStore()
const weather = useWeatherStore()
const progressStore = useProgressStore()
const navStore = useNavigationStore()
const router = useRouter()
const userName = authStore.user?.nickname || 'Explorer'

const randomTasks = ref([])
const loadingTasks = ref(false)
const showModal = ref(false)
const selectedTask = ref(null)
const fileInput = ref(null)
const capturedPhoto = ref(null)
const evaluating = ref(false)
const evalResult = ref(null)

// Location verification state
const PROXIMITY_RADIUS = 200 // meters
const locationStatus = ref('checking')
const locationMessage = ref('Checking your location...')

// Recommended parks (no-route parks)
const recParks = ref([])
const recParksLoading = ref(false)

// ─── Active navigation (shared store) ───────────────────────
// A park / task reached via the Map keeps a live route. Home shows it
// as "currently navigating": the card turns green and its action
// button becomes a red X that cancels (the only way to end it).
function parkNavId(rp) { return `park-${rp.parkId}` }
function taskNavId(t) { return t.taskId ? `task-${t.taskId}` : `park-${t.taskName}` }

const sortedRecParks = computed(() => {
  const list = [...recParks.value]
  const navId = navStore.navigatingId
  if (!navId) return list
  const idx = list.findIndex(rp => parkNavId(rp) === navId)
  if (idx > 0) {
    const [active] = list.splice(idx, 1)
    list.unshift(active)
  }
  return list
})

// Today's Mission with the task currently being navigated pinned first
// (and only when it is not already completed).
const sortedRandomTasks = computed(() => {
  const list = [...randomTasks.value]
  const navId = navStore.navigatingId
  if (!navId) return list
  const idx = list.findIndex(t => taskNavId(t) === navId && !t.done)
  if (idx > 0) {
    const [active] = list.splice(idx, 1)
    list.unshift(active)
  }
  return list
})

function cancelNavigation() {
  navStore.cancel()
}

const canTakePhoto = computed(() => {
  if (selectedTask.value?.latitude == null) return true
  return locationStatus.value === 'in_range'
})

const completedRandomCount = computed(() =>
  randomTasks.value.filter(t => t.done).length
)

// ─── Onboarding ──────────────────────────────────────────────
const ONBOARDING_KEY = 'snaphunter_home_onboarded'
const showOnboarding = ref(false)
const onboardingStep = ref(0)

const onboardingSteps = [
  { id: 'mission' },
  { id: 'parks' },
  { id: 'tags' },
]

const onboardingTooltipStyle = computed(() => '')

function nextOnboardingStep() {
  if (onboardingStep.value < onboardingSteps.length - 1) {
    onboardingStep.value++
  } else {
    showOnboarding.value = false
    localStorage.setItem(ONBOARDING_KEY, 'true')
  }
}

function checkOnboarding() {
  if (!localStorage.getItem(ONBOARDING_KEY)) {
    showOnboarding.value = true
    onboardingStep.value = 0
  }
}

// ─── Recommended parks ───────────────────────────────────────

function formatDistM(m) {
  if (m == null) return ''
  return m < 1000 ? `${Math.round(m)}m` : `${(m / 1000).toFixed(1)}km`
}

function sizeTagStyle(parkHa) {
  if (!parkHa) return 'background:#f1f5f9;color:#64748b'
  if (parkHa.toLowerCase().includes('large')) return 'background:#dbeafe;color:#1d4ed8'
  if (parkHa.toLowerCase().includes('medium')) return 'background:#e0e7ff;color:#4338ca'
  return 'background:#f1f5f9;color:#64748b'
}

function accessTagStyle(access) {
  if (!access) return 'background:#f1f5f9;color:#64748b'
  if (access.toLowerCase().includes('high')) return 'background:#dcfce7;color:#15803d'
  if (access.toLowerCase().includes('medium')) return 'background:#fef9c3;color:#a16207'
  return 'background:#fef2f2;color:#b91c1c'
}

function richnessTagStyle(richness) {
  if (!richness) return 'background:#f1f5f9;color:#64748b'
  if (richness.toLowerCase().includes('high')) return 'background:#fce7f3;color:#be185d'
  if (richness.toLowerCase().includes('medium')) return 'background:#fff7ed;color:#c2410c'
  return 'background:#f5f5f4;color:#78716c'
}

async function fetchRecommendedParks(force = false) {
  recParksLoading.value = true
  try {
    // Get user location first
    const pos = await new Promise((resolve, reject) => {
      navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 10000 })
    })
    const res = await axios.get(`${BASE_URL}/api/common-parks`, {
      params: {
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        random: force,
      }
    })
    recParks.value = res.data || []
    saveDailyParks(recParks.value)
  } catch (e) {
    console.error('Failed to fetch recommended parks:', e)
  } finally {
    recParksLoading.value = false
  }
}

// Same daily-persistence model as Today's Mission: use the cached
// list for the rest of the day, only re-fetch when the day rolls
// over (00:00) or the user spends a reroll.
async function loadOrFetchRecommendedParks() {
  const cached = loadDailyParks()
  if (cached && cached.length > 0) {
    recParks.value = cached
  } else {
    await fetchRecommendedParks()
  }
}

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

function handleRecParkRefresh() {
  if (!progressStore.useRefresh()) return
  fetchRecommendedParks(true)
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
  if (task) {
    task.done = true
    progressStore.completeTask(task.rewardPoint || 10)
    if (weather.desc === 'Clear sky') {
      progressStore.completeSunnyTask()
    }
    saveDailyTasks(randomTasks.value)
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
      navId: task.taskId ? `task-${task.taskId}` : `park-${task.taskName}`,
    }
  })
}

function goNavigatePark(rp) {
  if (rp.latitude == null || rp.longitude == null) return
  // NOTE: tapping Navigate is only intent, not an actual visit. The park
  // is marked visited later by the map's GPS arrival check, so we do NOT
  // record a visit here (doing so wrongly flipped parks to "visited").
  trackEvent('park_navigate', { parkId: rp.parkId, parkName: rp.parkName })
  router.push({
    path: '/map',
    query: {
      navLat: String(rp.latitude),
      navLng: String(rp.longitude),
      navName: rp.parkName,
      navId: `park-${rp.parkId}`,
    }
  })
}

onMounted(() => {
  progressStore.init()
  navStore.load()
  if (!weather.temp) weather.fetchWeather()
  loadOrFetchRandomTasks()
  loadOrFetchRecommendedParks()
  checkOnboarding()
})
</script>
<style>
.rec-park-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 7px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 800;
  line-height: 1;
  font-family: var(--font-game), system-ui, sans-serif
}

.ob-card {
  position: absolute;
  width: calc(100% - 32px);
  max-width: 360px;
  padding: 20px;
  border-radius: 24px;
  background: white;
  border: 2px solid #d1fae5;
  border-bottom: 4px solid #34d399;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  z-index: 1000;
  font-family: var(--font-game), system-ui, sans-serif
}

.ob-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px
}

.ob-next-btn {
  padding: 8px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-bottom: 3px solid #047857;
  color: white;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
  font-family: var(--font-game), system-ui, sans-serif
}

.ob-arrow-up {
  position: absolute;
  top: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-bottom: 10px solid white
}

.ob-arrow-down {
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