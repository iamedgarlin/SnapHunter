import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import WelcomeView from './views/WelcomeView.vue'
import HomeView from './views/HomeView.vue'
import TasksView from './views/TasksView.vue'
import MapView from './views/MapView.vue'
import BadgesView from './views/BadgesView.vue'
import ProfileView from './views/ProfileView.vue'

const protectedRoutes = ['/home', '/tasks', '/map', '/badges', '/profile']

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',        redirect: '/welcome' },
    { path: '/welcome', component: WelcomeView },
    { path: '/home',    component: HomeView },
    { path: '/tasks',   component: TasksView },
    { path: '/map',     component: MapView },
    { path: '/badges',  component: BadgesView },
    { path: '/profile', component: ProfileView },
  ]
})

const pinia = createPinia()
const app = createApp(App)
app.use(pinia)
app.use(router)

import { useAuthStore } from './stores/auth'

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (protectedRoutes.includes(to.path) && !auth.isLoggedIn) {
    return '/welcome'
  }
  if (to.path === '/welcome' && auth.isLoggedIn) {
    return '/home'
  }
})

app.mount('#app')