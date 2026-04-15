<template>
  <div class="flex flex-col h-full" style="font-family: var(--font-game)">

    <!-- Map -->
    <div class="relative" style="height: 55vh; flex-shrink: 0">
      <div id="map" class="w-full h-full"></div>

      <!-- Unlock animation -->
      <Transition name="pop">
        <div v-if="unlockAnim"
          class="absolute inset-0 flex items-center justify-center z-50 pointer-events-none">
          <div class="flex flex-col items-center gap-2">
            <div class="rounded-3xl px-6 py-4 flex flex-col items-center gap-1"
              style="background: white; border: 3px solid #34d399; border-bottom: 5px solid #16a34a">
              <PhMapPin :size="32" weight="duotone" color="#16a34a" />
              <p class="text-base font-black text-emerald-800">Park Unlocked!</p>
              <p class="text-sm font-bold text-emerald-600">{{ unlockAnim.name }}</p>
              <div class="flex items-center gap-1 mt-1">
                <PhLightning :size="14" weight="duotone" color="#f59e0b" />
                <span class="text-sm font-black text-amber-500">+50 XP</span>
              </div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Center button -->
      <button
        class="absolute bottom-4 right-4 z-40 w-10 h-10 rounded-2xl flex items-center justify-center"
        style="background: white; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1"
        @click="centerOnUser">
        <PhNavigationArrow :size="18" weight="duotone" color="#10b981" />
      </button>

      <!-- Victoria badge -->
      <div class="absolute top-4 left-4 z-40 rounded-2xl px-3 py-1.5 flex items-center gap-1.5"
        style="background: white; border: 2px solid #bbf7d0; border-bottom: 2px solid #34d399">
        <PhMapTrifold :size="14" weight="duotone" color="#10b981" />
        <span class="text-xs font-black text-emerald-700">Victoria, AU</span>
      </div>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
  PhMapPin, PhLightning, PhNavigationArrow,
  PhMapTrifold, PhTree, PhSealCheck
} from '@phosphor-icons/vue'

const UNLOCK_RADIUS_KM = 0.2

