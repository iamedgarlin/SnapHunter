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
            :style="badge.earned
              ? `background: ${badge.iconBg}; border: 2px solid ${badge.borderColor}; border-bottom: 3px solid ${badge.borderBottomColor}`
              : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'"
            @click="badge.earned ? null : router.push('/tasks')">

            <!-- Badge icon -->
            <div class="w-14 h-14 rounded-2xl flex items-center justify-center relative"
              :style="badge.earned
                ? `background: white; border: 2px solid ${badge.borderColor}; border-bottom: 3px solid ${badge.borderBottomColor}`
                : 'background: #f1f5f9; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'">
              <component :is="badge.icon" :size="28" weight="duotone"
                :color="badge.earned ? badge.color : '#cbd5e1'" />
              <!-- Lock overlay for unearned -->
              <div v-if="!badge.earned"
                class="absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center"
                style="background: #e2e8f0; border: 1.5px solid white">
                <PhLock :size="10" weight="bold" color="#94a3b8" />
              </div>
            </div>

            <p class="text-xs font-black text-center leading-tight"
              :style="badge.earned ? `color: ${badge.color}` : 'color: #94a3b8'">
              {{ badge.name }}
            </p>

            <div v-if="badge.earned"
              class="text-xs font-black px-2 py-0.5 rounded-lg"
              :style="`background: ${badge.borderColor}; color: ${badge.color}`">
              Earned!
            </div>
            <p v-else class="text-xs font-semibold text-gray-400 text-center leading-tight">
              Tap to start
            </p>
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
            class="flex flex-col items-center gap-2 p-3 rounded-2xl"
            :style="badge.earned
              ? 'background: white; border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24'
              : 'background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1'">
            <div class="w-12 h-12 rounded-2xl flex items-center justify-center"
              :style="badge.earned
                ? 'background: #fef3c7; border: 2px solid #fde68a'
                : 'background: #f1f5f9; border: 2px solid #e2e8f0'">
              <component :is="badge.icon" :size="24" weight="duotone"
                :color="badge.earned ? '#d97706' : '#cbd5e1'" />
            </div>
            <p class="text-xs font-black text-center leading-tight"
              :style="badge.earned ? 'color: #92400e' : 'color: #94a3b8'">
              {{ badge.name }}
            </p>
            <p class="text-xs font-semibold text-gray-400 text-center leading-tight">
              {{ badge.description }}
            </p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  PhMedal, PhStarFour, PhTrophy, PhLock,
  PhTree, PhBuildings, PhPaintBrush,
  PhSneaker, PhFlame, PhCamera, PhMapPin, PhSun
} from '@phosphor-icons/vue'

const router = useRouter()

const seriesBadges = [
  {
    id: 'nature',
    name: 'Nature Explorer',
    icon: PhTree,
    color: '#16a34a',
    iconBg: '#f0fdf4',
    borderColor: '#bbf7d0',
    borderBottomColor: '#34d399',
    earned: true,
  },
  {
    id: 'urban',
    name: 'City Hunter',
    icon: PhBuildings,
    color: '#3b82f6',
    iconBg: '#eff6ff',
    borderColor: '#bfdbfe',
    borderBottomColor: '#93c5fd',
    earned: false,
  },
  {
    id: 'art',
    name: 'Art Spotter',
    icon: PhPaintBrush,
    color: '#a855f7',
    iconBg: '#faf5ff',
    borderColor: '#e9d5ff',
    borderBottomColor: '#d8b4fe',
    earned: false,
  },
]

const achievementBadges = [
  { id: 1, name: 'First Step',   description: 'Complete first task',     icon: PhSneaker, earned: true  },
  { id: 2, name: 'On Fire!',     description: '3-day streak',            icon: PhFlame,   earned: true  },
  { id: 3, name: 'Snap Happy',   description: 'Submit 10 photos',        icon: PhCamera,  earned: false },
  { id: 4, name: 'Park Pioneer', description: 'Unlock first park',       icon: PhMapPin,  earned: false },
  { id: 5, name: 'Week Warrior', description: '7-day streak',            icon: PhFlame,   earned: false },
  { id: 6, name: 'Sun Chaser',   description: 'Complete sunny day task', icon: PhSun,     earned: false },
]

const totalCount = seriesBadges.length + achievementBadges.length
const earnedCount = computed(() =>
  seriesBadges.filter(b => b.earned).length + achievementBadges.filter(b => b.earned).length
)
</script>