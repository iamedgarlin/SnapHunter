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

      <!-- XP / Level bar -->
      <div class="card-game">
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center font-black text-white text-base"
              style="background: linear-gradient(135deg, #f59e0b, #ef4444); border-bottom: 3px solid #b45309">
              3
            </div>
            <div>
              <p class="text-xs font-black text-gray-500 uppercase tracking-wide">Level</p>
              <div class="flex items-center gap-1">
                <PhCompass :size="14" weight="duotone" color="#10b981" />
                <p class="text-sm font-black text-gray-800">Explorer</p>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <PhLightning :size="14" weight="duotone" color="#f59e0b" />
            <p class="text-xs font-black text-amber-500">240 / 300 XP</p>
          </div>
        </div>
        <div class="h-4 rounded-full overflow-hidden border-2 border-gray-200" style="background: #f1f5f9">
          <div class="h-full rounded-full relative"
            style="width: 80%; background: linear-gradient(to right, #fbbf24, #f59e0b)">
            <div class="absolute right-2 top-0 h-full flex items-center">
              <span class="text-white text-xs font-black">80%</span>
            </div>
          </div>
        </div>
        <p class="text-xs font-semibold text-gray-400 mt-1.5">60 XP to next level</p>
      </div>

      <!-- Today's mission -->
      <div class="card-game" style="border-color: #bbf7d0; border-bottom-color: #34d399">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-1.5">
            <PhTarget :size="18" weight="duotone" color="#10b981" />
            <p class="text-base font-black text-gray-800">Today's Mission</p>
          </div>
          <div class="bg-emerald-100 rounded-xl px-2 py-1">
            <span class="text-xs font-black text-emerald-700">2 / 3</span>
          </div>
        </div>
        <div class="flex flex-col gap-2">
          <div v-for="task in todayTasks" :key="task.id"
            class="flex items-center gap-3 p-3 rounded-2xl"
            :style="task.done
              ? 'background: #f0fdf4; border: 2px solid #bbf7d0'
              : 'background: #f8fafc; border: 2px solid #e2e8f0'">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0"
              :style="task.done ? 'background: #dcfce7' : 'background: #f1f5f9'">
              <component :is="task.icon" :size="18" weight="duotone"
                :color="task.done ? '#16a34a' : '#94a3b8'" />
            </div>
            <p class="text-sm font-bold flex-1"
              :style="task.done ? 'color: #16a34a; text-decoration: line-through' : 'color: #374151'">
              {{ task.name }}
            </p>
            <div v-if="!task.done" class="flex items-center gap-0.5">
              <PhLightning :size="12" weight="duotone" color="#f59e0b" />
              <span class="text-xs font-black text-amber-500">+{{ task.xp }}</span>
            </div>
            <PhCheckCircle v-else :size="18" weight="duotone" color="#16a34a" />
          </div>
        </div>
      </div>

      <!-- CTA button -->
      <button class="btn-game text-xl font-black tracking-wide flex items-center justify-center gap-2">
        <PhMagnifyingGlass :size="22" weight="duotone" color="white" />
        Start Hunting!
      </button>

      <!-- Streak -->
      <div class="card-game">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-1.5">
            <PhFlame :size="18" weight="duotone" color="#f59e0b" />
            <p class="text-sm font-black text-gray-800">Streak</p>
          </div>
          <span class="text-xs font-black text-amber-500">5 days!</span>
        </div>
        <div class="flex gap-2">
          <div v-for="(day, i) in weekDays" :key="i" class="flex-1 flex flex-col items-center gap-1">
            <div class="streak-dot"
              :style="day.done
                ? 'background:#f59e0b; border-color:#d97706'
                : 'background:#e2e8f0; border-color:#cbd5e1'">
            </div>
            <span class="text-xs font-bold" :style="day.done ? 'color:#d97706' : 'color:#94a3b8'">
              {{ day.label }}
            </span>
          </div>
        </div>
      </div>

      <!-- Recent badges -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <div class="flex items-center gap-1.5">
            <PhMedal :size="16" weight="duotone" color="#f59e0b" />
            <p class="text-sm font-black text-gray-700">Recent Badges</p>
          </div>
          <button class="text-xs font-black text-emerald-500">See all →</button>
        </div>
        <div class="flex gap-3">
          <div v-for="badge in recentBadges" :key="badge.name"
            class="flex-1 flex flex-col items-center gap-2 p-3 rounded-2xl"
            style="background: white; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1">
            <component :is="badge.icon" :size="32" weight="duotone" :color="badge.color" />
            <p class="text-xs font-black text-gray-700 text-center">{{ badge.name }}</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useWeatherStore } from '../stores/weather'
import {
  PhSun, PhCloud, PhCloudRain, PhPawPrint, PhCompass, PhLightning,
  PhTarget, PhFlame, PhMedal, PhMagnifyingGlass, PhCheckCircle,
  PhFlower, PhTree, PhSneaker
} from '@phosphor-icons/vue'

const authStore = useAuthStore()
const weather = useWeatherStore()
const userName = authStore.user?.displayName?.split(' ')[0] || 'Explorer'

onMounted(() => {
  if (!weather.temp) weather.fetchWeather()
})

const todayTasks = [
  { id: 1, name: 'Find a flower', icon: PhFlower,  xp: 20, done: true },
  { id: 2, name: 'Spot 3 trees',  icon: PhTree,    xp: 20, done: true },
  { id: 3, name: 'Walk 10 mins',  icon: PhSneaker, xp: 30, done: false },
]

const weekDays = [
  { label: 'M', done: true },
  { label: 'T', done: true },
  { label: 'W', done: true },
  { label: 'T', done: true },
  { label: 'F', done: true },
  { label: 'S', done: false },
  { label: 'S', done: false },
]

const recentBadges = [
  { name: 'First Step', icon: PhSneaker, color: '#10b981' },
  { name: 'Explorer',   icon: PhCompass, color: '#f59e0b' },
  { name: 'Nature Eye', icon: PhTree,    color: '#16a34a' },
]
</script>