const parks = ref([
  { id: 1,  name: 'Flagstaff Gardens',      lat: -37.8090, lng: 144.9520, unlocked: true,  distance: null },
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
const unlockAnim = ref(null)

let map = null
let userMarker = null
let watchId = null
let fogOverlay = null
const parkMarkers = {}

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

const sortedParks = computed(() =>
  [...parks.value].sort((a, b) => {
    if (a.distance === null) return 1
    if (b.distance === null) return -1
    return a.distance - b.distance
  })
)

const unlockedCount = computed(() => parks.value.filter(p => p.unlocked).length)

function makePinIcon(unlocked, inRange = false) {
  const fill = unlocked ? '#16a34a' : inRange ? '#f59e0b' : '#cbd5e1'
  const stroke = unlocked ? '#064e3b' : inRange ? '#b45309' : '#94a3b8'
  const size = 22

  return L.divIcon({
    className: '',
    html: `
      <div style="width:${size}px;height:${Math.round(size * 1.25)}px;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.2))">
        <svg viewBox="0 0 32 40" fill="none" xmlns="http://www.w3.org/2000/svg"
          width="${size}" height="${Math.round(size * 1.25)}">
          <path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z"
            fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
          <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
        </svg>
      </div>`,
    iconSize: [size, Math.round(size * 1.25)],
    iconAnchor: [size / 2, Math.round(size * 1.25)],
    popupAnchor: [0, -Math.round(size * 1.25)],
  })
}

const FogCanvas = L.Layer.extend({
  onAdd(map) {
    this._map = map
    this._canvas = document.createElement('canvas')
    this._canvas.style.position = 'absolute'
    this._canvas.style.top = '0'
    this._canvas.style.left = '0'
    this._canvas.style.pointerEvents = 'none'
    this._canvas.style.zIndex = '400'
    map.getPane('overlayPane').appendChild(this._canvas)
    map.on('move zoom moveend zoomend resize', this._redraw, this)
    this._redraw()
  },

  onRemove(map) {
    map.off('move zoom moveend zoomend resize', this._redraw, this)
    this._canvas.remove()
  },

  _redraw() {
    const map = this._map
    const size = map.getSize()
    const canvas = this._canvas
    canvas.width = size.x
    canvas.height = size.y

    const topLeft = map.containerPointToLayerPoint([0, 0])
    L.DomUtil.setPosition(canvas, topLeft)

    const ctx = canvas.getContext('2d')
    ctx.clearRect(0, 0, size.x, size.y)

    ctx.fillStyle = 'rgba(20, 24, 35, 0.72)'
    ctx.fillRect(0, 0, size.x, size.y)

    ctx.globalCompositeOperation = 'destination-out'

    parks.value.filter(p => p.unlocked).forEach(park => {
      const pt = map.latLngToContainerPoint([park.lat, park.lng])

      // Convert 400m geographic radius to pixels at current zoom
      const edgePt = map.latLngToContainerPoint([
        park.lat + (0.4 / 111),
        park.lng
      ])
      const pixelRadius = Math.abs(edgePt.y - pt.y)

      const grad = ctx.createRadialGradient(pt.x, pt.y, 0, pt.x, pt.y, pixelRadius)
      grad.addColorStop(0,    'rgba(0,0,0,1)')
      grad.addColorStop(0.75, 'rgba(0,0,0,0.95)')
      grad.addColorStop(1,    'rgba(0,0,0,0)')

      ctx.beginPath()
      ctx.arc(pt.x, pt.y, pixelRadius, 0, Math.PI * 2)
      ctx.fillStyle = grad
      ctx.fill()
    })

    ctx.globalCompositeOperation = 'source-over'
  },

  update() {
    this._redraw()
  }
})

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
      </div>
    `, { closeButton: false, offset: [0, -8] })
  parkMarkers[park.id] = marker
}

function refreshMarker(park) {
  parkMarkers[park.id]?.setIcon(makePinIcon(park.unlocked))
}

function startTracking() {
  if (!navigator.geolocation) return

  watchId = navigator.geolocation.watchPosition(
    ({ coords: { latitude: lat, longitude: lng } }) => {
      userPos.value = { lat, lng }

      parks.value.forEach(p => {
        p.distance = haversine(lat, lng, p.lat, p.lng)
      })

      if (!userMarker) {
        const icon = L.divIcon({
          className: '',
          html: `<div style="
            width:18px;height:18px;border-radius:50%;
            background:#3b82f6;border:3px solid white;
            box-shadow:0 0 0 5px rgba(59,130,246,0.25)">
          </div>`,
          iconSize: [18, 18],
          iconAnchor: [9, 9],
        })
        userMarker = L.marker([lat, lng], { icon, zIndexOffset: 1000 }).addTo(map)
        map.setView([lat, lng], 14)
      } else {
        userMarker.setLatLng([lat, lng])
      }

      checkUnlocks(lat, lng)
    },
    err => console.warn('Geo error:', err),
    { enableHighAccuracy: true, maximumAge: 10000, timeout: 15000 }
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
      // TODO: POST to backend to save unlock
    }
  })
  if (anyNew) fogOverlay?.update()
}

function showUnlockAnim(park) {
  unlockAnim.value = park
  setTimeout(() => { unlockAnim.value = null }, 3000)
}

function centerOnUser() {
  if (userPos.value) map.setView([userPos.value.lat, userPos.value.lng], 15)
}

function focusPark(park) {
  map.setView([park.lat, park.lng], 16)
  parkMarkers[park.id]?.openPopup()
}

function navigateToPark(park) {
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent)
  const isAndroid = /Android/.test(navigator.userAgent)

  if (isIOS) {
    window.location.href = `maps://maps.apple.com/?daddr=${park.lat},${park.lng}&dirflg=w`
  } else if (isAndroid) {
    window.location.href = `geo:${park.lat},${park.lng}?q=${encodeURIComponent(park.name)}`
  } else {
    window.open(
      `https://www.google.com/maps/dir/?api=1&destination=${park.lat},${park.lng}&travelmode=walking`,
      '_blank'
    )
  }
}

onMounted(() => {
  initMap()
  startTracking()
})

onUnmounted(() => {
  if (watchId !== null) navigator.geolocation.clearWatch(watchId)
  map?.remove()
})
</script>

<style scoped>
#map :deep(.leaflet-popup-content-wrapper) {
  border-radius: 14px;
  border: 1.5px solid #e2e8f0;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  padding: 2px;
}
#map :deep(.leaflet-popup-tip-container) {
  display: none;
}
#map :deep(.leaflet-popup-content) {
  margin: 8px 12px;
}
.pop-enter-active { animation: popIn 0.3s ease; }
.pop-leave-active { animation: popIn 0.2s ease reverse; }
@keyframes popIn {
  from { transform: scale(0.8); opacity: 0; }
  to   { transform: scale(1);   opacity: 1; }
}
</style>