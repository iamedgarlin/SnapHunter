<template>
  <div class="flex flex-col h-full" style="font-family: var(--font-game)">

    <!-- Unlock animation overlay -->
    <Transition name="unlock-pop">
      <div v-if="unlockAnim" class="unlock-overlay" @click="unlockAnim = null">
        <div class="leaflet-hud-unlock-inner">
          <svg width="24" height="24" viewBox="0 0 256 256" fill="none">
            <path
              d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.36,134.57a8,8,0,0,0,9.28,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Z"
              fill="#16a34a" opacity="0.2" />
            <path
              d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.36,134.57a8,8,0,0,0,9.28,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Z"
              fill="none" stroke="#16a34a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="128" cy="104" r="32" fill="none" stroke="#16a34a" stroke-width="16" />
          </svg>
          <p class="unlock-name">{{ unlockAnim.name }}</p>
          <div class="unlock-xp">
            <svg width="12" height="12" viewBox="0 0 256 256" fill="none">
              <path
                d="M213.85,125.46l-112,120a8,8,0,0,1-13.69-7l14.66-73.33L45.19,143.49a8,8,0,0,1-3-13l112-120a8,8,0,0,1,13.69,7L153.18,90.9l57.63,21.61a8,8,0,0,1,3,12.95Z"
                fill="#f59e0b" opacity="0.2" />
              <path
                d="M213.85,125.46l-112,120a8,8,0,0,1-13.69-7l14.66-73.33L45.19,143.49a8,8,0,0,1-3-13l112-120a8,8,0,0,1,13.69,7L153.18,90.9l57.63,21.61a8,8,0,0,1,3,12.95Z"
                fill="none" stroke="#f59e0b" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span>+50 XP</span>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Epic Park welcome overlay -->
    <Transition name="unlock-pop">
      <div v-if="epicWelcome" class="unlock-overlay" @click="epicWelcome = null">
        <div class="epic-welcome-card" @click.stop>
          <div class="epic-welcome-badge">EPIC PARK</div>
          <PhCastleTurret :size="36" weight="duotone" color="#7c3aed" />
          <p class="text-base font-black text-gray-800 mt-1">Welcome to</p>
          <p class="text-lg font-black text-violet-600">{{ epicWelcome.name }}</p>
          <p class="text-xs text-gray-500 mt-1 text-center leading-snug" style="max-width: 200px">
            {{ epicWelcome.description }}
          </p>
          <button class="epic-welcome-btn" @click="enterEpicPark(epicWelcome)">
            <PhCompass :size="16" weight="duotone" color="white" />
            Start Exploring
          </button>
          <button class="text-xs font-semibold text-gray-400 mt-1" @click="epicWelcome = null">Maybe later</button>
        </div>
      </div>
    </Transition>

    <!-- Map -->
    <div class="relative" style="height: 55vh; flex-shrink: 0">
      <div id="map" class="w-full h-full"></div>
    </div>

    <!-- Parks list -->
    <div ref="parkListRef" class="flex-1 overflow-y-auto" style="background: #f0fdf4">
      <div class="px-4 pt-4 pb-6 flex flex-col gap-3">

        <!-- Route info card -->
        <div v-if="routeInfo" class="route-info-card"
          :style="routeInfo.arrived ? 'border-color:#bbf7d0;border-bottom-color:#34d399' : ''">
          <div class="route-info-header" @click="routeStepsOpen = !routeStepsOpen">
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <PhPath :size="16" weight="duotone" :color="routeInfo.arrived ? '#16a34a' : '#3b82f6'" />
              <span class="text-xs font-black truncate"
                :style="routeInfo.arrived ? 'color:#16a34a' : 'color:#1e40af'">{{ routeInfo.name }}</span>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <span v-if="routeInfo.arrived" class="text-xs font-black text-emerald-600">Arrived!</span>
              <template v-else>
                <span class="text-xs font-semibold text-gray-500">{{ routeInfo.distance }}</span>
                <span class="text-xs font-semibold text-gray-500">~{{ routeInfo.duration }}</span>
              </template>
            </div>
            <button v-if="!routeInfo.arrived" class="flex-shrink-0 ml-1" @click.stop="voiceEnabled = !voiceEnabled">
              <PhSpeakerHigh v-if="voiceEnabled" :size="16" weight="duotone" color="#3b82f6" />
              <PhSpeakerSlash v-else :size="16" weight="duotone" color="#94a3b8" />
            </button>
            <PhCaretDown v-if="routeInfo.steps?.length && !routeInfo.arrived" :size="14" weight="bold" color="#94a3b8"
              class="flex-shrink-0 ml-1 transition-transform duration-200"
              :style="routeStepsOpen ? 'transform:rotate(180deg)' : ''" />
          </div>
          <div v-if="routeStepsOpen && routeInfo.steps?.length && !routeInfo.arrived" class="route-steps-list">
            <div v-for="(step, i) in routeInfo.steps" :key="i" class="route-step-item">
              <div class="route-step-icon">
                <component :is="stepIcon(step.modifier)" :size="14" weight="bold" color="#3b82f6" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-gray-700 leading-tight">{{ step.instruction }}</p>
                <p v-if="step.name" class="text-xs text-gray-400 leading-tight mt-0.5">{{ step.name }}</p>
              </div>
              <span class="text-xs font-semibold text-gray-400 flex-shrink-0">{{ step.distanceText }}</span>
            </div>
          </div>
        </div>

        <!-- ═══ Epic Parks ═══ -->
        <div v-if="epicParks.length" class="flex items-center justify-between mt-1">
          <div class="flex items-center gap-1.5">
            <PhCastleTurret :size="16" weight="duotone" color="#7c3aed" />
            <p class="text-sm font-black text-violet-700">Epic Parks</p>
          </div>
          <span class="text-xs font-black text-violet-600 bg-violet-100 rounded-xl px-2 py-1">
            {{ epicUnlockedCount }} / {{ epicParks.length }} unlocked
          </span>
        </div>

        <div v-for="ep in epicParks" :key="'epic-' + ep.id"
          class="card-game flex items-center gap-3 cursor-pointer active:scale-95 transition-all"
          :style="ep.unlocked
            ? 'border-color:#ddd6fe;border-bottom-color:#8b5cf6;background:linear-gradient(135deg,#faf5ff,#f5f3ff)'
            : 'border-color:#e2e8f0;border-bottom-color:#cbd5e1'"
          @click="focusPark(ep)">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
            :style="ep.unlocked
              ? 'background:#ede9fe;border:2px solid #ddd6fe;border-bottom:3px solid #a78bfa'
              : 'background:#f1f5f9;border:2px solid #e2e8f0;border-bottom:3px solid #cbd5e1'">
            <PhCastleTurret :size="24" weight="duotone" :color="ep.unlocked ? '#7c3aed' : '#94a3b8'" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-black truncate" :style="ep.unlocked ? 'color:#5b21b6' : 'color:#64748b'">{{ ep.name }}</p>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs font-semibold text-gray-400">{{ formatDistance(ep.distance) }}</span>
              <div class="flex items-center gap-0.5">
                <PhLightning :size="11" weight="duotone" color="#f59e0b" />
                <span class="text-xs font-black text-amber-500">+50</span>
              </div>
              <div v-if="ep.epic?.totalBonus" class="flex items-center gap-0.5">
                <PhTrophy :size="11" weight="duotone" color="#7c3aed" />
                <span class="text-xs font-black text-violet-500">+{{ ep.epic.totalBonus }}</span>
              </div>
            </div>
          </div>
          <!-- CHANGED: purple nav button for epic parks instead of gray -->
          <button class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" :style="navigatingId === `park-${ep.id}`
            ? (routeInfo?.arrived ? 'background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #34d399'
              : 'background:#fef2f2;border:2px solid #fecaca;border-bottom:3px solid #f87171')
            : 'background:#f5f3ff;border:2px solid #ddd6fe;border-bottom:3px solid #a78bfa'"
            @click.stop="toggleNavigation({ lat: ep.lat, lng: ep.lng, name: ep.name, id: `park-${ep.id}` })">
            <PhCheck v-if="navigatingId === `park-${ep.id}` && routeInfo?.arrived" :size="16" weight="bold"
              color="#16a34a" />
            <PhX v-else-if="navigatingId === `park-${ep.id}`" :size="16" weight="bold" color="#ef4444" />
            <PhNavigationArrow v-else :size="16" weight="duotone" color="#7c3aed" />
          </button>
        </div>

        <!-- ═══ Adventure Parks (with routes) ═══ -->
        <div :class="epicParks.length ? 'mt-2' : ''">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5">
              <PhCompass :size="16" weight="duotone" color="#10b981" />
              <p class="text-sm font-black text-gray-700">Adventure Parks</p>
            </div>
            <span v-if="commonParks.length" class="text-xs font-black text-emerald-600 bg-emerald-100 rounded-xl px-2 py-1">
              {{ adventureUnlockedCount }} / {{ commonParks.length }} unlocked
            </span>
          </div>
        </div>

        <!-- Loading state -->
        <div v-if="commonParksLoading && !commonParks.length" class="flex flex-col items-center gap-2 py-6">
          <PhSpinnerGap :size="24" weight="bold" color="#10b981" class="animate-spin" />
          <p class="text-xs font-semibold text-gray-400">Finding adventure parks...</p>
        </div>

        <!-- No parks -->
        <div v-else-if="!commonParksLoading && !commonParks.length && commonParksFetched" class="card-game flex flex-col items-center gap-2 py-4">
          <PhCloudRain :size="28" weight="duotone" color="#94a3b8" />
          <p class="text-xs font-black text-gray-500 text-center">No adventure parks available right now</p>
          <p class="text-xs text-gray-400 text-center">Check back when conditions improve!</p>
        </div>

        <!-- Park recommendation cards -->
        <div v-for="cp in commonParks" :key="'common-' + cp.parkId"
          class="common-park-card cursor-pointer active:scale-[0.98] transition-all"
          @click="focusCommonPark(cp)">
          <!-- Top row: name + nav button -->
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0"
              style="background:#ecfdf5;border:2px solid #a7f3d0;border-bottom:3px solid #6ee7b7">
              <PhTree :size="20" weight="duotone" color="#059669" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-black text-gray-800 truncate">{{ cp.parkName }}</p>
              <div class="flex items-center gap-2 mt-0.5">
                <span class="text-xs font-semibold text-gray-400">{{ formatDistanceM(cp.distance) }}</span>
                <div class="flex items-center gap-0.5">
                  <PhLightning :size="11" weight="duotone" color="#f59e0b" />
                  <span class="text-xs font-black text-amber-500">+50</span>
                </div>
              </div>
            </div>
            <button class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
              :style="navigatingId === `common-${cp.parkId}`
                ? (routeInfo?.arrived ? 'background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #34d399'
                  : 'background:#fef2f2;border:2px solid #fecaca;border-bottom:3px solid #f87171')
                : 'background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #86efac'"
              @click.stop="toggleNavigation({ lat: cp.latitude, lng: cp.longitude, name: cp.parkName, id: `common-${cp.parkId}` })">
              <PhCheck v-if="navigatingId === `common-${cp.parkId}` && routeInfo?.arrived" :size="16" weight="bold"
                color="#16a34a" />
              <PhX v-else-if="navigatingId === `common-${cp.parkId}`" :size="16" weight="bold" color="#ef4444" />
              <PhNavigationArrow v-else :size="16" weight="duotone" color="#10b981" />
            </button>
          </div>
          <!-- Tags row -->
          <div class="flex flex-wrap gap-1.5 mt-2">
            <span class="common-park-tag" :style="sizeTagStyle(cp.parkHa)">
              <PhMapPin :size="10" weight="bold" />
              {{ cp.parkHa }}
            </span>
            <span class="common-park-tag" :style="accessTagStyle(cp.transportAccessibility)">
              <PhBus :size="10" weight="bold" />
              {{ cp.transportAccessibility }}
            </span>
            <span class="common-park-tag" :style="richnessTagStyle(cp.taskRichness)">
              <PhFlower :size="10" weight="bold" />
              {{ cp.taskRichness }}
            </span>
          </div>
          <!-- Description -->
          <p class="text-xs text-gray-500 mt-2 leading-relaxed">{{ cp.recommendDescription }}</p>
          <!-- Adventure button -->
          <button class="adventure-btn mt-2"
            @click.stop="startAdventure(cp)">
            <PhCompass :size="14" weight="duotone" color="white" />
            <span>Start Adventure</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Onboarding overlay -->
    <Teleport to="body">
      <div v-if="showMapOnboarding" class="map-onboarding-overlay" @click="nextMapOnboardingStep">
        <div class="absolute inset-0 bg-black/50"></div>

        <!-- Step 1: Map overview -->
        <div v-if="mapOnboardingStep === 0" class="map-ob-card" style="top: 12%; left: 50%; transform: translateX(-50%);">
          <div class="flex items-center gap-2 mb-2">
            <PhMapTrifold :size="20" weight="duotone" color="#3b82f6" />
            <p class="text-base font-black text-gray-800">Discovery Map</p>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed">
            Your blue dot shows where you are. Walk near parks to unlock them! Epic Parks have story quizzes for bonus XP.
          </p>
          <div class="map-ob-arrow-down"></div>
          <div class="map-ob-footer">
            <span class="text-xs font-bold text-gray-400">1 / 3</span>
            <button class="map-ob-next-btn" @click.stop="nextMapOnboardingStep">Next</button>
          </div>
        </div>

        <!-- Step 2: Adventure Parks -->
        <div v-if="mapOnboardingStep === 1" class="map-ob-card" style="bottom: 24%; left: 50%; transform: translateX(-50%);">
          <div class="flex items-center gap-2 mb-2">
            <PhCompass :size="20" weight="duotone" color="#10b981" />
            <p class="text-base font-black text-gray-800">Adventure Parks</p>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed">
            These parks have walking trails with photo and sensor tasks. Tap "Start Adventure" to begin a guided route! Use the green arrow to get directions.
          </p>
          <div class="map-ob-arrow-down"></div>
          <div class="map-ob-footer">
            <span class="text-xs font-bold text-gray-400">2 / 3</span>
            <button class="map-ob-next-btn" @click.stop="nextMapOnboardingStep">Next</button>
          </div>
        </div>

        <!-- Step 3: Tags -->
        <div v-if="mapOnboardingStep === 2" class="map-ob-card" style="bottom: 18%; left: 50%; transform: translateX(-50%);">
          <div class="flex items-center gap-2 mb-2">
            <PhInfo :size="20" weight="duotone" color="#3b82f6" />
            <p class="text-base font-black text-gray-800">Understanding Park Tags</p>
          </div>
          <div class="flex flex-col gap-2.5 mt-1">
            <div class="flex items-start gap-2">
              <PhMapPin :size="16" weight="duotone" color="#4338ca" class="flex-shrink-0 mt-0.5" />
              <div>
                <p class="text-sm font-black text-gray-700">Park Size</p>
                <p class="text-xs text-gray-500">Small (&lt;1 ha): quick visits. Medium (1-5 ha): short exploration. Large (&gt;5 ha): longer walks.</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <PhBus :size="16" weight="duotone" color="#15803d" class="flex-shrink-0 mt-0.5" />
              <div>
                <p class="text-sm font-black text-gray-700">Transport Access</p>
                <p class="text-xs text-gray-500">How easy to reach by public transport. Easy, moderate, or harder to reach.</p>
              </div>
            </div>
            <div class="flex items-start gap-2">
              <PhFlower :size="16" weight="duotone" color="#be185d" class="flex-shrink-0 mt-0.5" />
              <div>
                <p class="text-sm font-black text-gray-700">Activity Richness</p>
                <p class="text-xs text-gray-500">How many exploration points the park offers for tasks and discovery.</p>
              </div>
            </div>
          </div>
          <div class="map-ob-footer">
            <span class="text-xs font-bold text-gray-400">3 / 3</span>
            <button class="map-ob-next-btn" @click.stop="nextMapOnboardingStep">Got it!</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { useProgressStore } from '../stores/progress'
