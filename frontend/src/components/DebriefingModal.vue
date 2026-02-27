<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useHistoryStore } from '@/stores/history'
import { useUiStore }      from '@/stores/ui'
import { pStyle, fmtDuration, fmtDate, fmtTime, formatMessage } from '@/utils'
import { useI18n } from '@/i18n'

const history = useHistoryStore()
const ui      = useUiStore()
const { t: tr } = useI18n()

const data    = ref(null)
const loading = ref(true)
const error   = ref(false)

onMounted(async () => {
  try {
    data.value = await history.getDetail(ui.debriefingId)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
})

function handleKeydown(e) {
  if (e.key === 'Escape') ui.closeDebriefing()
}
onMounted(() => document.addEventListener('keydown', handleKeydown))
onUnmounted(() => document.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div
    class="fixed inset-0 z-40 flex flex-col overflow-hidden"
    style="background:rgba(0,0,0,.7);backdrop-filter:blur(6px)"
  >
    <!-- Modal header -->
    <div
      class="db-modal-hd flex items-center justify-between px-6 py-3 flex-shrink-0"
      style="background:var(--surface);border-bottom:1px solid var(--border)"
    >
      <div class="flex items-center gap-3 min-w-0">
        <span class="text-lg flex-shrink-0">📊</span>
        <div class="min-w-0">
          <p class="text-sm font-bold truncate" style="color:var(--text)">
            {{ data ? `Debriefing — Incident #${data.id} · ${data.type}` : 'Debriefing' }}
          </p>
          <p class="text-xs truncate" style="color:var(--text3)">
            {{ data ? `📍 ${data.location}` : '—' }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2 flex-shrink-0">
        <span
          v-if="data"
          class="text-xs font-bold px-3 py-1 rounded-full border"
          :style="pStyle(data.priority).pill + ';font-size:11px;padding:3px 12px;border-radius:9999px;font-weight:700'"
        >P{{ data.priority }}</span>
        <span class="text-xs font-bold px-3 py-1 rounded-full" style="background:#fee2e2;color:#dc2626;border:1px solid #fca5a5">
          {{ tr('dm.ended') }}
        </span>
        <button
          @click="ui.closeDebriefing()"
          class="text-sm px-4 py-1.5 rounded-lg font-medium transition"
          style="border:1px solid var(--border);color:var(--text2);background:var(--surface)"
        >{{ tr('dm.close') }}</button>
      </div>
    </div>

    <!-- Modal body -->
    <div class="db-modal-body flex flex-1 overflow-hidden" style="background:var(--bg)">

      <!-- Left: transcript -->
      <div
        class="db-transcript flex-1 flex flex-col min-w-0"
        style="background:var(--surface);border-right:1px solid var(--border)"
      >
        <div
          class="db-tc-hd px-5 py-2.5 flex-shrink-0"
          style="background:var(--surface2);border-bottom:1px solid var(--border)"
        >
          <h3 class="text-xs font-bold uppercase tracking-widest" style="color:var(--text3)">
            {{ tr('dm.transcript') }}
          </h3>
        </div>
        <div
          class="db-tc-area flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-3"
          style="background:var(--chat-bg)"
        >
          <!-- Loading -->
          <div v-if="loading" class="m-auto text-center" style="color:var(--text3)">
            <p class="text-3xl mb-2">⏳</p>
            <p class="text-xs">{{ tr('dm.loading') }}</p>
          </div>
          <!-- Error -->
          <p v-else-if="error" class="text-red-500 text-xs m-auto">{{ tr('dm.error') }}</p>
          <!-- Empty -->
          <p v-else-if="!data?.transcript?.length" class="text-xs m-auto" style="color:var(--text3)">
            {{ tr('dm.no_messages') }}
          </p>
          <!-- Messages -->
          <template v-else>
            <div
              v-for="(msg, i) in data.transcript"
              :key="i"
              :class="msg.role === 'user' ? 'flex justify-end' : 'flex justify-start'"
            >
              <div :class="msg.role === 'user' ? 'flex flex-col items-end max-w-[75%]' : 'flex flex-col items-start max-w-[75%]'">
                <div
                  class="px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap"
                  :class="msg.role === 'user' ? 'bop' : 'bal'"
                  v-html="formatMessage(msg.content)"
                ></div>
                <p class="text-xs mt-0.5" style="color:var(--text3)">
                  {{ msg.role === 'user' ? tr('dm.operator') : tr('dm.caller') }} · {{ fmtTime(msg.timestamp) }}
                </p>
              </div>
            </div>
          </template>
        </div>
      </div>

      <!-- Right: metrics + fitxa -->
      <div
        class="db-meta w-80 flex-shrink-0 flex flex-col overflow-y-auto"
        style="background:var(--surface);border-left:1px solid var(--border)"
      >
        <div class="p-4" style="border-bottom:1px solid var(--border)">
          <h3 class="text-xs font-bold uppercase tracking-widest mb-3" style="color:var(--text3)">{{ tr('dm.metrics') }}</h3>
          <div class="flex flex-col gap-2">

            <div class="metric-card flex justify-between items-center p-3 rounded-xl" style="background:var(--surface2);border:1px solid var(--border)">
              <div>
                <p class="text-xs font-semibold" style="color:var(--text2)">{{ tr('dm.duration') }}</p>
                <p class="text-xs mt-0.5" style="color:var(--text3)">{{ tr('dm.duration_sub') }}</p>
              </div>
              <span class="font-mono text-2xl font-bold text-indigo-500 tabular-nums">
                {{ data ? fmtDuration(data.duration_seconds) : '—' }}
              </span>
            </div>

            <div class="metric-card flex justify-between items-center p-3 rounded-xl" style="background:var(--surface2);border:1px solid var(--border)">
              <div>
                <p class="text-xs font-semibold" style="color:var(--text2)">{{ tr('dm.response') }}</p>
                <p class="text-xs mt-0.5" style="color:var(--text3)">{{ tr('dm.response_sub') }}</p>
              </div>
              <span class="font-mono text-2xl font-bold text-cyan-500 tabular-nums">
                {{ data ? fmtDuration(data.initial_response_seconds) : '—' }}
              </span>
            </div>

            <div class="grid grid-cols-2 gap-2">
              <div class="metric-card p-3 rounded-xl text-center" style="background:var(--surface2);border:1px solid var(--border)">
                <p class="text-xs mb-1" style="color:var(--text3)">{{ tr('dm.msg_count') }}</p>
                <p class="font-mono text-xl font-bold" style="color:var(--text)">{{ data?.message_count ?? '—' }}</p>
              </div>
              <div class="metric-card p-3 rounded-xl text-center" style="background:var(--surface2);border:1px solid var(--border)">
                <p class="text-xs mb-1" style="color:var(--text3)">{{ tr('dm.priority') }}</p>
                <p
                  class="font-mono text-xl font-bold"
                  :style="data ? pStyle(data.priority).large : ''"
                >{{ data ? `P${data.priority}` : '—' }}</p>
              </div>
            </div>

            <div class="metric-card p-3 rounded-xl" style="background:var(--surface2);border:1px solid var(--border)">
              <p class="text-xs" style="color:var(--text3)">{{ tr('dm.call_start') }}</p>
              <p class="text-sm font-mono mt-0.5" style="color:var(--text)">{{ data ? fmtDate(data.call_start_at) : '—' }}</p>
            </div>

            <div class="db-warn-box p-3 rounded-xl" style="background:#fffbeb;border:1px solid #fde68a">
              <p class="text-xs text-amber-500">{{ tr('dm.scenario') }}</p>
              <p class="text-sm font-semibold text-amber-800 mt-0.5">
                {{ data?.scenario_title || tr('dm.free_emergency') }}
              </p>
            </div>
          </div>
        </div>

        <!-- Fitxa data -->
        <div class="p-4">
          <h3 class="text-xs font-bold uppercase tracking-widest mb-3" style="color:var(--text3)">{{ tr('dm.data_sheet') }}</h3>
          <div class="flex flex-col rounded-xl overflow-hidden" style="border:1px solid var(--border)">
            <template v-if="!data || !data.intervention">
              <div class="text-center p-4" style="color:var(--text3)">
                <p class="text-xl mb-1">📋</p>
                <p class="text-xs">{{ tr('dm.no_sheet') }}</p>
              </div>
            </template>
            <template v-else>
              <div class="fitxa-row-odd flex justify-between items-start px-4 py-3"
                   style="background:var(--surface2);border-bottom:1px solid var(--border2)">
                <span class="text-xs" style="color:var(--text3)">{{ tr('dm.address') }}</span>
                <span class="text-xs font-medium text-right ml-4" style="color:var(--text)">
                  {{ data.intervention.exact_address || '—' }}
                </span>
              </div>
              <div class="fitxa-row-even flex justify-between items-center px-4 py-3"
                   style="background:var(--surface);border-bottom:1px solid var(--border2)">
                <span class="text-xs" style="color:var(--text3)">{{ tr('dm.phone') }}</span>
                <span class="text-xs font-medium" style="color:var(--text)">
                  {{ data.intervention.contact_phone || '—' }}
                </span>
              </div>
              <div class="fitxa-row-odd flex justify-between items-center px-4 py-3"
                   style="background:var(--surface2);border-bottom:1px solid var(--border2)">
                <span class="text-xs" style="color:var(--text3)">{{ tr('dm.injured') }}</span>
                <span
                  class="text-base font-bold font-mono"
                  :style="data.intervention.num_injured > 0 ? 'color:#ef4444' : 'color:var(--text3)'"
                >{{ data.intervention.num_injured }}</span>
              </div>
              <div
                v-if="data.intervention.additional_risks"
                class="fitxa-row-even px-4 py-3"
                style="background:var(--surface);border-bottom:1px solid var(--border2)"
              >
                <p class="text-xs mb-2" style="color:var(--text3)">{{ tr('dm.risks') }}</p>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="r in data.intervention.additional_risks.split(',').filter(Boolean)"
                    :key="r"
                    class="text-xs px-2 py-0.5 rounded-full"
                    style="background:#ffedd5;color:#ea580c;border:1px solid #fed7aa"
                  >{{ r }}</span>
                </div>
              </div>
              <div
                v-if="data.intervention.operator_notes"
                class="fitxa-row-odd px-4 py-3"
                style="background:var(--surface2);border-bottom:1px solid var(--border2)"
              >
                <p class="text-xs mb-1.5" style="color:var(--text3)">{{ tr('dm.notes') }}</p>
                <p class="text-xs leading-relaxed" style="color:var(--text2)">{{ data.intervention.operator_notes }}</p>
              </div>
              <div class="fitxa-db-foot px-4 py-2 text-right" style="background:var(--surface)">
                <p class="text-xs" style="color:var(--text3)">{{ tr('dm.saved') }} {{ fmtDate(data.intervention.saved_at) }}</p>
              </div>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
