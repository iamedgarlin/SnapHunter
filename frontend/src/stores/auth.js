import { defineStore } from 'pinia'
import { ref } from 'vue'
import { auth, googleProvider, signInWithRedirect, signOut, getRedirectResult } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const loading = ref(true)

  async function loginWithGoogle() {
    try {
      await signInWithRedirect(auth, googleProvider)
    } catch (error) {
      console.error('Login error:', error)
    }
  }

  async function logout() {
    await signOut(auth)
    user.value = null
    isLoggedIn.value = false
  }

  function init() {
    getRedirectResult(auth)
      .then((result) => {
        if (result?.user) {
          user.value = result.user
          isLoggedIn.value = true
          // 手动跳转，不依赖路由守卫
          window.location.href = '/home'
        }
      })
      .catch((error) => {
        console.error('Redirect result error:', error)
      })
      .finally(() => {
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
      })
  }

  return { user, isLoggedIn, loading, loginWithGoogle, logout, init }
})