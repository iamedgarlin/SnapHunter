<template>
  <div class="flex flex-col h-full" style="font-family: var(--font-game)">

    <!-- Map -->
    <div class="relative" style="height: 55vh; flex-shrink: 0">
      <div id="map" class="w-full h-full"></div>
    </div>

    <!-- Parks list -->
    <div class="flex-1 overflow-y-auto" style="background: #f0fdf4">
      <div class="px-4 pt-4 pb-6 flex flex-col gap-3">

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

          <button
            class="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
            style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac"
            @click.stop="navigateToPark(park)">
            <PhNavigationArrow :size="16" weight="duotone" color="#10b981" />
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  PhMapPin, PhLightning, PhNavigationArrow,
  PhMapTrifold, PhTree, PhSealCheck
} from '@phosphor-icons/vue'

/* ─── Constants ─── */
const UNLOCK_RADIUS_KM = 0.2
const MIN_RECORD_DIST_M = 3          // ← 缩小到3m，记录更密集，路径更连续
const FOG_TRAIL_RADIUS_KM = 0.015    // ← 15m ≈ 一条马路的宽度

/* ─── State ─── */
const parks = ref([
  { id: 1,  name: 'Flagstaff Gardens',      lat: -37.8090, lng: 144.9520, unlocked: false, distance: null },  // ← 改为 false
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
const trailPoints = ref([])

let map = null
let userMarker = null
let watchId = null
let fogOverlay = null
const parkMarkers = {}

// HUD DOM references (managed manually via L.Control)
let hudDistEl = null
let hudUnlockEl = null
let unlockTimer = null

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

const sortedParks = computed(() =>
  [...parks.value].sort((a, b) => {
    if (a.distance === null) return 1
    if (b.distance === null) return -1
    return a.distance - b.distance
  })
)

const unlockedCount = computed(() => parks.value.filter(p => p.unlocked).length)

// Keep HUD distance text in sync
watch(trackDistanceKm, () => {
  if (hudDistEl) hudDistEl.textContent = fmtTrackDist()
})

/* ─── Trail persistence ─── */
function persistTrail() {
  try {
    localStorage.setItem('snaphunter_trail', JSON.stringify(trailPoints.value))
    localStorage.setItem('snaphunter_trail_km', String(trackDistanceKm.value))
  } catch (e) { /* full or unavailable */ }
}

function loadTrail() {
  try {
    const raw = localStorage.getItem('snaphunter_trail')
    if (raw) trailPoints.value = JSON.parse(raw)
    const km = localStorage.getItem('snaphunter_trail_km')
    if (km) trackDistanceKm.value = parseFloat(km) || 0
  } catch (e) { /* ignore */ }
}

function addTrailPoint(lat, lng) {
  const pts = trailPoints.value
  if (pts.length > 0) {
    const last = pts[pts.length - 1]
    const distM = haversine(last.lat, last.lng, lat, lng) * 1000
    if (distM < MIN_RECORD_DIST_M) return false
    trackDistanceKm.value += distM / 1000
  }
  pts.push({ lat, lng })
  if (pts.length % 10 === 0) persistTrail()
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

    // 2) Trail — 街道宽度级别的探索揭雾
    //    用连续线段 stroke 代替独立圆点，避免缝隙
    const pts = trailPoints.value
    if (pts.length > 0) {
      const b = m.getBounds()
      const mLat = (b.getNorth()-b.getSouth())*0.2
      const mLng = (b.getEast()-b.getWest())*0.2

      // 计算 trail 线条的像素宽度（基于 FOG_TRAIL_RADIUS_KM）
      const refPt = m.latLngToContainerPoint([pts[0].lat, pts[0].lng])
      const refPt2 = m.latLngToContainerPoint([pts[0].lat + FOG_TRAIL_RADIUS_KM/111, pts[0].lng])
      const trailRadiusPx = Math.max(Math.abs(refPt2.y - refPt.y), 2)

      // 用粗线条描绘路径 — 一笔画完所有连续点
      ctx.lineCap = 'round'
      ctx.lineJoin = 'round'
      ctx.lineWidth = trailRadiusPx * 2  // 直径 = 2 × 半径
      ctx.strokeStyle = 'rgba(0,0,0,1)'
      ctx.fillStyle = 'rgba(0,0,0,1)'

      ctx.beginPath()
      let started = false
      for (let i = 0; i < pts.length; i++) {
        const p = pts[i]
        const cp = m.latLngToContainerPoint([p.lat, p.lng])
        if (!started) {
          ctx.moveTo(cp.x, cp.y)
          started = true
        } else {
          ctx.lineTo(cp.x, cp.y)
        }
      }
      ctx.stroke()

      // 也在每个点画一个小圆，保证起点和单点也有揭雾
      if (pts.length === 1) {
        const cp = m.latLngToContainerPoint([pts[0].lat, pts[0].lng])
        ctx.beginPath()
        ctx.arc(cp.x, cp.y, trailRadiusPx, 0, Math.PI * 2)
        ctx.fill()
      }
    }

    ctx.globalCompositeOperation = 'source-over'
  },
  update() { this._redraw() }
})

