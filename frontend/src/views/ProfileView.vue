<template>
  <div class="min-h-full pb-6" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Header -->
    <div class="relative overflow-hidden px-4"
      style="background: linear-gradient(160deg, #bbf7d0, #6ee7b7); border-radius: 0 0 32px 32px; border-bottom: 4px solid #34d399; min-height: 220px; display: flex; align-items: center;">
      <div class="flex items-center gap-4 w-full py-8">

        <!-- Avatar -->
        <div class="w-20 h-20 rounded-3xl flex-shrink-0 overflow-hidden flex items-center justify-center"
          style="background: white; border: 3px solid #34d399; border-bottom: 4px solid #16a34a">
          <PhUser :size="36" weight="duotone" color="#16a34a" />
        </div>

        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 flex-wrap">
            <div class="flex-shrink-0 w-7 h-7 rounded-lg flex items-center justify-center font-black text-white text-sm"
              style="background: linear-gradient(135deg, #f59e0b, #ef4444); border-bottom: 2px solid #b45309">
              {{ progressStore.level }}
            </div>
            <p class="text-xl font-black text-emerald-900">{{ userName }}</p>
            <!-- Title selector - only show if user has unlocked titles -->
            <button v-if="progressStore.unlockedTitles.length > 0"
              class="inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 active:scale-95 transition-all flex-shrink-0"
              style="background: white; border: 2px solid #34d399; border-bottom: 3px solid #16a34a"
              @click="showTitleModal = true">
              <span class="text-xs font-black text-emerald-700">
                {{ progressStore.activeTitle?.name || 'Choose title' }}
              </span>
              <PhCaretDown :size="11" weight="bold" color="#16a34a" />
            </button>
          </div>
          <div class="mt-3">
            <div class="flex items-center justify-between mb-1.5">
              <div class="flex items-center gap-1">
                <PhLightning :size="11" weight="duotone" color="#f59e0b" />
                <span class="text-xs font-black text-emerald-800">
                  {{ progressStore.xpInCurrentLevel }} / {{ progressStore.xpNeededForLevel }} XP
                </span>
              </div>
              <span class="text-xs font-semibold text-emerald-600">
                {{ progressStore.xpNeededForLevel - progressStore.xpInCurrentLevel }} to level up
              </span>
            </div>
            <div class="h-2.5 rounded-full overflow-hidden" style="background: rgba(255,255,255,0.4)">
              <div class="h-full rounded-full transition-all duration-500"
                :style="`width: ${progressStore.xpPercent}%; background: linear-gradient(to right, #fbbf24, #f59e0b)`"></div>
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
          <p class="text-xl font-black text-gray-800">{{ progressStore.progress.totalTasksCompleted }}</p>
          <p class="text-xs font-bold text-gray-400 text-center leading-tight">Tasks</p>
        </div>
        <div class="flex flex-col items-center gap-1 p-3 rounded-2xl"
          style="background: white; border: 2px solid #fde68a; border-bottom: 3px solid #fbbf24">
          <p class="text-xl font-black text-amber-500">{{ progressStore.progress.earnedBadges.length }}</p>
          <p class="text-xs font-bold text-gray-400 text-center leading-tight">Badges</p>
        </div>
        <div class="flex flex-col items-center gap-1 p-3 rounded-2xl"
          style="background: white; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399">
          <p class="text-xl font-black text-emerald-600">{{ progressStore.parksVisitedCount }}</p>
          <p class="text-xs font-bold text-gray-400 text-center leading-tight">Parks</p>
        </div>
        <div class="flex flex-col items-center gap-1 p-3 rounded-2xl"
          style="background: white; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74">
          <p class="text-xl font-black text-orange-500">{{ progressStore.progress.currentStreak }}</p>
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
          <span class="text-xs font-black text-amber-500">
            {{ progressStore.progress.currentStreak }} day{{ progressStore.progress.currentStreak === 1 ? '' : 's' }}!
          </span>
        </div>
        <div class="flex gap-2">
          <div v-for="(day, i) in progressStore.weekStreakDisplay" :key="i" class="flex-1 flex flex-col items-center gap-1">
            <div class="streak-dot" :style="day.done
              ? 'background:#f59e0b; border-color:#d97706'
              : 'background:#e2e8f0; border-color:#cbd5e1'">
            </div>
            <span class="text-xs font-bold" :style="day.done ? 'color:#d97706' : 'color:#94a3b8'">
              {{ day.label }}
            </span>
          </div>
        </div>
        <p class="text-xs font-semibold text-gray-400 mt-2">
          Best streak: {{ progressStore.progress.bestStreak }} day{{ progressStore.progress.bestStreak === 1 ? '' : 's' }}
        </p>
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

        <!-- No title option -->
        <div
          class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all"
          :style="!progressStore.progress.activeTitle
            ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 2px solid #34d399'
            : 'background: #f8fafc; border: 2px solid #e2e8f0'"
          @click="selectTitle(null)">
          <PhX :size="22" weight="duotone" color="#94a3b8" />
          <div class="flex-1">
            <p class="text-sm font-black text-gray-800">No title</p>
            <p class="text-xs font-semibold text-gray-400">Hide your title</p>
          </div>
          <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
            :style="!progressStore.progress.activeTitle
              ? 'background: #16a34a'
              : 'background: white; border: 2px solid #e2e8f0'">
            <PhCheck v-if="!progressStore.progress.activeTitle" :size="12" weight="bold" color="white" />
          </div>
        </div>

        <!-- Unlocked titles -->
        <div v-for="title in progressStore.unlockedTitles" :key="title.id"
          class="flex items-center gap-3 p-3 rounded-2xl cursor-pointer active:scale-95 transition-all" :style="progressStore.progress.activeTitle === title.id
            ? 'background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 2px solid #34d399'
            : 'background: #f8fafc; border: 2px solid #e2e8f0'" @click="selectTitle(title.id)">
          <PhMedal :size="22" weight="duotone" color="#f59e0b" />
          <div class="flex-1">
            <p class="text-sm font-black text-gray-800">{{ title.name }}</p>
            <p class="text-xs font-semibold text-gray-400">{{ title.requirement }}</p>
          </div>
          <div class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0" :style="progressStore.progress.activeTitle === title.id
            ? 'background: #16a34a'
            : 'background: white; border: 2px solid #e2e8f0'">
            <PhCheck v-if="progressStore.progress.activeTitle === title.id" :size="12" weight="bold" color="white" />
          </div>
        </div>

        <div v-if="progressStore.unlockedTitles.length === 0"
          class="flex items-center gap-1.5 p-3 rounded-xl" style="background: #f1f5f9; border: 1.5px solid #e2e8f0">
          <PhLock :size="14" weight="duotone" color="#94a3b8" />
          <p class="text-xs font-semibold text-gray-400">Complete tasks and earn badges to unlock titles!</p>
        </div>
      </div>
    </div>

  </div>

  <!-- Onboarding -->
  <Teleport to="body">
    <div v-if="showOb" class="fixed inset-0 z-[999]" @click="nextOb">
      <div class="absolute inset-0 bg-black/50"></div>
      <div v-if="obStep === 0" class="ob-card-profile" style="top: 44%; left: 50%; transform: translateX(-50%);">
        <div class="ob-arrow-up-p"></div>
        <div class="flex items-center gap-2 mb-2">
          <PhUser :size="20" weight="duotone" color="#16a34a" />
          <p class="text-base font-black text-gray-800">Your Profile</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Track your XP level, tasks completed, badges earned, parks visited, and daily streaks all in one place.
        </p>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">1 / 2</span>
          <button class="ob-next-p" @click.stop="nextOb">Next</button>
        </div>
      </div>
      <div v-if="obStep === 1" class="ob-card-profile" style="bottom: 28%; left: 50%; transform: translateX(-50%);">
        <div class="flex items-center gap-2 mb-2">
          <PhFlame :size="20" weight="duotone" color="#f59e0b" />
          <p class="text-base font-black text-gray-800">Streaks & Titles</p>
        </div>
        <p class="text-sm text-gray-600 leading-relaxed">
          Complete tasks on consecutive days to build your streak. Unlock titles by levelling up and earning badges. Tap the title button to choose which one to display!
        </p>
        <div class="ob-arrow-down-p"></div>
        <div class="flex items-center justify-between mt-4">
          <span class="text-xs font-bold text-gray-400">2 / 2</span>
          <button class="ob-next-p" @click.stop="nextOb">Got it!</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useProgressStore } from '../stores/progress'
