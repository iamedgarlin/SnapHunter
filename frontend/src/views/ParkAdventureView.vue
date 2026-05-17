<template>
    <div class="adventure-root" style="font-family: var(--font-game)">

        <!-- ═══ Phase 1: Route Selection ═══ -->
        <template v-if="phase === 'select'">
            <div class="adv-topbar">
                <button class="topbar-back" @click="goBack">
                    <PhArrowLeft :size="18" weight="bold" color="#16a34a" />
                </button>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-black text-gray-800 truncate">{{ parkName }}</p>
                    <p class="text-xs font-bold text-gray-400">Choose your trail</p>
                </div>
            </div>

            <div class="select-body">
                <div class="intro-icon-wrap">
                    <PhCompass :size="32" weight="duotone" color="#16a34a" />
                </div>
                <p class="text-base font-black text-gray-800 mt-2">Pick a Trail</p>
                <p class="text-xs font-semibold text-gray-400 text-center mt-1" style="max-width: 260px">
                    Each trail visits different spots. Easier trails are shorter!
                </p>

                <div v-if="routesLoading" class="flex flex-col items-center gap-2 py-8">
                    <PhSpinnerGap :size="24" weight="bold" color="#10b981" class="animate-spin" />
                    <p class="text-xs font-semibold text-gray-400">Loading trails...</p>
                </div>

                <div v-else-if="!routes.length" class="flex flex-col items-center gap-2 py-8">
                    <PhMapPin :size="28" weight="duotone" color="#94a3b8" />
                    <p class="text-xs font-black text-gray-500 text-center">No trails available for this park yet</p>
                    <button class="text-xs font-bold text-emerald-600 mt-1" @click="goBack">Back to Map</button>
                </div>

                <div v-else class="select-routes">
                    <div v-for="r in routes" :key="r.routeId" class="route-card" :style="routeCardBorder(r.difficulty)"
                        @click="selectRoute(r)">
                        <div class="route-card-top">
                            <div class="route-diff-badge" :style="diffBadgeBg(r.difficulty)">
                                <component :is="diffIcon(r.difficulty)" :size="12" weight="bold" color="white" />
                                <span>{{ r.difficulty }}</span>
                            </div>
                            <div class="flex items-center gap-1">
                                <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                                <span class="text-xs font-black text-amber-500">{{ r.totalXp }} XP</span>
                            </div>
                        </div>
                        <p class="text-sm font-black text-gray-800 mt-2">{{ r.routeName }}</p>
                        <p class="text-xs font-semibold text-gray-500 mt-1 leading-relaxed">{{ r.storyTheme }}</p>
                        <div class="route-card-meta">
                            <div class="flex items-center gap-1">
                                <PhTimer :size="12" weight="duotone" color="#64748b" />
                                <span class="text-xs font-bold text-gray-400">~{{ r.estimatedMinutes }} min</span>
                            </div>
                            <div class="flex items-center gap-1">
                                <PhFlag :size="12" weight="duotone" color="#64748b" />
                                <span class="text-xs font-bold text-gray-400">{{ r.totalTasks }} stops</span>
                            </div>
                            <div v-if="r.distanceMeters" class="flex items-center gap-1">
                                <PhPath :size="12" weight="duotone" color="#64748b" />
                                <span class="text-xs font-bold text-gray-400">{{ formatDist(r.distanceMeters) }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>

        <!-- ═══ Phase 2: Active Route ═══ -->
        <template v-if="phase === 'active'">
            <div class="adv-topbar">
                <button class="topbar-back" @click="confirmExit">
                    <PhArrowLeft :size="18" weight="bold" color="#16a34a" />
                </button>
                <div class="flex-1 min-w-0">
                    <p class="text-sm font-black text-gray-800 truncate">{{ selectedRoute?.routeName }}</p>
                    <p class="text-xs font-bold text-gray-400">
                        Stop {{ currentWpIndex + 1 }} / {{ waypoints.length }}
                    </p>
                </div>
                <div class="topbar-xp-pill" @click="teleportToWaypoint" title="Tap to teleport (debug)" style="cursor:pointer">
                    <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                    <span class="text-xs font-black text-amber-500">{{ earnedXp }} XP</span>
                </div>
            </div>

            <!-- Progress bar -->
            <div class="progress-bar-track">
                <div class="progress-bar-fill" :style="`width: ${progressPercent}%`" />
            </div>

            <!-- Map -->
            <div class="adventure-map-wrap">
                <div id="advMap" class="adventure-map"></div>
            </div>

            <!-- Bottom card: current task -->
            <div class="task-bottom-sheet">

                <!-- Eye rest -->
                <div v-if="showEyeRest" class="eye-rest-inline">
                    <div class="eye-rest-ring-sm">
                        <svg viewBox="0 0 80 80">
                            <circle cx="40" cy="40" r="34" fill="none" stroke="#e2e8f0" stroke-width="6" />
                            <circle cx="40" cy="40" r="34" fill="none" stroke="#10b981" stroke-width="6"
                                stroke-linecap="round" :stroke-dasharray="2 * Math.PI * 34"
                                :stroke-dashoffset="2 * Math.PI * 34 * (1 - eyeRestProgress)"
                                style="transition: stroke-dashoffset 1s linear; transform: rotate(-90deg); transform-origin: center" />
                        </svg>
                        <span class="eye-rest-num-sm">{{ eyeRestSeconds }}</span>
                    </div>
                    <div>
                        <p class="text-sm font-black text-emerald-700">Rest your eyes!</p>
                        <p class="text-xs font-semibold text-gray-400">Look at the farthest thing you can see</p>
                    </div>
                </div>

                <!-- Celebration -->
                <div v-else-if="allDone" class="celebration-inline">
                    <PhTrophy :size="36" weight="duotone" color="#f59e0b" />
                    <div>
                        <p class="text-lg font-black text-gray-800">Trail Complete!</p>
                        <p class="text-sm font-semibold text-amber-500">+{{ earnedXp }} XP earned</p>
                    </div>
                    <button class="btn-game celebration-btn" @click="goBack">
                        <PhArrowLeft :size="14" weight="bold" color="white" />
                        Back to Map
                    </button>
                </div>

                <!-- Current task -->
                <template v-else-if="currentWp">
                    <div class="task-header">
                        <div class="task-type-icon" :style="taskIconStyle(currentWp.taskType)">
                            <component :is="taskTypeIcon(currentWp.taskType)" :size="20" weight="duotone"
                                :color="taskTypeColor(currentWp.taskType)" />
                        </div>
                        <div class="flex-1 min-w-0">
                            <p class="text-sm font-black text-gray-800 truncate">{{ currentWp.taskName }}</p>
                            <p class="text-xs font-semibold text-gray-400 truncate">{{ currentWp.taskDescription }}</p>
                        </div>
                        <div class="flex items-center gap-0.5">
                            <PhLightning :size="12" weight="duotone" color="#f59e0b" />
                            <span class="text-xs font-black text-amber-500">+{{ currentWp.xpReward }}</span>
                        </div>
                    </div>

                    <!-- Distance hint (if not arrived) -->
                    <div v-if="!arrivedAtWaypoint" class="distance-hint">
                        <PhNavigationArrow :size="14" weight="duotone" color="#3b82f6" />
                        <span class="text-xs font-bold text-blue-500">
                            Walk to {{ currentWp.waypointName }} ({{ distToWaypoint }})
                        </span>
                    </div>

                    <!-- Photo task UI -->
                    <div v-else-if="currentWp.taskType === 'photo'" class="photo-task-ui">
                        <div v-if="capturedPhoto" class="photo-preview">
                            <img :src="capturedPhoto" />
                        </div>
                        <div v-if="evaluating" class="flex items-center gap-2 py-1">
                            <PhSpinnerGap :size="16" weight="bold" color="#10b981" class="animate-spin" />
                            <span class="text-xs font-bold text-gray-400">Checking photo...</span>
                        </div>
                        <div v-if="evalResult" class="eval-result"
                            :class="evalResult.matched ? 'eval-pass' : 'eval-fail'">
                            <PhCheckCircle v-if="evalResult.matched" :size="16" weight="duotone" color="#16a34a" />
                            <PhXCircle v-else :size="16" weight="duotone" color="#ef4444" />
                            <span class="text-xs font-black">{{ evalResult.matched ? 'Matched!' : 'Try again' }}</span>
                            <span class="text-xs font-semibold text-gray-500 ml-1">{{ evalResult.reason }}</span>
                        </div>
                        <button v-if="!evalResult?.matched" class="btn-game photo-btn" @click="triggerCamera">
                            <PhCamera :size="16" weight="duotone" color="white" />
                            {{ capturedPhoto ? 'Retake' : 'Take Photo' }}
                        </button>
                        <button v-if="evalResult?.matched" class="btn-game photo-btn" @click="completeCurrentTask">
                            <PhCheck :size="16" weight="bold" color="white" />
                            Claim XP!
                        </button>
                    </div>

                    <!-- Sensor task UI -->
                    <div v-else class="sensor-task-ui">
                        <div class="sensor-meter-row">
                            <div class="sensor-meter">
                                <div class="sensor-meter-fill"
                                    :style="`width: ${sensorProgress * 100}%; background: ${taskTypeColor(currentWp.taskType)}`" />
                            </div>
                            <div class="sensor-stats">
                                <span class="text-sm font-black" :style="`color: ${taskTypeColor(currentWp.taskType)}`">
                                    {{ sensorDisplayValue }}
                                </span>
                                <span class="text-xs font-bold text-gray-400">{{ sensorDisplayUnit }}</span>
                            </div>
                        </div>
                        <button v-if="!sensorStarted" class="btn-game sensor-btn"
                            :style="sensorBtnBg(currentWp.taskType)" @click="startSensor">
                            <PhPlay :size="14" weight="fill" color="white" />
                            Start
                        </button>
                        <p v-else class="sensor-hint-text" :style="`color: ${taskTypeColor(currentWp.taskType)}`">
                            {{ sensorHint }}
                        </p>
                    </div>
                </template>
            </div>

            <!-- Hidden file input for photo tasks -->
            <input ref="fileInput" type="file" accept="image/*" capture="environment" class="hidden"
                @change="handlePhotoCapture" />
        </template>
    </div>

    <!-- Onboarding: Select phase (choose trail) -->
    <Teleport to="body">
      <div v-if="showSelectOb && phase === 'select'" class="fixed inset-0 z-[999]" @click="dismissSelectOb">
        <div class="absolute inset-0 bg-black/50"></div>
        <div class="ob-card-adv" style="top: 45%; left: 50%; transform: translateX(-50%);">
          <div class="ob-arrow-up-adv"></div>
          <div class="flex items-center gap-2 mb-2">
            <PhPath :size="20" weight="duotone" color="#10b981" />
            <p class="text-base font-black text-gray-800">Choose a Trail</p>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed">
            Pick a difficulty to start your adventure. Easy trails are shorter with fewer stops, harder ones offer more challenges and XP!
          </p>
          <div class="flex items-center justify-between mt-4">
            <span class="text-xs font-bold text-gray-400">Tap to continue</span>
            <button class="ob-next-btn-adv" @click.stop="dismissSelectOb">Got it!</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Onboarding: Active phase (tasks + eye rest) -->
    <Teleport to="body">
      <div v-if="showActiveOb && phase === 'active'" class="fixed inset-0 z-[999]" @click="nextActiveOb">
        <div class="absolute inset-0 bg-black/50"></div>

        <div v-if="activeObStep === 0" class="ob-card-adv" style="bottom: 28%; left: 50%; transform: translateX(-50%);">
          <div class="flex items-center gap-2 mb-2">
            <PhCamera :size="20" weight="duotone" color="#3b82f6" />
            <p class="text-base font-black text-gray-800">Complete Tasks</p>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed">
            Walk to each numbered marker on the map (within 30m). Photo tasks ask you to photograph something specific. Sensor tasks include shaking, spinning, or walking!
          </p>
          <div class="ob-arrow-down-adv"></div>
          <div class="flex items-center justify-between mt-4">
            <span class="text-xs font-bold text-gray-400">1 / 2</span>
            <button class="ob-next-btn-adv" @click.stop="nextActiveOb">Next</button>
          </div>
        </div>

        <div v-if="activeObStep === 1" class="ob-card-adv" style="top: 8%; left: 50%; transform: translateX(-50%);">
          <div class="flex items-center gap-2 mb-2">
            <PhEye :size="20" weight="duotone" color="#8b5cf6" />
            <p class="text-base font-black text-gray-800">Eye Rest & Tips</p>
          </div>
          <p class="text-sm text-gray-600 leading-relaxed">
            Between tasks, take a short eye rest break by looking into the distance. This helps prevent myopia!
          </p>
          <p class="text-sm text-gray-600 leading-relaxed mt-2">
            <PhLightning :size="12" weight="duotone" color="#f59e0b" class="inline" />
            <strong>Tip:</strong> Tap the XP badge to quickly jump to the current task location for testing.
          </p>
          <div class="ob-arrow-down-adv"></div>
          <div class="flex items-center justify-between mt-4">
            <span class="text-xs font-bold text-gray-400">2 / 2</span>
            <button class="ob-next-btn-adv" @click.stop="nextActiveOb">Let's go!</button>
          </div>
        </div>
      </div>
    </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProgressStore } from '../stores/progress'
