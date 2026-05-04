<template>
  <div class="min-h-full flex flex-col pb-10 relative" style="background: #f0fdf4; font-family: var(--font-game)">

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
            @keyup.enter="attemptStart"
          />
        </div>
      </div>

      <button
        class="btn-game text-lg font-black flex items-center justify-center gap-2 w-full relative z-10"
        style="background: #16a34a; border-bottom-color: #14532d"
        :style="{ opacity: nickname.trim().length === 0 ? 0.5 : 1 }"
        :disabled="nickname.trim().length === 0"
        @click="attemptStart">
        <PhRocketLaunch :size="22" weight="duotone" color="white" />
        Start Adventure!
      </button>
      <p class="text-xs text-emerald-700 font-medium mt-3 relative z-10">
        Free for families · No ads · Victoria, Australia
      </p>
    </div>

    <div class="px-5 flex flex-col gap-4 mt-5">
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
            <p class="text-xs font-bold text-blue-400 mt-0.5">avg screen time/day</p>
          </div>
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #faf5ff; border: 2px solid #e9d5ff; border-bottom: 3px solid #d8b4fe">
            <p class="text-2xl font-black text-purple-600">+21%</p>
            <p class="text-xs font-bold text-purple-400 mt-0.5">myopia risk/hr</p>
          </div>
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74">
            <p class="text-2xl font-black text-orange-500">24cm</p>
            <p class="text-xs font-bold text-orange-400 mt-0.5">avg screen dist</p>
          </div>
        </div>
      </div>

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
    </div>

    <div v-if="showConsentModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div class="bg-white rounded-3xl w-full max-w-sm overflow-hidden flex flex-col max-h-[85vh]"
        style="border: 4px solid #34d399; box-shadow: 0 10px 25px rgba(0,0,0,0.2)">
        
        <div class="p-4 bg-emerald-50 border-b border-emerald-100 flex items-center gap-3">
          <PhShieldCheck :size="28" weight="duotone" color="#16a34a" />
          <div>
            <h3 class="font-black text-emerald-900 text-lg leading-tight">Parental Gate</h3>
            <p class="text-xs font-bold text-emerald-600">Ask an adult to unlock</p>
          </div>
        </div>

        <div class="p-4 overflow-y-auto flex-1 bg-gray-50 text-xs text-gray-600 space-y-3 font-sans">
          <p class="font-bold text-gray-800 text-sm">Privacy Policy</p>
          <p><strong>Effective Date:</strong> April 27, 2026</p>
          <p>Welcome to SnapHunter! Protecting the privacy of our young users (ages 5-10) and providing transparency to parents is our top priority.</p>
          <p><strong>1. Information We Collect</strong><br/>
          To improve the app experience, we collect limited analytics data: User ID, nickname, account creation date, session duration, and in-app events (like tasks completed and photos taken). We do NOT collect precise GPS locations, real names, or contact information.</p>
          <p><strong>2. Data Storage & Usage</strong><br/>
          Data is stored locally and periodically synced to our secure cloud servers. It is used strictly for internal analysis to improve educational features and fix bugs.</p>
          <p><strong>3. Children's Privacy</strong><br/>
          We comply with applicable children's privacy laws. We do not use collected data for targeted advertising or share it with third-party data brokers. Parents may request the review or deletion of data.</p>
          <p><strong>4. Contact Us</strong><br/>
          For any questions, contact: elin0027@student.monash.edu</p>
        </div>

        <div class="p-5 bg-white border-t border-gray-100">
          <p class="text-sm font-black text-gray-800 mb-3 text-center">
            Parents: Please solve to agree and continue
          </p>
          <div class="flex items-center justify-center gap-3 mb-4">
            <span class="text-2xl font-black text-emerald-600">{{ mathNum1 }} &times; {{ mathNum2 }} =</span>
            <input 
              v-model="mathAnswer" 
              type="number" 
              class="w-20 p-2 text-center text-xl font-black rounded-xl outline-none"
              style="background: #f0fdf4; border: 2px solid #34d399"
              placeholder="?"
            />
          </div>
          
          <div class="flex gap-3">
            <button 
              @click="showConsentModal = false"
              class="flex-1 py-3 rounded-xl font-bold text-gray-500 bg-gray-100 active:bg-gray-200">
              Cancel
            </button>
            <button 
              @click="verifyAndProceed"
              class="flex-1 py-3 rounded-xl font-black text-white"
              style="background: #16a34a; border-bottom: 3px solid #14532d"
              :style="{ opacity: mathAnswer ? 1 : 0.5 }">
              I Agree
            </button>
          </div>
          <p v-if="mathError" class="text-red-500 text-xs font-bold text-center mt-2">Incorrect answer. Please try again.</p>
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
  PhMedal, PhTree, PhSneaker, PhCompass, PhShieldCheck
} from '@phosphor-icons/vue'

const router = useRouter()
const authStore = useAuthStore()

const nickname = ref('')
const showConsentModal = ref(false)
const mathNum1 = ref(0)
const mathNum2 = ref(0)
const mathAnswer = ref('')
const mathError = ref(false)

function attemptStart() {
  const name = nickname.value.trim()
  if (!name) return

  const hasConsent = localStorage.getItem('snaphunter_parental_consent') === 'true'
  
  if (hasConsent) {
    finalizeStart(name)
  } else {
    mathNum1.value = Math.floor(Math.random() * 4) + 6 
    mathNum2.value = Math.floor(Math.random() * 4) + 6 
    mathAnswer.value = ''
    mathError.value = false
    showConsentModal.value = true
  }
}

function verifyAndProceed() {
  const expected = mathNum1.value * mathNum2.value
  if (parseInt(mathAnswer.value) === expected) {
    localStorage.setItem('snaphunter_parental_consent', 'true')
    showConsentModal.value = false
    finalizeStart(nickname.value.trim())
  } else {
    mathError.value = true
  }
}

function finalizeStart(name) {
  authStore.login(name)
  trackEvent('user_registered', { nickname: name })
  startSession()
  syncUserProfile()
  router.push('/home')
}
</script>

<style scoped>
.btn-game {
  padding: 14px 24px;
  border-radius: 16px;
  border: 2px solid transparent;
  border-bottom-width: 5px;
  transition: all 0.15s ease;
}
.btn-game:active:not(:disabled) {
  transform: translateY(3px);
  border-bottom-width: 2px;
  margin-bottom: 3px;
}
.card-game {
  background: white;
  border: 2px solid transparent;
  border-bottom-width: 4px;
  border-radius: 24px;
  padding: 16px;
}
.float-circle {
  position: absolute;
  background: white;
  border-radius: 50%;
  animation: float 4s ease-in-out infinite;
}
@keyframes float {
  0% { transform: translateY(0px) scale(1); }
  50% { transform: translateY(-15px) scale(1.1); }
  100% { transform: translateY(0px) scale(1); }
}
</style>