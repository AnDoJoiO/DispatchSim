<script setup lang="ts">
import { onMounted } from 'vue'
import { useScenarioStore } from '@/stores/scenarios'
import ScenarioEditor from '@/components/ScenarioEditor.vue'
import { useI18n } from '@/i18n'
import { RefreshCw, Trash2 } from 'lucide-vue-next'

const scenarios = useScenarioStore()
const { t: tr } = useI18n()

onMounted(() => scenarios.loadScenarios())

async function deleteScenario(id: number) {
  if (!confirm(tr('sp.confirm_delete'))) return
  await scenarios.deleteScenario(id)
}
</script>

<template>
  <div class="sp">

    <!-- Sidebar: scenario list -->
    <div class="sp-sidebar">
      <div class="sp-sidebar-hd">
        <span>{{ tr('sp.header', { n: scenarios.scenariosCache.length }) }}</span>
        <button class="sp-refresh" @click="scenarios.loadScenarios()" :title="tr('title.refresh')">
          <RefreshCw :size="13" />
        </button>
      </div>

      <ul class="sp-list">
        <li v-if="!scenarios.scenariosCache.length" class="sp-empty">
          {{ tr('sp.empty') }}
        </li>
        <li
          v-for="s in scenarios.scenariosCache"
          :key="s.id"
          class="sp-item"
        >
          <div class="sp-item-info">
            <p class="sp-item-title">{{ s.title }}</p>
            <p class="sp-item-type">{{ tr('type.' + s.incident_type) }}</p>
            <div v-if="s.victim_status || s.initial_emotion" class="sp-item-tags">
              <span v-if="s.victim_status" class="sp-tag sp-tag--victim">{{ tr('vs.' + s.victim_status) }}</span>
              <span v-if="s.initial_emotion" class="sp-tag sp-tag--emotion">{{ tr('ie.' + s.initial_emotion) }}</span>
            </div>
          </div>
          <button class="sp-del" @click.stop="deleteScenario(s.id)" :title="tr('title.delete')">
            <Trash2 :size="13" />
          </button>
        </li>
      </ul>
    </div>

    <!-- Editor -->
    <ScenarioEditor @created="scenarios.loadScenarios()" />

  </div>
</template>

<style scoped>
.sp {
  width: 100%;
  display: flex;
  gap: 0;
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 8px;
}

/* ── Sidebar ── */
.sp-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: 1px solid var(--border);
  background: var(--surface);
}
.sp-sidebar-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--surface-raised);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.sp-refresh {
  width: 26px; height: 26px; border-radius: 5px; display: flex;
  align-items: center; justify-content: center; cursor: pointer;
  border: 1px solid var(--border); background: transparent;
  color: var(--text-muted); transition: all .15s;
}
.sp-refresh:hover { background: var(--surface-raised); color: var(--text); }

.sp-list {
  list-style: none; padding: 0; margin: 0;
  overflow-y: auto; flex: 1;
}
.sp-empty {
  font-size: 12px; color: var(--text-muted);
  padding: 24px 14px; text-align: center;
}
.sp-item {
  display: flex; align-items: flex-start; gap: 8px;
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  transition: background .1s;
}
.sp-item:hover { background: var(--surface-raised); }

.sp-item-info { min-width: 0; flex: 1; }
.sp-item-title { font-size: 13px; font-weight: 600; color: var(--text); margin: 0; line-height: 1.3; }
.sp-item-type { font-size: 11px; color: var(--text-muted); margin: 2px 0 0; }
.sp-item-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }

.sp-tag {
  font-size: 10px; font-weight: 500; padding: 2px 7px; border-radius: 3px;
}
.sp-tag--victim { background: var(--warning-bg); color: var(--warning); border: 1px solid var(--warning-border); }
.sp-tag--emotion { background: #f3e8ff; color: #7c3aed; border: 1px solid #e9d5ff; }
[data-theme="dark"] .sp-tag--emotion { background: rgba(124,58,237,.1); border-color: rgba(124,58,237,.3); }

.sp-del {
  flex-shrink: 0; width: 26px; height: 26px; border-radius: 5px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; border: 1px solid transparent; background: transparent;
  color: var(--text-muted); transition: all .15s; opacity: 0;
}
.sp-item:hover .sp-del { opacity: 1; }
.sp-del:hover { background: var(--danger-bg); color: var(--danger); border-color: var(--danger-border); }
</style>