import { trackEvent } from '../services/analytics'
import {
  PhNavigationArrow, PhTree, PhSealCheck, PhX, PhPath, PhCheck,
  PhCaretDown, PhArrowUp, PhArrowBendDownRight, PhArrowBendDownLeft,
  PhArrowUUpRight, PhArrowUUpLeft, PhCastleTurret, PhCompass,
  PhSpeakerHigh, PhSpeakerSlash, PhLightning, PhTrophy,
  PhSpinnerGap, PhCloudRain, PhMapPin, PhBus,
  PhFlower, PhSun, PhCloud, PhCloudSun, PhSnowflake, PhCloudFog, PhThermometerSimple,
  PhMapTrifold, PhInfo
} from '@phosphor-icons/vue'

const PARKS_UNLOCK_KEY = 'snaphunter_parks_unlocked'
const MAP_ONBOARDING_KEY = 'snaphunter_map_onboarded'

// ─── Map onboarding ─────────────────────────────────────────
const showMapOnboarding = ref(false)
const mapOnboardingStep = ref(0)

const mapOnboardingSteps = [
  { id: 'map' },
  { id: 'adventure' },
  { id: 'tags' },
]

function nextMapOnboardingStep() {
  if (mapOnboardingStep.value < mapOnboardingSteps.length - 1) {
    mapOnboardingStep.value++
  } else {
    showMapOnboarding.value = false
    localStorage.setItem(MAP_ONBOARDING_KEY, 'true')
  }
}

