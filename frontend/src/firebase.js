import { initializeApp } from 'firebase/app'
import {
  getAuth,
  GoogleAuthProvider,
  signInWithPopup,
  signOut,
  setPersistence,
  browserLocalPersistence
} from 'firebase/auth'

const firebaseConfig = {
  apiKey: "AIzaSyDA3Wm3-2ehtiEhcsULgax4PSCKRVa7nkE",
  authDomain: "snaphunter-5a8ad.firebaseapp.com",
  projectId: "snaphunter-5a8ad",
  storageBucket: "snaphunter-5a8ad.firebasestorage.app",
  messagingSenderId: "182070306939",
  appId: "1:182070306939:web:af5de62db3f0b55b5e9ade",
  measurementId: "G-H07B7ET7PQ"
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const googleProvider = new GoogleAuthProvider()

await setPersistence(auth, browserLocalPersistence)

export {
  auth,
  googleProvider,
  signInWithPopup,
  signOut
}