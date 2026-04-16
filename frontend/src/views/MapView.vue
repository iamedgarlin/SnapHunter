<template>
  <div class="flex flex-col h-full" style="font-family: var(--font-game)">

    <!-- Unlock animation overlay (fixed, above everything) -->
    <Transition name="unlock-pop">
      <div v-if="unlockAnim" class="unlock-overlay" @click="unlockAnim = null">
        <div class="leaflet-hud-unlock-inner">
          <svg width="24" height="24" viewBox="0 0 256 256" fill="none">
            <path d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.36,134.57a8,8,0,0,0,9.28,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Z"
              fill="#16a34a" opacity="0.2"/>
            <path d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.36,134.57a8,8,0,0,0,9.28,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Z"
              fill="none" stroke="#16a34a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="128" cy="104" r="32" fill="none" stroke="#16a34a" stroke-width="16"/>
          </svg>
          <p class="unlock-name">{{ unlockAnim.name }}</p>
          <div class="unlock-xp">
            <svg width="12" height="12" viewBox="0 0 256 256" fill="none">
              <path d="M213.85,125.46l-112,120a8,8,0,0,1-13.69-7l14.66-73.33L45.19,143.49a8,8,0,0,1-3-13l112-120a8,8,0,0,1,13.69,7L153.18,90.9l57.63,21.61a8,8,0,0,1,3,12.95Z"
                fill="#f59e0b" opacity="0.2"/>
              <path d="M213.85,125.46l-112,120a8,8,0,0,1-13.69-7l14.66-73.33L45.19,143.49a8,8,0,0,1-3-13l112-120a8,8,0,0,1,13.69,7L153.18,90.9l57.63,21.61a8,8,0,0,1,3,12.95Z"
                fill="none" stroke="#f59e0b" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>+50 XP</span>
          </div>
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

        <!-- Route info bar (when navigating) -->
        <div v-if="routeInfo" class="route-info-card"
          :style="routeInfo.arrived
            ? 'border-color: #bbf7d0; border-bottom-color: #34d399'
            : ''">
          <!-- Header row (always visible, clickable to toggle steps) -->
          <div class="route-info-header" @click="routeStepsOpen = !routeStepsOpen">
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <PhPath :size="16" weight="duotone" :color="routeInfo.arrived ? '#16a34a' : '#3b82f6'" />
              <span class="text-xs font-black truncate"
                :style="routeInfo.arrived ? 'color: #16a34a' : 'color: #1e40af'">
                {{ routeInfo.name }}
              </span>
            </div>
            <div class="flex items-center gap-3 flex-shrink-0">
              <span v-if="routeInfo.arrived" class="text-xs font-black text-emerald-600">Arrived!</span>
              <template v-else>
                <span class="text-xs font-semibold text-gray-500">{{ routeInfo.distance }}</span>
                <span class="text-xs font-semibold text-gray-500">~{{ routeInfo.duration }}</span>
              </template>
            </div>
            <!-- Chevron toggle (only when steps exist and not arrived) -->
            <PhCaretDown v-if="routeInfo.steps?.length && !routeInfo.arrived"
              :size="14" weight="bold" color="#94a3b8"
              class="flex-shrink-0 ml-1 transition-transform duration-200"
              :style="routeStepsOpen ? 'transform: rotate(180deg)' : ''" />
          </div>

          <!-- Steps list (collapsible) -->
          <div v-if="routeStepsOpen && routeInfo.steps?.length && !routeInfo.arrived" class="route-steps-list">
            <div v-for="(step, i) in routeInfo.steps" :key="i" class="route-step-item">
              <div class="route-step-icon">
                <component :is="stepIcon(step.modifier)" :size="14" weight="bold" color="#3b82f6" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-gray-700 leading-tight">
                  {{ step.instruction }}
                </p>
                <p v-if="step.name" class="text-xs text-gray-400 leading-tight mt-0.5">
                  {{ step.name }}
                </p>
              </div>
              <span class="text-xs font-semibold text-gray-400 flex-shrink-0">
                {{ step.distanceText }}
              </span>
            </div>
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <PhTree :size="16" weight="duotone" color="#10b981" />
            <p class="text-sm font-black text-gray-700">Nearby Parks</p>
          </div>
          <span class="text-xs font-black text-emerald-600 bg-emerald-100 rounded-xl px-2 py-1">
            {{ unlockedCount }} / {{ parks.length }} unlocked
          </span>
        </div>

        <div v-for="park in sortedParks" :key="park.id"
          class="card-game flex items-center gap-3 cursor-pointer active:scale-95 transition-all"
          :style="park.unlocked ? 'border-color: #bbf7d0; border-bottom-color: #34d399' : ''"
          @click="focusPark(park)">

          <div class="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
            :style="park.unlocked
              ? 'background: #dcfce7; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac'
              : 'background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'">
            <PhTree :size="24" weight="duotone" :color="park.unlocked ? '#16a34a' : '#cbd5e1'" />
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-1.5">
              <p class="text-sm font-black truncate"
                :style="park.unlocked ? 'color: #16a34a' : 'color: #1f2937'">
                {{ park.name }}
              </p>
              <PhSealCheck v-if="park.unlocked" :size="14" weight="duotone" color="#16a34a" />
            </div>
            <div class="flex items-center gap-2 mt-0.5">
              <span class="text-xs font-semibold text-gray-400">
                {{ formatDistance(park.distance) }}
              </span>
              <span v-if="park.distance !== null && park.distance <= 0.2"
                class="text-xs font-black px-1.5 py-0.5 rounded-lg"
                style="background: #fef3c7; color: #d97706">
                In range!
              </span>
            </div>
          </div>

          <!-- Button: X to cancel nav, check on arrived, nav arrow otherwise -->
          <button
            class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            :style="navigatingId === `park-${park.id}`
              ? (routeInfo?.arrived
                  ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399'
                  : 'background: #fef2f2; border: 2px solid #fecaca; border-bottom: 3px solid #f87171')
              : 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac'"
            @click.stop="toggleNavigation({ lat: park.lat, lng: park.lng, name: park.name, id: `park-${park.id}` })">
            <PhCheck v-if="navigatingId === `park-${park.id}` && routeInfo?.arrived" :size="16" weight="bold" color="#16a34a" />
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
import { useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  PhMapPin, PhLightning, PhNavigationArrow,
  PhMapTrifold, PhTree, PhSealCheck, PhX, PhPath, PhCheck, PhCheckCircle, PhXCircle,
  PhCaretDown, PhArrowUp, PhArrowBendDownRight, PhArrowBendDownLeft,
  PhArrowUUpRight, PhArrowUUpLeft, PhFlagCheckered, PhMapPinLine
} from '@phosphor-icons/vue'

