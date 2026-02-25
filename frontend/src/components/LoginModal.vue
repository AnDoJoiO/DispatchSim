<script setup>
import { ref } from 'vue'
import { useAuthStore }      from '@/stores/auth'
import { useEmergencyStore } from '@/stores/emergency'

const auth      = useAuthStore()
const emergency = useEmergencyStore()

const username = ref('')
const password = ref('')
const error    = ref('')
const loading  = ref(false)

async function doLogin() {
  error.value   = ''
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    await emergency.loadScenarios()
    emergency.setPriority(1)
  } catch (e) {
    error.value = e.message || 'Error de connexió'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center"
    style="background:rgba(15,23,42,.65);backdrop-filter:blur(6px)"
  >
    <div class="flex flex-col items-center gap-4 w-full max-w-sm">

      <div class="login-card w-full rounded-2xl shadow-2xl overflow-hidden" style="background:var(--surface)">
        <div class="login-card-hd px-8 pt-8 pb-5 text-center" style="border-bottom:1px solid var(--border)">
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mx-auto mb-3"
            style="background:var(--accent-bg);border:1px solid var(--accent-br)"
          >🚨</div>
          <h1 class="text-base font-bold tracking-wide" style="color:var(--text)">DISPATCHSIM</h1>
          <p class="text-xs mt-1" style="color:var(--text3)">Sistema de simulació · Andorra</p>
        </div>

        <div class="px-8 py-6 flex flex-col gap-3">
          <div>
            <label class="fl">Nom d'usuari</label>
            <input
              v-model="username"
              type="text"
              placeholder="usuari"
              class="fc"
              @keydown.enter="doLogin"
            />
          </div>
          <div>
            <label class="fl">Contrasenya</label>
            <input
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="fc"
              @keydown.enter="doLogin"
            />
          </div>
          <p v-if="error" class="text-xs text-red-500 -mb-1">{{ error }}</p>
          <button
            @click="doLogin"
            :disabled="loading"
            class="w-full py-2.5 rounded-lg font-bold text-sm text-white transition mt-1"
            style="background:var(--accent)"
          >
            {{ loading ? 'Accedint...' : 'Accedir' }}
          </button>
        </div>
      </div>

      <a href="/" class="back-link flex items-center gap-1.5 text-xs font-medium">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5M12 5l-7 7 7 7"/>
        </svg>
        Tornar a la pàgina principal
      </a>

    </div>
  </div>
</template>
