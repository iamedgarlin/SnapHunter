<template>
  <div class="min-h-full pb-8" style="background: #f0fdf4; font-family: var(--font-game)">

    <!-- Sticky header -->
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

    <div class="px-5 flex flex-col gap-4 mt-5">

      <!-- What is eye strain -->
      <div class="card-game" style="border-color: #bfdbfe; border-bottom-color: #60a5fa">
        <div class="flex items-center gap-2 mb-3">
          <PhQuestion :size="18" weight="duotone" color="#3b82f6" />
          <p class="text-sm font-black text-gray-800">What is digital eye strain?</p>
        </div>
        <p class="text-xs font-semibold text-gray-500 leading-relaxed">
          Digital eye strain (also called Computer Vision Syndrome) happens when children
          spend too long looking at screens — phones, tablets, laptops or TVs.
          Their eyes have to work extra hard to focus, which causes tiredness and discomfort.
        </p>
      </div>

      <!-- Key stats -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <PhChartBar :size="16" weight="duotone" color="#3b82f6" />
          <p class="text-sm font-black text-gray-700">Key statistics</p>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div v-for="stat in stats" :key="stat.label"
            class="rounded-2xl p-4 flex flex-col gap-1"
            :style="`background: ${stat.bg}; border: 2px solid ${stat.border}; border-bottom: 3px solid ${stat.borderBottom}`">
            <component :is="stat.icon" :size="22" weight="duotone" :color="stat.color" />
            <p class="text-2xl font-black mt-1" :style="`color: ${stat.color}`">{{ stat.value }}</p>
            <p class="text-xs font-bold" :style="`color: ${stat.labelColor}`">{{ stat.label }}</p>
          </div>
        </div>
      </div>

      <!-- Symptoms -->
      <div class="card-game" style="border-color: #fde68a; border-bottom-color: #fbbf24">
        <div class="flex items-center gap-2 mb-3">
          <PhWarning :size="18" weight="duotone" color="#f59e0b" />
          <p class="text-sm font-black text-gray-800">Common symptoms</p>
        </div>
        <div class="flex flex-col gap-2">
          <div v-for="symptom in symptoms" :key="symptom.text"
            class="flex items-center gap-3 p-2.5 rounded-xl"
            style="background: #fffbeb; border: 1.5px solid #fde68a">
            <component :is="symptom.icon" :size="18" weight="duotone" color="#f59e0b" />
            <p class="text-xs font-bold text-amber-800">{{ symptom.text }}</p>
          </div>
        </div>
      </div>

      <!-- 20-20-20 rule -->
      <div class="card-game" style="border-color: #bbf7d0; border-bottom-color: #34d399">
        <div class="flex items-center gap-2 mb-3">
          <PhLightbulb :size="18" weight="duotone" color="#10b981" />
          <p class="text-sm font-black text-gray-800">The 20-20-20 Rule</p>
        </div>
        <div class="flex gap-2">
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac">
            <p class="text-3xl font-black text-emerald-600">20</p>
            <p class="text-xs font-bold text-emerald-500 mt-0.5">minutes of screen time</p>
          </div>
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac">
            <p class="text-3xl font-black text-emerald-600">20</p>
            <p class="text-xs font-bold text-emerald-500 mt-0.5">feet away to look</p>
          </div>
          <div class="flex-1 rounded-2xl p-3 text-center"
            style="background: #f0fdf4; border: 2px solid #bbf7d0; border-bottom: 3px solid #86efac">
            <p class="text-3xl font-black text-emerald-600">20</p>
            <p class="text-xs font-bold text-emerald-500 mt-0.5">seconds of rest</p>
          </div>
        </div>
        <p class="text-xs font-semibold text-gray-400 text-center mt-3">
          Every 20 minutes, look at something 20 feet away for 20 seconds!
        </p>
      </div>

      <!-- How SnapHunter helps -->
      <div class="card-game" style="border-color: #bbf7d0; border-bottom-color: #34d399">
        <div class="flex items-center gap-2 mb-3">
          <PhPawPrint :size="18" weight="duotone" color="#10b981" />
          <p class="text-sm font-black text-gray-800">How SnapHunter helps</p>
        </div>
        <p class="text-xs font-semibold text-gray-500 leading-relaxed">
          SnapHunter turns screen breaks into a fun adventure! Complete outdoor tasks,
          earn XP and badges, and help your child build healthy habits — one hunt at a time.
        </p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import {
  PhEye, PhArrowLeft, PhQuestion, PhChartBar,
  PhWarning, PhLightbulb, PhPawPrint,
  PhDeviceMobile, PhSmiley, PhTimer, PhSun, PhBrain
} from '@phosphor-icons/vue'

const router = useRouter()

const stats = [
  {
    value: '65%',
    label: 'of kids have eye strain',
    icon: PhEye,
    color: '#3b82f6',
    labelColor: '#60a5fa',
    bg: '#eff6ff',
    border: '#bfdbfe',
    borderBottom: '#93c5fd'
  },
  {
    value: '4h+',
    label: 'avg screen time per day',
    icon: PhDeviceMobile,
    color: '#a855f7',
    labelColor: '#c084fc',
    bg: '#faf5ff',
    border: '#e9d5ff',
    borderBottom: '#d8b4fe'
  },
  {
    value: '1 in 4',
    label: 'kids are overweight in AU',
    icon: PhSmiley,
    color: '#f97316',
    labelColor: '#fb923c',
    bg: '#fff7ed',
    border: '#fed7aa',
    borderBottom: '#fdba74'
  },
  {
    value: '2hrs',
    label: 'WHO recommended limit',
    icon: PhTimer,
    color: '#10b981',
    labelColor: '#34d399',
    bg: '#f0fdf4',
    border: '#bbf7d0',
    borderBottom: '#86efac'
  },
]

const symptoms = [
  { text: 'Eye fatigue and dryness',      icon: PhEye },
  { text: 'Headaches after screen use',   icon: PhBrain },
  { text: 'Blurred or double vision',     icon: PhEye },
  { text: 'Neck and shoulder pain',       icon: PhTimer },
  { text: 'Difficulty concentrating',     icon: PhSmiley },
]
</script>