function checkMapOnboarding() {
  if (!localStorage.getItem(MAP_ONBOARDING_KEY)) {
    showMapOnboarding.value = true
    mapOnboardingStep.value = 0
  }
}

const UNLOCK_RADIUS_KM = 0.2
const ARRIVAL_RADIUS_KM = 0.05
const EPIC_TRIGGER_RADIUS_KM = 0.4

/* ─── API ─── */
const API_BASE = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'

// Epic parks data fetched from API
const epicParksMap = ref({})  // { parkId: { name, description, lat, lng, totalBonus } }

async function fetchEpicParks() {
  try {
    const res = await axios.get(`${API_BASE}/api/epic-parks`)
    const data = res.data
    const map = {}

    for (const ep of data) {
      let totalBonus = 0

      try {
        const storiesRes = await axios.get(
          `${API_BASE}/api/epic-parks/stories`,
          { params: { parkId: ep.parkId } }
        )

        for (const story of storiesRes.data) {
          // Prefer summary fields from the stories API so the browser does not make
          // an intentional final request that returns 404.
          const storyBonus = Number(
            story.totalBonus ?? story.totalReward ?? story.bonusReward ?? story.reward ?? 0
          )

          if (storyBonus > 0) {
            totalBonus += storyBonus
            continue
          }

          if (Array.isArray(story.questions)) {
            totalBonus += story.questions.reduce((sum, q) => sum + Number(q.reward || 0), 0)
            continue
          }

          const questionCount = Number(
            story.questionCount ?? story.totalQuestions ?? story.questionsCount ?? 0
          )

          if (!questionCount || questionCount <= 0) {
            continue
          }

          for (let idx = 1; idx <= questionCount; idx++) {
            const qRes = await axios.get(
              `${API_BASE}/api/epic-parks/stories/question`,
              {
                params: {
                  storyId: story.storyId,
                  orderIndex: idx,
                },
              }
            )

            const question = qRes.data

            if (!question || !question.questionId) {
              continue
            }

            totalBonus += Number(question.reward || 0)
          }
        }
      } catch (err) {
        console.error('Fetch story error:', err)
      }

      map[ep.parkId] = {
        name: ep.parkName,
        description: ep.description,
        lat: ep.latitude,
        lng: ep.longitude,
        totalBonus,
      }

      const exists = parks.value.find(p => p.id === ep.parkId)

      if (exists) {
        exists.name = ep.parkName
        exists.lat = ep.latitude
        exists.lng = ep.longitude
      } else {
        parks.value.push({
          id: ep.parkId,
          name: ep.parkName,
          lat: ep.latitude,
          lng: ep.longitude,
          unlocked: false,
          distance: null,
        })
      }
    }

    epicParksMap.value = map
  } catch (e) {
    console.error('Failed to fetch epic parks:', e)
  }
}

/* ─── Common Parks (API-driven recommendations) ─── */
const commonParks = ref([])
const commonParksLoading = ref(false)
const commonParksFetched = ref(false)
const commonParkMarkers = {}

async function fetchCommonParks() {
  if (!userPos.value) return
  commonParksLoading.value = true
  try {
    const res = await axios.get(`${API_BASE}/api/common-route-parks`, {
      params: {
        latitude: userPos.value.lat,
        longitude: userPos.value.lng,
      }
    })
    commonParks.value = res.data || []
    commonParksFetched.value = true

    // Clear old common park markers
    Object.values(commonParkMarkers).forEach(m => m.remove())
    Object.keys(commonParkMarkers).forEach(k => delete commonParkMarkers[k])

    // Add markers for common parks on the map
    if (map) {
      for (const cp of commonParks.value) {
        const m = L.marker([cp.latitude, cp.longitude], {
          icon: makePinIcon(false, false),
        }).addTo(map)
          .bindPopup(commonParkPopupHtml(cp), { closeButton: false, offset: [0, -8] })
        commonParkMarkers[cp.parkId] = m
      }
    }
  } catch (e) {
    console.error('Failed to fetch adventure parks:', e)
    commonParks.value = []
    commonParksFetched.value = true
  } finally {
    commonParksLoading.value = false
  }
}

function commonParkPopupHtml(cp) {
  return `<div style="font-family:sans-serif;text-align:center;padding:4px 2px">
    <p style="font-weight:900;font-size:13px;margin:0 0 2px">${cp.parkName}</p>
    <p style="font-size:10px;color:#059669;margin:0">${cp.parkHa} · ${cp.transportAccessibility}</p></div>`
}