/* ─────────────────────────────────────────────
 *  HUD via L.Control
 * ───────────────────────────────────────────── */

function createHudControls() {
  // ── Top-left: Victoria badge ──
  const BadgeControl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-badge')
      el.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 256 256" fill="none">
          <path d="M228.92,49.69a8,8,0,0,0-6.86-1.45L160.93,63.52,99.58,32.84a8,8,0,0,0-5.52-.6l-64,16A8,8,0,0,0,24,56V200a8,8,0,0,0,9.94,7.76l60.06-15,61.35,30.68A8,8,0,0,0,160,224a8.43,8.43,0,0,0,1.73-.19l64-16A8,8,0,0,0,232,200V56A8,8,0,0,0,228.92,49.69Z"
            fill="#10b981" opacity="0.2"/>
          <path d="M228.92,49.69a8,8,0,0,0-6.86-1.45L160.93,63.52,99.58,32.84a8,8,0,0,0-5.52-.6l-64,16A8,8,0,0,0,24,56V200a8,8,0,0,0,9.94,7.76l60.06-15,61.35,30.68A8,8,0,0,0,160,224a8.43,8.43,0,0,0,1.73-.19l64-16A8,8,0,0,0,232,200V56A8,8,0,0,0,228.92,49.69ZM96,176a8,8,0,0,0-1.73.19L40,190.71V61.29l56-14V152a8,8,0,0,0,0,16Zm64,18.71-48-24V65.29l48,24ZM216,194.71l-40,10V99.29" 
            fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>Victoria, AU</span>`
      L.DomEvent.disableClickPropagation(el)
      return el
    }
  })

  // ── Top-right: distance tracker ──
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

  // ── Bottom-right: center button ──
  const CenterControl = L.Control.extend({
    options: { position: 'bottomright' },
    onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-btn')
      el.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 256 256" fill="none">
          <path d="M213.49,101.07l-128-80a12,12,0,0,0-13.16.65A12,12,0,0,0,68,32V224a12,12,0,0,0,4.33,9.28,12,12,0,0,0,13.16.65l128-80a12,12,0,0,0,0-20.43Z"
            fill="#10b981" opacity="0.2"/>
          <path d="M234.35,114.35l-128-80A12,12,0,0,0,88,44V212a12,12,0,0,0,18.35,10.18l128-84a12,12,0,0,0,0-20.36Z"
            fill="none" stroke="#10b981" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"
            transform="rotate(-45 128 128)"/>
        </svg>`
      el.style.cursor = 'pointer'
      L.DomEvent.disableClickPropagation(el)
      L.DomEvent.on(el, 'click', () => centerOnUser())
      return el
    }
  })

  // ── Center: unlock popup (initially hidden) ──
  const UnlockControl = L.Control.extend({
    options: { position: 'topleft' },
    onAdd() {
      const el = L.DomUtil.create('div', 'leaflet-hud-unlock')
      el.style.display = 'none'
      hudUnlockEl = el
      L.DomEvent.disableClickPropagation(el)
      return el
    }
  })

  new BadgeControl().addTo(map)
  new DistControl().addTo(map)
  new CenterControl().addTo(map)
  new UnlockControl().addTo(map)
}

