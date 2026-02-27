<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore }  from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useUiStore }    from '@/stores/ui'
import { ROLE_STYLES } from '@/utils'
import { useI18n } from '@/i18n'

const auth  = useAuthStore()
const users = useUsersStore()
const ui    = useUiStore()
const { t: tr } = useI18n()

const username  = ref('')
const password  = ref('')
const role      = ref('operador')
const expiryVal = ref('')
const error     = ref('')

onMounted(() => users.load())

const showExpiry = computed(() => role.value === 'operador')

async function createUser() {
  error.value = ''
  if (username.value.trim().length < 3) { error.value = tr('up.error_username'); return }
  if (password.value.length < 6)         { error.value = tr('up.error_password'); return }
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
  <div class="w-full flex gap-4 overflow-hidden">

    <!-- Columna esquerra: formulari -->
    <div class="w-80 flex-shrink-0 flex flex-col gap-3 overflow-y-auto pb-1">
      <div class="panel">
        <div class="panel-hd">{{ tr('up.new_user') }}</div>
        <div class="panel-body flex flex-col gap-3">
          <div>
            <label class="fl">{{ tr('up.username') }}</label>
            <input v-model="username" type="text" :placeholder="tr('up.username_ph')" class="fc" />
          </div>
          <div>
            <label class="fl">{{ tr('up.password') }}</label>
            <input v-model="password" type="password" :placeholder="tr('up.password_ph')" class="fc" />
          </div>
          <div>
            <label class="fl">{{ tr('up.role') }}</label>
            <select v-model="role" class="fc">
              <option value="operador">{{ tr('up.role_operator') }}</option>
              <option v-if="auth.canManage" value="formador">{{ tr('up.role_trainer') }}</option>
              <option v-if="auth.isAdmin"   value="admin">{{ tr('up.role_admin') }}</option>
            </select>
          </div>
          <div v-if="showExpiry">
            <label class="fl">{{ tr('up.expiry') }}</label>
            <input v-model="expiryVal" type="date" class="fc" />
          </div>
          <p v-if="error" class="text-xs text-red-500 -mt-1">{{ error }}</p>
          <button
            @click="createUser"
            class="w-full py-2 rounded-lg font-bold text-sm text-white transition"
            style="background:var(--accent)"
          >{{ tr('up.create_btn') }}</button>
        </div>
      </div>
    </div>

    <!-- Columna dreta: llista d'usuaris -->
    <div class="flex-1 flex flex-col gap-3 overflow-y-auto pb-1">
      <div class="panel flex-1 flex flex-col">
        <div class="panel-hd flex items-center justify-between">
          <span>{{ tr('up.users_header', { n: users.items.length }) }}</span>
          <button
            @click="users.load()"
            class="text-xs normal-case font-normal tracking-normal transition"
            style="color:var(--text3);letter-spacing:normal"
          >{{ tr('up.refresh') }}</button>
        </div>
        <div class="overflow-y-auto flex-1">
          <p v-if="!users.items.length" class="text-xs px-4 py-3" style="color:var(--text3)">{{ tr('up.empty') }}</p>
          <div
            v-for="u in users.items"
            :key="u.id"
            class="flex items-center justify-between px-4 py-3 hover:bg-blue-50 transition gap-3"
            :style="`border-bottom:1px solid var(--border2)${isExpired(u) ? ';background:#fff5f5' : ''}`"
          >
            <div class="flex items-center gap-3 min-w-0 flex-1">
              <span class="text-xs font-mono w-5 text-right flex-shrink-0" style="color:var(--text3)">{{ u.id }}</span>
              <span class="text-sm font-medium truncate" style="color:var(--text)">{{ u.username }}</span>
              <span
                v-if="isExpired(u)"
                class="text-xs px-1.5 py-0.5 rounded font-bold flex-shrink-0"
                style="background:#fee2e2;color:#dc2626"
              >{{ tr('up.expired') }}</span>
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
              >{{ tr('role.' + u.role) || u.role }}</span>
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

  </div>
</template>