/* ─── Constants ─── */
const UNLOCK_RADIUS_KM = 0.2
const MIN_RECORD_DIST_M = 3
const FOG_TRAIL_RADIUS_KM = 0.015
const ARRIVAL_RADIUS_KM = 0.05          // 50m = "arrived"
const MAX_TRAIL_GAP_KM = 0.3            // max 300m between trail points before inserting a break

/* ─── State ─── */
const parks = ref([
  { id: 1,  name: 'Flagstaff Gardens',      lat: -37.8090, lng: 144.9520, unlocked: false, distance: null },
  { id: 2,  name: 'Fitzroy Gardens',         lat: -37.8136, lng: 144.9793, unlocked: true,  distance: null },
  { id: 3,  name: 'Royal Botanic Gardens',   lat: -37.8304, lng: 144.9799, unlocked: false, distance: null },
  { id: 4,  name: 'Carlton Gardens',         lat: -37.8033, lng: 144.9716, unlocked: false, distance: null },
  { id: 5,  name: 'Yarra Park',              lat: -37.8224, lng: 144.9836, unlocked: false, distance: null },
  { id: 6,  name: 'Albert Park',             lat: -37.8468, lng: 144.9658, unlocked: false, distance: null },
  { id: 7,  name: 'Princes Park',            lat: -37.7833, lng: 144.9608, unlocked: false, distance: null },
  { id: 8,  name: 'Edinburgh Gardens',       lat: -37.7890, lng: 144.9790, unlocked: false, distance: null },
  { id: 9,  name: 'Moonee Valley Parklands', lat: -37.7607, lng: 144.9286, unlocked: false, distance: null },
  { id: 10, name: 'Jells Park',              lat: -37.8980, lng: 145.2020, unlocked: false, distance: null },
])

const userPos = ref(null)
const trackDistanceKm = ref(0)
const trailPoints = ref([])              // now: Array of segments: [[{lat,lng}, ...], [{lat,lng}, ...]]
const navigatingId = ref(null)
const routeInfo = ref(null)
const parkListRef = ref(null)
const unlockAnim = ref(null)            // { name } when showing unlock animation
const routeStepsOpen = ref(false)       // whether step-by-step list is expanded

/* ─── Step icon mapping ─── */
function stepIcon(modifier) {
  if (!modifier) return PhArrowUp
  if (modifier.includes('left') && modifier.includes('uturn')) return PhArrowUUpLeft
  if (modifier.includes('right') && modifier.includes('uturn')) return PhArrowUUpRight
  if (modifier.includes('left')) return PhArrowBendDownLeft
  if (modifier.includes('right')) return PhArrowBendDownRight
  if (modifier === 'straight') return PhArrowUp
  return PhArrowUp
}

