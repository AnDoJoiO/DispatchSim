<script setup>
import { onMounted } from 'vue'
import { useEmergencyStore } from '@/stores/emergency'
import ScenarioEditor from '@/components/ScenarioEditor.vue'

const emergency = useEmergencyStore()

onMounted(() => emergency.loadScenarios())

async function deleteScenario(id) {
  if (!confirm('Eliminar aquest escenari?')) return
  await emergency.deleteScenario(id)
}
</script>

<template>
  <div class="w-full flex gap-0 overflow-hidden" style="border:1px solid var(--border);border-radius:12px">

    <!-- Sidebar esquerra: llista d'escenaris -->
    <div
      class="w-64 flex-shrink-0 flex flex-col overflow-hidden"
      style="border-right:1px solid var(--border);background:var(--surface)"
    >
      <div
        class="px-4 py-3 text-xs font-semibold tracking-wide flex-shrink-0 flex items-center justify-between"
        style="border-bottom:1px solid var(--border);color:var(--text2)"
      >
        <span>ESCENARIS ({{ emergency.scenariosCache.length }})</span>
        <button
          @click="emergency.loadScenarios()"
          title="Actualitzar"
          style="color:var(--text3)"
        >↺</button>
      </div>

      <ul class="flex flex-col overflow-y-auto flex-1 py-1">
        <li
          v-if="!emergency.scenariosCache.length"
          class="text-xs px-4 py-6 text-center"
          style="color:var(--text3)"
        >
          Cap escenari creat
        </li>
        <li
          v-for="s in emergency.scenariosCache"
          :key="s.id"
          class="group flex items-start gap-2 px-3 py-3 transition"
          style="border-bottom:1px solid var(--border2)"
          :class="{ 'hover:bg-blue-50': true }"
        >
          <div class="min-w-0 flex-1">
            <p class="text-xs font-semibold leading-snug" style="color:var(--text)">{{ s.title }}</p>
            <p class="text-xs mt-0.5" style="color:var(--text3)">{{ s.incident_type }}</p>
            <div v-if="s.victim_status || s.initial_emotion" class="flex flex-wrap gap-1 mt-1.5">
              <span
                v-if="s.victim_status"
                class="text-xs px-1.5 py-0.5 rounded-full"
                style="background:#fef9c3;color:#854d0e"
              >{{ s.victim_status }}</span>
              <span
                v-if="s.initial_emotion"
                class="text-xs px-1.5 py-0.5 rounded-full"
                style="background:#ede9fe;color:#5b21b6"
              >{{ s.initial_emotion }}</span>
            </div>
          </div>
          <button
            @click.stop="deleteScenario(s.id)"
            class="flex-shrink-0 text-xs px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition"
            style="color:var(--text3)"
            title="Eliminar"
          >✕</button>
        </li>
      </ul>
    </div>

    <!-- Vista central: editor -->
    <ScenarioEditor @created="emergency.loadScenarios()" />

  </div>
</template>
