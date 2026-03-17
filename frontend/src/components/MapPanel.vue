<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue'
import { useCallStore } from '@/stores/call'
import { useChatStore } from '@/stores/chat'
import { useI18n } from '@/i18n'
import { MapPin, Crosshair, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-vue-next'
import 'leaflet/dist/leaflet.css'
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet'

const call = useCallStore()
const chat = useChatStore()
const { t: tr } = useI18n()

const collapsed = ref(false)
const markerVisible = ref(false)
const locating = ref(false)
const locFailed = ref(false)
const mapRef = ref<any>(null)
let abortCtrl: AbortController | null = null

const DEFAULT_CENTER: [number, number] = [42.5063, 1.5218]
const MAP_ZOOM = 16
const FALLBACK_ZOOM = 13

const center = ref<[number, number]>(DEFAULT_CENTER)
const markerPos = ref<[number, number]>(DEFAULT_CENTER)
const currentZoom = ref(MAP_ZOOM)

// Invalidate map size when expanding
watch(collapsed, async (val) => {
  if (!val) {
    await nextTick()
    mapRef.value?.leafletObject?.invalidateSize()
  }
})

// ── Nominatim geocoding ──────────────────────────────────

async function geocode(query: string): Promise<[number, number] | null> {
  if (abortCtrl) abortCtrl.abort()
  abortCtrl = new AbortController()
  const timeout = setTimeout(() => abortCtrl?.abort(), 4000)
  try {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`
    const res = await fetch(url, {
      headers: { 'User-Agent': 'DispatchSim/1.0' },
      signal: abortCtrl.signal,
    })
    clearTimeout(timeout)
    if (!res.ok) return null
    const data = await res.json()
    if (data.length > 0) {
      return [parseFloat(data[0].lat), parseFloat(data[0].lon)]
    }
    return null
  } catch {
    clearTimeout(timeout)
    return null
  }
}

// Try full address first, then fallback to city/location only
async function locateIncident(): Promise<void> {
  const inc = call.currentIncident
  if (!inc) return

  locating.value = true
  locFailed.value = false
  markerVisible.value = false

  // Build search queries: full location first, then just the base location
  const queries: string[] = []
  if (inc.location) queries.push(inc.location)
  // If location has comma (e.g., "Carrer Major 14, Andorra la Vella"), also try just the city part
  if (inc.location?.includes(',')) {
    const parts = inc.location.split(',')
    queries.push(parts[parts.length - 1].trim())
  }
  // Also try the incident type + location as last resort
  if (inc.type && inc.location) queries.push(`${inc.type} ${inc.location}`)

  let coords: [number, number] | null = null
  for (const q of queries) {
    if (!q) continue
    coords = await geocode(q)
    if (coords) break
  }

  if (coords) {
    center.value = coords
    markerPos.value = coords
    currentZoom.value = MAP_ZOOM
    markerVisible.value = true
  } else {
    // Total fallback: center on default but show warning
    center.value = DEFAULT_CENTER
    markerPos.value = DEFAULT_CENTER
    currentZoom.value = FALLBACK_ZOOM
    markerVisible.value = true
    locFailed.value = true
  }

  locating.value = false

  // Ensure map re-renders with new center
  await nextTick()
  const map = mapRef.value?.leafletObject
  if (map) {
    map.invalidateSize()
    map.setView(center.value, currentZoom.value)
  }
}

// ── Watchers ─────────────────────────────────────────────

// When a new message from ALT arrives, try to geocode address from the conversation
// (the AI might have given the address — re-geocode with latest info)
let lastGeocodedMsgCount = 0

watch(() => call.callActive, (active) => {
  if (active) {
    lastGeocodedMsgCount = 0
    locateIncident()
  } else {
    markerVisible.value = false
    locating.value = false
    locFailed.value = false
    if (abortCtrl) { abortCtrl.abort(); abortCtrl = null }
  }
})

watch(() => call.currentIncidentId, (id) => {
  if (id && call.callActive) {
    lastGeocodedMsgCount = 0
    locateIncident()
  }
})

onUnmounted(() => { if (abortCtrl) abortCtrl.abort() })
</script>

<template>
  <div class="mp" v-if="call.currentIncidentId">

    <!-- Header -->
    <button class="mp-hd" @click="collapsed = !collapsed">
      <div class="mp-hd-left">
        <MapPin :size="14" />
        <span class="mp-hd-title">{{ tr('map.title') || 'Localització' }}</span>
        <span v-if="locating" class="mp-badge mp-badge--warn">
          <Crosshair :size="12" class="mp-locating-icon" />
          {{ tr('map.locating') || 'Localitzant...' }}
        </span>
        <span v-else-if="locFailed" class="mp-badge mp-badge--err">
          <AlertTriangle :size="11" />
          ~
        </span>
        <span v-else-if="markerVisible" class="mp-badge mp-badge--ok">GPS</span>
      </div>
      <ChevronUp v-if="!collapsed" :size="14" />
      <ChevronDown v-else :size="14" />
    </button>

    <!-- Map -->
    <div v-show="!collapsed" class="mp-body">
      <LMap
        ref="mapRef"
        :zoom="currentZoom"
        :center="center"
        :use-global-leaflet="false"
        class="mp-map"
      >
        <LTileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap"
        />
        <LMarker
          v-if="markerVisible"
          :lat-lng="markerPos"
        >
          <LPopup>
            <div class="mp-popup">
              <strong>#{{ call.currentIncidentId }}</strong>
              <span>{{ call.currentIncident?.type }}</span>
              <span v-if="call.currentIncident?.location" class="mp-popup-loc">{{ call.currentIncident.location }}</span>
              <span v-if="locFailed" class="mp-popup-approx">{{ tr('map.approximate') || 'Ubicació aproximada' }}</span>
            </div>
          </LPopup>
        </LMarker>
      </LMap>
    </div>
  </div>
</template>

<style scoped>
.mp {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
}

.mp-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--surface-raised);
  border: none;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  width: 100%;
  font-family: inherit;
  color: var(--text-muted);
  transition: color .15s;
}
.mp-hd:hover { color: var(--text); }
.mp-hd-left { display: flex; align-items: center; gap: 6px; }
.mp-hd-title { font-size: 12px; font-weight: 600; }

.mp-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 3px;
}
.mp-badge--warn { color: var(--warning); background: var(--warning-bg); }
.mp-badge--ok   { color: var(--success); background: var(--success-bg); }
.mp-badge--err  { color: var(--danger);  background: var(--danger-bg); }

.mp-locating-icon { animation: spin-slow 2s linear infinite; }
@keyframes spin-slow { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.mp-body { height: 200px; }
.mp-map { width: 100%; height: 100%; z-index: 0; }

.mp-popup {
  display: flex; flex-direction: column; gap: 2px;
  font-size: 12px; font-family: 'Inter', system-ui, sans-serif;
}
.mp-popup strong {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 11px; color: var(--text-muted);
}
.mp-popup-loc { color: var(--text-muted); font-size: 11px; }
.mp-popup-approx { color: var(--warning); font-size: 10px; font-style: italic; }
</style>
