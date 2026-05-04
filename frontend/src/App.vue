<template>
  <!-- Password gate overlay -->
  <div v-if="!authenticated" class="password-gate">
    <div class="password-gate-card">
      <img src="/web-app-manifest-512x512.png" alt="SnapHunter" class="password-gate-logo" />
      <p class="password-gate-title">SnapHunter</p>
      <p class="password-gate-subtitle">Enter password to continue</p>
      <input
        v-model="passwordInput"
        type="password"
        placeholder="Password"
        class="password-gate-input"
        @keyup.enter="checkPassword"
      />
      <p v-if="passwordError" class="password-gate-error">Wrong password, try again</p>
      <button class="password-gate-btn" @click="checkPassword">
        Enter
      </button>
    </div>
  </div>

  <template v-else>
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

/* ─── Password gate ─── */
const SITE_PASSWORD = 'snaphunter2026'
const PASSWORD_KEY = 'snaphunter_site_auth'

const passwordInput = ref('')
const passwordError = ref(false)
const authenticated = ref(sessionStorage.getItem(PASSWORD_KEY) === 'true')

function checkPassword() {
  if (passwordInput.value === SITE_PASSWORD) {
    authenticated.value = true
    sessionStorage.setItem(PASSWORD_KEY, 'true')
    passwordError.value = false
  } else {
    passwordError.value = true
  }
}

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
/* ─── Password gate ─── */
.password-gate {
  position: fixed;
  inset: 0;
  z-index: 99999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #ecfdf5, #d1fae5, #a7f3d0);
  font-family: var(--font-game, 'Nunito', system-ui, sans-serif);
}

.password-gate-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 28px;
  border-radius: 28px;
  background: white;
  border: 3px solid #bbf7d0;
  border-bottom: 5px solid #34d399;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  width: 300px;
}

.password-gate-logo {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  margin-bottom: 12px;
}

.password-gate-title {
  font-size: 20px;
  font-weight: 900;
  color: #065f46;
  margin: 0 0 4px;
}

.password-gate-subtitle {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  margin: 0 0 20px;
}

.password-gate-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 14px;
  border: 2px solid #d1d5db;
  font-family: var(--font-game, 'Nunito', system-ui, sans-serif);
  font-size: 14px;
  font-weight: 700;
  color: #1f2937;
  outline: none;
  text-align: center;
  transition: border-color 0.2s;
}

.password-gate-input:focus {
  border-color: #34d399;
}

.password-gate-error {
  font-size: 12px;
  font-weight: 700;
  color: #ef4444;
  margin: 8px 0 0;
}

.password-gate-btn {
  width: 100%;
  margin-top: 14px;
  padding: 10px;
  border-radius: 14px;
  border: none;
  border-bottom: 3px solid #059669;
  background: #10b981;
  color: white;
  font-family: var(--font-game, 'Nunito', system-ui, sans-serif);
  font-size: 14px;
  font-weight: 900;
  cursor: pointer;
  transition: transform 0.1s;
}

.password-gate-btn:active {
  transform: scale(0.96);
}

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