<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore }  from '@/stores/auth'
import { useUsersStore } from '@/stores/users'
import { useUiStore }    from '@/stores/ui'
import { useI18n } from '@/i18n'
import { UserPlus, RefreshCw, Pencil } from 'lucide-vue-next'

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
  const body: any = { username: username.value.trim(), password: password.value, role: role.value }
  if (role.value === 'operador' && expiryVal.value)
    body.expires_at = expiryVal.value + 'T00:00:00'
  try {
    await users.create(body)
    username.value = password.value = expiryVal.value = ''
    role.value = 'operador'
  } catch (e: any) {
    error.value = e.message
  }
}

function openEdit(id: number) { ui.openEditUser(id) }

function isExpired(u: any) {
  if (!u.expires_at) return false
  const d = new Date(u.expires_at.endsWith('Z') || u.expires_at.includes('+') ? u.expires_at : u.expires_at + 'Z')
  return d < new Date()
}
function fmtExpiry(iso: string) {
  const d = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z')
  return d.toLocaleDateString('ca-AD', { day: '2-digit', month: '2-digit', year: '2-digit' })
}
</script>

<template>
  <div class="up">

    <!-- Create form -->
    <div class="up-form-col">
      <div class="up-section">
        <div class="up-section-hd">
          <UserPlus :size="14" />
          {{ tr('up.new_user') }}
        </div>
        <div class="up-section-body">
          <div class="up-field">
            <label for="up-username" class="fp-label">{{ tr('up.username') }}</label>
            <input id="up-username" v-model="username" type="text" :placeholder="tr('up.username_ph')" class="fc" />
          </div>
          <div class="up-field">
            <label for="up-password" class="fp-label">{{ tr('up.password') }}</label>
            <input id="up-password" v-model="password" type="password" :placeholder="tr('up.password_ph')" class="fc" />
          </div>
          <div class="up-field">
            <label for="up-role" class="fp-label">{{ tr('up.role') }}</label>
            <select id="up-role" v-model="role" class="fc">
              <option value="operador">{{ tr('up.role_operator') }}</option>
              <option v-if="auth.canManage" value="formador">{{ tr('up.role_trainer') }}</option>
              <option v-if="auth.isAdmin"   value="admin">{{ tr('up.role_admin') }}</option>
            </select>
          </div>
          <div v-if="showExpiry" class="up-field">
            <label for="up-expiry" class="fp-label">{{ tr('up.expiry') }}</label>
            <input id="up-expiry" v-model="expiryVal" type="date" class="fc" />
          </div>
          <p v-if="error" class="up-error">{{ error }}</p>
          <button @click="createUser" class="up-create-btn">{{ tr('up.create_btn') }}</button>
        </div>
      </div>
    </div>

    <!-- Users table -->
    <div class="up-table-col">
      <div class="up-section up-section--flex">
        <div class="up-section-hd">
          <span>{{ tr('up.users_header', { n: users.items.length }) }}</span>
          <button class="up-refresh" @click="users.load()" :title="tr('up.refresh')">
            <RefreshCw :size="13" />
          </button>
        </div>

        <div class="up-table-wrap">
          <p v-if="!users.items.length" class="up-empty">{{ tr('up.empty') }}</p>
          <table v-else class="up-table">
            <thead>
              <tr>
                <th class="up-th up-th--id">#</th>
                <th class="up-th">{{ tr('up.username') || 'Usuari' }}</th>
                <th class="up-th up-th--role">{{ tr('up.role') || 'Rol' }}</th>
                <th class="up-th up-th--status">{{ tr('up.col_status') || 'Estat' }}</th>
                <th class="up-th up-th--exp">{{ tr('up.expiry') || 'Caducitat' }}</th>
                <th class="up-th up-th--act"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in users.items"
                :key="u.id"
                class="up-row"
                :class="{ 'up-row--expired': isExpired(u) }"
              >
                <td class="up-td up-td--id">{{ u.id }}</td>
                <td class="up-td up-td--name">{{ u.username }}</td>
                <td class="up-td">
                  <span class="up-role-badge" :class="`up-role--${u.role}`">{{ tr('role.' + u.role) || u.role }}</span>
                </td>
                <td class="up-td up-td--status">
                  <span class="up-status-dot" :class="u.is_active ? 'up-status--on' : 'up-status--off'"></span>
                  <span v-if="isExpired(u)" class="up-expired-tag">{{ tr('up.expired') }}</span>
                </td>
                <td class="up-td up-td--exp">
                  {{ u.expires_at ? fmtExpiry(u.expires_at) : '—' }}
                </td>
                <td class="up-td up-td--act">
                  <button
                    v-if="auth.canManage && u.role === 'operador'"
                    @click="openEdit(u.id)"
                    class="up-edit-btn"
                    :title="tr('up.edit') || 'Editar'"
                  >
                    <Pencil :size="13" />
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.up { width: 100%; display: flex; gap: 16px; overflow: hidden; }

