<template>
  <div class="min-h-full pb-8" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Header -->
    <div class="sticky top-0 z-10 relative overflow-hidden px-5 pt-10 pb-5"
      style="background: linear-gradient(160deg, #bfdbfe, #93c5fd); border-radius: 0 0 32px 32px; border-bottom: 4px solid #60a5fa">
      <button class="flex items-center gap-1 mb-3" @click="router.push('/welcome')">
        <PhArrowLeft :size="18" weight="duotone" color="#1e40af" />
        <span class="text-xs font-black text-blue-800">Back</span>
      </button>
      <div class="flex items-center gap-3">
        <div class="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0"
          style="background: white; border: 2px solid #93c5fd; border-bottom: 4px solid #60a5fa">
          <PhEye :size="32" weight="duotone" color="#3b82f6" />
        </div>
        <div>
          <h1 class="text-2xl font-black text-blue-900">Eye Health</h1>
          <p class="text-xs font-bold text-blue-600">Why going outside matters</p>
        </div>
      </div>
    </div>

    <div class="px-5 flex flex-col gap-5 mt-5">

      <!-- MODULE 1: Reality Check -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <div class="w-6 h-6 rounded-lg flex items-center justify-center font-black text-white text-xs"
            style="background: #3b82f6; border-bottom: 2px solid #1d4ed8">1</div>
          <p class="text-sm font-black text-gray-700">The Reality Check</p>
        </div>
        <div class="card-game" style="border-color: #bfdbfe; border-bottom-color: #93c5fd">
          <p class="text-sm font-black text-blue-900 mb-2">Are we the "Indoor Generation"?</p>
          <p class="text-xs font-semibold text-gray-500 leading-relaxed mb-4">
            Australian primary school students now average an astonishing
            <span class="font-black text-blue-600">6.34 hours</span> of screen time daily —
            up from 4.24 hours before COVID. Health guidelines recommend a maximum of just
            <span class="font-black text-emerald-600">2 hours</span>.
            You're not alone — this is a challenge for every modern family.
          </p>
          <div class="grid grid-cols-3 gap-2">
            <div class="rounded-2xl p-3 text-center"
              style="background: #eff6ff; border: 2px solid #bfdbfe; border-bottom: 3px solid #93c5fd">
              <p class="text-xl font-black text-blue-600">6.34h</p>
              <p class="text-xs font-bold text-blue-400 mt-0.5 leading-tight">avg screen time (AU kids)</p>
            </div>
            <div class="rounded-2xl p-3 text-center"
              style="background: #faf5ff; border: 2px solid #e9d5ff; border-bottom: 3px solid #d8b4fe">
              <p class="text-xl font-black text-purple-600">2h</p>
              <p class="text-xs font-bold text-purple-400 mt-0.5 leading-tight">WHO recommended limit</p>
            </div>
            <div class="rounded-2xl p-3 text-center"
              style="background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74">
              <p class="text-xl font-black text-orange-500">50%</p>
              <p class="text-xs font-bold text-orange-400 mt-0.5 leading-tight">kids myopic by 2050</p>
            </div>
          </div>
        </div>
      </div>

      <!-- MODULE 2: Screens vs Books + Video 1 -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <div class="w-6 h-6 rounded-lg flex items-center justify-center font-black text-white text-xs"
            style="background: #f59e0b; border-bottom: 2px solid #b45309">2</div>
          <p class="text-sm font-black text-gray-700">Why Screens Are Different</p>
        </div>

        <!-- Video 1 placeholder -->
        <div class="rounded-3xl overflow-hidden mb-3"
          style="border: 2px solid #fde68a; border-bottom: 4px solid #fbbf24">
          <div class="bg-amber-50 px-4 pt-3 pb-2">
            <div class="flex items-center gap-2">
              <PhFilmSlate :size="16" weight="duotone" color="#d97706" />
              <p class="text-xs font-black text-amber-700">Animation 1 · Eye Sprite Battery Crisis</p>
            </div>
          </div>
          <video
            class="w-full"
            controls
            playsinline
            style="max-height: 220px; background: #1f2937">
            <source src="/videos/eye-sprite-battery.mp4" type="video/mp4" />
            Your browser does not support video.
          </video>
        </div>

        <div class="card-game" style="border-color: #fde68a; border-bottom-color: #fbbf24">
          <p class="text-sm font-black text-amber-900 mb-2">The Battery Drain 🔋</p>
          <p class="text-xs font-semibold text-gray-500 leading-relaxed mb-3">
            Kids hold screens at an average distance of just
            <span class="font-black text-orange-500">24cm</span> —
            far closer than books (40–50cm). Combined with artificial light and reduced blinking,
            screens drain your child's "eye battery" much faster.
          </p>
          <div class="flex gap-2">
            <div class="flex-1 rounded-2xl p-3 text-center"
              style="background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74">
              <p class="text-lg font-black text-orange-500">24cm</p>
              <p class="text-xs font-bold text-orange-400 mt-0.5 leading-tight">screen distance</p>
            </div>
            <div class="flex-1 rounded-2xl p-3 text-center"
              style="background: #eff6ff; border: 2px solid #bfdbfe; border-bottom: 3px solid #93c5fd">
              <p class="text-lg font-black text-blue-600">40cm</p>
              <p class="text-xs font-bold text-blue-400 mt-0.5 leading-tight">book distance</p>
            </div>
            <div class="flex-1 rounded-2xl p-3 text-center"
              style="background: #faf5ff; border: 2px solid #e9d5ff; border-bottom: 3px solid #d8b4fe">
              <p class="text-lg font-black text-purple-600">↓66%</p>
              <p class="text-xs font-bold text-purple-400 mt-0.5 leading-tight">less blinking</p>
            </div>
          </div>
        </div>
      </div>

      <!-- MODULE 3: Risk Multiplier -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <div class="w-6 h-6 rounded-lg flex items-center justify-center font-black text-white text-xs"
            style="background: #ef4444; border-bottom: 2px solid #b91c1c">3</div>
          <p class="text-sm font-black text-gray-700">The +21% Risk Rule</p>
        </div>
        <div class="card-game" style="border-color: #fecaca; border-bottom-color: #f87171">
          <p class="text-sm font-black text-red-800 mb-2">Every extra hour matters (JAMA, 335,000+ children)</p>
          <p class="text-xs font-semibold text-gray-500 leading-relaxed mb-4">
            Based on a study of over 335,000 children, every extra hour of screen time
            increases myopia risk by <span class="font-black text-red-500">21%</span>.
            The danger zone rises sharply between 1 to 4 hours.
            The safe threshold? Ideally under <span class="font-black text-emerald-600">1 hour</span> per day.
          </p>
          <!-- Risk bar visual -->
          <div class="flex flex-col gap-2">
            <div v-for="bar in riskBars" :key="bar.hours" class="flex items-center gap-2">
              <span class="text-xs font-black text-gray-500 w-8 flex-shrink-0">{{ bar.hours }}h</span>
              <div class="flex-1 h-5 rounded-xl overflow-hidden" style="background: #f1f5f9">
                <div class="h-full rounded-xl flex items-center justify-end pr-2 transition-all"
                  :style="`width: ${bar.percent}%; background: ${bar.color}`">
                  <span class="text-xs font-black text-white">{{ bar.label }}</span>
                </div>
              </div>
            </div>
          </div>
          <p class="text-xs font-semibold text-gray-400 mt-3 text-center">
            Source: JAMA Network Open, 2023
          </p>
        </div>
      </div>

      <!-- MODULE 4: Solution + Videos 2 & 3 -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <div class="w-6 h-6 rounded-lg flex items-center justify-center font-black text-white text-xs"
            style="background: #10b981; border-bottom: 2px solid #047857">4</div>
          <p class="text-sm font-black text-gray-700">The Solution</p>
        </div>

        <!-- Video 2 -->
        <div class="rounded-3xl overflow-hidden mb-3"
          style="border: 2px solid #bbf7d0; border-bottom: 4px solid #34d399">
          <div class="bg-emerald-50 px-4 pt-3 pb-2">
            <div class="flex items-center gap-2">
              <PhFilmSlate :size="16" weight="duotone" color="#16a34a" />
              <p class="text-xs font-black text-emerald-700">Animation 2 · The 20-20-20 Ninja Secret</p>
            </div>
          </div>
          <video
            class="w-full"
            controls
            playsinline
            style="max-height: 220px; background: #1f2937">
            <source src="/videos/ninja-20-20-20.mp4" type="video/mp4" />
            Your browser does not support video.
          </video>
        </div>

        <!-- 20-20-20 rule -->
        <div class="card-game mb-3" style="border-color: #bbf7d0; border-bottom-color: #34d399">
          <div class="flex items-center gap-2 mb-3">
            <PhLightbulb :size="18" weight="duotone" color="#10b981" />
            <p class="text-sm font-black text-gray-800">The 20-20-20 Ninja Secret</p>
          </div>
          <div class="flex gap-2 mb-3">
            <div class="flex-1 rounded-2xl p-3 text-center"
              style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac">
              <p class="text-3xl font-black text-emerald-600">20</p>
              <p class="text-xs font-bold text-emerald-500 mt-0.5">minutes</p>
            </div>
            <div class="flex-1 rounded-2xl p-3 text-center"
              style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac">
              <p class="text-3xl font-black text-emerald-600">20</p>
              <p class="text-xs font-bold text-emerald-500 mt-0.5">feet away</p>
            </div>
            <div class="flex-1 rounded-2xl p-3 text-center"
              style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac">
              <p class="text-3xl font-black text-emerald-600">20</p>
              <p class="text-xs font-bold text-emerald-500 mt-0.5">seconds rest</p>
            </div>
          </div>
          <p class="text-xs font-semibold text-gray-400 text-center">
            Master this, and you become an Eye Care Master! 🥷
          </p>
        </div>

        <!-- Video 3 -->
        <div class="rounded-3xl overflow-hidden mb-3"
          style="border: 2px solid #bbf7d0; border-bottom: 4px solid #34d399">
          <div class="bg-emerald-50 px-4 pt-3 pb-2">
            <div class="flex items-center gap-2">
              <PhFilmSlate :size="16" weight="duotone" color="#16a34a" />
              <p class="text-xs font-black text-emerald-700">Animation 3 · Real World Open World Game</p>
            </div>
          </div>
          <video
            class="w-full"
            controls
            playsinline
            style="max-height: 220px; background: #1f2937">
            <source src="/videos/real-world-adventure.mp4" type="video/mp4" />
            Your browser does not support video.
          </video>
        </div>

        <!-- SnapHunter solution card -->
        <div class="card-game" style="border-color: #bbf7d0; border-bottom-color: #34d399">
          <div class="flex items-center gap-2 mb-2">
            <PhPawPrint :size="18" weight="duotone" color="#10b981" />
            <p class="text-sm font-black text-gray-800">The Ultimate Antidote</p>
          </div>
          <p class="text-xs font-semibold text-gray-500 leading-relaxed mb-3">
            Medical experts recommend <span class="font-black text-emerald-600">2 hours of outdoor natural light</span> daily
            to combat myopia. Confiscating devices causes family friction —
            so we built SnapHunter to turn outdoor time into an adventure kids actually want.
          </p>
          <div class="rounded-2xl p-3 flex items-center gap-3"
            style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #34d399">
            <PhSun :size="28" weight="duotone" color="#16a34a" />
            <div>
              <p class="text-sm font-black text-emerald-800">2 hrs outdoor light/day</p>
              <p class="text-xs font-semibold text-emerald-600">reduces myopia risk by up to 50%</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  PhEye, PhArrowLeft, PhLightbulb, PhPawPrint,
  PhFilmSlate, PhSun
} from '@phosphor-icons/vue'

const router = useRouter()

const riskBars = [
  { hours: '≤1', percent: 20,  color: '#34d399', label: 'Safe'  },
  { hours: '2',  percent: 42,  color: '#fbbf24', label: '+21%'  },
  { hours: '3',  percent: 63,  color: '#f97316', label: '+42%'  },
  { hours: '4+', percent: 90,  color: '#ef4444', label: '+63%+' },
]
</script>