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
        <div v-if="epicParks.length" class="flex items-center gap-1.5 mt-1">
          <PhCastleTurret :size="16" weight="duotone" color="#7c3aed" />
          <p class="text-sm font-black text-violet-700">Epic Parks</p>
        </div>

        <div v-for="ep in epicParks" :key="'epic-' + ep.id"
          class="card-game flex items-center gap-3 cursor-pointer active:scale-95 transition-all"
          style="border-color:#ddd6fe;border-bottom-color:#8b5cf6;background:linear-gradient(135deg,#faf5ff,#f5f3ff)"
          @click="focusPark(ep)">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
            style="background:#ede9fe;border:2px solid #ddd6fe;border-bottom:3px solid #a78bfa">
            <PhCastleTurret :size="24" weight="duotone" color="#7c3aed" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5">
              <p class="text-sm font-black text-violet-700 truncate">{{ ep.name }}</p>
              <span class="text-xs font-black text-violet-500 bg-violet-100 rounded-lg px-1.5 py-0.5">EPIC</span>
            </div>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs font-semibold text-gray-400">{{ formatDistance(ep.distance) }}</span>
              <span class="text-xs text-violet-400">{{ ep.epic.poiCount }} spots to explore</span>
            </div>
          </div>
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

        <!-- ═══ Nearby Parks ═══ -->
        <div class="flex items-center justify-between" :class="epicParks.length ? 'mt-2' : ''">
          <div class="flex items-center gap-1.5">
            <PhTree :size="16" weight="duotone" color="#10b981" />
            <p class="text-sm font-black text-gray-700">Nearby Parks</p>
          </div>
          <span class="text-xs font-black text-emerald-600 bg-emerald-100 rounded-xl px-2 py-1">
            {{ unlockedCount }} / {{ parks.length }} unlocked
          </span>
        </div>

        <div v-for="park in sortedNearbyParks" :key="park.id"
          class="card-game flex items-center gap-3 cursor-pointer active:scale-95 transition-all"
          :style="park.unlocked ? 'border-color:#bbf7d0;border-bottom-color:#34d399' : ''" @click="focusPark(park)">
          <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0" :style="park.unlocked
            ? 'background:#dcfce7;border:2px solid #bbf7d0;border-bottom:3px solid #86efac'
            : 'background:#f1f5f9;border:2px solid #e2e8f0;border-bottom:3px solid #cbd5e1'">
            <PhTree :size="24" weight="duotone" :color="park.unlocked ? '#16a34a' : '#cbd5e1'" />
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5">
              <p class="text-sm font-black truncate" :style="park.unlocked ? 'color:#16a34a' : 'color:#1f2937'">{{
                park.name }}
              </p>
              <PhSealCheck v-if="park.unlocked" :size="14" weight="duotone" color="#16a34a" />
            </div>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs font-semibold text-gray-400">{{ formatDistance(park.distance) }}</span>
              <span v-if="park.distance !== null && park.distance <= 0.2" class="text-xs font-black px-1.5 py-0.5 rounded-lg"
                style="background:#fef3c7;color:#d97706">In range!</span>
            </div>
          </div>
          <button class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0" :style="navigatingId === `park-${park.id}`
            ? (routeInfo?.arrived ? 'background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #34d399'
              : 'background:#fef2f2;border:2px solid #fecaca;border-bottom:3px solid #f87171')
            : 'background:#f0fdf4;border:2px solid #bbf7d0;border-bottom:3px solid #86efac'"
            @click.stop="toggleNavigation({ lat: park.lat, lng: park.lng, name: park.name, id: `park-${park.id}` })">
            <PhCheck v-if="navigatingId === `park-${park.id}` && routeInfo?.arrived" :size="16" weight="bold"
              color="#16a34a" />
            <PhX v-else-if="navigatingId === `park-${park.id}`" :size="16" weight="bold" color="#ef4444" />
            <PhNavigationArrow v-else :size="16" weight="duotone" color="#10b981" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  PhNavigationArrow, PhTree, PhSealCheck, PhX, PhPath, PhCheck,
  PhCaretDown, PhArrowUp, PhArrowBendDownRight, PhArrowBendDownLeft,
  PhArrowUUpRight, PhArrowUUpLeft, PhCastleTurret, PhCompass,
  PhSpeakerHigh, PhSpeakerSlash
} from '@phosphor-icons/vue'

