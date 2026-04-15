import { initializeApp } from 'firebase/app'
import { getAuth, GoogleAuthProvider, signInWithRedirect, signInWithPopup, signOut, getRedirectResult, setPersistence, browserLocalPersistence } from 'firebase/auth'

const firebaseConfig = {
  apiKey: "AIzaSyDv4i4n4xteDQVPlMT1RWfamRPPsAzp7ZU",
  authDomain: "snaphunter-365c8.firebaseapp.com",
  projectId: "snaphunter-365c8",
  storageBucket: "snaphunter-365c8.firebasestorage.app",
  messagingSenderId: "510694824286",
  appId: "1:510694824286:web:4b68bd5d5b83723c1fd7cf"
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const googleProvider = new GoogleAuthProvider()

setPersistence(auth, browserLocalPersistence)

export { auth, googleProvider, signInWithRedirect, signInWithPopup, signOut, getRedirectResult }