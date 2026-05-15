<template>
  <div class="min-h-full pb-6" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Header -->
    <div class="relative overflow-hidden px-4 pt-6 pb-5"
      style="background: linear-gradient(160deg, #fef3c7, #fde68a); border-radius: 0 0 32px 32px; border-bottom: 4px solid #fbbf24">
      <h1 class="text-2xl font-black text-amber-900">Your Badges</h1>
      <p class="text-xs font-bold text-amber-700 mt-1">Collect them all!</p>
      <div class="mt-3 inline-flex items-center gap-1 bg-white/60 rounded-full px-3 py-1">
        <PhMedal :size="14" weight="duotone" color="#d97706" />
        <span class="text-xs font-black text-amber-800">{{ earnedCount }} / {{ totalCount }} earned</span>
      </div>
    </div>

    <div class="px-4 flex flex-col gap-5 mt-4">

      <!-- Series badges -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <PhStarFour :size="16" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-gray-700">Series Badges</p>
        </div>
        <div class="flex gap-3">
          <div v-for="badge in seriesBadges" :key="badge.id"
            class="flex-1 flex flex-col items-center gap-2 p-4 rounded-2xl cursor-pointer active:scale-95 transition-all"
            :style="isBadgeEarned(badge.id)
              ? `background: ${badge.iconBg}; border: 2px solid ${badge.borderColor}; border-bottom: 3px solid ${badge.borderBottomColor}`
              : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'"
            @click="openBadgeDetail(badge)">

            <!-- Badge icon -->
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center relative"
              :style="isBadgeEarned(badge.id)
                ? `background: white; border: 2px solid ${badge.borderColor}; border-bottom: 3px solid ${badge.borderBottomColor}`
                : 'background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'">
              <component :is="badge.icon" :size="28" weight="duotone"
                :color="isBadgeEarned(badge.id) ? badge.color : '#cbd5e1'" />
              <!-- Lock overlay for unearned -->
              <div v-if="!isBadgeEarned(badge.id)"
                class="absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center"
                style="background: #e2e8f0; border: 1.5px solid white">
                <PhLock :size="10" weight="bold" color="#94a3b8" />
              </div>
            </div>

            <p class="text-xs font-black text-center leading-tight"
              :style="isBadgeEarned(badge.id) ? `color: ${badge.color}` : 'color: #94a3b8'">
              {{ badge.name }}
            </p>

            <div v-if="isBadgeEarned(badge.id)"
              class="text-xs font-black px-2 py-0.5 rounded-lg"
              :style="`background: ${badge.borderColor}; color: ${badge.color}`">
              Earned!
            </div>
            <p v-else class="text-xs font-semibold text-gray-400 text-center leading-tight">
              Tap to see how
            </p>
          </div>
        </div>
      </div>

      <!-- Epic Park Badges -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <PhMapTrifold :size="16" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-gray-700">Epic Park Badges</p>
        </div>

        <!-- Individual epic park badges -->
        <div class="grid grid-cols-3 gap-3 mb-3">
          <div v-for="badge in epicParkBadges" :key="badge.id"
            class="flex flex-col items-center gap-2 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all"
            :style="isBadgeEarned(badge.id)
              ? 'background: #ecfdf5; border: 2px solid #a7f3d0; border-bottom: 3px solid #34d399'
              : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'"
            @click="openBadgeDetail(badge)">
            <div class="w-14 h-14 rounded-2xl overflow-hidden relative"
              :style="isBadgeEarned(badge.id)
                ? 'border: 2px solid #a7f3d0; border-bottom: 3px solid #34d399'
                : 'border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'">
              <img :src="badge.image" :alt="badge.name"
                class="w-full h-full object-contain p-1"
                :class="{ 'grayscale opacity-40': !isBadgeEarned(badge.id) }" />
              <!-- Lock overlay for unearned -->
              <div v-if="!isBadgeEarned(badge.id)"
                class="absolute inset-0 flex items-center justify-center">
                <div class="w-6 h-6 rounded-full flex items-center justify-center"
                  style="background: rgba(226,232,240,0.9); border: 1.5px solid white">
                  <PhLock :size="12" weight="bold" color="#94a3b8" />
                </div>
              </div>
            </div>
            <p class="text-xs font-black text-center leading-tight"
              :style="isBadgeEarned(badge.id) ? 'color: #065f46' : 'color: #94a3b8'">
              {{ badge.name }}
            </p>
            <div v-if="isBadgeEarned(badge.id)"
              class="text-xs font-black px-2 py-0.5 rounded-lg"
              style="background: #a7f3d0; color: #065f46">
              Earned!
            </div>
            <p v-else class="text-xs font-semibold text-gray-400 text-center leading-tight">
              Tap to see how
            </p>
          </div>
        </div>

        <!-- Master epic badge (Melbourne Epic) -->
        <div
          class="flex items-center gap-4 p-4 rounded-2xl cursor-pointer active:scale-95 transition-all"
          :style="isBadgeEarned(epicMasterBadge.id)
            ? 'background: linear-gradient(135deg, #ecfdf5, #fef3c7); border: 2px solid #a7f3d0; border-bottom: 4px solid #fbbf24'
            : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 4px solid #cbd5e1'"
          @click="openBadgeDetail(epicMasterBadge)">
          <div class="w-16 h-16 rounded-2xl overflow-hidden flex-shrink-0 relative"
            :style="isBadgeEarned(epicMasterBadge.id)
              ? 'border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24'
              : 'border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'">
            <img :src="epicMasterBadge.image" :alt="epicMasterBadge.name"
              class="w-full h-full object-contain p-1"
              :class="{ 'grayscale opacity-40': !isBadgeEarned(epicMasterBadge.id) }" />
            <div v-if="!isBadgeEarned(epicMasterBadge.id)"
              class="absolute inset-0 flex items-center justify-center">
              <div class="w-6 h-6 rounded-full flex items-center justify-center"
                style="background: rgba(226,232,240,0.9); border: 1.5px solid white">
                <PhLock :size="12" weight="bold" color="#94a3b8" />
              </div>
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-black leading-tight"
              :style="isBadgeEarned(epicMasterBadge.id) ? 'color: #92400e' : 'color: #94a3b8'">
              {{ epicMasterBadge.name }}
            </p>
            <p class="text-xs font-semibold mt-0.5 leading-tight"
              :style="isBadgeEarned(epicMasterBadge.id) ? 'color: #d97706' : 'color: #cbd5e1'">
              {{ epicMasterBadge.description }}
            </p>
            <!-- Progress dots -->
            <div class="flex items-center gap-1.5 mt-2">
              <div v-for="park in epicParkBadges" :key="park.id"
                class="w-4 h-4 rounded-full flex items-center justify-center"
                :style="isBadgeEarned(park.id)
                  ? 'background: #34d399; border: 1.5px solid #10b981'
                  : 'background: #e2e8f0; border: 1.5px solid #cbd5e1'">
                <PhCheck v-if="isBadgeEarned(park.id)" :size="10" weight="bold" color="white" />
              </div>
              <span class="text-xs font-bold ml-1"
                :style="isBadgeEarned(epicMasterBadge.id) ? 'color: #10b981' : 'color: #94a3b8'">
                {{ epicParkEarnedCount }} / {{ epicParkBadges.length }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Achievement badges -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <PhTrophy :size="16" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-gray-700">Achievements</p>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div v-for="badge in achievementBadges" :key="badge.id"
            class="flex flex-col items-center gap-2 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all"
            :style="isBadgeEarned(badge.id)
              ? 'background: white; border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24'
              : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'"
            @click="openBadgeDetail(badge)">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center relative"
              :style="isBadgeEarned(badge.id)
                ? 'background: #fef3c7; border: 2px solid #fde68a'
                : 'background: #f1f5f9; border: 2px solid #e2e8f0'">
              <component :is="badge.icon" :size="24" weight="duotone"
                :color="isBadgeEarned(badge.id) ? '#d97706' : '#cbd5e1'" />
              <div v-if="!isBadgeEarned(badge.id)"
                class="absolute -bottom-1 -right-1 w-4 h-4 rounded-full flex items-center justify-center"
                style="background: #e2e8f0; border: 1.5px solid white">
                <PhLock :size="8" weight="bold" color="#94a3b8" />
              </div>
            </div>
            <p class="text-xs font-black text-center leading-tight"
              :style="isBadgeEarned(badge.id) ? 'color: #92400e' : 'color: #94a3b8'">
              {{ badge.name }}
            </p>
            <p class="text-xs font-semibold text-gray-400 text-center leading-tight">
              {{ badge.description }}
            </p>
          </div>
        </div>
      </div>

    </div>

    <!-- Badge detail modal -->
    <div v-if="showDetail"
      class="fixed inset-0 flex items-center justify-center z-50 px-6"
      style="background: rgba(0,0,0,0.4)"
      @click.self="showDetail = false">
      <div class="w-full max-w-sm bg-white rounded-3xl p-6 flex flex-col items-center gap-4"
        style="border-bottom: 4px solid #fbbf24">

        <!-- Large badge icon / image -->
        <div v-if="detailBadge.image"
          class="w-24 h-24 rounded-3xl overflow-hidden"
          :style="isBadgeEarned(detailBadge.id)
            ? 'border: 3px solid #a7f3d0; border-bottom: 5px solid #34d399'
            : 'border: 3px solid #e2e8f0; border-bottom: 5px solid #cbd5e1'">
          <img :src="detailBadge.image" :alt="detailBadge.name"
            class="w-full h-full object-contain p-1"
            :class="{ 'grayscale opacity-40': !isBadgeEarned(detailBadge.id) }" />
        </div>
        <div v-else class="w-24 h-24 rounded-3xl flex items-center justify-center"
          :style="isBadgeEarned(detailBadge.id)
            ? `background: ${detailBadge.iconBg || '#fef3c7'}; border: 3px solid ${detailBadge.borderColor || '#fde68a'}; border-bottom: 5px solid ${detailBadge.borderBottomColor || '#fbbf24'}`
            : 'background: #f1f5f9; border: 3px solid #e2e8f0; border-bottom: 5px solid #cbd5e1'">
          <component :is="detailBadge.icon" :size="48" weight="duotone"
            :color="isBadgeEarned(detailBadge.id) ? (detailBadge.color || '#d97706') : '#cbd5e1'" />
        </div>

        <div class="text-center">
          <p class="text-xl font-black text-gray-800">{{ detailBadge.name }}</p>
          <p class="text-sm font-semibold text-gray-400 mt-1">{{ detailBadge.description }}</p>
        </div>

        <!-- Earned or how to get -->
        <div v-if="isBadgeEarned(detailBadge.id)"
          class="w-full rounded-2xl p-4 text-center"
          style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399">
          <div class="flex items-center justify-center gap-2 mb-1">
            <PhCheckCircle :size="18" weight="duotone" color="#16a34a" />
            <p class="text-sm font-black text-emerald-700">Badge Earned!</p>
          </div>
          <p class="text-xs font-semibold text-emerald-500">Congratulations, keep going!</p>
        </div>
        <div v-else
          class="w-full rounded-2xl p-4"
          style="background: #fffbeb; border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24">
          <div class="flex items-center gap-2 mb-2">
            <PhLock :size="16" weight="duotone" color="#d97706" />
            <p class="text-sm font-black text-amber-800">How to unlock</p>
          </div>
          <p class="text-sm font-semibold text-amber-700">{{ detailBadge.howToGet }}</p>
        </div>

        <button class="w-full py-3 rounded-2xl font-black text-sm text-gray-500 transition-all active:scale-95"
          style="background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1"
          @click="showDetail = false">
          Close
        </button>
      </div>
    </div>

  </div>

  <!-- Onboarding -->
  <Teleport to="body">
    <div v-if="showOb" class="fixed inset-0 z-[999]" @click="nextOb">
      <div class="absolute inset-0 bg-black/50"></div>
      <div v-if="obStep === 0" class="ob-card-badges" style="top: 28%; left: 50%; transform: translateX(-50%);">
        <div class="ob-arrow-up-b"></div>
        <div class="flex items-center gap-2 mb-2">
          <PhMedal :size="20" weight="duotone" color="#f59e0b" />
          <p class="text-base font-black text-gray-800">Your Badge Collection</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Earn badges by completing series tasks, visiting Epic Parks, and reaching achievements like streaks or photo milestones.
        </p>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">1 / 2</span>
          <button class="ob-next-b" @click.stop="nextOb">Next</button>
        </div>
      </div>
      <div v-if="obStep === 1" class="ob-card-badges" style="top: 42%; left: 50%; transform: translateX(-50%);">
        <div class="flex items-center gap-2 mb-2">
          <PhLock :size="20" weight="duotone" color="#d97706" />
          <p class="text-base font-black text-gray-800">Unlock Badges</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Tap any badge to see how to unlock it. Locked badges show what you need to do. Earned badges display a green checkmark!
        </p>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">2 / 2</span>
          <button class="ob-next-b" @click.stop="nextOb">Got it!</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProgressStore } from '../stores/progress'
