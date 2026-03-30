<template>
    <div class="min-h-full flex flex-col" style="background: #f0fdf4; font-family: var(--font-game)">

        <!-- Hero -->
        <div class="flex-1 flex flex-col items-center justify-center px-6 text-center gap-6">
            <div class="w-28 h-28 rounded-3xl flex items-center justify-center"
                style="background: white; border: 3px solid #34d399; border-bottom: 5px solid #16a34a">
                <PhPawPrint :size="64" weight="duotone" color="#16a34a" />
            </div>

            <div>
                <h1 class="text-4xl font-black text-emerald-900">SnapHunter</h1>
                <p class="text-sm font-semibold text-emerald-600 mt-1">Go outside. Hunt nature. Level up!</p>
            </div>

            <!-- Awareness stats -->
            <div class="w-full flex flex-col gap-3">
                <div class="card-game flex gap-3 items-center">
                    <div class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0"
                        style="background: #eff6ff; border: 2px solid #bfdbfe; border-bottom: 3px solid #93c5fd">
                        <PhEye :size="20" weight="duotone" color="#3b82f6" />
                    </div>
                    <p class="text-xs font-bold text-gray-600 text-left">
                        65% of kids get eye strain from too much screen time
                    </p>
                </div>
                <div class="card-game flex gap-3 items-center">
                    <div class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0"
                        style="background: #faf5ff; border: 2px solid #e9d5ff; border-bottom: 3px solid #d8b4fe">
                        <PhTree :size="20" weight="duotone" color="#a855f7" />
                    </div>
                    <p class="text-xs font-bold text-gray-600 text-left">
                        Going outside daily helps protect your child's vision
                    </p>
                </div>
                <div class="card-game flex gap-3 items-center">
                    <div class="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0"
                        style="background: #fff7ed; border: 2px solid #fed7aa; border-bottom: 3px solid #fdba74">
                        <PhTrophy :size="20" weight="duotone" color="#f97316" />
                    </div>
                    <p class="text-xs font-bold text-gray-600 text-left">
                        Complete outdoor tasks, earn badges and level up!
                    </p>
                </div>
            </div>
        </div>

        <!-- Login button -->
        <div class="px-6 pb-12 flex flex-col gap-3">
            <button class="btn-game text-lg font-black flex items-center justify-center gap-2" @click="handleLogin">
                <PhGoogleLogo :size="22" weight="duotone" color="white" />
                Continue with Google
            </button>
            <p class="text-xs text-center text-gray-400 font-medium">
                Free for families · No ads · Victoria, Australia
            </p>
        </div>

    </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { PhPawPrint, PhEye, PhTree, PhTrophy, PhGoogleLogo } from '@phosphor-icons/vue'

const router = useRouter()
const auth = useAuthStore()

async function handleLogin() {
    await auth.loginWithGoogle()
    router.push('/home')
}
</script>