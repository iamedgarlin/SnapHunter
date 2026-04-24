<template>
    <div class="flex flex-col h-full" style="font-family: var(--font-game)">

        <!-- POI detail modal -->
        <Transition name="pop">
            <div v-if="activePoi" class="poi-overlay" @click="activePoi = null">
                <div class="poi-detail-card" @click.stop>
                    <div class="poi-type-badge" :style="`background:${typeColor(activePoi.type)}`">
                        {{ typeLabel(activePoi.type) }}
                    </div>
                    <component :is="typeIcon(activePoi.type)" :size="32" weight="duotone"
                        :color="typeColor(activePoi.type)" />
                    <p class="text-base font-black text-gray-800 mt-1">{{ activePoi.name }}</p>
                    <p class="text-xs text-gray-500 text-center leading-snug mt-1" style="max-width: 260px">
                        {{ activePoi.story }}
                    </p>
                    <div class="poi-fun-fact" v-if="activePoi.funFact">
                        <PhLightning :size="14" weight="duotone" color="#f59e0b" />
                        <span>{{ activePoi.funFact }}</span>
                    </div>
                    <div v-if="activePoi.task" class="poi-task-card">
                        <p class="text-xs font-black text-blue-700">Challenge</p>
                        <p class="text-xs text-gray-600 mt-0.5">{{ activePoi.task }}</p>
                    </div>
                    <button class="poi-close-btn" @click="activePoi = null">Got it!</button>
                </div>
            </div>
        </Transition>

        <!-- Header -->
        <div class="relative overflow-hidden px-4 pt-5 pb-4"
            style="background: linear-gradient(160deg, #ddd6fe, #c4b5fd); border-radius: 0 0 28px 28px; border-bottom: 4px solid #8b5cf6">
            <button class="absolute top-5 left-4 w-8 h-8 rounded-xl flex items-center justify-center"
                style="background: rgba(255,255,255,0.5); border: 1.5px solid #a78bfa" @click="$router.back()">
                <PhCaretLeft :size="18" weight="bold" color="#7c3aed" />
            </button>
            <div class="text-center">
                <div
                    class="inline-flex items-center gap-1 bg-white/50 rounded-full px-2.5 py-0.5 text-xs font-black text-violet-700 mb-1">
                    <PhCastleTurret :size="12" weight="duotone" color="#7c3aed" />
                    EPIC PARK
                </div>
                <h1 class="text-xl font-black text-violet-900">{{ parkData.name }}</h1>
                <p class="text-xs text-violet-600 mt-0.5">{{ discoveredCount }}/{{ parkData.pois.length }} spots
                    discovered</p>
            </div>
            <div class="flex justify-center gap-1.5 mt-2">
                <div v-for="poi in parkData.pois" :key="poi.id"
                    class="w-2.5 h-2.5 rounded-full transition-all duration-300" :style="isDiscovered(poi.id)
                        ? 'background: #7c3aed; box-shadow: 0 0 6px rgba(124,58,237,0.4)'
                        : 'background: white; opacity: 0.5'" />
            </div>
        </div>

        <!-- Map -->
        <div class="relative" style="height: 30vh; flex-shrink: 0">
            <div id="explore-map" class="w-full h-full"></div>
        </div>

        <!-- POI list -->
        <div class="flex-1 overflow-y-auto" style="background: #faf5ff">
            <div class="px-4 pt-3 pb-6 flex flex-col gap-2.5">
                <div class="flex items-center gap-1.5 mb-1">
                    <PhMapPin :size="14" weight="duotone" color="#7c3aed" />
                    <p class="text-xs font-black text-violet-700">Treasure Spots</p>
                </div>

                <div v-for="poi in sortedPois" :key="poi.id" class="poi-card"
                    :class="{ 'poi-card-active': isNearby(poi) && !isDiscovered(poi.id), 'poi-card-discovered': isDiscovered(poi.id) }"
                    @click="handlePoiTap(poi)">

                    <div class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0" :style="isDiscovered(poi.id)
                        ? `background:${typeColor(poi.type)}15; border:2px solid ${typeColor(poi.type)}40; border-bottom:3px solid ${typeColor(poi.type)}60`
                        : isNearby(poi)
                            ? 'background:#fef3c7; border:2px solid #fde68a; border-bottom:3px solid #f59e0b'
                            : 'background:#f1f5f9; border:2px solid #e2e8f0; border-bottom:3px solid #cbd5e1'">
                        <component :is="typeIcon(poi.type)" :size="20" weight="duotone"
                            :color="isDiscovered(poi.id) ? typeColor(poi.type) : isNearby(poi) ? '#d97706' : '#94a3b8'" />
                    </div>

                    <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-1.5">
                            <p class="text-sm font-black truncate"
                                :style="isDiscovered(poi.id) ? `color:${typeColor(poi.type)}` : isNearby(poi) ? 'color:#92400e' : 'color:#6b7280'">
                                {{ poi.name }}
                            </p>
                            <PhSealCheck v-if="isDiscovered(poi.id)" :size="13" weight="duotone"
                                :color="typeColor(poi.type)" />
                        </div>
                        <p class="text-xs text-gray-400 mt-0.5 truncate">
                            <template v-if="isNearby(poi) && !isDiscovered(poi.id)">
                                <span class="font-black text-amber-600">Tap to discover!</span>
                            </template>
                            <template v-else-if="isDiscovered(poi.id)">
                                {{ poi.brief }}
                            </template>
                            <template v-else>
                                {{ formatPoiDistance(poi) }} away
                            </template>
                        </p>
                    </div>

                    <span class="text-xs font-bold px-2 py-0.5 rounded-lg flex-shrink-0" :style="isDiscovered(poi.id)
                        ? `background:${typeColor(poi.type)}15; color:${typeColor(poi.type)}`
                        : 'background:#f1f5f9; color:#94a3b8'">
                        {{ typeLabel(poi.type) }}
                    </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import {
    PhCastleTurret, PhCaretLeft, PhMapPin, PhSealCheck, PhLightning,
    PhTree, PhBuildings, PhPalette
} from '@phosphor-icons/vue'

