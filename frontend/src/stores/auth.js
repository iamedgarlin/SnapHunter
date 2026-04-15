import { defineStore } from 'pinia'
import { ref } from 'vue'
import { auth, googleProvider, signInWithPopup, signOut } from '../firebase'
import { onAuthStateChanged, signInWithRedirect } from 'firebase/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const loading = ref(true)

  async function loginWithGoogle() {
    try {
      const isPWA = window.matchMedia('(display-mode: standalone)').matches
      console.log('loginWithGoogle, isPWA:', isPWA)
      if (isPWA) {
        await signInWithRedirect(auth, googleProvider)
      } else {
        await signInWithPopup(auth, googleProvider)
      }
    } catch (error) {
      console.error('Login error:', error)
    }
  }

  async function logout() {
    await signOut(auth)
  }

  function init() {
    onAuthStateChanged(auth, (firebaseUser) => {
      if (firebaseUser) {
        user.value = firebaseUser
        isLoggedIn.value = true
      } else {
        user.value = null
        isLoggedIn.value = false
      }
      loading.value = false
    })
  }

  return { user, isLoggedIn, loading, loginWithGoogle, logout, init }
})