let map = null
let userMarker = null
let watchId = null
let fogOverlay = null
let routeLayer = null
let taskMarker = null
const parkMarkers = {}

let hudDistEl = null
let unlockTimer = null

/* ─── Vue Router ─── */
const route = useRoute()

/* ─── Helpers ─── */
function haversine(lat1, lng1, lat2, lng2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2
    + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180)
    * Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function formatDistance(km) {
  if (km === undefined || km === null) return '—'
  if (km < 1) return `${Math.round(km * 1000)}m`
  return `${km.toFixed(1)}km`
}

function fmtTrackDist() {
  const km = trackDistanceKm.value
  if (!km || km === 0) return '0m'
  if (km < 1) return `${Math.round(km * 1000)}m`
  return `${km.toFixed(1)}km`
}

const formatTrackDistance = computed(() => fmtTrackDist())

const sortedParks = computed(() => {
  const sorted = [...parks.value].sort((a, b) => {
    if (a.distance === null) return 1
    if (b.distance === null) return -1
    return a.distance - b.distance
  })
  // Pin the navigating park to the top of the list
  if (navigatingId.value) {
    const idx = sorted.findIndex(p => `park-${p.id}` === navigatingId.value)
    if (idx > 0) {
      const [pinned] = sorted.splice(idx, 1)
      sorted.unshift(pinned)
    }
  }
  return sorted
})

const unlockedCount = computed(() => parks.value.filter(p => p.unlocked).length)

watch(trackDistanceKm, () => {
  if (hudDistEl) hudDistEl.textContent = fmtTrackDist()
})

/* ─── Trail persistence (multi-segment) ─── */
function persistTrail() {
  try {
    localStorage.setItem('snaphunter_trail', JSON.stringify(trailPoints.value))
    localStorage.setItem('snaphunter_trail_km', String(trackDistanceKm.value))
  } catch (e) { /* full or unavailable */ }
}

function loadTrail() {
  try {
    const raw = localStorage.getItem('snaphunter_trail')
    if (raw) {
      const parsed = JSON.parse(raw)
      // Migration: old format was flat array [{lat,lng},...], new is segments [[{lat,lng},...],...]
      if (parsed.length > 0 && !Array.isArray(parsed[0])) {
        // Old flat format → wrap in a single segment
        trailPoints.value = [parsed]
      } else {
        trailPoints.value = parsed
      }
    }
    const km = localStorage.getItem('snaphunter_trail_km')
    if (km) trackDistanceKm.value = parseFloat(km) || 0
  } catch (e) { /* ignore */ }
}

function getLastTrailPoint() {
  const segs = trailPoints.value
  if (segs.length === 0) return null
  const lastSeg = segs[segs.length - 1]
  if (!lastSeg || lastSeg.length === 0) return null
  return lastSeg[lastSeg.length - 1]
}

function addTrailPoint(lat, lng) {
  const segs = trailPoints.value
  const lastPt = getLastTrailPoint()

  if (lastPt) {
    const distKm = haversine(lastPt.lat, lastPt.lng, lat, lng)
    const distM = distKm * 1000

    // Too close — skip
    if (distM < MIN_RECORD_DIST_M) return false

    // If gap is too large (phone slept / background), start a new segment
    if (distKm > MAX_TRAIL_GAP_KM) {
      segs.push([{ lat, lng }])
    } else {
      // Normal: append to current segment
      trackDistanceKm.value += distKm
      segs[segs.length - 1].push({ lat, lng })
    }
  } else {
    // First point ever — start first segment
    segs.push([{ lat, lng }])
  }

  // Persist every 10 total points
  const totalPts = segs.reduce((n, s) => n + s.length, 0)
  if (totalPts % 10 === 0) persistTrail()
  return true
}

/* ─── Map pin icons ─── */
function makePinIcon(unlocked) {
  const fill = unlocked ? '#16a34a' : '#cbd5e1'
  const stroke = unlocked ? '#064e3b' : '#94a3b8'
  const s = 22
  return L.divIcon({
    className: '',
    html: `<div style="width:${s}px;height:${Math.round(s*1.25)}px;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.2))">
      <svg viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg" width="${s}" height="${Math.round(s*1.25)}">
        <path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
        <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
      </svg></div>`,
    iconSize: [s, Math.round(s * 1.25)],
    iconAnchor: [s / 2, Math.round(s * 1.25)],
    popupAnchor: [0, -Math.round(s * 1.25)],
  })
}

function makeTaskPinIcon() {
  const s = 26
  return L.divIcon({
    className: '',
    html: `<div style="width:${s}px;height:${Math.round(s*1.25)}px;filter:drop-shadow(0 2px 4px rgba(59,130,246,0.3))">
      <svg viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg" width="${s}" height="${Math.round(s*1.25)}">
        <path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z" fill="#3b82f6" stroke="#1e40af" stroke-width="1.5"/>
        <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
      </svg></div>`,
    iconSize: [s, Math.round(s * 1.25)],
    iconAnchor: [s / 2, Math.round(s * 1.25)],
    popupAnchor: [0, -Math.round(s * 1.25)],
  })
}