const UNLOCK_RADIUS_KM = 0.2
const ARRIVAL_RADIUS_KM = 0.05
const EPIC_TRIGGER_RADIUS_KM = 0.4

/* ─── Epic Park Data ─── */
const EPIC_PARKS_DATA = {
  2: {
    description: 'Discover history, nature, and hidden treasures in one of Melbourne\'s oldest parks.',
    poiCount: 6,
    pois: [
      { id: 'cooks-cottage', name: "Captain Cook's Cottage", lat: -37.8148, lng: 144.9802, type: 'history', brief: 'Shipped brick-by-brick from England in 1934' },
      { id: 'fairies-tree', name: "Fairies' Tree", lat: -37.8130, lng: 144.9810, type: 'culture', brief: 'A 300-year-old tree carved with fairies and elves' },
      { id: 'conservatory', name: 'Conservatory', lat: -37.8142, lng: 144.9778, type: 'nature', brief: 'A beautiful flower house built in 1930' },
      { id: 'tudor-village', name: 'Model Tudor Village', lat: -37.8125, lng: 144.9785, type: 'history', brief: 'Tiny English village gifted after World War II' },
      { id: 'elm-avenue', name: 'Avenue of Elms', lat: -37.8135, lng: 144.9770, type: 'nature', brief: 'Walk under 100-year-old elm trees' },
      { id: 'river-gums', name: 'River Red Gums', lat: -37.8150, lng: 144.9815, type: 'nature', brief: 'Ancient Australian trees sacred to Indigenous people' },
    ],
  },
}

/* ─── State ─── */
const parks = ref([
  { id: 1, name: 'Flagstaff Gardens', lat: -37.8090, lng: 144.9520, unlocked: false, distance: null },
  { id: 2, name: 'Fitzroy Gardens', lat: -37.8136, lng: 144.9793, unlocked: false, distance: null },
  { id: 3, name: 'Royal Botanic Gardens', lat: -37.8304, lng: 144.9799, unlocked: false, distance: null },
  { id: 4, name: 'Carlton Gardens', lat: -37.8033, lng: 144.9716, unlocked: false, distance: null },
  { id: 5, name: 'Yarra Park', lat: -37.8224, lng: 144.9836, unlocked: false, distance: null },
  { id: 6, name: 'Albert Park', lat: -37.8468, lng: 144.9658, unlocked: false, distance: null },
  { id: 7, name: 'Princes Park', lat: -37.7833, lng: 144.9608, unlocked: false, distance: null },
  { id: 8, name: 'Edinburgh Gardens', lat: -37.7890, lng: 144.9790, unlocked: false, distance: null },
  { id: 9, name: 'Moonee Valley Parklands', lat: -37.7607, lng: 144.9286, unlocked: false, distance: null },
  { id: 10, name: 'Jells Park', lat: -37.8980, lng: 145.2020, unlocked: false, distance: null },
])

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

const route = useRoute()
const router = useRouter()

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
  parks.value.filter(p => EPIC_PARKS_DATA[p.id])
    .map(p => ({ ...p, epic: EPIC_PARKS_DATA[p.id] }))
    .sort((a, b) => (a.distance ?? 999) - (b.distance ?? 999))
)
const sortedNearbyParks = computed(() => {
  const sorted = [...parks.value.filter(p => !EPIC_PARKS_DATA[p.id])].sort((a, b) => {
    if (a.distance == null) return 1; if (b.distance == null) return -1; return a.distance - b.distance
  })
  if (navigatingId.value) {
    const idx = sorted.findIndex(p => `park-${p.id}` === navigatingId.value)
    if (idx > 0) { const [pin] = sorted.splice(idx, 1); sorted.unshift(pin) }
  }
  return sorted
})
const unlockedCount = computed(() => parks.value.filter(p => p.unlocked).length)