import {
  PhMedal, PhStarFour, PhTrophy, PhLock, PhCheckCircle, PhCheck,
  PhTree, PhBuildings, PhPaintBrush, PhMapTrifold,
  PhSneaker, PhFlame, PhCamera, PhMapPin, PhSun
} from '@phosphor-icons/vue'

const progressStore = useProgressStore()
const DEFS = progressStore.BADGE_DEFINITIONS

const showDetail = ref(false)
const detailBadge = ref(null)

// Onboarding
const OB_KEY = 'snaphunter_badges_onboarded'
const showOb = ref(false)
const obStep = ref(0)
function nextOb() {
  if (obStep.value < 1) { obStep.value++ } else { showOb.value = false; localStorage.setItem(OB_KEY, 'true') }
}

// Series badges with visual config
const seriesBadges = [
  {
    id: 'nature',
    name: DEFS.nature.name,
    description: DEFS.nature.description,
    howToGet: DEFS.nature.howToGet,
    icon: PhTree,
    color: '#16a34a',
    iconBg: '#f0fdf4',
    borderColor: '#bbf7d0',
    borderBottomColor: '#34d399',
  },
  {
    id: 'urban',
    name: DEFS.urban.name,
    description: DEFS.urban.description,
    howToGet: DEFS.urban.howToGet,
    icon: PhBuildings,
    color: '#3b82f6',
    iconBg: '#eff6ff',
    borderColor: '#bfdbfe',
    borderBottomColor: '#93c5fd',
  },
  {
    id: 'art',
    name: DEFS.art.name,
    description: DEFS.art.description,
    howToGet: DEFS.art.howToGet,
    icon: PhPaintBrush,
    color: '#a855f7',
    iconBg: '#faf5ff',
    borderColor: '#e9d5ff',
    borderBottomColor: '#d8b4fe',
  },
]