/* ─── Fog overlay ─── */
const FogCanvas = L.Layer.extend({
  onAdd(m) {
    this._map = m
    this._canvas = document.createElement('canvas')
    Object.assign(this._canvas.style, {
      position: 'absolute', top: '0', left: '0', pointerEvents: 'none',
    })
    m.getPane('overlayPane').appendChild(this._canvas)
    m.on('move zoom moveend zoomend resize', this._redraw, this)
    this._redraw()
  },
  onRemove(m) {
    m.off('move zoom moveend zoomend resize', this._redraw, this)
    this._canvas.remove()
  },
  _redraw() {
    const m = this._map, size = m.getSize(), c = this._canvas
    c.width = size.x; c.height = size.y
    L.DomUtil.setPosition(c, m.containerPointToLayerPoint([0, 0]))

    const ctx = c.getContext('2d')
    ctx.clearRect(0, 0, size.x, size.y)
    ctx.fillStyle = 'rgba(20,24,35,0.72)'
    ctx.fillRect(0, 0, size.x, size.y)
    ctx.globalCompositeOperation = 'destination-out'

    // 1) Unlocked parks — 400m reveal radius
    parks.value.filter(p => p.unlocked).forEach(pk => {
      const pt = m.latLngToContainerPoint([pk.lat, pk.lng])
      const r = Math.abs(m.latLngToContainerPoint([pk.lat + 0.4/111, pk.lng]).y - pt.y)
      const g = ctx.createRadialGradient(pt.x,pt.y,0, pt.x,pt.y,r)
      g.addColorStop(0,'rgba(0,0,0,1)'); g.addColorStop(0.75,'rgba(0,0,0,0.95)'); g.addColorStop(1,'rgba(0,0,0,0)')
      ctx.beginPath(); ctx.arc(pt.x,pt.y,r,0,Math.PI*2); ctx.fillStyle=g; ctx.fill()
    })

    // 2) Trail — street-width fog reveal (multi-segment)
    const segs = trailPoints.value
    if (segs.length > 0) {
      // Calculate trail radius in pixels
      const firstSeg = segs.find(s => s.length > 0)
      if (firstSeg) {
        const refPt = m.latLngToContainerPoint([firstSeg[0].lat, firstSeg[0].lng])
        const refPt2 = m.latLngToContainerPoint([firstSeg[0].lat + FOG_TRAIL_RADIUS_KM/111, firstSeg[0].lng])
        const trailRadiusPx = Math.max(Math.abs(refPt2.y - refPt.y), 2)

        ctx.lineCap = 'round'
        ctx.lineJoin = 'round'
        ctx.lineWidth = trailRadiusPx * 2
        ctx.strokeStyle = 'rgba(0,0,0,1)'
        ctx.fillStyle = 'rgba(0,0,0,1)'

        // Draw each segment separately (no straight lines between segments)
        for (const seg of segs) {
          if (seg.length === 0) continue

          if (seg.length === 1) {
            const cp = m.latLngToContainerPoint([seg[0].lat, seg[0].lng])
            ctx.beginPath()
            ctx.arc(cp.x, cp.y, trailRadiusPx, 0, Math.PI * 2)
            ctx.fill()
          } else {
            ctx.beginPath()
            for (let i = 0; i < seg.length; i++) {
              const cp = m.latLngToContainerPoint([seg[i].lat, seg[i].lng])
              if (i === 0) {
                ctx.moveTo(cp.x, cp.y)
              } else {
                ctx.lineTo(cp.x, cp.y)
              }
            }
            ctx.stroke()
          }
        }
      }
    }

    ctx.globalCompositeOperation = 'source-over'
  },
  update() { this._redraw() }
})

/* ─── HUD Controls ─── */