const POI_DISCOVER_RADIUS_KM = 0.05

const ALL_PARKS = {
    2: {
        name: 'Fitzroy Gardens',
        center: { lat: -37.8136, lng: 144.9793 },
        zoom: 16,
        pois: [
            {
                id: 'cooks-cottage', name: "Captain Cook's Cottage",
                lat: -37.81375, lng: 144.97965, type: 'history',
                brief: 'Oldest building in Australia, shipped from England',
                story: "This cottage was built in 1755 in Yorkshire, England, by Captain James Cook's parents. In 1934, Sir Russell Grimwade purchased it for 800 pounds, had every brick numbered, packed into 253 cases and 40 barrels, and shipped it to Melbourne. Even the ivy growing on the walls came from cuttings of the original. It is the oldest building in Australia.",
                funFact: "Captain Cook probably never actually lived here. His father built it after James had already left for the navy.",
                task: 'Can you count how many windows the cottage has? Look carefully at both floors.',
            },
            {
                id: 'fairies-tree', name: "Fairies' Tree",
                lat: -37.81295, lng: 144.98020, type: 'culture',
                brief: 'A tree stump carved with magical creatures',
                story: "In 1934, artist Ola Cohn spent months carving fairies, pixies, kangaroos, emus, and possums into a 300-year-old red gum tree stump. She donated it to the children of Melbourne. The tiny carved figures tell stories of Australian bush creatures living alongside magical fairy-folk.",
                funFact: "Ola Cohn carved the tree during the same year Cook's Cottage arrived. 1934 was a big year for Fitzroy Gardens.",
                task: 'Find 3 different animals carved into the tree. What Australian animals can you spot?',
            },
            {
                id: 'conservatory', name: 'Conservatory',
                lat: -37.81355, lng: 144.97755, type: 'nature',
                brief: 'Spanish mission style flower house since 1930',
                story: "The Conservatory was built in 1930 in a beautiful Spanish mission architectural style. Inside, you will find stunning flower displays that change five times each year. This means the Conservatory is always in bloom with hydrangeas, fuchsias, begonias, cyclamens, and calceolarias. It is also a popular spot for wedding photographs.",
                funFact: 'The flowers inside change 5 times a year, so every visit looks different.',
                task: 'How many different colours of flowers can you spot? Try to count at least 5 different colours.',
            },
            {
                id: 'tudor-village', name: 'Model Tudor Village',
                lat: -37.81285, lng: 144.97990, type: 'history',
                brief: 'Miniature English village, a thank-you gift',
                story: "This tiny model village was created in the 1940s by Edgar Wilson, a retired London pensioner. He built it as a thank-you gift to Melbourne for sending food to Britain during World War II. The village has thatched cottages, a church, school, hotel, barns, and stocks, looking just like an English Tudor village from hundreds of years ago.",
                funFact: 'The village was a thank-you for food parcels Melbourne sent to London during World War II.',
                task: 'The village has tiny buildings. Can you find the church? How about the school?',
            },
            {
                id: 'elm-avenue', name: 'Avenue of Elms',
                lat: -37.81330, lng: 144.97680, type: 'nature',
                brief: 'Walk under 150-year-old English elm trees',
                story: "Fitzroy Gardens is famous for its grand avenues lined with English elm trees, many over 150 years old. These trees were planted in the 1860s and 1870s. In autumn, they turn brilliant gold and orange. The elm-lined paths follow the original Victorian-era design by Clement Hodgkinson.",
                funFact: 'Some of these elm trees are among the oldest surviving English elms in the world.',
                task: 'Stand under the biggest elm tree you can find. Can you wrap your arms around its trunk? How many people would it take?',
            },
            {
                id: 'scarred-tree', name: 'Scarred Tree',
                lat: -37.81410, lng: 144.97860, type: 'culture',
                brief: 'Aboriginal scar tree with deep cultural meaning',
                story: "This River Red Gum tree bears scars from bark removed by Wurundjeri Woi-wurrung people hundreds of years ago. Aboriginal people used the bark to make canoes, shields, and containers called coolamons. The scars are a powerful reminder that this land has been cared for by Indigenous Australians for tens of thousands of years.",
                funFact: 'The Wurundjeri people called this area Yarro-yarro, meaning flowing river, referring to the nearby Yarra.',
                task: 'Look at the scar on the tree. What shape is it? Can you guess what the bark was used to make?',
            },
        ],
    },
}