import {
  PhUser, PhLightning, PhFlame, PhMedal,
  PhSignOut, PhCheck, PhLock, PhX, PhCaretDown
} from '@phosphor-icons/vue'

const router = useRouter()
const authStore = useAuthStore()
const progressStore = useProgressStore()
const userName = authStore.user?.nickname || 'Explorer'
const showTitleModal = ref(false)

// Onboarding
const OB_KEY = 'snaphunter_profile_onboarded'
const showOb = ref(false)
const obStep = ref(0)
function nextOb() {
  if (obStep.value < 1) { obStep.value++ } else { showOb.value = false; localStorage.setItem(OB_KEY, 'true') }
}

function selectTitle(titleId) {
  progressStore.setActiveTitle(titleId)
  showTitleModal.value = false
}

async function handleLogout() {
  progressStore.resetAll()
  await authStore.logout()
  router.push('/welcome')
}

onMounted(() => {
  progressStore.init()
  if (!localStorage.getItem(OB_KEY)) { showOb.value = true; obStep.value = 0 }
})
</script>

<style>
.ob-card-profile { position: absolute; width: calc(100% - 32px); max-width: 360px; padding: 20px; border-radius: 24px; background: white; border: 2px solid #d1fae5; border-bottom: 4px solid #34d399; box-shadow: 0 8px 32px rgba(0,0,0,0.2); z-index: 1000; font-family: var(--font-game), system-ui, sans-serif }
.ob-next-p { padding: 8px 20px; border-radius: 14px; background: linear-gradient(135deg, #10b981, #059669); border: none; border-bottom: 3px solid #047857; color: white; font-size: 13px; font-weight: 900; cursor: pointer; font-family: var(--font-game), system-ui, sans-serif }
.ob-arrow-up-p { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 10px solid white }
.ob-arrow-down-p { position: absolute; bottom: -10px; left: 50%; transform: translateX(-50%); width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-top: 10px solid white }
</style>