function createHudControls() {
  const BadgeControl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-badge')
      el.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="24" y="48" width="208" height="160" rx="8" fill="#10b981" opacity="0.2"/>
          <rect x="24" y="48" width="208" height="160" rx="8" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="96" y1="48" x2="96" y2="208" stroke="#10b981" stroke-width="16" stroke-linecap="round"/>
          <line x1="160" y1="48" x2="160" y2="208" stroke="#10b981" stroke-width="16" stroke-linecap="round"/>
          <polyline points="96,128 128,96 160,128" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>Victoria, AU</span>`
      L.DomEvent.disableClickPropagation(el)
      return el
    }
  })

  const DistControl = L.Control.extend({
    options: { position: 'topright' },
    onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-badge')
      el.innerHTML = `<span class="leaflet-hud-pulse"></span><span class="leaflet-hud-dist">0m</span>`
      hudDistEl = el.querySelector('.leaflet-hud-dist')
      L.DomEvent.disableClickPropagation(el)
      return el
    }
  })

  const CenterControl = L.Control.extend({
    options: { position: 'bottomright' },
    onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-btn')
      el.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 256 256" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M224,120,48,24a8,8,0,0,0-11.6,9.6L68,128,36.4,222.4A8,8,0,0,0,48,232l176-96a8,8,0,0,0,0-14Z"
            fill="#10b981" opacity="0.2"/>
          <path d="M224,120,48,24a8,8,0,0,0-11.6,9.6L68,128,36.4,222.4A8,8,0,0,0,48,232l176-96a8,8,0,0,0,0-14Z"
            fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="68" y1="128" x2="224" y2="128" fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round"/>
        </svg>`
      el.style.cursor = 'pointer'
      L.DomEvent.disableClickPropagation(el)
      L.DomEvent.on(el, 'click', () => centerOnUser())
      return el
    }
  })

  new BadgeControl().addTo(map)
  new DistControl().addTo(map)
  new CenterControl().addTo(map)
}

function showUnlockAnim(park) {
  unlockAnim.value = { name: park.name }
  clearTimeout(unlockTimer)
  unlockTimer = setTimeout(() => {
    unlockAnim.value = null
  }, 3000)
}

/* ─── Map init ─── */
function initMap() {
  map = L.map('map', {
    center: [-37.8136, 144.9631],
    zoom: 13,
    zoomControl: false,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap',
    maxZoom: 19,
  }).addTo(map)

  fogOverlay = new FogCanvas()
  fogOverlay.addTo(map)

  parks.value.forEach(park => addParkMarker(park))

  createHudControls()

  // Event delegation: handle Cancel button clicks inside any Leaflet popup
  map.getContainer().addEventListener('click', (e) => {
    if (e.target.closest('.js-task-cancel')) {
      clearRoute()
    }
  })

  if (hudDistEl) hudDistEl.textContent = fmtTrackDist()
}

function parkPopupHtml(park) {
  return `
    <div style="font-family:sans-serif;text-align:center;padding:4px 2px">
      <p style="font-weight:900;font-size:13px;margin:0 0 2px">${park.name}</p>
      <p style="font-size:11px;color:${park.unlocked ? '#16a34a' : '#94a3b8'};margin:0">
        ${park.unlocked ? '✓ Unlocked' : 'Visit to unlock'}
      </p>
    </div>`
}

function taskPopupHtml(name, subtitle) {
  const cameraSvg = `<svg width="11" height="11" viewBox="0 0 256 256" fill="none" style="display:inline-block;vertical-align:-1px;margin-right:3px"><path d="M208,56H180.28L166.65,35.56A8,8,0,0,0,160,32H96a8,8,0,0,0-6.65,3.56L75.72,56H48A24,24,0,0,0,24,80V192a24,24,0,0,0,24,24H208a24,24,0,0,0,24-24V80A24,24,0,0,0,208,56Z" fill="#3b82f6" opacity="0.2"/><path d="M208,56H180.28L166.65,35.56A8,8,0,0,0,160,32H96a8,8,0,0,0-6.65,3.56L75.72,56H48A24,24,0,0,0,24,80V192a24,24,0,0,0,24,24H208a24,24,0,0,0,24-24V80A24,24,0,0,0,208,56Z" fill="none" stroke="#3b82f6" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/><circle cx="128" cy="132" r="36" fill="none" stroke="#3b82f6" stroke-width="16"/></svg>`
  const xSvg = `<svg width="10" height="10" viewBox="0 0 256 256" fill="none" style="display:inline-block;vertical-align:-1px;margin-right:2px"><line x1="200" y1="56" x2="56" y2="200" stroke="#ef4444" stroke-width="28" stroke-linecap="round"/><line x1="200" y1="200" x2="56" y2="56" stroke="#ef4444" stroke-width="28" stroke-linecap="round"/></svg>`
  const sub = subtitle || `${cameraSvg}Task location`
  return `
    <div style="font-family:sans-serif;text-align:center;padding:2px 0">
      <p style="font-weight:900;font-size:12px;margin:0 0 2px;color:#1f2937">${name}</p>
      <p style="font-size:10px;color:#3b82f6;margin:0 0 6px;line-height:1.2">${sub}</p>
      <button class="js-task-cancel"
        style="display:inline-flex;align-items:center;justify-content:center;gap:3px;
          padding:3px 10px;border-radius:10px;border:1.5px solid #fecaca;border-bottom:2px solid #f87171;
          background:#fef2f2;color:#ef4444;font-size:10px;font-weight:800;cursor:pointer;
          font-family:sans-serif;outline:none"
      >${xSvg}Cancel</button>
    </div>`
}