import {
    saveAdventureProgress, loadAdventureProgress,
    loadLatestAdventureForPark, clearAdventureProgress,
} from '../stores/progress'
import { useShake, useSpin, useSky, useStep } from '../composables/useSensors'
import { trackEvent } from '../services/analytics'
import axios from 'axios'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
    PhArrowLeft, PhCompass, PhSpinnerGap, PhLightning, PhTimer, PhFlag, PhPath,
    PhPlay, PhTrophy, PhEye, PhCheck, PhCheckCircle, PhXCircle, PhCamera,
    PhNavigationArrow, PhHandGrabbing, PhArrowsClockwise, PhCloudSun, PhSneaker,
    PhStar, PhFlame, PhCrown, PhMapPin
} from '@phosphor-icons/vue'

const route = useRoute()
const router = useRouter()
const progressStore = useProgressStore()

const API_BASE = 'https://tp35-kids-c7cxb7b7f7akbkah.southeastasia-01.azurewebsites.net'
const ARRIVE_RADIUS = 30 // meters - how close user must be to trigger task

// ─── Adventure onboarding (split: select phase + active phase) ──
const OB_SELECT_KEY = 'snaphunter_adv_select_onboarded'
const OB_ACTIVE_KEY = 'snaphunter_adv_active_onboarded'
const showSelectOb = ref(false)
const showActiveOb = ref(false)
const activeObStep = ref(0)

