<script setup lang="ts">
import { ref, watch, nextTick, onUnmounted } from 'vue'
import { useCallStore } from '@/stores/call'
import { useI18n } from '@/i18n'
import { MapPin, Crosshair, ChevronDown, ChevronUp } from 'lucide-vue-next'
import 'leaflet/dist/leaflet.css'
import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet'

const call = useCallStore()
const { t: tr } = useI18n()

const collapsed = ref(false)
const markerVisible = ref(false)
const locating = ref(false)
const mapRef = ref<any>(null)
let locTimer: ReturnType<typeof setTimeout> | null = null

// Invalidate map size when expanding (Leaflet needs this after visibility change)
watch(collapsed, async (val) => {
  if (!val) {
    await nextTick()
    mapRef.value?.leafletObject?.invalidateSize()
  }
})

// Default center (Andorra la Vella) — will be overridden by scenario location
const DEFAULT_CENTER: [number, number] = [42.5063, 1.5218]
const MAP_ZOOM = 15

// Generate pseudo-random coordinates near center based on incident id
function coordsForIncident(id: number | null): [number, number] {
  if (!id) return DEFAULT_CENTER
  // Simple deterministic offset from id — same incident always same coords
  const seed1 = Math.sin(id * 7919) * 0.008
  const seed2 = Math.cos(id * 6271) * 0.008
  return [DEFAULT_CENTER[0] + seed1, DEFAULT_CENTER[1] + seed2]
}

const center = ref<[number, number]>(DEFAULT_CENTER)
const markerPos = ref<[number, number]>(DEFAULT_CENTER)

// When call starts, simulate CAD location delay
watch(() => call.callActive, (active) => {
  if (active) {
    markerVisible.value = false
    locating.value = true
    const coords = coordsForIncident(call.currentIncidentId)
    center.value = coords
    markerPos.value = coords
    // Simulate 4s CAD location delay
    locTimer = setTimeout(() => {
      markerVisible.value = true
      locating.value = false
    }, 4000)
  } else {
    markerVisible.value = false
    locating.value = false
    if (locTimer) { clearTimeout(locTimer); locTimer = null }
  }
})

// If incident changes (switchIncident), update coords
watch(() => call.currentIncidentId, (id) => {
  if (id) {
    const coords = coordsForIncident(id)
    center.value = coords
    markerPos.value = coords
    if (call.callActive) {
      markerVisible.value = false
      locating.value = true
      if (locTimer) clearTimeout(locTimer)
      locTimer = setTimeout(() => {
        markerVisible.value = true
        locating.value = false
      }, 4000)
    }
  }
})

onUnmounted(() => { if (locTimer) clearTimeout(locTimer) })
</script>

<template>
  <div class="mp" v-if="call.currentIncidentId">

    <!-- Header (clickable to collapse) -->
    <button class="mp-hd" @click="collapsed = !collapsed">
      <div class="mp-hd-left">
        <MapPin :size="14" />
        <span class="mp-hd-title">{{ tr('map.title') || 'Localització' }}</span>
        <span v-if="locating" class="mp-locating">
          <Crosshair :size="12" class="mp-locating-icon" />
          {{ tr('map.locating') || 'Localitzant...' }}
        </span>
        <span v-else-if="markerVisible" class="mp-located">GPS</span>
      </div>
      <ChevronUp v-if="!collapsed" :size="14" />
      <ChevronDown v-else :size="14" />
    </button>

    <!-- Map -->
    <div v-show="!collapsed" class="mp-body">
      <LMap
        ref="mapRef"
        :zoom="MAP_ZOOM"
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

/* ── Header ── */
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
.mp-hd-left {
  display: flex;
  align-items: center;
  gap: 6px;
}
.mp-hd-title {
  font-size: 12px;
  font-weight: 600;
}

.mp-locating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 10px;
  font-weight: 500;
  color: var(--warning);
  padding: 2px 6px;
  border-radius: 3px;
  background: var(--warning-bg);
}
.mp-locating-icon {
  animation: spin-slow 2s linear infinite;
}
@keyframes spin-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.mp-located {
  font-size: 10px;
  font-weight: 600;
  color: var(--success);
  padding: 2px 6px;
  border-radius: 3px;
  background: var(--success-bg);
}

/* ── Map ── */
.mp-body {
  height: 200px;
}
.mp-map {
  width: 100%;
  height: 100%;
  z-index: 0;
}

/* ── Popup ── */
.mp-popup {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  font-family: 'Inter', system-ui, sans-serif;
}
.mp-popup strong {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 11px;
  color: var(--text-muted);
}
.mp-popup-loc {
  color: var(--text-muted);
  font-size: 11px;
}
</style>
