<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore }      from '@/stores/auth'
import { useAppStore }       from '@/stores/app'
import { useEmergencyStore } from '@/stores/emergency'

const auth      = useAuthStore()
const app       = useAppStore()
const emergency = useEmergencyStore()

// Live clock
const clock = ref('00:00:00')
let _clockTimer = null

function tickClock() {
  clock.value = new Date().toLocaleTimeString('ca-AD', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  })
}

onMounted(() => {
  tickClock()
  _clockTimer = setInterval(tickClock, 1000)
})

onUnmounted(() => {
  if (_clockTimer) clearInterval(_clockTimer)
})
</script>

<template>
  <header
    class="header-wrap flex items-center flex-shrink-0 px-5"
    style="height:52px;background:var(--surface);border-bottom:1px solid var(--border)"
  >
    <!-- Logo -->
    <div class="flex items-center gap-2.5 mr-6 flex-shrink-0">
      <div
        class="w-7 h-7 rounded-lg flex items-center justify-center text-base"
        style="background:var(--accent-bg);border:1px solid var(--accent-br)"
      >🚨</div>
      <span class="font-bold text-sm tracking-wide" style="color:var(--accent)">DISPATCHSIM</span>
    </div>

    <div class="h-sep w-px h-6 mr-4 flex-shrink-0"></div>

    <!-- Nav tabs -->
    <nav class="flex items-stretch h-full flex-1 min-w-0 overflow-x-auto">
      <button
        id="nav-emergency"
        class="nav-tab"
        :class="{ active: app.activeTab === 'emergency' }"
        @click="app.showTab('emergency')"
      >
        <svg fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/>
          <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        Emergència
      </button>

      <button
        v-if="auth.canManage"
        class="nav-tab"
        :class="{ active: app.activeTab === 'scenarios' }"
        @click="app.showTab('scenarios')"
      >
        <svg fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>
        </svg>
        Escenaris
      </button>

      <button
        v-if="auth.canManage"
        class="nav-tab"
        :class="{ active: app.activeTab === 'users' }"
        @click="app.showTab('users')"
      >
        <svg fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
        Usuaris
      </button>

      <button
        v-if="auth.canManage"
        class="nav-tab"
        :class="{ active: app.activeTab === 'history' }"
        @click="app.showTab('history')"
      >
        <svg fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
        </svg>
        Historial
      </button>
    </nav>

    <!-- Right: badge + user info + clock + actions -->
    <div class="flex items-center gap-3 flex-shrink-0 ml-4">

      <!-- Active incident badge -->
      <div
        v-if="emergency.currentIncidentId"
        class="text-xs font-bold px-3 py-1 rounded-full"
        style="background:#fee2e2;color:#b91c1c;border:1px solid #fca5a5"
      >
        #{{ emergency.currentIncidentId }} · {{ emergency.currentIncident?.type || '—' }}
      </div>

      <!-- User info -->
      <div class="flex items-center gap-2 text-xs" style="color:var(--text3)">
        <span class="sdot w-2 h-2 rounded-full bg-emerald-400 inline-block"></span>
        <span>{{ auth.user?.username }} · {{ auth.user?.role }}</span>
      </div>

      <!-- Clock -->
      <div class="font-mono text-sm font-bold tabular-nums" style="color:var(--text2)">
        {{ clock }}
      </div>

      <!-- Theme toggle -->
      <button class="theme-btn" @click="app.toggleTheme()" title="Canviar tema">
        <svg v-if="app.theme === 'light'" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
        <svg v-else fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
      </button>

      <!-- Home -->
      <button
        @click="() => window.location.href = '/'"
        class="logout-btn text-xs px-3 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5"
        title="Pàgina principal"
      >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        Inici
      </button>

      <!-- Logout -->
      <button @click="auth.logout()" class="logout-btn text-xs px-3 py-1.5 rounded-lg font-medium transition">
        Sortir
      </button>
    </div>
  </header>
</template>