function dismissSelectOb() {
    showSelectOb.value = false
    localStorage.setItem(OB_SELECT_KEY, 'true')
}

function nextActiveOb() {
    if (activeObStep.value < 1) { activeObStep.value++ }
    else { showActiveOb.value = false; localStorage.setItem(OB_ACTIVE_KEY, 'true') }
}

function checkSelectOb() {
    if (!localStorage.getItem(OB_SELECT_KEY)) { showSelectOb.value = true }
}

function checkActiveOb() {
    if (!localStorage.getItem(OB_ACTIVE_KEY)) { showActiveOb.value = true; activeObStep.value = 0 }
}

// ─── State ──────────────────────────────────────────────────
const phase = ref('select')
const parkId = ref(null)
const parkName = ref('')
const routes = ref([])
const routesLoading = ref(false)
const selectedRoute = ref(null)
const waypoints = ref([])
const pathSegments = ref([])
const currentWpIndex = ref(0)
const earnedXp = ref(0)

// Map
let advMap = null
let userMarker = null
let waypointMarkers = []
let pathLayers = []
let geoWatchId = null
const userPos = ref(null)

// Once the user reaches a waypoint we "latch" arrival so the task UI
// (photo preview / "Checking photo..." / result / sensor) stays mounted
// even if GPS jitter or a debug teleport later moves userPos away.
// Reset to false whenever we advance to a new waypoint.
const arrivalLatched = ref(false)

// Task state
const sensorStarted = ref(false)
const sensorProgress = ref(0)
const sensorDisplayValue = ref('0')
const sensorDisplayUnit = ref('')
const sensorHint = ref('')
let activeSensor = null

// Photo task state
const fileInput = ref(null)
const capturedPhoto = ref(null)
const evaluating = ref(false)
const evalResult = ref(null)

// Eye rest
const showEyeRest = ref(false)
const eyeRestSeconds = ref(15)
const eyeRestProgress = ref(0)
let eyeRestTimer = null

// ─── Computed ───────────────────────────────────────────────
const currentWp = computed(() => waypoints.value[currentWpIndex.value])
const allDone = computed(() => waypoints.value.length > 0 && waypoints.value.every(w => w.completed))
const progressPercent = computed(() => {
    if (!waypoints.value.length) return 0
    return Math.round((waypoints.value.filter(w => w.completed).length / waypoints.value.length) * 100)
})

const arrivedAtWaypoint = computed(() => {
    // Stay "arrived" once latched, so the photo / checking / result UI
    // does not disappear mid-flow due to GPS updates.
    if (arrivalLatched.value) return true
    if (!currentWp.value || !userPos.value) return false
    const d = haversineM(userPos.value.lat, userPos.value.lng, currentWp.value.latitude, currentWp.value.longitude)
    return d <= ARRIVE_RADIUS
})

