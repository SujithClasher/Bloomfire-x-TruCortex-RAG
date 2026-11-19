<template>
  <div class="fullscreen apple-canvas-ambient row items-center justify-center q-pa-md select-none">
    <!-- Centered Frosted Glass Authentication Card -->
    <div class="apple-login-card q-pa-xl column items-center">
      <!-- Logo with glow -->
      <div class="shield-container q-mb-md row items-center justify-center">
        <img src="/icon.png" alt="TruCortex Logo" class="login-logo" />
      </div>

      <!-- Header Typography -->
      <h1 class="apple-title q-ma-none text-center">CIBIL Intelligence</h1>
      <p class="apple-subtitle q-mt-xs q-mb-lg text-center">
        TruCortex x Bloomfire KMP • Authenticated via Ping + IDMart SSO
      </p>

      <!-- Segmented Portal Mode Toggle: Admin vs Department Workspace -->
      <div class="portal-segmented-bar row items-center full-width q-mb-lg">
        <button
          type="button"
          class="segmented-btn col cursor-pointer row items-center justify-center no-wrap"
          :class="{ 'segmented-active': portalMode === 'admin' }"
          @click="portalMode = 'admin'"
        >
          <q-icon name="admin_panel_settings" size="15px" class="q-mr-xs text-blue-4" />
          <span>Platform Admin</span>
        </button>
        <button
          type="button"
          class="segmented-btn col cursor-pointer row items-center justify-center no-wrap"
          :class="{ 'segmented-active': portalMode === 'workspace' }"
          @click="portalMode = 'workspace'"
        >
          <q-icon name="domain" size="15px" class="q-mr-xs text-emerald" />
          <span>Department User</span>
        </button>
      </div>

      <!-- 1. PLATFORM ADMIN AUTHENTICATION FORM -->
      <div v-if="portalMode === 'admin'" class="full-width column q-gutter-y-md q-mb-lg">
        <!-- Admin Identity Selection Card -->
        <div class="admin-identity-card q-pa-md rounded-borders">
          <div class="row items-center justify-between no-wrap q-mb-xs">
            <span class="admin-badge-tag">MASTER CLEARANCE</span>
            <span class="admin-status-dot"></span>
          </div>
          <div class="row items-center no-wrap q-mt-xs">
            <q-avatar size="38px" class="q-mr-sm admin-avatar">
              <q-icon name="person" size="22px" color="blue-4" />
            </q-avatar>
            <div class="col ellipsis">
              <div class="text-weight-bold text-white ellipsis text-subtitle2">
                {{ selectedAdmin?.full_name || 'Ananya Iyer' }}
              </div>
              <div class="text-caption text-secondary ellipsis" style="font-size: 11.5px;">
                {{ selectedAdmin?.role_title || 'Platform Admin (Senior PM)' }}
              </div>
            </div>
          </div>

          <!-- Quick Admin Switcher (If multiple admins exist) -->
          <div v-if="adminUsers.length > 1" class="row items-center q-gutter-x-xs q-mt-sm border-top-hairline q-pt-xs">
            <span class="text-caption text-secondary" style="font-size: 10.5px;">Select Admin:</span>
            <button
              v-for="adm in adminUsers"
              :key="adm.username"
              type="button"
              class="admin-sub-switch cursor-pointer"
              :class="{ 'sub-switch-active': selectedAdmin?.username === adm.username }"
              @click="selectedAdmin = adm"
            >
              {{ adm.full_name.split(' ')[0] }}
            </button>
          </div>
        </div>

        <!-- Clearance Summary Pill -->
        <div class="clearance-summary-pill q-pa-xs text-center text-caption text-secondary" style="font-size: 11px;">
          ✓ Authorized for Document Ingestion & Impact Radar
        </div>

        <!-- Single SSO Credential Field -->
        <div>
          <label class="apple-field-label">Ping Identity SSO Token / PIN</label>
          <div class="apple-input-box row items-center q-px-sm">
            <q-icon name="key" size="16px" color="grey-6" class="q-mr-sm" />
            <input
              v-model="ssoPin"
              type="password"
              class="apple-naked-input col text-white"
              placeholder="Enter enterprise PIN"
              @keyup.enter="handleLogin"
            />
            <span class="sso-verified-chip">SSO ACTIVE</span>
          </div>
        </div>
      </div>

      <!-- 2. DEPARTMENT WORKSPACE AUTHENTICATION FORM -->
      <div v-else class="full-width column q-gutter-y-md q-mb-lg">
        <!-- Single Sleek Role & Department Select Dropdown -->
        <div>
          <label class="apple-field-label">Select Department Identity</label>
          <q-select
            v-model="selectedDeptUser"
            :options="departmentUsers"
            option-label="full_name"
            dark
            dense
            outlined
            class="apple-select-field"
            popup-content-class="apple-popup-menu"
          >
            <template #selected>
              <div v-if="selectedDeptUser" class="row items-center no-wrap q-gutter-x-xs">
                <span class="dept-dot-indicator" :style="{ backgroundColor: getDeptColor(selectedDeptUser.department) }"></span>
                <span class="text-white text-caption text-weight-medium">{{ selectedDeptUser.full_name }}</span>
                <span class="text-secondary text-caption" style="font-size: 11px;">({{ selectedDeptUser.department }})</span>
              </div>
            </template>
            <template #option="scope">
              <q-item v-bind="scope.itemProps" class="apple-dropdown-item">
                <q-item-section avatar style="min-width: 24px;">
                  <span class="dept-dot-indicator" :style="{ backgroundColor: getDeptColor(scope.opt.department) }"></span>
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-white text-caption text-weight-medium">
                    {{ scope.opt.full_name }}
                  </q-item-label>
                  <q-item-label caption class="text-secondary" style="font-size: 10.5px;">
                    {{ scope.opt.role_title || scope.opt.department }}
                  </q-item-label>
                </q-item-section>
                <q-item-section side>
                  <span
                    class="role-clearance-mini"
                    :class="scope.opt.is_owner ? 'tag-owner' : 'tag-analyst'"
                  >
                    {{ scope.opt.is_owner ? 'Owner' : 'Analyst' }}
                  </span>
                </q-item-section>
              </q-item>
            </template>
          </q-select>
        </div>

        <!-- Selected Persona Detail Bar -->
        <div v-if="selectedDeptUser" class="dept-preview-card q-pa-sm rounded-borders">
          <div class="row items-center justify-between text-caption" style="font-size: 11px;">
            <span class="text-secondary">Role:</span>
            <span class="text-white text-weight-medium">{{ selectedDeptUser.role_title }}</span>
          </div>
          <div class="row items-center justify-between text-caption q-mt-xs" style="font-size: 11px;">
            <span class="text-secondary">Clearance:</span>
            <span class="text-blue-4">{{ selectedDeptUser.is_owner ? 'Dept Ingestion & Query' : 'Query Only (Read-Only)' }}</span>
          </div>
        </div>

        <!-- Single SSO Credential Field -->
        <div>
          <label class="apple-field-label">Ping IDMart SSO PIN</label>
          <div class="apple-input-box row items-center q-px-sm">
            <q-icon name="fingerprint" size="16px" color="grey-6" class="q-mr-sm" />
            <input
              v-model="ssoPin"
              type="password"
              class="apple-naked-input col text-white"
              placeholder="Enter enterprise PIN"
              @keyup.enter="handleLogin"
            />
            <span class="sso-verified-chip">IDMART VERIFIED</span>
          </div>
        </div>
      </div>

      <!-- High-Contrast Full-Width White Pill Button -->
      <button
        class="apple-cta-button full-width text-weight-semibold cursor-pointer row items-center justify-center no-wrap"
        :disabled="portalMode === 'admin' ? !selectedAdmin : !selectedDeptUser"
        @click="handleLogin"
      >
        <span>{{ submitButtonLabel }}</span>
        <q-icon name="arrow_forward" size="16px" class="q-ml-xs" />
      </button>

      <!-- Quiet System Disclaimer -->
      <div class="q-mt-lg text-center system-footnote">
        Protected by Kernel RBAC & Regex PII GuardLLM • Zero External Cloud
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore, User } from '../stores/auth'