function addParkMarker(park) {
  const marker = L.marker([park.lat, park.lng], { icon: makePinIcon(park.unlocked) })
    .addTo(map)
    .bindPopup(parkPopupHtml(park), { closeButton: false, offset: [0, -8] })
  parkMarkers[park.id] = marker
}

function refreshMarker(park) {
  const marker = parkMarkers[park.id]
  if (!marker) return
  marker.setIcon(makePinIcon(park.unlocked))
  marker.setPopupContent(parkPopupHtml(park))
}

/* ─── Geolocation ─── */
function startTracking() {
  if (!navigator.geolocation) return
  watchId = navigator.geolocation.watchPosition(
    ({ coords: { latitude: lat, longitude: lng } }) => {
      userPos.value = { lat, lng }
      parks.value.forEach(p => { p.distance = haversine(lat, lng, p.lat, p.lng) })

      if (!userMarker) {
        const icon = L.divIcon({
          className: '',
          html: `<div style="width:18px;height:18px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 0 0 5px rgba(59,130,246,0.25)"></div>`,
          iconSize: [18, 18], iconAnchor: [9, 9],
        })
        userMarker = L.marker([lat, lng], { icon, zIndexOffset: 1000 }).addTo(map)
        // Only auto-center if not navigating (navigation sets its own view)
        if (!navigatingId.value) map.setView([lat, lng], 14)
      } else {
        userMarker.setLatLng([lat, lng])
      }

      checkUnlocks(lat, lng)
      const added = addTrailPoint(lat, lng)
      if (added) fogOverlay?.update()

      // Check arrival at navigation destination
      checkArrival(lat, lng)
    },
    err => console.warn('Geo error:', err),
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 }
  )
}

function checkUnlocks(lat, lng) {
  let anyNew = false
  parks.value.forEach(park => {
    if (park.unlocked) return
    if (haversine(lat, lng, park.lat, park.lng) <= UNLOCK_RADIUS_KM) {
      park.unlocked = true
      anyNew = true
      refreshMarker(park)
      showUnlockAnim(park)
    }
  })
  if (anyNew) fogOverlay?.update()
}

/* ─── Arrival detection ─── */
let navTarget = null   // store the current navigation target coords

function checkArrival(lat, lng) {
  if (!navTarget || !navigatingId.value) return
  if (routeInfo.value?.arrived) return  // already arrived

  const distToTarget = haversine(lat, lng, navTarget.lat, navTarget.lng)
  if (distToTarget <= ARRIVAL_RADIUS_KM) {
    // Mark as arrived
    routeInfo.value = {
      ...routeInfo.value,
      arrived: true,
    }
    // Remove the route line (keep the bar visible as "arrived")
    if (routeLayer) { routeLayer.remove(); routeLayer = null }
  }
}

function centerOnUser() {
  if (userPos.value) map.setView([userPos.value.lat, userPos.value.lng], 15)
}

function focusPark(park) {
  map.setView([park.lat, park.lng], 16)
  parkMarkers[park.id]?.openPopup()
}

/* ─── OSRM Navigation ─── */

/**
 * Toggle navigation to a target { lat, lng, name, id }
 * Called from park list buttons and from route query deep-links.
 */