const distToWaypoint = computed(() => {
    if (!currentWp.value || !userPos.value) return '...'
    const d = haversineM(userPos.value.lat, userPos.value.lng, currentWp.value.latitude, currentWp.value.longitude)
    return d < 1000 ? `${Math.round(d)}m` : `${(d / 1000).toFixed(1)}km`
})

// Latch arrival the moment the user genuinely enters the waypoint radius.
// After this, GPS updates can't kick them back out of the task UI.
let parkVisitRecorded = false
watch(userPos, () => {
    if (arrivalLatched.value) return
    if (!currentWp.value || !userPos.value) return
    const d = haversineM(userPos.value.lat, userPos.value.lng, currentWp.value.latitude, currentWp.value.longitude)
    if (d <= ARRIVE_RADIUS) {
        arrivalLatched.value = true
        // First real arrival inside this park = a genuine visit. Record
        // it once (shared with Home "x/3 done" + Tasks "Parks Series" +
        // map gray->green pins).
        if (!parkVisitRecorded && parkId.value) {
            parkVisitRecorded = true
            progressStore.recordParkVisit({
                parkId: parkId.value,
                parkName: parkName.value,
            })
        }
    }
})

// ─── Sensor task types (cycle through for variety) ───────────
const SENSOR_TYPES = ['shake', 'sky', 'spin', 'step']
const SENSOR_CONFIGS = {
    shake: { taskName: 'Shake Detector', taskDescription: 'Shake your phone 3 times to scan for hidden signals!', targetValue: 3 },
    sky: { taskName: 'Satellite Link', taskDescription: 'Point your phone at the sky for 3 seconds!', targetValue: 3 },
    spin: { taskName: 'Compass Calibration', taskDescription: 'Turn 360 degrees to calibrate your explorer compass!', targetValue: 360 },
    step: { taskName: 'Power Walk', taskDescription: 'Walk 15 steps to charge your explorer energy!', targetValue: 15 },
}

// ─── Helpers ────────────────────────────────────────────────
function haversineM(lat1, lng1, lat2, lng2) {
    const R = 6371000, dLat = (lat2 - lat1) * Math.PI / 180, dLng = (lng2 - lng1) * Math.PI / 180
    const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) ** 2
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}
function formatDist(m) { return m < 1000 ? `${Math.round(m)}m` : `${(m / 1000).toFixed(1)}km` }

// Helper: estimate cumulative fraction along route for a lat/lng
function fractionAlongRoute(routeCoords, lat, lng) {
    if (!routeCoords || routeCoords.length < 2) return 0
    let totalDist = 0
    const segDists = []
    for (let i = 1; i < routeCoords.length; i++) {
        const d = haversineM(routeCoords[i - 1][1], routeCoords[i - 1][0], routeCoords[i][1], routeCoords[i][0])
        segDists.push(d)
        totalDist += d
    }
    if (totalDist === 0) return 0

    // Find nearest point on route
    let bestDist = Infinity
    let bestCumDist = 0
    let cumDist = 0
    for (let i = 0; i < routeCoords.length; i++) {
        const d = haversineM(lat, lng, routeCoords[i][1], routeCoords[i][0])
        if (d < bestDist) { bestDist = d; bestCumDist = cumDist }
        if (i < segDists.length) cumDist += segDists[i]
    }
    return bestCumDist / totalDist
}

// ─── API ────────────────────────────────────────────────────
async function fetchRoutes() {
    routesLoading.value = true
    try {
        const res = await axios.get(`${API_BASE}/api/common-parks/routes`, {
            params: { parkId: parkId.value },
            timeout: 8000,
        })
        if (Array.isArray(res.data) && res.data.length) {
            routes.value = res.data.map(r => ({
                routeId: r.routeId,
                parkId: parkId.value,
                routeName: `${r.difficultyLevel} Trail`,
                difficulty: (r.difficultyLevel || 'easy').toLowerCase(),
                storyTheme: `A ${(r.distanceM / 1000).toFixed(1)}km ${(r.difficultyLevel || '').toLowerCase()} exploration route with ${r.taskCount} photo stops and ${(r.sensorPoints || []).length} sensor challenges.`,
                estimatedMinutes: Math.round((r.estimatedTimeSec || 600) / 60),
                totalTasks: r.taskCount + (r.sensorPoints || []).length,
                totalXp: (r.taskCount * 25) + ((r.sensorPoints || []).length * 20),
                distanceMeters: Math.round(r.distanceM || 0),
                // Keep raw data for later
                _raw: r,
            }))
        } else {
            routes.value = []
        }
    } catch (e) {
        console.error('Failed to fetch routes:', e)
        routes.value = []
    } finally {
        routesLoading.value = false
    }
}