// Epic Park badges (individual parks)
const epicParkBadges = [
  {
    id: 'epic_flinders',
    name: 'Flinders St Station',
    description: 'Complete the Flinders Street Station epic park',
    howToGet: 'Visit and complete all tasks at Flinders Street Station to unlock this badge.',
    image: '/flinders.png',
  },
  {
    id: 'epic_fitzroy',
    name: 'Fitzroy Garden',
    description: 'Complete the Fitzroy Garden epic park',
    howToGet: 'Visit and complete all tasks at Fitzroy Garden to unlock this badge.',
    image: '/fitzory.png',
  },
  {
    id: 'epic_greatoceanroad',
    name: 'Great Ocean Road',
    description: 'Complete the Great Ocean Road epic park',
    howToGet: 'Visit and complete all tasks at Great Ocean Road to unlock this badge.',
    image: '/greatoceanroad.png',
  },
]

// Master epic badge (complete all epic parks)
const epicMasterBadge = {
  id: 'epic_master',
  name: 'Melbourne Epic Explorer',
  description: 'Complete all Epic Parks to become a true Melbourne explorer!',
  howToGet: 'Unlock all three Epic Park badges (Flinders St Station, Fitzroy Garden, and Great Ocean Road) to earn this ultimate badge.',
  image: '/melbepic.png',
}