function showUnlockAnim(park) {
  if (!hudUnlockEl) return
  hudUnlockEl.innerHTML = `
    <div class="leaflet-hud-unlock-inner">
      <svg width="24" height="24" viewBox="0 0 256 256" fill="none">
        <path d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.36,134.57a8,8,0,0,0,9.28,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Z"
          fill="#16a34a" opacity="0.2"/>
        <path d="M128,16a88,88,0,0,0-88,88c0,75.3,80,132.17,83.36,134.57a8,8,0,0,0,9.28,0C136,236.17,216,179.3,216,104A88,88,0,0,0,128,16Z"
          fill="none" stroke="#16a34a" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="128" cy="104" r="32" fill="none" stroke="#16a34a" stroke-width="16"/>
      </svg>
      <p class="unlock-name">${park.name}</p>
      <div class="unlock-xp">
        <svg width="12" height="12" viewBox="0 0 256 256" fill="none">
          <path d="M213.85,125.46l-112,120a8,8,0,0,1-13.69-7l14.66-73.33L45.19,143.49a8,8,0,0,1-3-13l112-120a8,8,0,0,1,13.69,7L153.18,90.9l57.63,21.61a8,8,0,0,1,3,12.95Z"
            fill="#f59e0b" opacity="0.2"/>
          <path d="M213.85,125.46l-112,120a8,8,0,0,1-13.69-7l14.66-73.33L45.19,143.49a8,8,0,0,1-3-13l112-120a8,8,0,0,1,13.69,7L153.18,90.9l57.63,21.61a8,8,0,0,1,3,12.95Z"
            fill="none" stroke="#f59e0b" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>+50 XP</span>
      </div>
    </div>`
  hudUnlockEl.style.display = 'block'
  hudUnlockEl.classList.remove('pop-anim')
  void hudUnlockEl.offsetWidth // force reflow
  hudUnlockEl.classList.add('pop-anim')

  clearTimeout(unlockTimer)
  unlockTimer = setTimeout(() => {
    hudUnlockEl.style.display = 'none'
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

  // Create HUD elements as Leaflet controls
  createHudControls()

  // Set initial distance text
  if (hudDistEl) hudDistEl.textContent = fmtTrackDist()
}

function addParkMarker(park) {
  const marker = L.marker([park.lat, park.lng], { icon: makePinIcon(park.unlocked) })
    .addTo(map)
    .bindPopup(`
      <div style="font-family:sans-serif;text-align:center;padding:4px 2px">
        <p style="font-weight:900;font-size:13px;margin:0 0 2px">${park.name}</p>
        <p style="font-size:11px;color:${park.unlocked ? '#16a34a' : '#94a3b8'};margin:0">
          ${park.unlocked ? '✓ Unlocked' : 'Visit to unlock'}
        </p>
      </div>`, { closeButton: false, offset: [0, -8] })
  parkMarkers[park.id] = marker
}

function refreshMarker(park) {
  parkMarkers[park.id]?.setIcon(makePinIcon(park.unlocked))
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
        map.setView([lat, lng], 14)
      } else {
        userMarker.setLatLng([lat, lng])
      }

      checkUnlocks(lat, lng)
      const added = addTrailPoint(lat, lng)
      if (added) fogOverlay?.update()
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

function centerOnUser() {
  if (userPos.value) map.setView([userPos.value.lat, userPos.value.lng], 15)
}

function focusPark(park) {
  map.setView([park.lat, park.lng], 16)
  parkMarkers[park.id]?.openPopup()
}

function navigateToPark(park) {
  const ua = navigator.userAgent
  if (/iPad|iPhone|iPod/.test(ua)) {
    window.location.href = `maps://maps.apple.com/?daddr=${park.lat},${park.lng}&dirflg=w`
  } else if (/Android/.test(ua)) {
    window.location.href = `geo:${park.lat},${park.lng}?q=${encodeURIComponent(park.name)}`
  } else {
    window.open(`https://www.google.com/maps/dir/?api=1&destination=${park.lat},${park.lng}&travelmode=walking`, '_blank')
  }
}

/* ─── Lifecycle ─── */
onMounted(() => {
  loadTrail()
  initMap()
  startTracking()
})

onUnmounted(() => {
  if (watchId !== null) navigator.geolocation.clearWatch(watchId)
  clearTimeout(unlockTimer)
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

.leaflet-hud-btn:active {
  transform: scale(0.9) !important;
}

/* ═══════════════════════════════════
   Pulse
   ═══════════════════════════════════ */
.leaflet-hud-pulse {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: leaflet-hud-pulse-anim 1.5s ease-in-out infinite;
}

@keyframes leaflet-hud-pulse-anim {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.75); }
}

.leaflet-hud-dist {
  color: #059669 !important;
}

/* ═══════════════════════════════════
   UNLOCK
   ═══════════════════════════════════ */
.leaflet-hud-unlock {
  position: absolute !important;
  left: 50% !important;
  top: 50% !important;
  transform: translate(-50%, -50%) !important;
  pointer-events: none !important;
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

  box-shadow: 0 12px 32px rgba(0,0,0,0.18);

  font-family: var(--font-game), system-ui, sans-serif;
}

.pop-anim {
  animation: leaflet-hud-pop 0.3s ease, leaflet-hud-fadeout 0.4s ease 2.4s forwards;
}

@keyframes leaflet-hud-pop {
  from { transform: translate(-50%, -50%) scale(0.7); opacity: 0; }
  to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
}

@keyframes leaflet-hud-fadeout {
  from { opacity: 1; }
  to { opacity: 0; }
}
</style>

<style scoped>
/* Leaflet popup overrides */
#map :deep(.leaflet-popup-content-wrapper) {
  border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 2px;
}
#map :deep(.leaflet-popup-tip-container) { display: none; }
#map :deep(.leaflet-popup-content) { margin: 8px 12px; }

/* Override Leaflet control margins for tighter spacing */
#map :deep(.leaflet-top.leaflet-left .leaflet-control) { margin-left: 16px; margin-top: 16px; }
#map :deep(.leaflet-top.leaflet-right .leaflet-control) { margin-right: 16px; margin-top: 16px; }
#map :deep(.leaflet-bottom.leaflet-right .leaflet-control) { margin-right: 16px; margin-bottom: 16px; }
</style>