/* ─── Map pin icons ─── */
function makePinIcon(unlocked, isEpic) {
  const fill = isEpic ? '#8b5cf6' : unlocked ? '#16a34a' : '#cbd5e1'
  const stroke = isEpic ? '#5b21b6' : unlocked ? '#064e3b' : '#94a3b8'
  const s = isEpic ? 26 : 22
  return L.divIcon({
    className: '',
    html: `<div style="width:${s}px;height:${Math.round(s * 1.25)}px;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.2))">
      <svg viewBox="0 0 32 40" width="${s}" height="${Math.round(s * 1.25)}">
        <path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
        <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
        ${isEpic ? `<text x="16" y="15" text-anchor="middle" font-size="8" font-weight="bold" fill="${stroke}">★</text>` : ''}
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
  const Badge = L.Control.extend({
    options: { position: 'topleft' }, onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-badge')
      el.innerHTML = `<svg width="14" height="14" viewBox="0 0 256 256" fill="none"><rect x="24" y="48" width="208" height="160" rx="8" fill="#10b981" opacity="0.2"/><rect x="24" y="48" width="208" height="160" rx="8" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><line x1="96" y1="48" x2="96" y2="208" stroke="#10b981" stroke-width="16" stroke-linecap="round"/><line x1="160" y1="48" x2="160" y2="208" stroke="#10b981" stroke-width="16" stroke-linecap="round"/><polyline points="96,128 128,96 160,128" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/></svg><span>Victoria, AU</span>`
      L.DomEvent.disableClickPropagation(el); return el
    }
  })
  const Center = L.Control.extend({
    options: { position: 'bottomright' }, onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-btn')
      el.innerHTML = `<svg width="18" height="18" viewBox="0 0 256 256" fill="none"><path d="M224,120,48,24a8,8,0,0,0-11.6,9.6L68,128,36.4,222.4A8,8,0,0,0,48,232l176-96a8,8,0,0,0,0-14Z" fill="#10b981" opacity="0.2"/><path d="M224,120,48,24a8,8,0,0,0-11.6,9.6L68,128,36.4,222.4A8,8,0,0,0,48,232l176-96a8,8,0,0,0,0-14Z" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><line x1="68" y1="128" x2="224" y2="128" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round"/></svg>`
      el.style.cursor = 'pointer'; L.DomEvent.disableClickPropagation(el)
      L.DomEvent.on(el, 'click', () => centerOnUser()); return el
    }
  })
  new Badge().addTo(map); new Center().addTo(map)
}

function showUnlockAnim(park) {
  unlockAnim.value = { name: park.name }
  clearTimeout(unlockTimer)
  unlockTimer = setTimeout(() => { unlockAnim.value = null }, 3000)
}

/* ─── Map init ─── */
function initMap() {
  map = L.map('map', { center: [-37.8136, 144.9631], zoom: 13, zoomControl: false })
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap', maxZoom: 19 }).addTo(map)
  parks.value.forEach(p => addParkMarker(p))
  createHudControls()
  map.getContainer().addEventListener('click', e => { if (e.target.closest('.js-task-cancel')) clearRoute() })
}

function parkPopupHtml(park) {
  const isEpic = !!EPIC_PARKS_DATA[park.id]
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
  const isEpic = !!EPIC_PARKS_DATA[park.id]
  const m = L.marker([park.lat, park.lng], { icon: makePinIcon(park.unlocked, isEpic) }).addTo(map)
    .bindPopup(parkPopupHtml(park), { closeButton: false, offset: [0, -8] })
  parkMarkers[park.id] = m
}
function refreshMarker(park) {
  const m = parkMarkers[park.id]; if (!m) return
  m.setIcon(makePinIcon(park.unlocked, !!EPIC_PARKS_DATA[park.id]))
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
    } else { userMarker.setLatLng([lat, lng]) }
    checkUnlocks(lat, lng); checkArrival(lat, lng); checkEpicParkProximity(lat, lng)
  }, err => console.warn('Geo error:', err), { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 })
}

function checkUnlocks(lat, lng) {
  parks.value.forEach(park => {
    if (park.unlocked) return
    if (haversine(lat, lng, park.lat, park.lng) <= UNLOCK_RADIUS_KM) {
      park.unlocked = true; refreshMarker(park); showUnlockAnim(park)
    }
  })
}

function checkEpicParkProximity(lat, lng) {
  for (const park of parks.value) {
    const ed = EPIC_PARKS_DATA[park.id]; if (!ed) continue
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

function centerOnUser() { if (userPos.value) map.setView([userPos.value.lat, userPos.value.lng], 15) }
function focusPark(park) { map.setView([park.lat, park.lng], 16); parkMarkers[park.id]?.openPopup() }

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

onMounted(() => { initMap(); startTracking(); handleRouteQuery() })
onUnmounted(() => {
  if (watchId !== null) navigator.geolocation.clearWatch(watchId)
  clearTimeout(unlockTimer); clearRoute(); map?.remove()
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