import { defineStore } from 'pinia'
import { ref } from 'vue'
import { auth, googleProvider, signInWithPopup, signOut } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const loading = ref(true)

  async function loginWithGoogle() {
    try {
      await signInWithPopup(auth, googleProvider)
    } catch (error) {
      console.error('Login error:', error)
    }
  }

  async function logout() {
    await signOut(auth)
  }

  function init() {
    return new Promise((resolve) => {
      let resolved = false
      onAuthStateChanged(auth, (firebaseUser) => {
        if (firebaseUser) {
          user.value = firebaseUser
          isLoggedIn.value = true
        } else {
          user.value = null
          isLoggedIn.value = false
        }

        loading.value = false

        if (!resolved) {
          resolved = true
          resolve()
        }
      })
    })
  }

  return {
    user,
    isLoggedIn,
    loading,
    loginWithGoogle,
    logout,
    init
  }
})