/* ─── Other Parks (all remaining parks, map markers only) ─── */
// Every park that is NOT an Epic park and NOT an Adventure (route) park
// is still shown on the map as a small muted pin, so kids can see there
// are more green spaces around them even if they have no special route.
const otherParks = ref([])
const otherParkMarkers = {}

function makeOtherParkIcon(visited) {
  // Same teardrop pin as makePinIcon, just a touch smaller so it reads
  // as a secondary park. Gray until visited, green once visited —
  // exactly like the Epic / Adventure unlock behaviour.
  const fill = visited ? '#16a34a' : '#cbd5e1'
  const stroke = visited ? '#064e3b' : '#94a3b8'
  const s = 18
  return L.divIcon({
    className: '',
    html: `<div style="width:${s}px;height:${Math.round(s * 1.25)}px;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.2))">
      <svg viewBox="0 0 32 40" width="${s}" height="${Math.round(s * 1.25)}">
        <path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
        <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
        ${visited ? `<path d="M13 12.5l2 2 4-4" fill="none" stroke="${stroke}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>` : ''}
      </svg></div>`,
    iconSize: [s, Math.round(s * 1.25)], iconAnchor: [s / 2, Math.round(s * 1.25)], popupAnchor: [0, -Math.round(s * 1.25)],
  })
}

function otherParkPopupHtml(p, visited) {
  const meta = [p.parkHa, p.transportAccessibility].filter(Boolean).join(' · ')
  return `<div style="font-family:sans-serif;text-align:center;padding:4px 2px">
    <p style="font-weight:900;font-size:13px;margin:0 0 2px">${p.parkName}</p>
    ${meta ? `<p style="font-size:10px;color:#059669;margin:0 0 2px">${meta}</p>` : ''}
    <p style="font-size:11px;color:${visited ? '#16a34a' : '#94a3b8'};margin:0">${visited ? '✓ Visited' : 'Visit to unlock'}</p></div>`
}

function clearOtherParkMarkers() {
  Object.values(otherParkMarkers).forEach(m => m.remove())
  Object.keys(otherParkMarkers).forEach(k => delete otherParkMarkers[k])
}

// Re-derive which parks are "other" and refresh their markers. Called
// after all-parks loads and whenever epic / adventure sets change so a
// park never gets pinned twice, and whenever the visited set changes so
// markers flip gray -> green once the park has been visited.
function refreshOtherParkMarkers() {
  if (!map) return
  const epicIds = new Set(Object.keys(epicParksMap.value).map(String))
  const advIds = new Set(commonParks.value.map(cp => String(cp.parkId)))
  const visited = visitedParkIdSet.value

  clearOtherParkMarkers()
  for (const p of otherParks.value) {
    const id = String(p.parkId)
    if (epicIds.has(id) || advIds.has(id)) continue
    if (p.latitude == null || p.longitude == null) continue
    const isVisited = visited.has(id)
    const m = L.marker([p.latitude, p.longitude], {
      icon: makeOtherParkIcon(isVisited),
      zIndexOffset: isVisited ? -50 : -100, // visited float a bit above unvisited, both under epic/adventure
    }).addTo(map)
      .bindPopup(otherParkPopupHtml(p, isVisited), { closeButton: false, offset: [0, -8] })
    otherParkMarkers[id] = m
  }
}

async function fetchOtherParks() {
  if (!userPos.value) return
  try {
    const res = await axios.get(`${API_BASE}/api/all-parks`, {
      params: {
        latitude: userPos.value.lat,
        longitude: userPos.value.lng,
      }
    })
    otherParks.value = Array.isArray(res.data) ? res.data : []
    refreshOtherParkMarkers()
  } catch (e) {
    console.error('Failed to fetch all parks:', e)
    otherParks.value = []
  }
}

function focusCommonPark(cp) {
  if (map) {
    map.setView([cp.latitude, cp.longitude], 16)
    commonParkMarkers[cp.parkId]?.openPopup()
  }
}

function startAdventure(cp) {
  router.push({
    path: '/adventure',
    query: { parkId: String(cp.parkId), parkName: cp.parkName },
  })
}

/* ─── Tag styling helpers ─── */
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

/* ─── Weather ─── */
const weather = ref(null)

async function fetchWeather(lat, lng) {
  try {
    const res = await axios.get('https://api.open-meteo.com/v1/forecast', {
      params: {
        latitude: lat,
        longitude: lng,
        current: 'temperature_2m,weather_code,uv_index',
        timezone: 'auto',
      }
    })
    const c = res.data?.current
    if (c) {
      weather.value = {
        temp: Math.round(c.temperature_2m),
        weatherCode: c.weather_code,
        uv: c.uv_index != null ? Math.round(c.uv_index) : null,
      }
      updateWeatherHud()
    }
  } catch (e) {
    console.error('Weather fetch error:', e)
  }
}

function weatherLabel(code) {
  if (code == null) return 'Unknown'
  if (code === 0) return 'Clear'
  if (code <= 3) return 'Cloudy'
  if (code <= 48) return 'Foggy'
  if (code <= 67) return 'Rainy'
  if (code <= 77) return 'Snowy'
  if (code <= 82) return 'Showers'
  if (code <= 86) return 'Snow Showers'
  return 'Stormy'
}

function weatherEmoji(code) {
  if (code == null) return '🌤'
  if (code === 0) return '☀️'
  if (code <= 2) return '⛅'
  if (code === 3) return '☁️'
  if (code <= 48) return '🌫️'
  if (code <= 67) return '🌧️'
  if (code <= 77) return '❄️'
  if (code <= 82) return '🌦️'
  if (code <= 86) return '🌨️'
  return '⛈️'
}

function uvColor(uv) {
  if (uv == null) return '#94a3b8'
  if (uv <= 2) return '#22c55e'
  if (uv <= 5) return '#f59e0b'
  if (uv <= 7) return '#f97316'
  if (uv <= 10) return '#ef4444'
  return '#7c3aed'
}

function uvLabel(uv) {
  if (uv == null) return ''
  if (uv <= 2) return 'Low'
  if (uv <= 5) return 'Moderate'
  if (uv <= 7) return 'High'
  if (uv <= 10) return 'Very High'
  return 'Extreme'
}

let weatherHudEl = null
function updateWeatherHud() {
  if (!weatherHudEl || !weather.value) return
  const w = weather.value
  weatherHudEl.innerHTML = `
    <span style="font-size:14px;line-height:1">${weatherEmoji(w.weatherCode)}</span>
    <span>${w.temp}°C</span>
    <span style="color:${uvColor(w.uv)};font-size:10px">UV ${w.uv != null ? w.uv : '–'}</span>
  `
}

/* ─── State ─── */
const parks = ref([])

const userPos = ref(null)
const navigatingId = ref(null)
const routeInfo = ref(null)
const parkListRef = ref(null)
const unlockAnim = ref(null)
const routeStepsOpen = ref(false)
const voiceEnabled = ref(true)
const epicWelcome = ref(null)
const epicTriggered = ref(new Set())

let map = null
let userMarker = null
let watchId = null
let routeLayer = null
let taskMarker = null
const parkMarkers = {}
let unlockTimer = null
let navTarget = null
let weatherFetched = false

const route = useRoute()
const router = useRouter()
const progressStore = useProgressStore()

/* ─── Unlock persistence ─── */
function loadUnlockedParks() {
  try {
    const saved = JSON.parse(localStorage.getItem(PARKS_UNLOCK_KEY) || '[]')
    const set = new Set(saved)
    parks.value.forEach(p => { if (set.has(p.id)) p.unlocked = true })
  } catch { /* ignore */ }
}
function saveUnlockedParks() {
  const ids = parks.value.filter(p => p.unlocked).map(p => p.id)
  localStorage.setItem(PARKS_UNLOCK_KEY, JSON.stringify(ids))
}

/* ─── Helpers ─── */
function haversine(a, b, c, d) {
  const R = 6371, dLat = (c - a) * Math.PI / 180, dLng = (d - b) * Math.PI / 180
  const x = Math.sin(dLat / 2) ** 2 + Math.cos(a * Math.PI / 180) * Math.cos(c * Math.PI / 180) * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x))
}
function formatDistance(km) {
  if (km == null) return '—'
  return km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`
}
function formatDistanceM(meters) {
  if (meters == null) return '—'
  return meters < 1000 ? `${Math.round(meters)}m` : `${(meters / 1000).toFixed(1)}km`
}

/* ─── Voice ─── */
function speak(text) {
  if (!voiceEnabled.value || !('speechSynthesis' in window)) return
  speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = 'en-AU'; u.rate = 0.9; u.pitch = 1.05
  speechSynthesis.speak(u)
}

function stepIcon(mod) {
  if (!mod) return PhArrowUp
  if (mod.includes('left') && mod.includes('uturn')) return PhArrowUUpLeft
  if (mod.includes('right') && mod.includes('uturn')) return PhArrowUUpRight
  if (mod.includes('left')) return PhArrowBendDownLeft
  if (mod.includes('right')) return PhArrowBendDownRight
  return PhArrowUp
}

/* ─── Computed ─── */
const epicParks = computed(() =>
  parks.value.filter(p => epicParksMap.value[p.id])
    .map(p => ({ ...p, epic: epicParksMap.value[p.id] }))
    .sort((a, b) => (a.distance ?? 999) - (b.distance ?? 999))
)
const epicUnlockedCount = computed(() => parks.value.filter(p => p.unlocked && epicParksMap.value[p.id]).length)

// Adventure parks the user has already visited (shared visited-parks state),
// used to show "x / x unlocked" the same way Epic Parks does.
const visitedParkIdSet = computed(() => {
  const set = new Set()
  for (const r of (progressStore.visitedParkRecords || [])) set.add(String(r.parkId))
  return set
})
const adventureUnlockedCount = computed(() =>
  commonParks.value.filter(cp => visitedParkIdSet.value.has(String(cp.parkId))).length
)

// Epic and Adventure park lists load asynchronously and can resolve
// after fetchOtherParks(); re-derive the "other" markers whenever
// either set changes so a park is never pinned twice.
watch(commonParks, () => { if (otherParks.value.length) refreshOtherParkMarkers() })
watch(epicParksMap, () => { if (otherParks.value.length) refreshOtherParkMarkers() }, { deep: true })
// When the user visits a park anywhere (Home / Adventure / Tasks), its
// pin here flips from gray to green without needing a page reload.
watch(visitedParkIdSet, () => { if (otherParks.value.length) refreshOtherParkMarkers() })

/* ─── Map pin icons ─── */
function makePinIcon(unlocked, isEpic) {
  const fill = unlocked ? (isEpic ? '#8b5cf6' : '#16a34a') : '#cbd5e1'
  const stroke = unlocked ? (isEpic ? '#5b21b6' : '#064e3b') : '#94a3b8'
  const s = isEpic ? 26 : 22
  return L.divIcon({
    className: '',
    html: `<div style="width:${s}px;height:${Math.round(s * 1.25)}px;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.2))">
      <svg viewBox="0 0 32 40" width="${s}" height="${Math.round(s * 1.25)}">
        <path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
        <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
        ${isEpic && unlocked ? `<text x="16" y="15" text-anchor="middle" font-size="8" font-weight="bold" fill="${stroke}">★</text>` : ''}
      </svg></div>`,
    iconSize: [s, Math.round(s * 1.25)], iconAnchor: [s / 2, Math.round(s * 1.25)], popupAnchor: [0, -Math.round(s * 1.25)],
  })
}
function makeTaskPinIcon() {
  const s = 26
  return L.divIcon({
    className: '',
    html: `<div style="width:${s}px;height:${Math.round(s * 1.25)}px;filter:drop-shadow(0 2px 4px rgba(59,130,246,0.3))"><svg viewBox="0 0 32 40" width="${s}" height="${Math.round(s * 1.25)}"><path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z" fill="#3b82f6" stroke="#1e40af" stroke-width="1.5"/><circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/></svg></div>`,
    iconSize: [s, Math.round(s * 1.25)], iconAnchor: [s / 2, Math.round(s * 1.25)], popupAnchor: [0, -Math.round(s * 1.25)],
  })
}

/* ─── HUD ─── */
function createHudControls() {
  // Victoria badge (top left)
  const Badge = L.Control.extend({
    options: { position: 'topleft' }, onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-badge')
      el.innerHTML = `<svg width="14" height="14" viewBox="0 0 256 256" fill="none"><rect x="24" y="48" width="208" height="160" rx="8" fill="#10b981" opacity="0.2"/><rect x="24" y="48" width="208" height="160" rx="8" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><line x1="96" y1="48" x2="96" y2="208" stroke="#10b981" stroke-width="16" stroke-linecap="round"/><line x1="160" y1="48" x2="160" y2="208" stroke="#10b981" stroke-width="16" stroke-linecap="round"/><polyline points="96,128 128,96 160,128" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Victoria, AU</span>`
      L.DomEvent.disableClickPropagation(el); return el
    }
  })

  // Weather badge (top right)
  const Weather = L.Control.extend({
    options: { position: 'topright' }, onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-weather')
      el.innerHTML = `<span style="font-size:14px;line-height:1">🌤</span><span>--°C</span><span style="color:#94a3b8;font-size:10px">UV –</span>`
      weatherHudEl = el
      L.DomEvent.disableClickPropagation(el)
      return el
    }
  })

  // Center button (bottom right)
  const Center = L.Control.extend({
    options: { position: 'bottomright' }, onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-btn')
      el.innerHTML = `<svg width="18" height="18" viewBox="0 0 256 256" fill="none"><path d="M224,120,48,24a8,8,0,0,0-11.6,9.6L68,128,36.4,222.4A8,8,0,0,0,48,232l176-96a8,8,0,0,0,0-14Z" fill="#10b981" opacity="0.2"/><path d="M224,120,48,24a8,8,0,0,0-11.6,9.6L68,128,36.4,222.4A8,8,0,0,0,48,232l176-96a8,8,0,0,0,0-14Z" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><line x1="68" y1="128" x2="224" y2="128" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round"/></svg>`
      el.style.cursor = 'pointer'; L.DomEvent.disableClickPropagation(el)
      L.DomEvent.on(el, 'click', () => centerOnUser()); return el
    }
  })

  new Badge().addTo(map)
  new Weather().addTo(map)
  new Center().addTo(map)
}