async function toggleNavigation(target) {
  if (navigatingId.value === target.id) {
    clearRoute()
    return
  }

  if (!userPos.value) {
    // Fallback: no GPS yet
    window.open(`https://www.google.com/maps/dir/?api=1&destination=${target.lat},${target.lng}&travelmode=walking`, '_blank')
    return
  }

  clearRoute()
  navigatingId.value = target.id
  navTarget = { lat: target.lat, lng: target.lng }

  // Scroll park list to top so the pinned card is visible
  nextTick(() => {
    parkListRef.value?.scrollTo({ top: 0, behavior: 'smooth' })
  })

  // Add a blue task marker if this is a task (not a park)
  if (String(target.id).startsWith('task-')) {
    taskMarker = L.marker([target.lat, target.lng], { icon: makeTaskPinIcon(), zIndexOffset: 900 })
      .addTo(map)
      .bindPopup(taskPopupHtml(target.name), { closeButton: false, offset: [0, -8], minWidth: 120 })
  }

  const { lat: uLat, lng: uLng } = userPos.value
  const url = `https://router.project-osrm.org/route/v1/foot/${uLng},${uLat};${target.lng},${target.lat}?overview=full&geometries=geojson&steps=true`

  try {
    const res = await fetch(url)
    const data = await res.json()

    if (data.code !== 'Ok' || !data.routes?.length) {
      console.warn('OSRM: no route found')
      clearRoute()
      return
    }

    const r = data.routes[0]
    const coords = r.geometry.coordinates.map(([lng, lat]) => [lat, lng])

    routeLayer = L.layerGroup()

    // Shadow line
    L.polyline(coords, {
      color: '#1e40af', weight: 7, opacity: 0.15,
      lineCap: 'round', lineJoin: 'round',
    }).addTo(routeLayer)

    // Main dashed line
    L.polyline(coords, {
      color: '#3b82f6', weight: 4, opacity: 0.85,
      lineCap: 'round', lineJoin: 'round',
      dashArray: '12 8',
      className: 'route-line-animated',
    }).addTo(routeLayer)

    routeLayer.addTo(map)

    const bounds = L.latLngBounds(coords)
    // Extra top padding (120px) to leave room for the task popup above the marker
    const isTask = String(target.id).startsWith('task-')
    map.fitBounds(bounds, { paddingTopLeft: [60, isTask ? 120 : 60], paddingBottomRight: [60, 60] })

    // Open task popup after map settles so it's not clipped
    if (isTask && taskMarker) {
      map.once('moveend', () => taskMarker?.openPopup())
    }

    const distKm = r.distance / 1000
    const durMin = Math.round(r.duration / 60)

    // Parse turn-by-turn steps
    const steps = []
    if (r.legs?.[0]?.steps) {
      for (const s of r.legs[0].steps) {
        if (s.maneuver?.type === 'arrive') {
          steps.push({
            instruction: 'Arrive at destination',
            name: target.name,
            modifier: null,
            distanceText: '',
            type: 'arrive',
          })
          continue
        }
        const distM = s.distance
        const distText = distM < 1000 ? `${Math.round(distM)}m` : `${(distM / 1000).toFixed(1)}km`
        const maneuver = s.maneuver || {}
        let instruction = ''
        switch (maneuver.type) {
          case 'depart':
            instruction = 'Head ' + (maneuver.modifier || 'forward')
            break
          case 'turn':
            instruction = 'Turn ' + (maneuver.modifier || '').replace('sharp ', 'sharply ')
            break
          case 'new name':
          case 'continue':
            instruction = maneuver.modifier === 'straight'
              ? 'Continue straight'
              : 'Continue ' + (maneuver.modifier || '')
            break
          case 'fork':
            instruction = 'At the fork, keep ' + (maneuver.modifier || 'going')
            break
          case 'end of road':
            instruction = 'At the end of road, turn ' + (maneuver.modifier || '')
            break
          case 'roundabout':
          case 'rotary':
            instruction = 'Enter roundabout, exit ' + (maneuver.modifier || '')
            break
          default:
            instruction = maneuver.modifier
              ? maneuver.type + ' ' + maneuver.modifier
              : maneuver.type || 'Continue'
            break
        }
        // Capitalize first letter
        instruction = instruction.charAt(0).toUpperCase() + instruction.slice(1)

        steps.push({
          instruction,
          name: s.name || '',
          modifier: maneuver.modifier || '',
          distanceText: distText,
          type: maneuver.type,
        })
      }
    }

    routeInfo.value = {
      name: target.name,
      distance: distKm < 1 ? `${Math.round(distKm * 1000)}m` : `${distKm.toFixed(1)}km`,
      duration: durMin < 60 ? `${durMin} min` : `${Math.floor(durMin/60)}h ${durMin%60}m`,
      arrived: false,
      steps,
    }
    routeStepsOpen.value = false

    // Immediately check if already within arrival radius
    checkArrival(uLat, uLng)

  } catch (err) {
    console.error('OSRM fetch error:', err)
    clearRoute()
  }
}

function clearRoute() {
  if (routeLayer) { routeLayer.remove(); routeLayer = null }
  if (taskMarker) { taskMarker.remove(); taskMarker = null }
  navigatingId.value = null
  routeInfo.value = null
  routeStepsOpen.value = false
  navTarget = null
}

/* ─── Handle deep-link from Home / Tasks ─── */
function handleRouteQuery() {
  const q = route.query
  if (q.navLat && q.navLng && q.navName) {
    const target = {
      lat: parseFloat(q.navLat),
      lng: parseFloat(q.navLng),
      name: q.navName,
      id: q.navId || `task-${q.navLat}-${q.navLng}`,
    }
    // Wait a tick for map + GPS to init, then navigate
    const tryNav = () => {
      if (userPos.value && map) {
        toggleNavigation(target)
      } else {
        // If GPS not ready yet, place marker and zoom to destination first
        if (map) {
          map.setView([target.lat, target.lng], 15)
          taskMarker = L.marker([target.lat, target.lng], { icon: makeTaskPinIcon(), zIndexOffset: 900 })
            .addTo(map)
            .bindPopup(taskPopupHtml(target.name, '<span style="color:#94a3b8">Waiting for GPS...</span>'), { closeButton: false, offset: [0, -8], minWidth: 120 })

          navigatingId.value = target.id
          // Retry when GPS arrives
          const unwatch = watch(userPos, (pos) => {
            if (pos) {
              unwatch()
              toggleNavigation(target)
            }
          })
        }
      }
    }
    setTimeout(tryNav, 500)
  }
}

