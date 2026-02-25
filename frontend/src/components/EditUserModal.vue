<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useUsersStore } from '@/stores/users'
import { useUiStore }    from '@/stores/ui'

const users = useUsersStore()
const ui    = useUiStore()

const isActive  = ref('true')
const expiryVal = ref('')
const error     = ref('')
const saving    = ref(false)

const targetUser = computed(() => users.items.find(u => u.id === ui.editUserId))

onMounted(() => {
  const u = targetUser.value
  if (u) {
    isActive.value  = u.is_active ? 'true' : 'false'
    expiryVal.value = u.expires_at ? u.expires_at.substring(0, 10) : ''
  }
})

function handleKeydown(e) {
  if (e.key === 'Escape') ui.closeEditUser()
}
onMounted(() => document.addEventListener('keydown', handleKeydown))
onUnmounted(() => document.removeEventListener('keydown', handleKeydown))

async function submit() {
  error.value  = ''
  saving.value = true
  try {
    await users.update(ui.editUserId, {
      is_active:  isActive.value === 'true',
      expires_at: expiryVal.value ? expiryVal.value + 'T00:00:00' : null,
    })
    ui.closeEditUser()
  } catch (e) {
    error.value = e.message
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center"
    style="background:rgba(15,23,42,.65);backdrop-filter:blur(6px)"
    @click.self="ui.closeEditUser()"
  >
    <div class="rounded-2xl shadow-2xl overflow-hidden w-full max-w-sm" style="background:var(--surface)">
      <!-- Header -->
      <div class="px-6 pt-5 pb-4" style="border-bottom:1px solid var(--border);background:var(--surface2)">
        <h2 class="text-sm font-bold" style="color:var(--text)">
          Editar usuari:
          <span class="font-mono">{{ targetUser?.username }}</span>
        </h2>
      </div>

      <!-- Form -->
      <div class="px-6 py-5 flex flex-col gap-4">
        <div>
          <label class="fl">Estat</label>
          <select v-model="isActive" class="fc">
            <option value="true">Actiu</option>
            <option value="false">Inactiu</option>
          </select>
        </div>
        <div>
          <label class="fl">Data de caducitat (opcional)</label>
          <input v-model="expiryVal" type="date" class="fc" />
          <p class="text-xs mt-1" style="color:var(--text3)">Deixa buit per eliminar la caducitat</p>
        </div>
        <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
      </div>

      <!-- Actions -->
      <div class="px-6 pb-5 flex gap-3 justify-end">
        <button
          @click="ui.closeEditUser()"
          class="text-sm px-4 py-2 rounded-lg font-medium transition"
          style="border:1px solid var(--border);color:var(--text2);background:var(--surface)"
        >Cancel·lar</button>
        <button
          @click="submit"
          :disabled="saving"
          class="text-sm px-4 py-2 rounded-lg font-bold text-white transition"
          style="background:var(--accent)"
        >{{ saving ? 'Desant...' : 'Desar' }}</button>
      </div>
    </div>
  </div>
</template>
