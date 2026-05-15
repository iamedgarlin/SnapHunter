import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import WelcomeView from './views/WelcomeView.vue'
import AwarenessView from './views/AwarenessView.vue'
import HomeView from './views/HomeView.vue'
import TasksView from './views/TasksView.vue'
import MapView from './views/MapView.vue'
import BadgesView from './views/BadgesView.vue'
import ProfileView from './views/ProfileView.vue'
import ParkExploreView from './views/ParkExploreView.vue'
import ParkAdventureView from './views/ParkAdventureView.vue'

import { useAuthStore } from './stores/auth'

const protectedRoutes = ['/home', '/tasks', '/map', '/badges', '/profile']

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/welcome' },
    { path: '/welcome', component: WelcomeView },
    { path: '/awareness', component: AwarenessView },
    { path: '/home', component: HomeView },
    { path: '/tasks', component: TasksView },
    { path: '/map', component: MapView },
    { path: '/explore', component: ParkExploreView },
    { path: '/adventure', component: ParkAdventureView },
    { path: '/badges', component: BadgesView },
    { path: '/profile', component: ProfileView },
  ]
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (protectedRoutes.includes(to.path) && !auth.isLoggedIn) {
    return '/welcome'
  }

  if (to.path === '/welcome' && auth.isLoggedIn) {
    return '/home'
  }
})

async function bootstrap() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  const authStore = useAuthStore()

  await authStore.init()

  app.use(router)
  app.mount('#app')
}

bootstrap()