/* ─── Lifecycle ─── */
onMounted(() => {
  loadTrail()
  initMap()
  startTracking()
  handleRouteQuery()
})

onUnmounted(() => {
  if (watchId !== null) navigator.geolocation.clearWatch(watchId)
  clearTimeout(unlockTimer)
  clearRoute()
  persistTrail()
  map?.remove()
})
</script>

<style>
/* ═══════════════════════════════════
   HUD ROOT RESET
   ═══════════════════════════════════ */
#map :deep(.leaflet-control) {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}

/* ═══════════════════════════════════
   BADGE
   ═══════════════════════════════════ */
.leaflet-hud-badge {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 6px 12px !important;
  border-radius: 16px !important;
  background: white !important;
  border: 2px solid #bbf7d0 !important;
  border-bottom: 2px solid #34d399 !important;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
  font-family: var(--font-game), system-ui, sans-serif !important;
  font-size: 12px !important;
  font-weight: 900 !important;
  color: #047857 !important;
  line-height: 1 !important;
}

/* ═══════════════════════════════════
   BUTTON
   ═══════════════════════════════════ */
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
  box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
  cursor: pointer !important;
  transition: transform 0.1s !important;
}
.leaflet-hud-btn:active { transform: scale(0.9) !important; }

/* ═══════════════════════════════════
   Pulse
   ═══════════════════════════════════ */
.leaflet-hud-pulse {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: leaflet-hud-pulse-anim 1.5s ease-in-out infinite;
}
@keyframes leaflet-hud-pulse-anim {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.75); }
}
.leaflet-hud-dist { color: #059669 !important; }

/* ═══════════════════════════════════
   UNLOCK OVERLAY (fixed, above everything)
   ═══════════════════════════════════ */
.unlock-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
}
.leaflet-hud-unlock-inner {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 16px 24px; border-radius: 24px;
  background: white;
  border: 3px solid #34d399; border-bottom: 5px solid #16a34a;
  box-shadow: 0 12px 32px rgba(0,0,0,0.18);
  font-family: var(--font-game), system-ui, sans-serif;
}
.unlock-name {
  font-weight: 900; font-size: 14px; color: #1f2937; margin: 0;
}
.unlock-xp {
  display: flex; align-items: center; gap: 4px;
  font-weight: 900; font-size: 13px; color: #d97706;
}

/* Vue Transition for unlock popup */
.unlock-pop-enter-active {
  animation: unlock-scale-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.unlock-pop-leave-active {
  animation: unlock-fade-out 0.4s ease forwards;
}
@keyframes unlock-scale-in {
  from { transform: scale(0.6); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
@keyframes unlock-fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* ═══════════════════════════════════
   Route line animation
   ═══════════════════════════════════ */
.route-line-animated { animation: route-dash-march 1.2s linear infinite; }
@keyframes route-dash-march { to { stroke-dashoffset: -20; } }

/* ═══════════════════════════════════
   Route info card (collapsible)
   ═══════════════════════════════════ */
.route-info-card {
  border-radius: 16px;
  background: white;
  border: 2px solid #bfdbfe; border-bottom: 3px solid #60a5fa;
  box-shadow: 0 2px 8px rgba(59,130,246,0.1);
  font-family: var(--font-game), system-ui, sans-serif;
  overflow: hidden;
}
.route-info-header {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  user-select: none;
}
.route-steps-list {
  border-top: 1.5px solid #e0ecff;
  max-height: 200px;
  overflow-y: auto;
}
.route-step-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 8px 14px;
}
.route-step-item + .route-step-item {
  border-top: 1px solid #f1f5f9;
}
.route-step-icon {
  width: 24px; height: 24px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: #eff6ff; flex-shrink: 0; margin-top: 1px;
}
</style>

<style scoped>
#map :deep(.leaflet-popup-content-wrapper) {
  border-radius: 14px; border: 1.5px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08); padding: 2px;
}
#map :deep(.leaflet-popup-tip-container) { display: none; }
#map :deep(.leaflet-popup-content) { margin: 8px 12px; }
#map :deep(.leaflet-top.leaflet-left .leaflet-control) { margin-left: 16px; margin-top: 16px; }
#map :deep(.leaflet-top.leaflet-right .leaflet-control) { margin-right: 16px; margin-top: 16px; }
#map :deep(.leaflet-bottom.leaflet-right .leaflet-control) { margin-right: 16px; margin-bottom: 16px; }
</style>