const authStore = useAuthStore()

const portalMode = ref<'admin' | 'workspace'>('admin')
const ssoPin = ref('••••••••••••')

// Find admin users
const adminUsers = computed(() => {
  return authStore.users.filter(u => u.is_admin || ['ananya', 'vikram'].includes(u.username))
})

// Find department workspace users
const departmentUsers = computed(() => {
  return authStore.users.filter(u => !u.is_admin && !['ananya'].includes(u.username))
})

const selectedAdmin = ref<User | null>(null)
const selectedDeptUser = ref<User | null>(null)

onMounted(async () => {
  await authStore.fetchUsers()
  selectedAdmin.value = adminUsers.value[0] || authStore.users[0]
  selectedDeptUser.value = departmentUsers.value[0] || authStore.users[1]
})

const submitButtonLabel = computed(() => {
  if (portalMode.value === 'admin') {
    return 'Sign In to Admin & Radar Panel'
  }
  return `Continue as ${selectedDeptUser.value?.full_name?.split(' ')[0] || 'User'}`
})

function getDeptColor(dept: string): string {
  return authStore.departmentColors[dept] || '#0A84FF'
}

function handleLogin() {
  if (portalMode.value === 'admin' && selectedAdmin.value) {
    authStore.login(selectedAdmin.value, 'admin')
  } else if (portalMode.value === 'workspace' && selectedDeptUser.value) {
    authStore.login(selectedDeptUser.value, 'chat')
  }
}
</script>

<style scoped>
.apple-login-card {
  width: 100%;
  max-width: 440px;
  background: rgba(22, 22, 24, 0.85);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 28px;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.85), 0 0 0 1px rgba(255, 255, 255, 0.05);
}

