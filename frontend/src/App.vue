<template>
  <div class="flex flex-col h-dvh max-w-md mx-auto bg-white">
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
  PhHouseSimple, PhCompass, PhMapTrifold, PhMedal, PhUser
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
  { path: '/home',    label: 'Home',    icon: PhHouseSimple },
  { path: '/tasks',   label: 'Quests',  icon: PhCompass },
  { path: '/map',     label: 'Map',     icon: PhMapTrifold },
  { path: '/badges',  label: 'Badges',  icon: PhMedal },
  { path: '/profile', label: 'Profile', icon: PhUser },
]
</script>