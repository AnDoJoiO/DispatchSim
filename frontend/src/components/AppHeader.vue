<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore }  from '@/stores/auth'
import { useAppStore }   from '@/stores/app'
import { useCallStore }  from '@/stores/call'
import { useI18n, LANG_LOCALE } from '@/i18n'
import {
  AlertTriangle, Clock, FileText, Users,
  Moon, Sun, Home, LogOut,
} from 'lucide-vue-next'

const auth = useAuthStore()
const app  = useAppStore()
const call = useCallStore()
const { t: tr, lang } = useI18n()

const clock = ref('00:00:00')
let _clockTimer: ReturnType<typeof setInterval> | null = null

function tickClock() {
  const locale = LANG_LOCALE[lang.value] || 'ca-AD'
  clock.value = new Date().toLocaleTimeString(locale, {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
  })
}

onMounted(() => { tickClock(); _clockTimer = setInterval(tickClock, 1000) })
onUnmounted(() => { if (_clockTimer) clearInterval(_clockTimer) })
</script>

<template>
  <header class="hdr">
    <!-- Logo -->
    <div class="hdr-logo">
      <span class="hdr-dot"></span>
      <span class="hdr-brand">DISPATCH</span>
    </div>

    <div class="hdr-sep"></div>

    <!-- Nav -->
    <nav class="hdr-nav">
      <button
        class="nav-tab"
        :class="{ active: app.activeTab === 'emergency' }"
        @click="app.showTab('emergency')"
      >
        <AlertTriangle :size="15" />
        {{ tr('nav.emergency') }}
      </button>

      <button
        v-if="auth.canManage"
        class="nav-tab"
        :class="{ active: app.activeTab === 'history' }"
        @click="app.showTab('history')"
      >
        <Clock :size="15" />
        {{ tr('nav.history') }}
      </button>

      <div v-if="auth.canManage" class="hdr-sep-v"></div>

      <button
        v-if="auth.canManage"
        class="nav-tab"
        :class="{ active: app.activeTab === 'scenarios' }"
        @click="app.showTab('scenarios')"
      >
        <FileText :size="15" />
        {{ tr('nav.scenarios') }}
      </button>

      <button
        v-if="auth.canManage"
        class="nav-tab"
        :class="{ active: app.activeTab === 'users' }"
        @click="app.showTab('users')"
      >
        <Users :size="15" />
        {{ tr('nav.users') }}
      </button>
    </nav>

    <!-- Right -->
    <div class="hdr-right">
      <!-- Active incident -->
      <div v-if="call.currentIncidentId" class="hdr-incident">
        <span class="hdr-incident-dot"></span>
        #{{ call.currentIncidentId }} · {{ call.currentIncident?.type || '—' }}
      </div>

      <!-- User -->
      <div class="hdr-user">
        <span class="hdr-user-dot"></span>
        {{ auth.user?.username }}
        <span class="hdr-role">{{ auth.user?.role }}</span>
      </div>

      <!-- Clock -->
      <div class="hdr-clock">{{ clock }}</div>

      <!-- Actions -->
      <button class="hdr-icon-btn" @click="app.toggleTheme()" :title="tr('title.toggle_theme')" :aria-label="tr('title.toggle_theme')">
        <Moon v-if="app.theme === 'light'" :size="15" />
        <Sun v-else :size="15" />
      </button>

      <button class="hdr-icon-btn" @click="() => (window as any).location.href = '/'" :title="tr('btn.home')" :aria-label="tr('btn.home')">
        <Home :size="15" />
      </button>

      <button class="hdr-text-btn" @click="auth.logout()" :aria-label="tr('btn.logout')">
        <LogOut :size="13" />
        {{ tr('btn.logout') }}
      </button>
    </div>
  </header>
</template>

<style scoped>
.hdr {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 16px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

/* ── Logo ── */
.hdr-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 20px;
  flex-shrink: 0;
}
.hdr-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--danger);
  animation: pulse-dot 2s ease infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(220,38,38,.4); }
  50% { opacity: .8; box-shadow: 0 0 0 4px rgba(220,38,38,0); }
}
.hdr-brand {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: .08em;
  color: var(--text);
}

/* ── Separators ── */
.hdr-sep {
  width: 1px;
  height: 24px;
  background: var(--border);
  margin-right: 12px;
  flex-shrink: 0;
}
.hdr-sep-v {
  width: 1px;
  height: 20px;
  background: var(--border);
  margin: 0 4px;
  flex-shrink: 0;
  align-self: center;
}

/* ── Nav ── */
.hdr-nav {
  display: flex;
  align-items: stretch;
  height: 100%;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  gap: 2px;
}

/* ── Right ── */
.hdr-right {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: 16px;
  flex-shrink: 0;
}

/* ── Incident badge ── */
.hdr-incident {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 4px;
  background: var(--danger-bg);
  color: var(--danger);
  border: 1px solid var(--danger-border);
}
.hdr-incident-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--danger);
  animation: pulse-dot 2s ease infinite;
}

/* ── User ── */
.hdr-user {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}
.hdr-user-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #10b981;
}
.hdr-role {
  font-size: 11px;
  color: var(--text-muted);
  padding: 1px 6px;
  border-radius: 3px;
  background: var(--surface-raised);
}

/* ── Clock ── */
.hdr-clock {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
}

/* ── Buttons ── */
.hdr-icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  transition: all .15s;
}
.hdr-icon-btn:hover {
  background: var(--surface-raised);
  color: var(--text-secondary);
}

.hdr-text-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  transition: all .15s;
  font-family: inherit;
}
.hdr-text-btn:hover {
  color: var(--text);
  background: var(--surface-raised);
}
</style>