function showUnlockAnim(park) {
  unlockAnim.value = { name: park.name }
  clearTimeout(unlockTimer)
  unlockTimer = setTimeout(() => { unlockAnim.value = null }, 3000)
}

/* ─── Map init ─── */
async function initMap() {
  await nextTick()

  const mapEl = document.getElementById('map')

  if (!mapEl) {
    console.warn('Leaflet map container #map was not found. Map initialisation skipped.')
    return false
  }

  if (map) {
    map.remove()
    map = null
  }

  map = L.map(mapEl, { center: [-37.8136, 144.9631], zoom: 13, zoomControl: false })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap', maxZoom: 19 }).addTo(map)
  parks.value.forEach(p => addParkMarker(p))
  createHudControls()
  map.getContainer().addEventListener('click', e => { if (e.target.closest('.js-task-cancel')) clearRoute() })
  return true
}

function parkPopupHtml(park) {
  const isEpic = !!epicParksMap.value[park.id]
  const badge = isEpic ? `<span style="display:inline-block;background:#ede9fe;color:#7c3aed;font-size:9px;font-weight:900;padding:1px 5px;border-radius:6px;margin-left:4px">EPIC</span>` : ''
  return `<div style="font-family:sans-serif;text-align:center;padding:4px 2px">
    <p style="font-weight:900;font-size:13px;margin:0 0 2px">${park.name}${badge}</p>
    <p style="font-size:11px;color:${park.unlocked ? '#16a34a' : '#94a3b8'};margin:0">${park.unlocked ? '✓ Unlocked' : 'Visit to unlock'}</p></div>`
}
function taskPopupHtml(name, subtitle) {
  const cam = `<svg width="11" height="11" viewBox="0 0 256 256" fill="none" style="display:inline-block;vertical-align:-1px;margin-right:3px"><path d="M208,56H180.28L166.65,35.56A8,8,0,0,0,160,32H96a8,8,0,0,0-6.65,3.56L75.72,56H48A24,24,0,0,0,24,80V192a24,24,0,0,0,24,24H208a24,24,0,0,0,24-24V80A24,24,0,0,0,208,56Z" fill="#3b82f6" opacity="0.2"/><path d="M208,56H180.28L166.65,35.56A8,8,0,0,0,160,32H96a8,8,0,0,0-6.65,3.56L75.72,56H48A24,24,0,0,0,24,80V192a24,24,0,0,0,24,24H208a24,24,0,0,0,24-24V80A24,24,0,0,0,208,56Z" fill="none" stroke="#3b82f6" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><circle cx="128" cy="132" r="36" fill="none" stroke="#3b82f6" stroke-width="16"/></svg>`
  const x = `<svg width="10" height="10" viewBox="0 0 256 256" fill="none" style="display:inline-block;vertical-align:-1px;margin-right:2px"><line x1="200" y1="56" x2="56" y2="200" stroke="#ef4444" stroke-width="28" stroke-linecap="round"/><line x1="200" y1="200" x2="56" y2="56" stroke="#ef4444" stroke-width="28" stroke-linecap="round"/></svg>`
  return `<div style="font-family:sans-serif;text-align:center;padding:2px 0">
    <p style="font-weight:900;font-size:12px;margin:0 0 2px;color:#1f2937">${name}</p>
    <p style="font-size:10px;color:#3b82f6;margin:0 0 6px;line-height:1.2">${subtitle || cam + 'Task location'}</p>
    <button class="js-task-cancel" style="display:inline-flex;align-items:center;justify-content:center;gap:3px;padding:3px 10px;border-radius:10px;border:1.5px solid #fecaca;border-bottom:2px solid #f87171;background:#fef2f2;color:#ef4444;font-size:10px;font-weight:800;cursor:pointer;font-family:sans-serif;outline:none">${x}Cancel</button></div>`
}