async function fetchRouteDetail(routeId) {
    const routeData = routes.value.find(r => r.routeId === routeId)?._raw
    if (!routeData) return null

    try {
        // Fetch photo tasks for this route
        const res = await axios.get(`${API_BASE}/api/common-parks/routes/tasks`, {
            params: { routeId: routeId },
            timeout: 8000,
        })
        const photoTasks = Array.isArray(res.data) ? res.data : []

        // Route line coordinates [lng, lat] from GeoJSON
        const routeLineCoords = routeData.stLine?.coordinates || []

        // Build photo task waypoints - fetch details for each task
        const photoWaypoints = await Promise.all(photoTasks.map(async (t, i) => {
            let taskName = `Photo Challenge ${i + 1}`
            let taskDescription = `Take a photo at this location`
            let xpReward = 25
            try {
                const detailRes = await axios.get(`${API_BASE}/api/tasks/detail`, {
                    params: { taskId: t.taskId },
                    timeout: 5000,
                })
                if (detailRes.data) {
                    taskName = detailRes.data.taskName || taskName
                    taskDescription = detailRes.data.taskDescription || taskDescription
                    xpReward = detailRes.data.rewardPoint || xpReward
                }
            } catch { /* use defaults */ }
            return {
                waypointId: t.taskId,
                orderIndex: 0,
                latitude: t.latitude,
                longitude: t.longitude,
                waypointName: taskName,
                taskType: 'photo',
                taskName,
                taskDescription,
                targetValue: null,
                xpReward,
                _fraction: fractionAlongRoute(routeLineCoords, t.latitude, t.longitude),
            }
        }))

        // Build sensor waypoints from sensorPoints
        const sensorPoints = routeData.sensorPoints || []
        const sensorWaypoints = sensorPoints.map((sp, i) => {
            const sType = SENSOR_TYPES[i % SENSOR_TYPES.length]
            const config = SENSOR_CONFIGS[sType]
            const lat = sp.coordinates[1]
            const lng = sp.coordinates[0]
            return {
                waypointId: `sensor-${routeId}-${i}`,
                orderIndex: 0,
                latitude: lat,
                longitude: lng,
                waypointName: `Sensor Point ${i + 1}`,
                taskType: sType,
                taskName: config.taskName,
                taskDescription: config.taskDescription,
                targetValue: config.targetValue,
                xpReward: 20,
                _fraction: fractionAlongRoute(routeLineCoords, lat, lng),
            }
        })

        // Merge and sort all waypoints by their position along the route
        const allWaypoints = [...photoWaypoints, ...sensorWaypoints]
        allWaypoints.sort((a, b) => a._fraction - b._fraction)
        allWaypoints.forEach((wp, i) => { wp.orderIndex = i + 1 })

        // Build path segments from route line (connect consecutive waypoints)
        // Use the full route line as one segment visual
        const routeLatLngs = routeLineCoords.map(c => [c[1], c[0]]) // [lat, lng]
        const pathSegments = []
        if (routeLatLngs.length >= 2) {
            // Single path segment for the entire route
            pathSegments.push({
                fromWaypointIndex: 0,
                toWaypointIndex: allWaypoints.length - 1,
                geometry: routeLatLngs,
                distanceMeters: routeData.distanceM || 0,
            })
        }

        return {
            routeId,
            waypoints: allWaypoints,
            pathSegments,
        }
    } catch (e) {
        console.error('Failed to fetch route tasks:', e)
        return null
    }
}

// ─── Route selection ────────────────────────────────────────
async function selectRoute(r) {
    selectedRoute.value = r

    // Try to restore a previously saved (unfinished) run of this exact trail
    const saved = loadAdventureProgress(parkId.value, r.routeId)
    if (saved && Array.isArray(saved.waypoints) && saved.waypoints.length
        && !saved.waypoints.every(w => w.completed)) {
        waypoints.value = saved.waypoints
        pathSegments.value = saved.pathSegments || []
        currentWpIndex.value = Math.min(saved.currentWpIndex || 0, saved.waypoints.length - 1)
        earnedXp.value = saved.earnedXp || 0
        sensorStarted.value = false
        arrivalLatched.value = false
        phase.value = 'active'

        await nextTick()
        initMap()
        startGeoWatch()
        checkActiveOb()
        trackEvent('adventure_resume', { parkId: parkId.value, routeId: r.routeId, difficulty: r.difficulty })
        return
    }

    const detail = await fetchRouteDetail(r.routeId)
    if (!detail || !detail.waypoints?.length) return

    waypoints.value = detail.waypoints.map(w => ({ ...w, completed: false }))
    pathSegments.value = detail.pathSegments || []
    currentWpIndex.value = 0
    earnedXp.value = 0
    sensorStarted.value = false
    arrivalLatched.value = false
    phase.value = 'active'

    // NOTE: selecting a route is intent, not arrival. The park visit is
    // recorded only when the user physically reaches the first waypoint
    // (GPS-verified) — see the userPos watcher above.

    await nextTick()
    initMap()
    startGeoWatch()
    checkActiveOb()
    persistAdventure()
    trackEvent('adventure_start', { parkId: parkId.value, routeId: r.routeId, difficulty: r.difficulty })
}

// ─── Progress persistence ───────────────────────────────────
function persistAdventure() {
    if (!selectedRoute.value) return
    if (allDone.value) {
        // Trail finished — no need to keep saved state around
        clearAdventureProgress(parkId.value, selectedRoute.value.routeId)
        return
    }
    saveAdventureProgress(parkId.value, selectedRoute.value.routeId, {
        parkName: parkName.value,
        difficulty: selectedRoute.value.difficulty,
        routeName: selectedRoute.value.routeName,
        waypoints: waypoints.value,
        pathSegments: pathSegments.value,
        currentWpIndex: currentWpIndex.value,
        earnedXp: earnedXp.value,
    })
}

// ─── Map ────────────────────────────────────────────────────
function initMap() {
    if (advMap) { advMap.remove(); advMap = null }
    waypointMarkers = []
    pathLayers = []

    const firstWp = waypoints.value[0]
    advMap = L.map('advMap', {
        center: [firstWp.latitude, firstWp.longitude],
        zoom: 17, zoomControl: false,
    })
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap', maxZoom: 19,
    }).addTo(advMap)

    // Draw path segments
    for (const seg of pathSegments.value) {
        const coords = seg.geometry || [
            [waypoints.value[seg.fromWaypointIndex].latitude, waypoints.value[seg.fromWaypointIndex].longitude],
            [waypoints.value[seg.toWaypointIndex].latitude, waypoints.value[seg.toWaypointIndex].longitude],
        ]
        L.polyline(coords, { color: '#1e40af', weight: 7, opacity: 0.15, lineCap: 'round' }).addTo(advMap)
        const line = L.polyline(coords, { color: '#3b82f6', weight: 4, opacity: 0.7, lineCap: 'round', dashArray: '10 6' }).addTo(advMap)
        pathLayers.push(line)
    }

    // Waypoint markers
    waypoints.value.forEach((wp, i) => {
        const isActive = i === currentWpIndex.value
        const m = L.marker([wp.latitude, wp.longitude], { icon: makeWpIcon(wp, i, isActive) }).addTo(advMap)
        m.bindPopup(`<div style="text-align:center;font-family:sans-serif;padding:2px">
      <p style="font-weight:900;font-size:12px;margin:0">${wp.waypointName}</p>
      <p style="font-size:10px;color:#6b7280;margin:2px 0 0">${wp.taskName}</p></div>`, { closeButton: false })
        waypointMarkers.push(m)
    })

    // Fit to path bounds
    const allCoords = waypoints.value.map(w => [w.latitude, w.longitude])
    advMap.fitBounds(L.latLngBounds(allCoords).pad(0.15))
}

