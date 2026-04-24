import { defineStore } from 'pinia'
import { ref } from 'vue'

const STORAGE_KEY = 'snaphunter_user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)

  /**
   * Load user from localStorage on app start
   */
  function init() {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try {
        user.value = JSON.parse(saved)
        isLoggedIn.value = true
      } catch {
        localStorage.removeItem(STORAGE_KEY)
      }
    }
  }

  /**
   * Create a new local user with nickname
   * @param {string} nickname
   */
  function login(nickname) {
    const userData = {
      uid: crypto.randomUUID(),
      nickname: nickname.trim(),
      createdAt: new Date().toISOString(),
    }
    user.value = userData
    isLoggedIn.value = true
    localStorage.setItem(STORAGE_KEY, JSON.stringify(userData))
  }

  /**
   * Clear user data and log out
   */
  function logout() {
    user.value = null
    isLoggedIn.value = false
    localStorage.removeItem(STORAGE_KEY)
  }

  return { user, isLoggedIn, login, logout, init }
})