function addParkMarker(park) {
  const isEpic = !!epicParksMap.value[park.id]
  const m = L.marker([park.lat, park.lng], { icon: makePinIcon(park.unlocked, isEpic) }).addTo(map)
    .bindPopup(parkPopupHtml(park), { closeButton: false, offset: [0, -8] })
  parkMarkers[park.id] = m
}
function refreshMarker(park) {
  const m = parkMarkers[park.id]; if (!m) return
  m.setIcon(makePinIcon(park.unlocked, !!epicParksMap.value[park.id]))
  m.setPopupContent(parkPopupHtml(park))
}

/* ─── Tracking ─── */
function startTracking() {
  if (!navigator.geolocation) return
  watchId = navigator.geolocation.watchPosition(({ coords: { latitude: lat, longitude: lng } }) => {
    userPos.value = { lat, lng }
    parks.value.forEach(p => { p.distance = haversine(lat, lng, p.lat, p.lng) })
    if (!userMarker) {
      userMarker = L.marker([lat, lng], {
        icon: L.divIcon({
          className: '',
          html: `<div style="width:18px;height:18px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 0 0 5px rgba(59,130,246,0.25)"></div>`,
          iconSize: [18, 18], iconAnchor: [9, 9]
        }), zIndexOffset: 1000
      }).addTo(map)
      if (!navigatingId.value) map.setView([lat, lng], 14)

      // Fetch weather + common parks on first GPS fix
      if (!weatherFetched) {
        weatherFetched = true
        fetchWeather(lat, lng)
        fetchCommonParks()
        fetchOtherParks()
      }
    } else { userMarker.setLatLng([lat, lng]) }
    checkUnlocks(lat, lng); checkArrival(lat, lng); checkEpicParkProximity(lat, lng)
    checkParkArrival(lat, lng)
  }, err => console.warn('Geo error:', err), { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 })
}

function checkUnlocks(lat, lng) {
  parks.value.forEach(park => {
    if (park.unlocked) return
    if (haversine(lat, lng, park.lat, park.lng) <= UNLOCK_RADIUS_KM) {
      park.unlocked = true
      refreshMarker(park)
      showUnlockAnim(park)
      saveUnlockedParks()
      progressStore.visitPark(park.id)
      // Also write the full visit record (real GPS arrival) so the
      // Tasks "Parks Series" and Home counter stay in sync with the map.
      progressStore.recordParkVisit({
        parkId: park.id,
        parkName: park.name,
        latitude: park.lat,
        longitude: park.lng,
      })
      progressStore.addXp(50)
      trackEvent('park_unlocked', { parkId: park.id, parkName: park.name })
    }
  })
}

// Real GPS-arrival detection for Adventure (common) parks and the
// "other" parks. These are not in parks.value (which is epic-only), so
// they previously had no arrival check at all. Reaching one now records
// a genuine visit, which flips its map pin gray->green and marks it
// visited in the Tasks "Parks Series".
const arrivedParkIds = new Set()
function checkParkArrival(lat, lng) {
  const consider = []
  for (const cp of commonParks.value) {
    consider.push({ id: cp.parkId, name: cp.parkName, lat: cp.latitude, lng: cp.longitude })
  }
  for (const op of otherParks.value) {
    consider.push({ id: op.parkId, name: op.parkName, lat: op.latitude, lng: op.longitude })
  }
  for (const p of consider) {
    if (p.lat == null || p.lng == null) continue
    const key = String(p.id)
    if (arrivedParkIds.has(key)) continue
    if (visitedParkIdSet.value.has(key)) { arrivedParkIds.add(key); continue }
    if (haversine(lat, lng, p.lat, p.lng) <= UNLOCK_RADIUS_KM) {
      arrivedParkIds.add(key)
      progressStore.recordParkVisit({
        parkId: p.id,
        parkName: p.name,
        latitude: p.lat,
        longitude: p.lng,
      })
      progressStore.addXp(50)
      trackEvent('park_visited', { parkId: p.id, parkName: p.name })
      // refreshOtherParkMarkers is already triggered by the
      // visitedParkIdSet watcher, so the pin will turn green.
    }
  }
}