function makeWpIcon(wp, index, isActive) {
    const completed = wp.completed
    const color = completed ? '#16a34a' : isActive ? '#3b82f6' : '#94a3b8'
    const fill = completed ? '#dcfce7' : isActive ? '#dbeafe' : '#f1f5f9'
    const border = completed ? '#059669' : isActive ? '#2563eb' : '#cbd5e1'
    const label = completed ? '✓' : String(index + 1)
    const size = isActive ? 30 : 24
    return L.divIcon({
        className: '',
        html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${fill};border:3px solid ${border};display:flex;align-items:center;justify-content:center;font-size:${completed ? 12 : 11}px;font-weight:900;color:${color};box-shadow:0 2px 6px rgba(0,0,0,0.15);${isActive ? 'animation:wp-pulse 2s infinite' : ''}">${label}</div>`,
        iconSize: [size, size], iconAnchor: [size / 2, size / 2],
    })
}

function refreshWaypointMarkers() {
    waypoints.value.forEach((wp, i) => {
        const isActive = i === currentWpIndex.value
        waypointMarkers[i]?.setIcon(makeWpIcon(wp, i, isActive))
    })
}

// ─── Debug teleport ────────────────────────────────────────
function teleportToWaypoint() {
    const wp = currentWp.value
    if (!wp) return
    // Simulate arriving at the current waypoint
    userPos.value = { lat: wp.latitude, lng: wp.longitude }
    arrivalLatched.value = true
    // Debug teleport simulates a real arrival, so record the visit once
    // too — keeps testing consistent with the GPS arrival path.
    if (!parkVisitRecorded && parkId.value) {
        parkVisitRecorded = true
        progressStore.recordParkVisit({
            parkId: parkId.value,
            parkName: parkName.value,
        })
    }
    if (advMap) {
        if (!userMarker) {
            userMarker = L.marker([wp.latitude, wp.longitude], {
                icon: L.divIcon({
                    className: '',
                    html: '<div style="width:16px;height:16px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 0 0 4px rgba(59,130,246,0.25)"></div>',
                    iconSize: [16, 16], iconAnchor: [8, 8],
                }), zIndexOffset: 1000,
            }).addTo(advMap)
        } else {
            userMarker.setLatLng([wp.latitude, wp.longitude])
        }
        advMap.setView([wp.latitude, wp.longitude], 17)
    }
}

// ─── GPS ────────────────────────────────────────────────────
function startGeoWatch() {
    if (!navigator.geolocation) return
    geoWatchId = navigator.geolocation.watchPosition(
        ({ coords }) => {
            userPos.value = { lat: coords.latitude, lng: coords.longitude }
            if (advMap) {
                if (!userMarker) {
                    userMarker = L.marker([coords.latitude, coords.longitude], {
                        icon: L.divIcon({
                            className: '',
                            html: '<div style="width:16px;height:16px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 0 0 4px rgba(59,130,246,0.25)"></div>',
                            iconSize: [16, 16], iconAnchor: [8, 8],
                        }), zIndexOffset: 1000,
                    }).addTo(advMap)
                } else {
                    userMarker.setLatLng([coords.latitude, coords.longitude])
                }
            }
        },
        err => console.warn('Geo error:', err),
        { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 }
    )
}

// ─── Task completion ────────────────────────────────────────
function completeCurrentTask() {
    const wp = currentWp.value
    if (!wp || wp.completed) return

    wp.completed = true
    earnedXp.value += wp.xpReward || 20
    progressStore.addXp(wp.xpReward || 20)
    progressStore.completeTask(0)

    stopActiveSensor()
    sensorStarted.value = false
    capturedPhoto.value = null
    evalResult.value = null
    refreshWaypointMarkers()

    trackEvent('adventure_task_complete', { parkId: parkId.value, taskType: wp.taskType, waypointId: wp.waypointId })

    if (waypoints.value.every(w => w.completed)) {
        clearAdventureProgress(parkId.value, selectedRoute.value?.routeId)
        trackEvent('adventure_complete', { parkId: parkId.value, routeId: selectedRoute.value?.routeId, totalXp: earnedXp.value })
        return
    }

    persistAdventure()
    startEyeRest()
}

function onSensorComplete() { completeCurrentTask() }

// ─── Sensor management ──────────────────────────────────────
async function startSensor() {
    const wp = currentWp.value
    if (!wp) return
    sensorStarted.value = true
    sensorProgress.value = 0

    const type = wp.taskType
    const target = wp.targetValue || 10

    if (type === 'shake') activeSensor = useShake(target, onSensorComplete)
    else if (type === 'spin') activeSensor = useSpin(target, onSensorComplete)
    else if (type === 'sky') activeSensor = useSky(target, onSensorComplete)
    else if (type === 'step') activeSensor = useStep(target, onSensorComplete)

    if (activeSensor) {
        const ok = await activeSensor.start()
        if (!ok) { sensorHint.value = 'Sensor not available. Try on mobile!'; sensorStarted.value = false; return }
        watch(activeSensor.progress, (val) => { sensorProgress.value = val; updateSensorDisplay() }, { immediate: true })
    }
}