const achievementBadges = [
  { id: 'first_step',   name: DEFS.first_step.name,   description: DEFS.first_step.description,   howToGet: DEFS.first_step.howToGet,   icon: PhSneaker, color: '#10b981', iconBg: '#f0fdf4',  borderColor: '#bbf7d0', borderBottomColor: '#34d399' },
  { id: 'on_fire',      name: DEFS.on_fire.name,      description: DEFS.on_fire.description,      howToGet: DEFS.on_fire.howToGet,      icon: PhFlame,   color: '#f59e0b', iconBg: '#fffbeb',  borderColor: '#fde68a', borderBottomColor: '#fbbf24' },
  { id: 'snap_happy',   name: DEFS.snap_happy.name,   description: DEFS.snap_happy.description,   howToGet: DEFS.snap_happy.howToGet,   icon: PhCamera,  color: '#3b82f6', iconBg: '#eff6ff',  borderColor: '#bfdbfe', borderBottomColor: '#93c5fd' },
  { id: 'park_pioneer',  name: DEFS.park_pioneer.name,  description: DEFS.park_pioneer.description,  howToGet: DEFS.park_pioneer.howToGet,  icon: PhMapPin,  color: '#16a34a', iconBg: '#f0fdf4',  borderColor: '#bbf7d0', borderBottomColor: '#34d399' },
  { id: 'week_warrior', name: DEFS.week_warrior.name, description: DEFS.week_warrior.description, howToGet: DEFS.week_warrior.howToGet, icon: PhFlame,   color: '#ef4444', iconBg: '#fef2f2',  borderColor: '#fecaca', borderBottomColor: '#f87171' },
  { id: 'sun_chaser',   name: DEFS.sun_chaser.name,   description: DEFS.sun_chaser.description,   howToGet: DEFS.sun_chaser.howToGet,   icon: PhSun,     color: '#f59e0b', iconBg: '#fffbeb',  borderColor: '#fde68a', borderBottomColor: '#fbbf24' },
]