function checkEpicParkProximity(lat, lng) {
  for (const park of parks.value) {
    const ed = epicParksMap.value[park.id]; if (!ed) continue
    if (epicTriggered.value.has(park.id)) continue
    if (haversine(lat, lng, park.lat, park.lng) <= EPIC_TRIGGER_RADIUS_KM) {
      epicTriggered.value.add(park.id)
      epicWelcome.value = { id: park.id, name: park.name, description: ed.description }
      speak(`Welcome to ${park.name}! Tap Start Exploring to discover hidden treasures.`)
    }
  }
}

function enterEpicPark(w) {
  epicWelcome.value = null
  router.push({ path: '/explore', query: { parkId: String(w.id) } })
}

function checkArrival(lat, lng) {
  if (!navTarget || !navigatingId.value || routeInfo.value?.arrived) return
  if (haversine(lat, lng, navTarget.lat, navTarget.lng) <= ARRIVAL_RADIUS_KM) {
    routeInfo.value = { ...routeInfo.value, arrived: true }
    if (routeLayer) { routeLayer.remove(); routeLayer = null }
    speak(`You have arrived at ${routeInfo.value.name}.`)
  }
}

function centerOnUser() { if (map && userPos.value) map.setView([userPos.value.lat, userPos.value.lng], 15) }
function focusPark(park) { if (!map) return; map.setView([park.lat, park.lng], 16); parkMarkers[park.id]?.openPopup() }

/* ─── OSRM Navigation ─── */
async function toggleNavigation(target) {
  if (navigatingId.value === target.id) { clearRoute(); return }
  if (!userPos.value) { window.open(`https://www.google.com/maps/dir/?api=1&destination=${target.lat},${target.lng}&travelmode=walking`, '_blank'); return }

  clearRoute()
  navigatingId.value = target.id
  navTarget = { lat: target.lat, lng: target.lng }
  nextTick(() => { parkListRef.value?.scrollTo({ top: 0, behavior: 'smooth' }) })

  if (String(target.id).startsWith('task-')) {
    taskMarker = L.marker([target.lat, target.lng], { icon: makeTaskPinIcon(), zIndexOffset: 900 }).addTo(map)
      .bindPopup(taskPopupHtml(target.name), { closeButton: false, offset: [0, -8], minWidth: 120 })
  }

  const { lat: uLat, lng: uLng } = userPos.value
  try {
    const res = await fetch(`https://router.project-osrm.org/route/v1/foot/${uLng},${uLat};${target.lng},${target.lat}?overview=full&geometries=geojson&steps=true`)
    const data = await res.json()
    if (data.code !== 'Ok' || !data.routes?.length) { clearRoute(); return }

    const r = data.routes[0]
    const coords = r.geometry.coordinates.map(([lng, lat]) => [lat, lng])
    routeLayer = L.layerGroup()
    L.polyline(coords, { color: '#1e40af', weight: 7, opacity: 0.15, lineCap: 'round', lineJoin: 'round' }).addTo(routeLayer)
    L.polyline(coords, { color: '#3b82f6', weight: 4, opacity: 0.85, lineCap: 'round', lineJoin: 'round', dashArray: '12 8', className: 'route-line-animated' }).addTo(routeLayer)
    routeLayer.addTo(map)

    const isTask = String(target.id).startsWith('task-')
    map.fitBounds(L.latLngBounds(coords), { paddingTopLeft: [60, isTask ? 120 : 60], paddingBottomRight: [60, 60] })
    if (isTask && taskMarker) map.once('moveend', () => taskMarker?.openPopup())

    const distKm = r.distance / 1000, durMin = Math.round(r.duration / 60)
    const steps = []
    if (r.legs?.[0]?.steps) {
      for (const s of r.legs[0].steps) {
        if (s.maneuver?.type === 'arrive') { steps.push({ instruction: 'Arrive at destination', name: target.name, modifier: null, distanceText: '', type: 'arrive' }); continue }
        const dm = s.distance, dt = dm < 1000 ? `${Math.round(dm)}m` : `${(dm / 1000).toFixed(1)}km`, mn = s.maneuver || {}
        let inst = ''
        switch (mn.type) {
          case 'depart': inst = 'Head ' + (mn.modifier || 'forward'); break
          case 'turn': inst = 'Turn ' + (mn.modifier || '').replace('sharp ', 'sharply '); break
          case 'new name': case 'continue': inst = mn.modifier === 'straight' ? 'Continue straight' : 'Continue ' + (mn.modifier || ''); break
          case 'fork': inst = 'At the fork, keep ' + (mn.modifier || 'going'); break
          case 'end of road': inst = 'At the end of road, turn ' + (mn.modifier || ''); break
          case 'roundabout': case 'rotary': inst = 'Enter roundabout, exit ' + (mn.modifier || ''); break
          default: inst = mn.modifier ? mn.type + ' ' + mn.modifier : mn.type || 'Continue'; break
        }
        inst = inst.charAt(0).toUpperCase() + inst.slice(1)
        steps.push({ instruction: inst, name: s.name || '', modifier: mn.modifier || '', distanceText: dt, type: mn.type })
      }
    }

    routeInfo.value = {
      name: target.name,
      distance: distKm < 1 ? `${Math.round(distKm * 1000)}m` : `${distKm.toFixed(1)}km`,
      duration: durMin < 60 ? `${durMin} min` : `${Math.floor(durMin / 60)}h ${durMin % 60}m`,
      arrived: false, steps,
    }
    routeStepsOpen.value = false
    if (steps.length > 0) { const f = steps[0]; speak(`${f.instruction}${f.name ? ' on ' + f.name : ''}, ${f.distanceText}`) }
    checkArrival(uLat, uLng)
  } catch (err) { console.error('OSRM error:', err); clearRoute() }
}

function clearRoute() {
  if (routeLayer) { routeLayer.remove(); routeLayer = null }
  if (taskMarker) { taskMarker.remove(); taskMarker = null }
  navigatingId.value = null; routeInfo.value = null; routeStepsOpen.value = false; navTarget = null
  speechSynthesis?.cancel()
}

function handleRouteQuery() {
  const q = route.query
  if (q.navLat && q.navLng && q.navName) {
    const target = { lat: parseFloat(q.navLat), lng: parseFloat(q.navLng), name: q.navName, id: q.navId || `task-${q.navLat}-${q.navLng}` }
    const tryNav = () => {
      if (userPos.value && map) { toggleNavigation(target) }
      else if (map) {
        map.setView([target.lat, target.lng], 15)
        taskMarker = L.marker([target.lat, target.lng], { icon: makeTaskPinIcon(), zIndexOffset: 900 }).addTo(map)
          .bindPopup(taskPopupHtml(target.name, '<span style="color:#94a3b8">Waiting for GPS...</span>'), { closeButton: false, offset: [0, -8], minWidth: 120 })
        navigatingId.value = target.id
        const unwatch = watch(userPos, pos => { if (pos) { unwatch(); toggleNavigation(target) } })
      }
    }
    setTimeout(tryNav, 500)
  }
}