function updateSensorDisplay() {
    const wp = currentWp.value
    if (!wp || !activeSensor) return
    const target = wp.targetValue || 10
    if (wp.taskType === 'shake') {
        sensorDisplayValue.value = String(activeSensor.shakeCount?.value ?? 0)
        sensorDisplayUnit.value = `/ ${target} shakes`
        sensorHint.value = 'Shake your phone!'
    } else if (wp.taskType === 'spin') {
        sensorDisplayValue.value = `${Math.round(activeSensor.totalRotation?.value ?? 0)}°`
        sensorDisplayUnit.value = `/ ${target}°`
        sensorHint.value = 'Turn your body!'
    } else if (wp.taskType === 'sky') {
        sensorDisplayValue.value = `${(activeSensor.holdTime?.value ?? 0).toFixed(1)}s`
        sensorDisplayUnit.value = `/ ${target}s`
        sensorHint.value = activeSensor.isFacingUp?.value ? 'Scanning sky...' : 'Point phone up!'
    } else if (wp.taskType === 'step') {
        sensorDisplayValue.value = String(activeSensor.stepCount?.value ?? 0)
        sensorDisplayUnit.value = `/ ${target} steps`
        sensorHint.value = 'Keep walking!'
    }
}

function stopActiveSensor() { if (activeSensor) { activeSensor.stop(); activeSensor = null } }

// ─── Photo task ─────────────────────────────────────────────
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
    try {
        const formData = new FormData()
        formData.append('taskId', currentWp.value.waypointId)
        formData.append('file', file)
        const res = await axios.post(`${API_BASE}/api/tasks/evaluate`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
        evalResult.value = res.data
    } catch {
        evalResult.value = { matched: false, reason: 'Something went wrong. Try again.' }
    } finally {
        evaluating.value = false
        event.target.value = ''
    }
}

// ─── Eye rest ───────────────────────────────────────────────
function startEyeRest() {
    const secs = 15
    eyeRestSeconds.value = secs
    eyeRestProgress.value = 0
    showEyeRest.value = true
    let elapsed = 0
    eyeRestTimer = setInterval(() => {
        elapsed++
        eyeRestProgress.value = elapsed / secs
        eyeRestSeconds.value = secs - elapsed
        if (elapsed >= secs) {
            clearInterval(eyeRestTimer)
            eyeRestTimer = null
            showEyeRest.value = false
            advanceWaypoint()
        }
    }, 1000)
}

function advanceWaypoint() {
    stopActiveSensor()
    capturedPhoto.value = null
    evalResult.value = null
    if (currentWpIndex.value < waypoints.value.length - 1) {
        currentWpIndex.value++
        arrivalLatched.value = false
        sensorStarted.value = false
        sensorProgress.value = 0
        sensorDisplayValue.value = '0'
        refreshWaypointMarkers()
        const wp = currentWp.value
        if (wp && advMap) advMap.setView([wp.latitude, wp.longitude], 17)
        persistAdventure()
    }
}

// ─── Navigation ─────────────────────────────────────────────
function goBack() {
    // Make sure the latest state is saved before leaving so the
    // user can resume this trail later.
    if (selectedRoute.value && !allDone.value
        && waypoints.value.some(w => w.completed)) {
        persistAdventure()
    }
    cleanup()
    router.push('/map')
}
function confirmExit() {
    if (waypoints.value.some(w => w.completed) && !allDone.value) {
        if (confirm("Leave this trail? Your progress is saved — you can pick up where you left off when you come back.")) {
            goBack()
        }
    } else goBack()
}
function cleanup() {
    stopActiveSensor()
    if (eyeRestTimer) { clearInterval(eyeRestTimer); eyeRestTimer = null }
    if (geoWatchId !== null) { navigator.geolocation.clearWatch(geoWatchId); geoWatchId = null }
    if (advMap) { advMap.remove(); advMap = null }
    userMarker = null
}

// ─── Style helpers ──────────────────────────────────────────
function routeCardBorder(d) {
    if (d === 'easy') return 'border-color:#bbf7d0;border-bottom-color:#34d399'
    if (d === 'medium') return 'border-color:#fde68a;border-bottom-color:#fbbf24'
    return 'border-color:#fecaca;border-bottom-color:#f87171'
}
function diffBadgeBg(d) { return d === 'easy' ? 'background:#16a34a' : d === 'medium' ? 'background:#f59e0b' : 'background:#ef4444' }
function diffIcon(d) { return d === 'easy' ? PhStar : d === 'medium' ? PhFlame : PhCrown }
function taskTypeIcon(t) { return t === 'photo' ? PhCamera : t === 'shake' ? PhHandGrabbing : t === 'spin' ? PhArrowsClockwise : t === 'sky' ? PhCloudSun : PhSneaker }
function taskTypeColor(t) { return t === 'photo' ? '#16a34a' : t === 'shake' ? '#f59e0b' : t === 'spin' ? '#7c3aed' : t === 'sky' ? '#3b82f6' : '#10b981' }
function taskIconStyle(t) { const c = taskTypeColor(t); return `background:${c}15;border:2px solid ${c}30;border-bottom:3px solid ${c}50` }
function sensorBtnBg(t) {
    const m = { shake: 'background:#f59e0b;border-bottom-color:#d97706', spin: 'background:#7c3aed;border-bottom-color:#5b21b6', sky: 'background:#3b82f6;border-bottom-color:#1d4ed8', step: 'background:#16a34a;border-bottom-color:#059669' }
    return m[t] || ''
}