.shield-container {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(99, 179, 237, 0.08);
  border: 1px solid rgba(99, 179, 237, 0.2);
  box-shadow: 0 0 32px rgba(99, 179, 237, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-logo {
  width: 48px;
  height: 48px;
  object-fit: contain;
  filter: drop-shadow(0 0 10px rgba(99, 179, 237, 0.5));
}

.apple-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: #F5F5F7;
  line-height: 1.2;
}

.apple-subtitle {
  font-size: 13px;
  font-weight: 400;
  color: #8E8E93;
  letter-spacing: -0.01em;
}

/* Segmented Mode Selector */
.portal-segmented-bar {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 3px;
}

.segmented-btn {
  background: transparent;
  border: none;
  border-radius: 11px;
  padding: 8px 12px;
  font-size: 12.5px;
  font-weight: 500;
  color: #8E8E93;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.segmented-btn:hover {
  color: #F5F5F7;
}

.segmented-active {
  background: rgba(255, 255, 255, 0.14);
  color: #FFFFFF !important;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

/* Admin Identity Card */
.admin-identity-card {
  background: rgba(10, 132, 255, 0.08);
  border: 1px solid rgba(10, 132, 255, 0.22);
  border-radius: 16px;
}

.admin-avatar {
  background: rgba(10, 132, 255, 0.15);
  border: 1px solid rgba(10, 132, 255, 0.3);
}

.admin-badge-tag {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.04em;
  background: rgba(10, 132, 255, 0.2);
  color: #0A84FF;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(10, 132, 255, 0.4);
}

.admin-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #30D158;
  box-shadow: 0 0 6px #30D158;
}

.admin-sub-switch {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #8E8E93;
  font-size: 10.5px;
  padding: 2px 8px;
  border-radius: 6px;
  transition: all 0.15s ease;
}

.admin-sub-switch:hover {
  color: #FFFFFF;
}

.sub-switch-active {
  background: rgba(10, 132, 255, 0.25);
  border-color: #0A84FF;
  color: #0A84FF;
  font-weight: 600;
}

.clearance-summary-pill {
  background: rgba(48, 209, 88, 0.08);
  border: 1px solid rgba(48, 209, 88, 0.2);
  border-radius: 8px;
  color: #30D158;
}

/* Department User Form */
.dept-preview-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.dept-dot-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.role-clearance-mini {
  font-size: 9px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 4px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.tag-owner {
  background: rgba(48, 209, 88, 0.15);
  color: #30D158;
  border: 1px solid rgba(48, 209, 88, 0.3);
}

.tag-analyst {
  background: rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

/* Inputs & Form Elements */
.apple-field-label {
  display: block;
  font-size: 11px;
  font-weight: 500;
  color: #8E8E93;
  letter-spacing: -0.01em;
  margin-bottom: 5px;
}

.apple-input-box {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 12px;
  height: 42px;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-input-box:focus-within {
  border-color: #0A84FF;
  box-shadow: 0 0 12px rgba(10, 132, 255, 0.25);
  background: rgba(255, 255, 255, 0.08);
}

.apple-naked-input {
  background: transparent;
  border: none;
  outline: none;
  font-size: 13px;
  font-family: inherit;
  letter-spacing: 0.15em;
}

.sso-verified-chip {
  font-size: 8.5px;
  font-weight: 700;
  letter-spacing: 0.04em;
  background: rgba(48, 209, 88, 0.15);
  color: #30D158;
  padding: 2px 5px;
  border-radius: 4px;
  border: 1px solid rgba(48, 209, 88, 0.3);
}

/* High Contrast CTA Button */
.apple-cta-button {
  background: #F5F5F7;
  color: #000000;
  border: none;
  border-radius: 9999px;
  padding: 13px 20px;
  font-size: 14px;
  font-family: inherit;
  letter-spacing: -0.01em;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-cta-button:hover:not(:disabled) {
  background: #FFFFFF;
  transform: scale(1.01);
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.25);
}

.apple-cta-button:active:not(:disabled) {
  transform: scale(0.99);
}

.apple-cta-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.system-footnote {
  font-size: 11px;
  color: #636366;
  letter-spacing: -0.01em;
}

:deep(.apple-select-field .q-field__control) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 12px;
  min-height: 42px;
  color: #F5F5F7;
}

:deep(.apple-select-field .q-field__control:hover) {
  border-color: rgba(255, 255, 255, 0.18);
}

:deep(.apple-popup-menu) {
  background: rgba(22, 22, 24, 0.95) !important;
  backdrop-filter: blur(24px) saturate(180%) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 14px !important;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8) !important;
}

:deep(.apple-dropdown-item) {
  border-radius: 8px;
  margin: 2px 4px;
  transition: background 0.15s ease;
}

:deep(.apple-dropdown-item:hover) {
  background: rgba(255, 255, 255, 0.08);
}
</style>