onMounted(async () => {
  progressStore.init()
  await fetchEpicParks()
  loadUnlockedParks()
  const mapReady = await initMap()
  if (mapReady) {
    startTracking()
    handleRouteQuery()
  }
  checkMapOnboarding()
})
onUnmounted(() => {
  if (watchId !== null) navigator.geolocation.clearWatch(watchId)
  clearTimeout(unlockTimer); clearRoute(); clearOtherParkMarkers(); map?.remove()
})
</script>

<style>
#map :deep(.leaflet-control) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important
}

.leaflet-hud-badge {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 6px 12px !important;
  border-radius: 16px !important;
  background: white !important;
  border: 2px solid #bbf7d0 !important;
  border-bottom: 2px solid #34d399 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
  font-family: var(--font-game), system-ui, sans-serif !important;
  font-size: 12px !important;
  font-weight: 900 !important;
  color: #047857 !important;
  line-height: 1 !important
}

.leaflet-hud-weather {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  padding: 6px 12px !important;
  border-radius: 16px !important;
  background: white !important;
  border: 2px solid #e2e8f0 !important;
  border-bottom: 2px solid #cbd5e1 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
  font-family: var(--font-game), system-ui, sans-serif !important;
  font-size: 12px !important;
  font-weight: 900 !important;
  color: #1f2937 !important;
  line-height: 1 !important
}

.leaflet-hud-btn {
  width: 42px !important;
  height: 42px !important;
  border-radius: 16px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  background: white !important;
  border: 2px solid #e2e8f0 !important;
  border-bottom: 3px solid #cbd5e1 !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
  cursor: pointer !important;
  transition: transform 0.1s !important
}

.leaflet-hud-btn:active {
  transform: scale(0.9) !important
}

.unlock-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.2);
  pointer-events: auto
}

.leaflet-hud-unlock-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 16px 24px;
  border-radius: 24px;
  background: white;
  border: 3px solid #34d399;
  border-bottom: 5px solid #16a34a;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  font-family: var(--font-game), system-ui, sans-serif
}

.unlock-name {
  font-weight: 900;
  font-size: 14px;
  color: #1f2937;
  margin: 0
}

.unlock-xp {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 900;
  font-size: 13px;
  color: #d97706
}

.epic-welcome-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 24px 28px 20px;
  border-radius: 28px;
  background: white;
  border: 3px solid #a78bfa;
  border-bottom: 5px solid #7c3aed;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
  font-family: var(--font-game), system-ui, sans-serif
}

.epic-welcome-badge {
  font-size: 9px;
  font-weight: 900;
  color: white;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  padding: 2px 10px;
  border-radius: 8px;
  letter-spacing: 1.5px;
  margin-bottom: 4px
}

.epic-welcome-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 20px;
  border-radius: 14px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  border: none;
  border-bottom: 3px solid #5b21b6;
  color: white;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
  font-family: var(--font-game), system-ui, sans-serif;
  transition: transform 0.1s
}

.epic-welcome-btn:active {
  transform: scale(0.95)
}

.unlock-pop-enter-active {
  animation: unlock-scale-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)
}

.unlock-pop-leave-active {
  animation: unlock-fade-out 0.4s ease forwards
}

@keyframes unlock-scale-in {
  from {
    transform: scale(0.6);
    opacity: 0
  }

  to {
    transform: scale(1);
    opacity: 1
  }
}

@keyframes unlock-fade-out {
  from {
    opacity: 1
  }

  to {
    opacity: 0
  }
}

.route-line-animated {
  animation: route-dash-march 1.2s linear infinite
}

@keyframes route-dash-march {
  to {
    stroke-dashoffset: -20
  }
}

.route-info-card {
  border-radius: 16px;
  background: white;
  border: 2px solid #bfdbfe;
  border-bottom: 3px solid #60a5fa;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
  font-family: var(--font-game), system-ui, sans-serif;
  overflow: hidden
}

.route-info-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  user-select: none
}

.route-steps-list {
  border-top: 1.5px solid #e0ecff;
  max-height: 200px;
  overflow-y: auto
}

.route-step-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 14px
}

.route-step-item+.route-step-item {
  border-top: 1px solid #f1f5f9
}

.route-step-icon {
  width: 24px;
  height: 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eff6ff;
  flex-shrink: 0;
  margin-top: 1px
}

/* ─── Common park card ─── */
.common-park-card {
  border-radius: 16px;
  background: white;
  border: 2px solid #d1fae5;
  border-bottom: 3px solid #6ee7b7;
  padding: 12px 14px;
  font-family: var(--font-game), system-ui, sans-serif;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.06)
}

.common-park-tag {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 2px 8px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 800;
  line-height: 1;
  font-family: var(--font-game), system-ui, sans-serif
}

.adventure-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 10px 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  border-bottom: 3px solid #047857;
  color: white;
  font-size: 13px;
  font-weight: 900;
  cursor: pointer;
  font-family: var(--font-game), system-ui, sans-serif;
  transition: transform 0.1s;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25)
}

.adventure-btn:active {
  transform: translateY(2px);
  border-bottom-width: 1px
}

.map-onboarding-overlay {
  position: fixed;
  inset: 0;
  z-index: 20000;
  isolation: isolate;
}

.map-onboarding-overlay > .absolute {
  z-index: 0;
}

.map-onboarding-tooltip {
  max-width: 320px;
  width: calc(100% - 48px);
  padding: 16px 20px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.92);
  backdrop-filter: blur(8px);
  border: 2px solid rgba(255,255,255,0.1);
  z-index: 1000;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3)
}

/* ─── Map onboarding card ─── */
.map-ob-card {
  position: absolute;
  width: calc(100% - 32px);
  max-width: 360px;
  padding: 20px;
  border-radius: 24px;
  background: white;
  border: 2px solid #d1fae5;
  border-bottom: 4px solid #34d399;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  z-index: 20001;
  font-family: var(--font-game), system-ui, sans-serif
}

.map-ob-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 16px
}

.map-ob-next-btn {
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

.map-ob-arrow-down {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 0; height: 0;
  border-left: 10px solid transparent;
  border-right: 10px solid transparent;
  border-top: 10px solid white
}

/* ─── Recommend mode toggle ─── */
.recommend-mode-toggle {
  display: flex;
  gap: 0;
  border-radius: 12px;
  background: #f1f5f9;
  padding: 3px;
  border: 2px solid #e2e8f0
}

.recommend-mode-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 6px 10px;
  border-radius: 9px;
  border: none;
  background: transparent;
  font-family: var(--font-game), system-ui, sans-serif;
  font-size: 12px;
  font-weight: 800;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
  outline: none
}

.recommend-mode-btn:active {
  transform: scale(0.96)
}

.recommend-mode-active {
  background: white;
  color: #059669;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
  border-bottom: 2px solid #34d399
}
</style>

<style scoped>
#map :deep(.leaflet-popup-content-wrapper) {
  border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 2px
}

#map :deep(.leaflet-popup-tip-container) {
  display: none
}

#map :deep(.leaflet-popup-content) {
  margin: 8px 12px
}

#map :deep(.leaflet-top.leaflet-left .leaflet-control) {
  margin-left: 16px;
  margin-top: 16px
}

#map :deep(.leaflet-top.leaflet-right .leaflet-control) {
  margin-right: 16px;
  margin-top: 16px
}

#map :deep(.leaflet-bottom.leaflet-right .leaflet-control) {
  margin-right: 16px;
  margin-bottom: 16px
}
</style>