const allBadges = [...seriesBadges, ...epicParkBadges, epicMasterBadge, ...achievementBadges]
const totalCount = allBadges.length

const earnedCount = computed(() => {
  return allBadges.filter(b => progressStore.earnedBadgeSet.has(b.id)).length
})

const epicParkEarnedCount = computed(() => {
  return epicParkBadges.filter(b => progressStore.earnedBadgeSet.has(b.id)).length
})

function isBadgeEarned(badgeId) {
  return progressStore.earnedBadgeSet.has(badgeId)
}

function openBadgeDetail(badge) {
  detailBadge.value = badge
  showDetail.value = true
}

onMounted(() => {
  progressStore.init()
  if (!localStorage.getItem(OB_KEY)) { showOb.value = true; obStep.value = 0 }
})
</script>

<style>
.ob-card-badges { position: absolute; width: calc(100% - 32px); max-width: 360px; padding: 20px; border-radius: 24px; background: white; border: 2px solid #fde68a; border-bottom: 4px solid #fbbf24; box-shadow: 0 8px 32px rgba(0,0,0,0.2); z-index: 1000; font-family: var(--font-game), system-ui, sans-serif }
.ob-next-b { padding: 8px 20px; border-radius: 14px; background: linear-gradient(135deg, #f59e0b, #d97706); border: none; border-bottom: 3px solid #b45309; color: white; font-size: 13px; font-weight: 900; cursor: pointer; font-family: var(--font-game), system-ui, sans-serif }
.ob-arrow-up-b { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 10px solid white }
</style>