// ─── Lifecycle ──────────────────────────────────────────────
async function tryResumeOnMount() {
    const saved = loadLatestAdventureForPark(parkId.value)
    if (!saved || !Array.isArray(saved.waypoints) || !saved.waypoints.length) return false
    if (saved.waypoints.every(w => w.completed)) return false

    // Rebuild a minimal selectedRoute object from the saved metadata so the
    // active phase header + persistence keep working.
    selectedRoute.value = {
        routeId: saved.routeId,
        difficulty: saved.difficulty || 'easy',
        routeName: saved.routeName || 'Your Trail',
    }
    waypoints.value = saved.waypoints
    pathSegments.value = saved.pathSegments || []
    currentWpIndex.value = Math.min(saved.currentWpIndex || 0, saved.waypoints.length - 1)
    earnedXp.value = saved.earnedXp || 0
    sensorStarted.value = false
    arrivalLatched.value = false
    phase.value = 'active'

    await nextTick()
    initMap()
    startGeoWatch()
    checkActiveOb()
    trackEvent('adventure_resume', { parkId: parkId.value, routeId: saved.routeId })
    return true
}

onMounted(async () => {
    progressStore.init()
    parkId.value = parseInt(route.query.parkId) || 0
    parkName.value = route.query.parkName || 'Park Adventure'

    // If we have an unfinished trail for this park, jump straight back in.
    const resumed = await tryResumeOnMount()
    if (resumed) return

    fetchRoutes()
    checkSelectOb()
})
onUnmounted(() => { cleanup() })
</script>

<style scoped>
.adventure-root {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #f0fdf4;
    overflow: hidden;
    overscroll-behavior: none
}

/* Topbar */
.adv-topbar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: white;
    border-bottom: 3px solid #bbf7d0;
    flex-shrink: 0;
    z-index: 10
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
    cursor: pointer
}

.topbar-back:active {
    transform: scale(0.9)
}

.topbar-xp-pill {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 10px;
    background: #fffbeb;
    border: 2px solid #fde68a;
    flex-shrink: 0
}

.topbar-teleport {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 12px;
    background: #f5f3ff;
    border: 2px solid #ddd6fe;
    border-bottom: 3px solid #a78bfa;
    flex-shrink: 0;
    cursor: pointer;
    transition: transform 0.1s
}

.topbar-teleport:active {
    transform: scale(0.9);
    border-bottom-width: 1px
}

/* Select phase */
.select-body {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px 16px
}

.intro-icon-wrap {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ecfdf5;
    border: 3px solid #bbf7d0;
    border-bottom: 4px solid #34d399
}

.select-routes {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 16px
}

.route-card {
    border-radius: 18px;
    background: white;
    border: 2px solid;
    border-bottom-width: 4px;
    padding: 14px 16px;
    cursor: pointer;
    transition: transform 0.15s
}

.route-card:active {
    transform: scale(0.97)
}

.route-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between
}

.route-diff-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 10px;
    border-radius: 8px;
    font-size: 10px;
    font-weight: 900;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.5px
}

.route-card-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 8px
}

/* Progress bar */
.progress-bar-track {
    height: 4px;
    background: #e2e8f0;
    flex-shrink: 0
}

.progress-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #34d399, #16a34a);
    border-radius: 0 2px 2px 0;
    transition: width 0.5s
}

/* Map */
.adventure-map-wrap {
    flex: 1;
    min-height: 0;
    position: relative
}

.adventure-map {
    width: 100%;
    height: 100%
}

/* Task bottom sheet */
.task-bottom-sheet {
    flex-shrink: 0;
    background: white;
    border-top: 3px solid #bbf7d0;
    padding: 14px 16px;
    padding-bottom: max(14px, env(safe-area-inset-bottom, 14px));
    z-index: 10
}

/* Task header */
.task-header {
    display: flex;
    align-items: center;
    gap: 10px
}

.task-type-icon {
    width: 40px;
    height: 40px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0
}

/* Distance hint */
.distance-hint {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    padding: 8px 12px;
    border-radius: 12px;
    background: #eff6ff;
    border: 1.5px solid #bfdbfe
}

/* Photo task */
.photo-task-ui {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 10px
}

.photo-preview {
    border-radius: 14px;
    overflow: hidden;
    border: 2px solid #d1fae5;
    max-height: 140px
}

.photo-preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block
}

.eval-result {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 12px;
    border-radius: 12px
}

.eval-pass {
    background: #f0fdf4;
    border: 1.5px solid #bbf7d0
}

.eval-fail {
    background: #fef2f2;
    border: 1.5px solid #fecaca
}

.photo-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 20px;
    border-radius: 14px;
    font-size: 14px
}

/* Sensor task */
.sensor-task-ui {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 10px
}

.sensor-meter-row {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%
}

.sensor-meter {
    flex: 1;
    min-width: 0;
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden
}

.sensor-meter-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.2s
}

.sensor-stats {
    display: flex;
    align-items: baseline;
    gap: 4px;
    flex-shrink: 0;
    white-space: nowrap
}

.sensor-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    width: 100%;
    padding: 12px 18px;
    border-radius: 14px;
    font-size: 14px;
    border-bottom: 3px solid;
    box-sizing: border-box
}

.sensor-hint-text {
    text-align: center;
    font-size: 13px;
    font-weight: 800;
    padding: 8px 0;
    margin: 0
}

/* Eye rest */
.eye-rest-inline {
    display: flex;
    align-items: center;
    gap: 12px
}

.eye-rest-ring-sm {
    position: relative;
    width: 56px;
    height: 56px;
    flex-shrink: 0
}

.eye-rest-ring-sm svg {
    width: 100%;
    height: 100%
}

.eye-rest-num-sm {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 900;
    color: #10b981
}

/* Celebration */
.celebration-inline {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap
}

.celebration-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 10px 20px;
    border-radius: 14px;
    font-size: 13px;
    margin-left: auto
}
</style>

<style>
@keyframes wp-pulse {

    0%,
    100% {
        box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.3)
    }

    50% {
        box-shadow: 0 0 0 8px rgba(59, 130, 246, 0)
    }
}
</style>

<style>
.ob-card-adv {
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

.ob-footer-adv {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 16px
}

.ob-next-btn-adv {
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

.ob-arrow-up-adv {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 0; height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-bottom: 10px solid white
}

.ob-arrow-down-adv {
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 0; height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-top: 10px solid white
}
</style>