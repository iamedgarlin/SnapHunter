<template>
  <!-- Desktop blocker overlay — only visible on wide screens -->
  <div class="desktop-blocker">
    <div class="desktop-blocker-content">
      <img src="/web-app-manifest-512x512.png" alt="SnapHunter" class="desktop-blocker-logo" />
      <h1>SnapHunter is designed for mobile</h1>
      <p>Please open this app on your phone for the best experience.</p>
      <div class="desktop-blocker-qr">
        <PhDeviceMobileCamera :size="28" weight="duotone" color="#10b981" />
        <span class="desktop-blocker-url">snaphunter.app</span>
      </div>
    </div>
  </div>

  <!-- Main app — hidden on desktop via CSS -->
  <div class="mobile-app flex flex-col h-dvh max-w-md mx-auto bg-white">
    <main ref="mainRef" class="flex-1 overflow-y-auto">
      <RouterView />
    </main>
    <nav v-if="showTabBar" class="flex border-t border-gray-200 bg-white pb-safe">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.path"
        :to="tab.path"
        class="flex flex-col items-center justify-center flex-1 py-2 gap-1 text-xs"
        :class="route.path === tab.path ? 'text-emerald-500' : 'text-gray-400'"
      >
        <component
          :is="tab.icon"
          :size="24"
          weight="duotone"
          :color="route.path === tab.path ? '#10b981' : '#94a3b8'"
        />
        <span :class="route.path === tab.path ? 'font-black' : 'font-medium'">
          {{ tab.label }}
        </span>
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { RouterView, RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import {
  PhHouseSimple, PhCompass, PhStamp, PhMedal, PhUser, PhDeviceMobileCamera
} from '@phosphor-icons/vue'

const route = useRoute()
const auth = useAuthStore()
const mainRef = ref(null)

auth.init()

watch(() => route.path, () => {
  if (mainRef.value) {
    mainRef.value.scrollTop = 0
  }
})

const showTabBar = computed(() =>
  !['/welcome', '/awareness'].includes(route.path)
)

const tabs = [
  { path: '/home',    label: 'Home',        icon: PhHouseSimple },
  { path: '/map',     label: 'Discovery',   icon: PhCompass },
  { path: '/badges',  label: 'Badges',      icon: PhMedal },
  { path: '/tasks',   label: 'Collection',  icon: PhStamp },
  { path: '/profile', label: 'Profile',     icon: PhUser },
]
</script>

<style scoped>
/* Desktop blocker — hidden by default (mobile-first) */
.desktop-blocker {
  display: none;
}

/* On screens wider than 768px, show blocker and hide app */
@media (min-width: 768px) {
  .desktop-blocker {
    display: flex;
    position: fixed;
    inset: 0;
    z-index: 9999;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 50%, #a7f3d0 100%);
  }

  .mobile-app {
    display: none !important;
  }
}

.desktop-blocker-content {
  text-align: center;
  padding: 2rem;
  max-width: 400px;
}

.desktop-blocker-logo {
  width: 80px;
  height: 80px;
  margin: 0 auto 1.5rem;
  border-radius: 1rem;
}

.desktop-blocker-content h1 {
  font-family: 'Nunito', sans-serif;
  font-size: 1.5rem;
  font-weight: 800;
  color: #065f46;
  margin-bottom: 0.5rem;
}

.desktop-blocker-content p {
  font-family: 'Nunito', sans-serif;
  font-size: 1rem;
  color: #047857;
  margin-bottom: 1.5rem;
}

.desktop-blocker-qr {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: white;
  padding: 0.75rem 1.25rem;
  border-radius: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.desktop-blocker-qr span:first-child {
  font-size: 1.5rem;
}

.desktop-blocker-url {
  font-family: 'Nunito', sans-serif;
  font-weight: 700;
  font-size: 1.1rem;
  color: #10b981;
}
</style>