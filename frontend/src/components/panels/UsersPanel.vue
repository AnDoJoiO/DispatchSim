<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore }  from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useUiStore }    from '@/stores/ui'
import { ROLE_LABELS, ROLE_STYLES } from '@/utils'

const auth  = useAuthStore()
const users = useUsersStore()
const ui    = useUiStore()

const username  = ref('')
const password  = ref('')
const role      = ref('operador')
const expiryVal = ref('')
const error     = ref('')

onMounted(() => users.load())

const showExpiry = computed(() => role.value === 'operador')

async function createUser() {
  error.value = ''
  if (username.value.trim().length < 3) { error.value = 'Mínim 3 caràcters'; return }
  if (password.value.length < 6)         { error.value = 'Mínim 6 caràcters'; return }
  const body = { username: username.value.trim(), password: password.value, role: role.value }
  if (role.value === 'operador' && expiryVal.value)
    body.expires_at = expiryVal.value + 'T00:00:00'
  const result = await users.create(body)
  if (result.error) { error.value = result.error; return }
  username.value = password.value = expiryVal.value = ''
  role.value = 'operador'
}

function openEdit(id) { ui.openEditUser(id) }

function isExpired(u) {
  if (!u.expires_at) return false
  const d = new Date(u.expires_at.endsWith('Z') || u.expires_at.includes('+') ? u.expires_at : u.expires_at + 'Z')
  return d < new Date()
}
function fmtExpiry(iso) {
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z')
  return d.toLocaleDateString('ca-AD', { day: '2-digit', month: '2-digit', year: '2-digit' })
}
</script>

<template>
  <div class="flex flex-col gap-3 overflow-y-auto flex-1 pb-1 pr-0.5">

    <!-- Create user form -->
    <div class="panel">
      <div class="panel-hd">Nou usuari</div>
      <div class="panel-body flex flex-col gap-3">
        <div>
          <label class="fl">Nom d'usuari</label>
          <input v-model="username" type="text" placeholder="Mínim 3 caràcters" class="fc" />
        </div>
        <div>
          <label class="fl">Contrasenya</label>
          <input v-model="password" type="password" placeholder="Mínim 6 caràcters" class="fc" />
        </div>
        <div>
          <label class="fl">Rol</label>
          <select v-model="role" class="fc">
            <option value="operador">Operador</option>
            <option v-if="auth.canManage" value="formador">Formador</option>
            <option v-if="auth.isAdmin"   value="admin">Administrador</option>
          </select>
        </div>
        <div v-if="showExpiry">
          <label class="fl">Data de caducitat (opcional)</label>
          <input v-model="expiryVal" type="date" class="fc" />
        </div>
        <p v-if="error" class="text-xs text-red-500 -mt-1">{{ error }}</p>
        <button
          @click="createUser"
          class="w-full py-2 rounded-lg font-bold text-sm text-white transition"
          style="background:var(--accent)"
        >+ Crear Usuari</button>
      </div>
    </div>

    <!-- Users list -->
    <div class="panel">
      <div class="panel-hd flex items-center justify-between">
        <span>Usuaris del sistema</span>
        <button
          @click="users.load()"
          class="text-xs normal-case font-normal tracking-normal transition"
          style="color:var(--text3);letter-spacing:normal"
        >↺</button>
      </div>
      <div class="max-h-80 overflow-y-auto">
        <p v-if="!users.items.length" class="text-xs px-4 py-3" style="color:var(--text3)">Cap usuari</p>
        <div
          v-for="u in users.items"
          :key="u.id"
          class="users-row flex items-center justify-between px-4 py-2.5 hover:bg-blue-50 transition"
          :style="`border-bottom:1px solid var(--border2)${isExpired(u) ? ';background:#fff5f5' : ''}`"
        >
          <div class="flex items-center gap-2 min-w-0 flex-1">
            <span class="text-xs font-mono w-5 text-right flex-shrink-0" style="color:var(--text3)">{{ u.id }}</span>
            <span class="text-sm font-medium truncate" style="color:var(--text)">{{ u.username }}</span>
            <span
              v-if="isExpired(u)"
              class="text-xs px-1.5 py-0.5 rounded font-bold flex-shrink-0"
              style="background:#fee2e2;color:#dc2626"
            >Caducat</span>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <span
              v-if="u.role === 'operador' && u.expires_at"
              class="text-xs"
              :style="`color:${isExpired(u) ? '#dc2626' : 'var(--text3)'}`"
            >{{ fmtExpiry(u.expires_at) }}</span>
            <span
              class="text-xs px-2 py-0.5 rounded-full font-semibold"
              :style="ROLE_STYLES[u.role] || ''"
            >{{ ROLE_LABELS[u.role] || u.role }}</span>
            <span
              class="w-2 h-2 rounded-full inline-block"
              :class="u.is_active ? 'bg-emerald-400' : 'bg-red-400'"
            ></span>
            <button
              v-if="auth.canManage && u.role === 'operador'"
              @click="openEdit(u.id)"
              class="text-xs px-2 py-0.5 rounded transition"
              style="color:var(--accent);border:1px solid var(--accent-br)"
            >✎</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>
