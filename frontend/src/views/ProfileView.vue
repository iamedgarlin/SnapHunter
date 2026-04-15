<template>
  <div class="min-h-full pb-6" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Header -->
    <div class="relative overflow-hidden px-4"
      style="background: linear-gradient(160deg, #bbf7d0, #6ee7b7); border-radius: 0 0 32px 32px; border-bottom: 4px solid #34d399; min-height: 220px; display: flex; align-items: center;">
      <div class="flex items-center gap-4 w-full py-8">

        <!-- Avatar -->
        <div class="w-20 h-20 rounded-3xl flex-shrink-0 overflow-hidden flex items-center justify-center"
          style="background: white; border: 3px solid #34d399; border-bottom: 4px solid #16a34a">
          <img v-if="authStore.user?.photoURL && !avatarError" :src="authStore.user.photoURL"
            class="w-full h-full object-cover" @error="avatarError = true" />
          <PhUser v-else :size="36" weight="duotone" color="#16a34a" />
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <div class="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center font-black text-white text-sm"
              style="background: linear-gradient(135deg, #f59e0b, #ef4444); border-bottom: 2px solid #b45309">
              3
            </div>
            <p class="text-xl font-black text-emerald-900">{{ userName }}</p>
            <button
              class="inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 active:scale-95 transition-all flex-shrink-0"
              style="background: white; border: 2px solid #34d399; border-bottom: 3px solid #16a34a"
              @click="showTitleModal = true">
              <span class="text-xs font-black text-emerald-700">{{ activeTitle }}</span>
              <PhCaretDown :size="11" weight="bold" color="#16a34a" />
            </button>
          </div>
          <div class="mt-3">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center gap-1">
                <PhLightning :size="11" weight="duotone" color="#f59e0b" />
                <span class="text-xs font-black text-emerald-800">240 / 300 XP</span>
              </div>
              <span class="text-xs font-semibold text-emerald-600">60 to level up</span>
            </div>
            <div class="h-2.5 rounded-full overflow-hidden" style="background: rgba(255,255,255,0.4)">
              <div class="h-full rounded-full"
                style="width: 80%; background: linear-gradient(to right, #fbbf24, #f59e0b)"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="px-4 flex flex-col gap-4 mt-4">

      <!-- Stats row -->
      <div class="grid grid-cols-4 gap-2">
        <div class="flex flex-col items-center gap-1 p-3 rounded-2xl"
          style="background: white; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1">
          <p class="text-xl font-black text-gray-800">14</p>
          <p class="text-xs font-bold text-gray-400 text-center leading-tight">Tasks</p>
        </div>
        <div class="flex flex-col items-center gap-1 p-3 rounded-2xl"
          style="background: white; border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24">
          <p class="text-xl font-black text-amber-500">3</p>
          <p class="text-xs font-bold text-gray-400 text-center leading-tight">Badges</p>
        </div>
        <div class="flex flex-col items-center gap-1 p-3 rounded-2xl"
          style="background: white; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399">
          <p class="text-xl font-black text-emerald-600">2</p>
          <p class="text-xs font-bold text-gray-400 text-center leading-tight">Parks</p>
        </div>
        <div class="flex flex-col items-center gap-1 p-3 rounded-2xl"
          style="background: white; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74">
          <p class="text-xl font-black text-orange-500">5</p>
          <p class="text-xs font-bold text-gray-400 text-center leading-tight">Streak</p>
        </div>
      </div>

      <!-- Streak -->
      <div class="card-game">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-1.5">
            <PhFlame :size="18" weight="duotone" color="#f59e0b" />
            <p class="text-sm font-black text-gray-800">This week</p>
          </div>
          <span class="text-xs font-black text-amber-500">5 days!</span>
        </div>
        <div class="flex gap-2">
          <div v-for="(day, i) in weekDays" :key="i" class="flex-1 flex flex-col items-center gap-1">
            <div class="streak-dot" :style="day.done
              ? 'background:#f59e0b; border-color:#d97706'
              : 'background:#e2e8f0; border-color:#cbd5e1'">
            </div>
            <span class="text-xs font-bold" :style="day.done ? 'color:#d97706' : 'color:#94a3b8'">
              {{ day.label }}
            </span>
          </div>
        </div>
        <p class="text-xs font-semibold text-gray-400 mt-2">Best streak: 5 days</p>
      </div>

      <!-- Sign out -->
      <button
        class="w-full py-3 rounded-2xl font-black text-sm text-white flex items-center justify-center gap-2 transition-all active:scale-95"
        style="background: #ef4444; border-bottom: 4px solid #b91c1c" @click="handleLogout">
        <PhSignOut :size="16" weight="duotone" color="white" />
        Sign out
      </button>

    </div>

    <!-- Title modal -->
    <div v-if="showTitleModal" class="fixed inset-0 flex items-end justify-center z-50"
      style="background: rgba(0,0,0,0.4)" @click.self="showTitleModal = false">
      <div class="w-full max-w-md bg-white rounded-t-3xl p-6 flex flex-col gap-4" style="border-top: 4px solid #34d399">
        <div class="flex items-center justify-between">
          <p class="text-lg font-black text-gray-800">Choose your title</p>
          <button @click="showTitleModal = false" class="w-8 h-8 rounded-xl flex items-center justify-center"
            style="background: #f1f5f9; border: 1.5px solid #e2e8f0">
            <PhX :size="14" weight="bold" color="#94a3b8" />
          </button>
        </div>
        <div class="flex flex-col gap-2">
          <div v-for="title in unlockedTitles" :key="title.id"
            class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all" :style="activeTitle === title.name
              ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 2px solid #34d399'
              : 'background: #f8fafc; border: 2px solid #e2e8f0'" @click="selectTitle(title.name)">
            <component :is="title.icon" :size="22" weight="duotone" :color="title.color" />
            <div class="flex-1">
              <p class="text-sm font-black text-gray-800">{{ title.name }}</p>
              <p class="text-xs font-semibold text-gray-400">{{ title.requirement }}</p>
            </div>
            <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0" :style="activeTitle === title.name
              ? 'background: #16a34a'
              : 'background: white; border: 2px solid #e2e8f0'">
              <PhCheck v-if="activeTitle === title.name" :size="12" weight="bold" color="white" />
            </div>
          </div>
        </div>
        <div class="flex items-center gap-1.5 p-3 rounded-xl" style="background: #f1f5f9; border: 1.5px solid #e2e8f0">
          <PhLock :size="14" weight="duotone" color="#94a3b8" />
          <p class="text-xs font-semibold text-gray-400">Complete more tasks to unlock new titles!</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  PhUser, PhCompass, PhLightning, PhFlame,
  PhSignOut, PhTree, PhBuildings, PhSneaker,
  PhCheck, PhLock, PhX, PhCaretDown
} from '@phosphor-icons/vue'

const router = useRouter()
const authStore = useAuthStore()
const userName = authStore.user?.displayName?.split(' ')[0] || 'Explorer'
const avatarError = ref(false)
const activeTitle = ref('Nature Explorer')
const showTitleModal = ref(false)

const weekDays = [
  { label: 'M', done: true },
  { label: 'T', done: true },
  { label: 'W', done: true },
  { label: 'T', done: true },
  { label: 'F', done: true },
  { label: 'S', done: false },
  { label: 'S', done: false },
]

const unlockedTitles = [
  { id: 1, name: 'First Timer', requirement: 'Complete first task', icon: PhSneaker, color: '#10b981' },
  { id: 2, name: 'Nature Explorer', requirement: 'Complete Nature Series', icon: PhTree, color: '#16a34a' },
  { id: 3, name: 'City Scout', requirement: 'Complete 5 Urban tasks', icon: PhBuildings, color: '#3b82f6' },
]

function selectTitle(name) {
  activeTitle.value = name
  showTitleModal.value = false
}

async function handleLogout() {
  await authStore.logout()
  router.push('/welcome')
}
</script>