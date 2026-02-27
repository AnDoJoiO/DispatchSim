<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore }      from '@/stores/auth'
import { useAppStore }       from '@/stores/app'
import { useEmergencyStore } from '@/stores/emergency'
import { useUiStore }        from '@/stores/ui'

import LoginModal      from '@/components/LoginModal.vue'
import AppHeader       from '@/components/AppHeader.vue'
import EmergencyPanel  from '@/components/panels/EmergencyPanel.vue'
import ScenariosPanel  from '@/components/panels/ScenariosPanel.vue'
import UsersPanel      from '@/components/panels/UsersPanel.vue'
import HistoryPanel    from '@/components/panels/HistoryPanel.vue'
import ChatWindow      from '@/components/ChatWindow.vue'
import FitxaPanel      from '@/components/FitxaPanel.vue'
import DebriefingModal from '@/components/DebriefingModal.vue'
import EditUserModal   from '@/components/EditUserModal.vue'

const auth      = useAuthStore()
const app       = useAppStore()
const emergency = useEmergencyStore()
const ui        = useUiStore()

const isManagementTab = computed(() =>
  app.activeTab === 'scenarios' || app.activeTab === 'users'
)

onMounted(async () => {
  if (auth.isLoggedIn) {
    await emergency.loadScenarios()
    emergency.setPriority(1)
  }
})
</script>

<template>
  <LoginModal v-if="!auth.isLoggedIn" />

  <template v-else>
    <AppHeader />

    <!-- Gestió — ocupa tot l'ample, independent del simulador -->
    <main v-if="isManagementTab" class="flex flex-1 overflow-hidden p-4">
      <ScenariosPanel v-if="app.activeTab === 'scenarios'" />
      <UsersPanel     v-else-if="app.activeTab === 'users'" />
    </main>

    <!-- Simulador — 3 columnes -->
    <main v-else class="flex flex-1 overflow-hidden p-3 gap-3">
      <div
        class="left-panel-wrap w-80 flex-shrink-0 flex flex-col gap-3 overflow-hidden"
        style="background:var(--bg)"
      >
        <EmergencyPanel v-if="app.activeTab === 'emergency'" />
        <HistoryPanel   v-else-if="app.activeTab === 'history'" />
      </div>

      <ChatWindow />
      <FitxaPanel />
    </main>

    <DebriefingModal v-if="ui.debriefingId !== null" />
    <EditUserModal   v-if="ui.editUserId !== null"   />
  </template>
</template>
