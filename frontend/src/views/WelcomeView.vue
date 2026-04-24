<template>
  <div class="min-h-full flex flex-col pb-10" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Hero -->
    <div class="relative overflow-hidden px-6 pt-14 pb-10 flex flex-col items-center text-center"
      style="background: linear-gradient(160deg, #bbf7d0, #6ee7b7); border-radius: 0 0 40px 40px; border-bottom: 4px solid #34d399">
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div class="float-circle" style="width:80px;height:80px;top:10%;left:5%;animation-delay:0s;opacity:0.15"></div>
        <div class="float-circle" style="width:50px;height:50px;top:20%;right:8%;animation-delay:0.8s;opacity:0.2"></div>
        <div class="float-circle" style="width:35px;height:35px;top:55%;left:12%;animation-delay:1.5s;opacity:0.12"></div>
        <div class="float-circle" style="width:60px;height:60px;top:40%;right:5%;animation-delay:0.4s;opacity:0.15"></div>
        <div class="float-circle" style="width:25px;height:25px;top:70%;right:20%;animation-delay:2s;opacity:0.2"></div>
        <div class="float-circle" style="width:45px;height:45px;top:75%;left:30%;animation-delay:1s;opacity:0.1"></div>
      </div>

      <div class="w-28 h-28 rounded-3xl flex items-center justify-center mb-4 relative z-10"
        style="background: white; border: 3px solid #34d399; border-bottom: 5px solid #16a34a">
        <PhPawPrint :size="64" weight="duotone" color="#16a34a" />
      </div>
      <h1 class="text-4xl font-black text-emerald-900 relative z-10">SnapHunter</h1>
      <p class="text-sm font-bold text-emerald-700 mt-1 mb-5 relative z-10">
        Go outside. Hunt nature. Level up!
      </p>

      <!-- Nickname input -->
      <div class="w-full relative z-10 mb-3">
        <div class="relative">
          <PhUser :size="20" weight="duotone" color="#16a34a"
            class="absolute left-4 top-1/2 -translate-y-1/2" />
          <input
            v-model="nickname"
            type="text"
            maxlength="20"
            placeholder="Enter your nickname..."
            class="w-full pl-11 pr-4 py-3.5 rounded-2xl text-base font-bold text-emerald-900 placeholder-emerald-400 outline-none"
            style="background: white; border: 3px solid #34d399; border-bottom: 5px solid #16a34a"
            @keyup.enter="handleStart"
          />
        </div>
      </div>

      <button
        class="btn-game text-lg font-black flex items-center justify-center gap-2 w-full relative z-10"
        style="background: #16a34a; border-bottom-color: #14532d"
        :style="{ opacity: nickname.trim().length === 0 ? 0.5 : 1 }"
        :disabled="nickname.trim().length === 0"
        @click="handleStart">
        <PhRocketLaunch :size="22" weight="duotone" color="white" />
        Start Adventure!
      </button>
      <p class="text-xs text-emerald-700 font-medium mt-3 relative z-10">
        Free for families · No ads · Victoria, Australia
      </p>
    </div>

    <div class="px-5 flex flex-col gap-4 mt-5">

      <!-- Did you know — updated with AU data -->
      <div @click="router.push('/awareness')"
        class="card-game cursor-pointer active:scale-95 transition-all"
        style="border-color: #bfdbfe; border-bottom-color: #93c5fd">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <PhEye :size="18" weight="duotone" color="#3b82f6" />
            <p class="text-sm font-black text-gray-800">Did you know?</p>
          </div>
          <span class="text-xs font-black text-blue-400">Learn more →</span>
        </div>
        <div class="flex gap-3">
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #eff6ff; border: 2px solid #bfdbfe; border-bottom: 3px solid #93c5fd">
            <p class="text-2xl font-black text-blue-600">6.34h</p>
            <p class="text-xs font-bold text-blue-400 mt-0.5">avg screen time/day (AU kids)</p>
          </div>
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #faf5ff; border: 2px solid #e9d5ff; border-bottom: 3px solid #d8b4fe">
            <p class="text-2xl font-black text-purple-600">+21%</p>
            <p class="text-xs font-bold text-purple-400 mt-0.5">myopia risk per extra hour</p>
          </div>
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74">
            <p class="text-2xl font-black text-orange-500">24cm</p>
            <p class="text-xs font-bold text-orange-400 mt-0.5">avg screen distance</p>
          </div>
        </div>
        <p class="text-xs font-semibold text-blue-400 text-center mt-3">
          Tap to watch our fun Eye Care animations! 👉
        </p>
      </div>

      <!-- How it works -->
      <div class="card-game" style="border-color: #bbf7d0; border-bottom-color: #34d399">
        <div class="flex items-center gap-2 mb-3">
          <PhStarFour :size="18" weight="duotone" color="#10b981" />
          <p class="text-sm font-black text-gray-800">How it works</p>
        </div>
        <div class="flex flex-col gap-3">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 font-black text-white text-sm"
              style="background: linear-gradient(135deg, #34d399, #10b981); border-bottom: 3px solid #065f46">1</div>
            <div>
              <p class="text-sm font-black text-gray-800">Get daily missions</p>
              <p class="text-xs font-semibold text-gray-400">New outdoor tasks every day</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 font-black text-white text-sm"
              style="background: linear-gradient(135deg, #fbbf24, #f59e0b); border-bottom: 3px solid #b45309">2</div>
            <div>
              <p class="text-sm font-black text-gray-800">Go outside and snap!</p>
              <p class="text-xs font-semibold text-gray-400">Complete tasks, take photos</p>
            </div>
          </div>
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 font-black text-white text-sm"
              style="background: linear-gradient(135deg, #f87171, #ef4444); border-bottom: 3px solid #991b1b">3</div>
            <div>
              <p class="text-sm font-black text-gray-800">Earn XP and badges!</p>
              <p class="text-xs font-semibold text-gray-400">Level up and unlock rewards</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Badges preview -->
      <div class="card-game">
        <div class="flex items-center gap-2 mb-3">
          <PhMedal :size="18" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-gray-800">Collect badges!</p>
        </div>
        <div class="flex gap-2">
          <div v-for="badge in previewBadges" :key="badge.name"
            class="flex-1 flex flex-col items-center gap-1.5 p-2.5 rounded-2xl"
            style="background: #f8fafc; border: 2px solid #e2e8f0; border-bottom: 3px solid #cbd5e1">
            <component :is="badge.icon" :size="28" weight="duotone" :color="badge.color" />
            <p class="text-xs font-black text-gray-600 text-center leading-tight">{{ badge.name }}</p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { syncUserProfile, startSession, trackEvent } from '../services/analytics'
import {
  PhPawPrint, PhEye, PhUser, PhRocketLaunch, PhStarFour,
  PhMedal, PhTree, PhSneaker, PhCompass
} from '@phosphor-icons/vue'

const router = useRouter()
const authStore = useAuthStore()
const nickname = ref('')

async function handleStart() {
  const name = nickname.value.trim()
  if (!name) return

  // Create local user
  authStore.login(name)

  // Track the new user and start session
  trackEvent('user_registered', { nickname: name })
  startSession()

  // Sync user profile to backend (fire and forget)
  syncUserProfile()

  router.push('/home')
}

const previewBadges = [
  { name: 'First Step',  icon: PhSneaker, color: '#10b981' },
  { name: 'Explorer',    icon: PhCompass, color: '#f59e0b' },
  { name: 'Nature Eye',  icon: PhTree,    color: '#16a34a' },
  { name: 'Snap Master', icon: PhEye,     color: '#3b82f6' },
]
</script>