/* ── Form column ── */
.up-form-col { width: 320px; flex-shrink: 0; overflow-y: auto; }

/* ── Table column ── */
.up-table-col { flex: 1; overflow: hidden; display: flex; flex-direction: column; }

/* ── Sections ── */
.up-section {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; overflow: hidden;
}
.up-section--flex { display: flex; flex-direction: column; flex: 1; }
.up-section-hd {
  display: flex; align-items: center; justify-content: space-between;
  gap: 8px; padding: 10px 14px; font-size: 12px; font-weight: 600;
  color: var(--text-muted); background: var(--surface-raised);
  border-bottom: 1px solid var(--border); flex-shrink: 0;
}
.up-section-body { padding: 14px; display: flex; flex-direction: column; gap: 10px; }

.up-field { display: flex; flex-direction: column; gap: 4px; }
.up-error { font-size: 12px; color: var(--danger); margin: 0; }

.up-create-btn {
  width: 100%; padding: 8px; border-radius: 6px; font-size: 13px;
  font-weight: 600; cursor: pointer; border: none; background: var(--accent);
  color: white; font-family: inherit; transition: all .15s;
}
.up-create-btn:hover { filter: brightness(1.1); }

.up-refresh {
  width: 26px; height: 26px; border-radius: 5px; display: flex;
  align-items: center; justify-content: center; cursor: pointer;
  border: 1px solid var(--border); background: transparent;
  color: var(--text-muted); transition: all .15s;
}
.up-refresh:hover { background: var(--surface-raised); color: var(--text); }

/* ── Table ── */
.up-table-wrap { flex: 1; overflow-y: auto; }
.up-empty { font-size: 12px; color: var(--text-muted); padding: 24px 14px; text-align: center; }
.up-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.up-th {
  text-align: left; padding: 8px 12px; font-size: 11px; font-weight: 600;
  color: var(--text-muted); background: var(--surface-raised);
  border-bottom: 1px solid var(--border); white-space: nowrap;
  position: sticky; top: 0; z-index: 1;
}
.up-th--id { width: 36px; }
.up-th--role { width: 90px; }
.up-th--status { width: 80px; }
.up-th--exp { width: 90px; }
.up-th--act { width: 44px; }

.up-row { transition: background .1s; }
.up-row:hover { background: var(--surface-raised); }
.up-row--expired { background: var(--danger-bg); }
.up-row:not(:last-child) .up-td { border-bottom: 1px solid var(--border); }

.up-td { padding: 8px 12px; vertical-align: middle; }
.up-td--id { font-family: 'JetBrains Mono', ui-monospace, monospace; color: var(--text-muted); font-size: 11px; }
.up-td--name { font-weight: 500; color: var(--text); }
.up-td--status { display: flex; align-items: center; gap: 6px; }
.up-td--exp { color: var(--text-muted); font-size: 11px; }
.up-td--act { text-align: center; }

.up-status-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.up-status--on { background: var(--success); }
.up-status--off { background: var(--danger); }

.up-expired-tag {
  font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 3px;
  background: var(--danger-bg); color: var(--danger);
}

.up-role-badge {
  font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px;
  display: inline-block;
}
.up-role--admin    { background: #f3e8ff; color: #7e22ce; }
.up-role--formador { background: var(--warning-bg); color: var(--warning); }
.up-role--operador { background: var(--accent-bg); color: var(--accent); }
[data-theme="dark"] .up-role--admin { background: rgba(126,34,206,.1); }

.up-edit-btn {
  width: 28px; height: 28px; border-radius: 5px; display: flex;
  align-items: center; justify-content: center; cursor: pointer;
  border: 1px solid var(--border); background: transparent;
  color: var(--text-muted); transition: all .15s;
}
.up-edit-btn:hover { background: var(--accent-bg); color: var(--accent); border-color: var(--accent-border); }
</style>