const route = useRoute()
const parkId = parseInt(route.query.parkId) || 2
const parkData = ALL_PARKS[parkId] || ALL_PARKS[2]

const userPos = ref(null)
const discovered = ref(new Set())
const activePoi = ref(null)

let map = null
let userMarker = null
let watchId = null
const poiMarkers = {}

function typeColor(t) { return t === 'history' ? '#b45309' : t === 'culture' ? '#7c3aed' : '#16a34a' }
function typeLabel(t) { return t === 'history' ? 'History' : t === 'culture' ? 'Culture' : 'Nature' }
function typeIcon(t) { return t === 'history' ? PhBuildings : t === 'culture' ? PhPalette : PhTree }

function haversine(a, b, c, d) {
    const R = 6371, dLat = (c - a) * Math.PI / 180, dLng = (d - b) * Math.PI / 180
    const x = Math.sin(dLat / 2) ** 2 + Math.cos(a * Math.PI / 180) * Math.cos(c * Math.PI / 180) * Math.sin(dLng / 2) ** 2
    return R * 2 * Math.atan2(Math.sqrt(x), Math.sqrt(1 - x))
}

function isNearby(poi) {
    if (!userPos.value) return false
    return haversine(userPos.value.lat, userPos.value.lng, poi.lat, poi.lng) <= POI_DISCOVER_RADIUS_KM
}
function isDiscovered(poiId) { return discovered.value.has(poiId) }
function formatPoiDistance(poi) {
    if (!userPos.value) return '?'
    const km = haversine(userPos.value.lat, userPos.value.lng, poi.lat, poi.lng)
    return km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`
}

const discoveredCount = computed(() => discovered.value.size)
const sortedPois = computed(() => {
    return [...parkData.pois].sort((a, b) => {
        const aD = isDiscovered(a.id) ? 0 : 1, bD = isDiscovered(b.id) ? 0 : 1
        if (aD !== bD) return aD - bD
        const aN = isNearby(a) ? 0 : 1, bN = isNearby(b) ? 0 : 1
        if (aN !== bN) return aN - bN
        if (!userPos.value) return 0
        return haversine(userPos.value.lat, userPos.value.lng, a.lat, a.lng) - haversine(userPos.value.lat, userPos.value.lng, b.lat, b.lng)
    })
})

function handlePoiTap(poi) {
    if (isNearby(poi) || isDiscovered(poi.id)) {
        discovered.value.add(poi.id)
        persistDiscovered()
        activePoi.value = poi
        refreshPoiMarker(poi)
        if ('speechSynthesis' in window) {
            const u = new SpeechSynthesisUtterance(`You found ${poi.name}. ${poi.brief}`)
            u.lang = 'en-AU'; u.rate = 0.9; speechSynthesis.speak(u)
        }
    } else {
        map?.setView([poi.lat, poi.lng], 18)
        poiMarkers[poi.id]?.openPopup()
    }
}

function persistDiscovered() {
    try { localStorage.setItem(`snaphunter_epic_${parkId}`, JSON.stringify([...discovered.value])) } catch (e) { }
}
function loadDiscovered() {
    try { const r = localStorage.getItem(`snaphunter_epic_${parkId}`); if (r) discovered.value = new Set(JSON.parse(r)) } catch (e) { }
}

function makePoiIcon(poi) {
    const disc = isDiscovered(poi.id), near = isNearby(poi)
    const fill = disc ? typeColor(poi.type) : near ? '#f59e0b' : '#94a3b8'
    const stroke = disc ? typeColor(poi.type) : near ? '#b45309' : '#64748b'
    const s = disc || near ? 24 : 20
    return L.divIcon({
        className: '',
        html: `<div style="width:${s}px;height:${Math.round(s * 1.25)}px;filter:drop-shadow(0 1px 3px rgba(0,0,0,0.25))${near && !disc ? ';animation:poi-pulse 1.5s ease-in-out infinite' : ''}">
      <svg viewBox="0 0 32 40" width="${s}" height="${Math.round(s * 1.25)}">
        <path d="M16 0C9.373 0 4 5.373 4 12c0 9 12 28 12 28S28 21 28 12C28 5.373 22.627 0 16 0z" fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>
        <circle cx="16" cy="12" r="5" fill="white" opacity="0.9"/>
      </svg></div>`,
        iconSize: [s, Math.round(s * 1.25)], iconAnchor: [s / 2, Math.round(s * 1.25)], popupAnchor: [0, -Math.round(s * 1.25)],
    })
}

function poiPopupHtml(poi) {
    const disc = isDiscovered(poi.id), near = isNearby(poi)
    const color = disc ? typeColor(poi.type) : '#6b7280'
    return `<div style="font-family:sans-serif;text-align:center;padding:3px 2px">
    <p style="font-weight:900;font-size:12px;margin:0 0 2px;color:${color}">${poi.name}</p>
    <p style="font-size:10px;color:#94a3b8;margin:0">${disc ? poi.brief : near ? 'Tap to discover!' : 'Get closer to unlock'}</p></div>`
}

function refreshPoiMarker(poi) {
    const m = poiMarkers[poi.id]; if (!m) return
    m.setIcon(makePoiIcon(poi)); m.setPopupContent(poiPopupHtml(poi))
}
function refreshAllMarkers() { parkData.pois.forEach(p => refreshPoiMarker(p)) }

function initMap() {
    map = L.map('explore-map', { center: [parkData.center.lat, parkData.center.lng], zoom: parkData.zoom, zoomControl: false })
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap', maxZoom: 19 }).addTo(map)
    parkData.pois.forEach(poi => {
        poiMarkers[poi.id] = L.marker([poi.lat, poi.lng], { icon: makePoiIcon(poi) }).addTo(map)
            .bindPopup(poiPopupHtml(poi), { closeButton: false, offset: [0, -6] })
    })
    map.fitBounds(L.latLngBounds(parkData.pois.map(p => [p.lat, p.lng])), { padding: [40, 40] })
}

function startTracking() {
    if (!navigator.geolocation) return
    watchId = navigator.geolocation.watchPosition(({ coords: { latitude: lat, longitude: lng } }) => {
        userPos.value = { lat, lng }
        if (!userMarker) {
            userMarker = L.marker([lat, lng], {
                icon: L.divIcon({
                    className: '',
                    html: `<div style="width:16px;height:16px;border-radius:50%;background:#3b82f6;border:3px solid white;box-shadow:0 0 0 4px rgba(59,130,246,0.25)"></div>`,
                    iconSize: [16, 16], iconAnchor: [8, 8]
                }), zIndexOffset: 1000
            }).addTo(map)
        } else { userMarker.setLatLng([lat, lng]) }
        refreshAllMarkers()
    }, err => console.warn('Geo:', err), { enableHighAccuracy: true, maximumAge: 5000, timeout: 15000 })
}

onMounted(() => { loadDiscovered(); initMap(); startTracking() })
onUnmounted(() => { if (watchId !== null) navigator.geolocation.clearWatch(watchId); map?.remove() })
</script>

<style>
@keyframes poi-pulse {

    0%,
    100% {
        transform: scale(1)
    }

    50% {
        transform: scale(1.15)
    }
}
</style>

<style scoped>
.poi-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 18px;
    background: white;
    border: 2px solid #e2e8f0;
    border-bottom: 3px solid #cbd5e1;
    cursor: pointer;
    transition: all 0.2s;
}

.poi-card:active {
    transform: scale(0.97)
}

.poi-card-active {
    border-color: #fde68a;
    border-bottom-color: #f59e0b;
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    animation: poi-glow 2s ease-in-out infinite;
}

@keyframes poi-glow {

    0%,
    100% {
        box-shadow: 0 0 0 0 rgba(245, 158, 11, 0)
    }

    50% {
        box-shadow: 0 0 12px 2px rgba(245, 158, 11, 0.15)
    }
}

.poi-card-discovered {
    border-color: #e9d5ff;
    border-bottom-color: #a78bfa;
    background: #faf5ff;
    animation: none;
}

.poi-overlay {
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(0, 0, 0, 0.25);
}

.poi-detail-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    padding: 24px 24px 20px;
    border-radius: 28px;
    background: white;
    border: 3px solid #ddd6fe;
    border-bottom: 5px solid #8b5cf6;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
    font-family: var(--font-game), system-ui, sans-serif;
    max-width: 320px;
    margin: 0 16px;
}

.poi-type-badge {
    font-size: 9px;
    font-weight: 900;
    color: white;
    padding: 2px 10px;
    border-radius: 8px;
    letter-spacing: 1px;
    margin-bottom: 2px;
}

.poi-fun-fact {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    background: #fffbeb;
    border: 1.5px solid #fde68a;
    border-radius: 12px;
    padding: 8px 12px;
    margin-top: 6px;
    font-size: 11px;
    color: #92400e;
    line-height: 1.4;
}

.poi-task-card {
    background: #eff6ff;
    border: 1.5px solid #bfdbfe;
    border-radius: 12px;
    padding: 8px 12px;
    margin-top: 4px;
    width: 100%;
}

.poi-close-btn {
    margin-top: 10px;
    padding: 8px 28px;
    border-radius: 14px;
    background: linear-gradient(135deg, #8b5cf6, #7c3aed);
    border: none;
    border-bottom: 3px solid #5b21b6;
    color: white;
    font-size: 13px;
    font-weight: 900;
    cursor: pointer;
    font-family: var(--font-game), system-ui, sans-serif;
    transition: transform 0.1s;
}

.poi-close-btn:active {
    transform: scale(0.95)
}

.pop-enter-active {
    animation: pop-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1)
}

.pop-leave-active {
    animation: pop-out 0.3s ease forwards
}

@keyframes pop-in {
    from {
        transform: scale(0.6);
        opacity: 0
    }

    to {
        transform: scale(1);
        opacity: 1
    }
}

@keyframes pop-out {
    from {
        opacity: 1
    }

    to {
        opacity: 0
    }
}

#explore-map :deep(.leaflet-popup-content-wrapper) {
    border-radius: 12px;
    border: 1.5px solid #e2e8f0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    padding: 2px
}

#explore-map :deep(.leaflet-popup-tip-container) {
    display: none
}

#explore-map :deep(.leaflet-popup-content) {
    margin: 6px 10px
}
</style>