<template>
  <q-dialog v-model="isOpen" maximized transition-show="slide-up" transition-hide="slide-down">
    <div class="fullscreen apple-canvas-ambient row items-center justify-center q-pa-md select-none">
      <div class="apple-admin-card column text-white">
        <!-- 1. Header Bar -->
        <div class="row items-center justify-between q-pa-lg border-bottom-hairline">
          <div class="row items-center q-gutter-x-md">
            <div class="admin-shield-container row items-center justify-center">
              <q-icon name="admin_panel_settings" size="24px" color="blue-4" />
            </div>
            <div>
              <div class="row items-center q-gutter-x-sm">
                <span class="text-h6 text-weight-bold text-white tracking-tight" style="font-size: 19px;">
                  Enterprise Admin Console
                </span>
                <span class="admin-top-badge">CIBIL / TruCortex</span>
              </div>
              <div class="text-caption text-secondary" style="font-size: 12px; margin-top: 2px;">
                Platform Governance, Department Ownership Matrix, and Zero-PII GuardLLM Policies
              </div>
            </div>
          </div>

          <!-- Right Status & Close -->
          <div class="row items-center q-gutter-x-sm">
            <button
              class="cursor-pointer text-caption text-weight-medium q-mr-xs"
              style="font-size: 11.5px; color: #0A84FF; background: rgba(10, 132, 255, 0.12); border: 1px solid rgba(10, 132, 255, 0.3); border-radius: 999px; padding: 4px 10px;"
              @click="authStore.activeView = 'admin'; isOpen = false;"
            >
              Open Full-Screen Admin Panel →
            </button>
            <div class="system-health-pill row items-center q-gutter-x-xs">
              <span class="status-pulse-dot"></span>
              <span class="text-caption text-weight-medium">Port 8010 • Active</span>
            </div>
            <button class="apple-circle-close cursor-pointer" @click="isOpen = false">
              <q-icon name="close" size="14px" />
            </button>
          </div>
        </div>

        <!-- 2. Four KPI Telemetry Tiles -->
        <div class="q-px-lg q-pt-md">
          <div class="row q-col-gutter-sm">
            <div class="col-12 col-sm-3">
              <div class="apple-metric-tile q-pa-sm">
                <div class="metric-label text-secondary">Platform Admins</div>
                <div class="metric-val text-blue-4 text-weight-bold">
                  {{ adminStore.overview?.metrics.platform_admins || 2 }}
                </div>
                <div class="metric-sub text-caption">Master Clearance (Ananya, Vikram)</div>
              </div>
            </div>
            <div class="col-12 col-sm-3">
              <div class="apple-metric-tile q-pa-sm">
                <div class="metric-label text-secondary">Department Owners</div>
                <div class="metric-val text-positive text-weight-bold">
                  {{ adminStore.overview?.metrics.department_owners || 4 }}
                </div>
                <div class="metric-sub text-caption">Approved Ingestion Leads</div>
              </div>
            </div>
            <div class="col-12 col-sm-3">
              <div class="apple-metric-tile q-pa-sm">
                <div class="metric-label text-secondary">Read-Only Analysts</div>
                <div class="metric-val text-grey-4 text-weight-bold">
                  {{ adminStore.overview?.metrics.analysts || 1 }}
                </div>
                <div class="metric-sub text-caption">Restricted from Uploads</div>
              </div>
            </div>
            <div class="col-12 col-sm-3">
              <div class="apple-metric-tile q-pa-sm">
                <div class="metric-label text-secondary">PII Intercepts</div>
                <div class="metric-val text-amber-5 text-weight-bold">
                  {{ adminStore.overview?.metrics.pii_intercepts || 0 }}
                </div>
                <div class="metric-sub text-caption">GuardLLM Zero-Leak Gate</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3. Apple Segmented Tab Selector -->
        <div class="q-px-lg q-pt-md">
          <div class="apple-segmented-bar row items-center no-wrap">
            <button
              class="segment-tab col cursor-pointer"
              :class="{ 'segment-tab-active': activeTab === 'ownership' }"
              @click="activeTab = 'ownership'"
            >
              <q-icon name="people" size="15px" class="q-mr-xs" />
              <span>Ownership Matrix</span>
            </button>
            <button
              class="segment-tab col cursor-pointer"
              :class="{ 'segment-tab-active': activeTab === 'vaults' }"
              @click="activeTab = 'vaults'"
            >
              <q-icon name="folder_special" size="15px" class="q-mr-xs" />
              <span>Enterprise Vaults</span>
            </button>
            <button
              class="segment-tab col cursor-pointer"
              :class="{ 'segment-tab-active': activeTab === 'guardllm' }"
              @click="activeTab = 'guardllm'"
            >
              <q-icon name="gpp_good" size="15px" class="q-mr-xs" />
              <span>Zero-PII GuardLLM</span>
            </button>
            <button
              class="segment-tab col cursor-pointer"
              :class="{ 'segment-tab-active': activeTab === 'telemetry' }"
              @click="activeTab = 'telemetry'"
            >
              <q-icon name="tune" size="15px" class="q-mr-xs" />
              <span>System Telemetry</span>
            </button>
          </div>
        </div>

        <!-- 4. Tab Body Content -->
        <div class="col scroll q-px-lg q-py-md">
          <!-- TAB 1: Ownership Matrix -->
          <div v-if="activeTab === 'ownership'">
            <div class="row items-center justify-between q-mb-sm">
              <div class="text-caption text-secondary">
                Configure approved Department Owners and Platform Admins. Only designated Owners & Admins hold ingestion clearance.
              </div>
              <button
                class="apple-pill-refresh cursor-pointer row items-center no-wrap"
                @click="adminStore.fetchOverview"
              >
                <q-icon name="refresh" size="13px" class="q-mr-xs" />
                <span>Refresh Directory</span>
              </button>
            </div>

            <!-- Users Table -->
            <div class="apple-table-wrapper rounded-borders">
              <table class="apple-table full-width">
                <thead>
                  <tr>
                    <th class="text-left">Persona / Identity</th>
                    <th class="text-left">Department</th>
                    <th class="text-left">Role Title</th>
                    <th class="text-center">Clearance Status</th>
                    <th class="text-right">Admin Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in adminStore.overview?.users || []" :key="u.username" class="table-row">
                    <td>
                      <div class="row items-center q-gutter-x-sm no-wrap">
                        <span class="user-color-dot" :style="{ backgroundColor: authStore.departmentColors[u.department] || '#0A84FF' }"></span>
                        <div>
                          <div class="text-weight-semibold text-white text-caption">{{ u.full_name }}</div>
                          <div class="text-secondary" style="font-size: 10.5px;">@{{ u.username }}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <span class="dept-chip">{{ u.department }}</span>
                    </td>
                    <td class="text-secondary text-caption">
                      {{ u.role_title }}
                    </td>
                    <td class="text-center">
                      <span
                        class="clearance-pill"
                        :class="u.is_admin ? 'pill-admin' : (u.is_owner ? 'pill-owner' : 'pill-analyst')"
                      >
                        {{ u.is_admin ? 'Platform Admin' : (u.is_owner ? 'Dept Owner' : 'Analyst (Read-Only)') }}
                      </span>
                    </td>
                    <td class="text-right">
                      <div class="row items-center justify-end q-gutter-x-xs no-wrap">
                        <!-- Toggle Ownership Button (Demonstrating live role elevation) -->
                        <button
                          v-if="!u.is_admin"
                          class="action-pill-btn cursor-pointer"
                          :title="u.is_owner ? 'Demote to Analyst (Remove Ingestion)' : 'Promote to Department Owner'"
                          @click="toggleOwnerRole(u)"
                        >
                          {{ u.is_owner ? 'Set Analyst' : 'Make Owner' }}
                        </button>
                        <!-- Quick Switch Identity Button -->
                        <button
                          class="action-pill-switch cursor-pointer"
                          title="Switch active user to this persona"
                          @click="switchUserPersona(u)"
                        >
                          {{ authStore.currentUser.username === u.username ? 'Active' : 'Switch' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- TAB 2: Enterprise Vaults -->
          <div v-else-if="activeTab === 'vaults'">
            <div class="row items-center justify-between q-mb-md">
              <div class="text-caption text-secondary">
                Overview of physical document repositories inside <code>/data_repositories/</code>.
              </div>
              <button
                class="apple-pill-primary cursor-pointer row items-center no-wrap text-caption"
                :disabled="foldersStore.isLoading"
                @click="triggerVaultSync"
              >
                <q-icon name="sync" size="13px" class="q-mr-xs" :class="{ 'btn-spinning': foldersStore.isLoading }" />
                <span>Re-Index All Repositories</span>
              </button>
            </div>

            <!-- Vault Cards Grid -->
            <div class="row q-col-gutter-sm">
              <div v-for="vault in vaultDirectory" :key="vault.name" class="col-12 col-sm-6">
                <div class="apple-vault-card q-pa-md">
                  <div class="row items-center justify-between q-mb-xs">
                    <div class="row items-center q-gutter-x-xs">
                      <q-icon :name="vault.icon" size="18px" :color="vault.color" />
                      <span class="text-weight-bold text-white text-caption">{{ vault.name }}</span>
                    </div>
                    <span class="vault-owner-tag">{{ vault.ownerRole }}</span>
                  </div>
                  <div class="text-caption text-secondary q-mb-sm" style="font-size: 11px;">
                    {{ vault.description }}
                  </div>
                  <div class="row items-center justify-between border-top-hairline q-pt-xs text-caption text-secondary" style="font-size: 11px;">
                    <span>Disk Location:</span>
                    <span class="text-white">{{ vault.path }}</span>
                  </div>
                  <div class="row items-center justify-between q-mt-xs text-caption text-secondary" style="font-size: 11px;">
                    <span>Ingestion Approval:</span>
                    <span :class="vault.isRestricted ? 'text-blue-4' : 'text-positive'">{{ vault.approvedOwners }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 3: Zero-PII GuardLLM Sandbox -->
          <div v-else-if="activeTab === 'guardllm'">
            <div class="text-caption text-secondary q-mb-md">
              Regex GuardLLM strictly monitors all chat queries and document streams. PAN & Aadhaar numbers are blocked before vector search (HTTP 422), while phone numbers and emails are automatically masked.
            </div>

            <!-- Active Rules Table -->
            <div class="apple-table-wrapper rounded-borders q-mb-lg">
              <table class="apple-table full-width">
                <thead>
                  <tr>
                    <th class="text-left">Policy Rule</th>
                    <th class="text-left">Regular Expression Pattern</th>
                    <th class="text-center">Enforcement Action</th>
                    <th class="text-left">Security Scope</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="rule in adminStore.overview?.guard_rules || []" :key="rule.rule_name" class="table-row">
                    <td>
                      <div class="text-weight-semibold text-white text-caption">{{ rule.rule_name }}</div>
                    </td>
                    <td>
                      <code class="regex-code">{{ rule.pattern }}</code>
                    </td>
                    <td class="text-center">
                      <span :class="rule.action.includes('BLOCK') ? 'pill-blocked' : 'pill-mask'">
                        {{ rule.action }}
                      </span>
                    </td>
                    <td class="text-secondary text-caption">
                      {{ rule.description }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Live GuardLLM Interactive Playground -->
            <div class="guard-sandbox-card q-pa-md">
              <div class="text-weight-bold text-white text-caption q-mb-xs">
                Live GuardLLM Interception Sandbox
              </div>
              <div class="text-secondary text-caption q-mb-sm" style="font-size: 11px;">
                Type or select sample tokens to test the real regex intercept engine:
              </div>

              <!-- Quick Test Buttons -->
              <div class="row q-gutter-xs q-mb-sm">
                <button class="sample-token-chip cursor-pointer" @click="adminStore.runGuardTest('What is the credit score for PAN ABCDE1234F?')">
                  Test PAN Leak: ABCDE1234F
                </button>
                <button class="sample-token-chip cursor-pointer" @click="adminStore.runGuardTest('Verify Aadhaar number 2345 6789 0123 for dispute ticket.')">
                  Test Aadhaar ID: 2345 6789 0123
                </button>
                <button class="sample-token-chip cursor-pointer" @click="adminStore.runGuardTest('Contact analyst at +91 9876543210 or ops@cibil.com')">
                  Test Phone & Email Masking
                </button>
              </div>

              <!-- Input and Run -->
              <div class="row q-gutter-x-sm items-center">
                <input
                  v-model="adminStore.testInput"
                  type="text"
                  class="sandbox-input col"
                  placeholder="Enter custom query string with identity tokens to test..."
                  @keyup.enter="adminStore.runGuardTest(adminStore.testInput)"
                />
                <button
                  class="apple-pill-primary cursor-pointer text-caption"
                  :disabled="adminStore.isTesting || !adminStore.testInput.trim()"
                  @click="adminStore.runGuardTest(adminStore.testInput)"
                >
                  <q-icon name="play_arrow" size="14px" class="q-mr-xs" />
                  <span>Run GuardLLM</span>
                </button>
              </div>

              <!-- Intercept Result Preview -->
              <div v-if="adminStore.testResult" class="q-mt-sm">
                <div
                  class="sandbox-result-box q-pa-sm rounded-borders"
                  :class="adminStore.testResult.blocked ? 'result-blocked' : 'result-sanitized'"
                >
                  <div class="row items-center q-gutter-x-xs text-weight-bold">
                    <q-icon :name="adminStore.testResult.blocked ? 'gpp_bad' : 'gpp_good'" size="16px" />
                    <span>{{ adminStore.testResult.status }}</span>
                  </div>
                  <div class="q-mt-xs" style="font-size: 11.5px;">
                    <strong>Decision:</strong> {{ adminStore.testResult.reason }}
                  </div>
                  <div v-if="!adminStore.testResult.blocked" class="q-mt-xs" style="font-size: 11.5px;">
                    <strong>Sanitized Payload:</strong> {{ adminStore.testResult.masked_preview }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- TAB 4: System Telemetry -->
          <div v-else-if="activeTab === 'telemetry'">
            <div class="row q-col-gutter-sm">
              <div class="col-12 col-sm-6">
                <div class="apple-metric-tile q-pa-md">
                  <div class="text-weight-bold text-white text-caption q-mb-sm">Core Architecture</div>
                  <div class="q-gutter-y-xs text-caption">
                    <div class="row justify-between"><span class="text-secondary">Platform:</span> <span class="text-white">Integrated KMP + TruCortex</span></div>
                    <div class="row justify-between"><span class="text-secondary">RAG Engine:</span> <span class="text-white">Grounded Extractive (Zero External LLMs)</span></div>
                    <div class="row justify-between"><span class="text-secondary">Vector Store:</span> <span class="text-white">ChromaDB Persistent (all-MiniLM-L6-v2)</span></div>
                    <div class="row justify-between"><span class="text-secondary">Database:</span> <span class="text-white">SQLite 3 (WAL mode)</span></div>
                    <div class="row justify-between"><span class="text-secondary">Gateway Port:</span> <span class="text-blue-4 text-weight-bold">http://localhost:8010</span></div>
                  </div>
                </div>
              </div>
              <div class="col-12 col-sm-6">
                <div class="apple-metric-tile q-pa-md">
                  <div class="text-weight-bold text-white text-caption q-mb-sm">RBAC & Governance Matrix</div>
                  <div class="q-gutter-y-xs text-caption">
                    <div class="row justify-between"><span class="text-secondary">Product Team Clearance:</span> <span class="text-positive">Master (Universal Access)</span></div>
                    <div class="row justify-between"><span class="text-secondary">Infosec Clearance:</span> <span class="text-positive">Master (Universal Access)</span></div>
                    <div class="row justify-between"><span class="text-secondary">Department Clearances:</span> <span class="text-white">Scoped to Owned Vault + Bloomfire</span></div>
                    <div class="row justify-between"><span class="text-secondary">Ingestion Authority:</span> <span class="text-blue-4">Restricted to Admins & Owners</span></div>
                    <div class="row justify-between"><span class="text-secondary">Radar Threshold:</span> <span class="text-amber-5">> 0.65 Cosine Similarity</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Footer -->
        <div class="row items-center justify-between q-px-lg q-py-sm border-top-hairline">
          <div class="text-caption text-secondary" style="font-size: 11px;">
            Authenticated as <strong>{{ authStore.currentUser.full_name }}</strong> ({{ authStore.currentUser.role_title }})
          </div>
          <button class="apple-btn-white cursor-pointer" @click="isOpen = false">
            Done
          </button>
        </div>
      </div>
    </div>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAdminStore, AdminUser } from '../stores/admin'
import { useAuthStore, User } from '../stores/auth'
import { useFoldersStore } from '../stores/folders'
import { Notify } from 'quasar'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', val: boolean): void
}>()

const isOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const adminStore = useAdminStore()
const authStore = useAuthStore()
const foldersStore = useFoldersStore()

const activeTab = ref<'ownership' | 'vaults' | 'guardllm' | 'telemetry'>('ownership')

onMounted(() => {
  adminStore.fetchOverview()
})

const vaultDirectory = [
  {
    name: 'Product Vault',
    ownerRole: 'Senior Product Manager',
    approvedOwners: 'Ananya Iyer (Admin) / Product Lead',
    description: 'Internal score models (TSM-2026), covariate weights, and product roadmaps.',
    path: '/sharepoint_trucortex/Product/',
    icon: 'category',
    color: 'blue-4',
    isRestricted: true,
  },
  {
    name: 'Operations & Bloomfire',
    ownerRole: 'Operations Lead',
    approvedOwners: 'Aarav Sharma (Owner) / Ananya (Admin)',
    description: 'Customer dispute adjudication SOPs, RBI turnaround mandates, and V-KYC protocols.',
    path: '/bloomfire_sops/',
    icon: 'support_agent',
    color: 'green-4',
    isRestricted: false,
  },
  {
    name: 'Technical Architecture',
    ownerRole: 'Systems Architect',
    approvedOwners: 'Chirag Mehta (Owner) / Ananya (Admin)',
    description: 'API Gateway schemas, CIR v5.0 mTLS transport security, and endpoint rate limits.',
    path: '/sharepoint_trucortex/Technical/',
    icon: 'terminal',
    color: 'cyan-4',
    isRestricted: false,
  },
  {
    name: 'Sales Enablement',
    ownerRole: 'Enterprise Sales Lead',
    approvedOwners: 'Priya Patel (Owner) / Ananya (Admin)',
    description: 'CreditVision CMR commercial pitch decks and client SLA enablement collateral.',
    path: '/sharepoint_trucortex/Sales/',
    icon: 'trending_up',
    color: 'amber-5',
    isRestricted: false,
  },
  {
    name: 'Governance & Risk',
    ownerRole: 'Head of Infosec',
    approvedOwners: 'Vikram Malhotra (Security Admin)',
    description: 'Data retention schedules, statutory RBI compliance, and Zero-PII scrubbing mandates.',
    path: '/sharepoint_trucortex/Governance_Risk/',
    icon: 'policy',
    color: 'purple-4',
    isRestricted: true,
  },
  {
    name: 'Finance Rate Cards',
    ownerRole: 'Pricing Controller',
    approvedOwners: 'Farhan Qureshi (Owner) / Ananya (Admin)',
    description: 'Bureau pricing rate cards, volume discount tiers (₹22 - ₹45), and billing meters.',
    path: '/sharepoint_trucortex/Finance/',
    icon: 'payments',
    color: 'yellow-5',
    isRestricted: false,
  },
]

async function toggleOwnerRole(user: AdminUser) {
  const newIsOwner = !user.is_owner
  const newRoleTitle = newIsOwner
    ? `${user.department} Lead (Department Owner)`
    : `${user.department} Analyst (Read-Only)`
  await adminStore.updateUserRole(user.username, user.is_admin, newIsOwner, newRoleTitle)
  await authStore.fetchUsers()
}

function switchUserPersona(u: AdminUser) {
  const matched = authStore.users.find(orig => orig.username === u.username)
  if (matched) {
    authStore.setUser(matched)
    Notify.create({
      type: 'info',
      message: `Active identity switched to ${matched.full_name} (${matched.role_title})`,
      icon: 'person_switch',
      timeout: 2500,
    })
  }
}

async function triggerVaultSync() {
  try {
    const res = await foldersStore.syncAndReindex()
    Notify.create({
      type: 'positive',
      message: `Re-Index Complete: ${res.total_chunks} chunks indexed across ${res.total_files} files in ${res.duration_seconds}s.`,
      icon: 'check_circle',
      timeout: 3000,
    })
  } catch (err: any) {
    Notify.create({
      type: 'negative',
      message: err.message || 'Sync failed.',
    })
  }
}
</script>

<style scoped>
.apple-admin-card {
  width: 100%;
  max-width: 900px;
  height: 90vh;
  max-height: 800px;
  background: rgba(20, 20, 22, 0.96);
  backdrop-filter: blur(36px) saturate(190%);
  -webkit-backdrop-filter: blur(36px) saturate(190%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 28px;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.9);
}

.border-bottom-hairline {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.border-top-hairline {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.admin-shield-container {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(10, 132, 255, 0.12);
  border: 1px solid rgba(10, 132, 255, 0.3);
}

.admin-top-badge {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.04em;
  background: rgba(10, 132, 255, 0.18);
  color: #0A84FF;
  border: 1px solid rgba(10, 132, 255, 0.35);
  padding: 1px 6px;
  border-radius: 4px;
}

.system-health-pill {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 11.5px;
  color: #8E8E93;
}

.status-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #30D158;
  box-shadow: 0 0 8px #30D158;
}

.apple-circle-close {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.apple-circle-close:hover {
  background: rgba(255, 255, 255, 0.14);
  color: #F5F5F7;
}

.apple-metric-tile {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  transition: all 0.2s ease;
}

.apple-metric-tile:hover {
  background: rgba(255, 255, 255, 0.05);
}

.metric-label {
  font-size: 11px;
  font-weight: 500;
}

.metric-val {
  font-size: 22px;
  letter-spacing: -0.02em;
  margin: 1px 0;
}

.metric-sub {
  font-size: 10px;
  color: #636366;
}

/* Apple Segmented Bar */
.apple-segmented-bar {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 3px;
  gap: 4px;
}

.segment-tab {
  background: transparent;
  border: none;
  color: #8E8E93;
  font-size: 12px;
  font-family: inherit;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.segment-tab:hover {
  color: #F5F5F7;
}

.segment-tab-active {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #FFFFFF !important;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

/* Tables */
.apple-table-wrapper {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.apple-table {
  border-collapse: collapse;
}

.apple-table th {
  padding: 10px 14px;
  font-size: 11px;
  font-weight: 600;
  color: #8E8E93;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.apple-table td {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.02);
}

.user-color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dept-chip {
  font-size: 11px;
  color: #8E8E93;
  background: rgba(255, 255, 255, 0.05);
  padding: 2px 7px;
  border-radius: 999px;
}

.clearance-pill {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
}

.pill-admin {
  background: rgba(10, 132, 255, 0.18);
  color: #0A84FF;
  border: 1px solid rgba(10, 132, 255, 0.35);
}

.pill-owner {
  background: rgba(48, 209, 88, 0.15);
  color: #30D158;
  border: 1px solid rgba(48, 209, 88, 0.3);
}

.pill-analyst {
  background: rgba(255, 255, 255, 0.08);
  color: #8E8E93;
}

.pill-blocked {
  font-size: 9.5px;
  font-weight: 700;
  color: #FF453A;
  background: rgba(255, 69, 58, 0.15);
  border: 1px solid rgba(255, 69, 58, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
}

.pill-mask {
  font-size: 9.5px;
  font-weight: 700;
  color: #FF9F0A;
  background: rgba(255, 159, 10, 0.15);
  border: 1px solid rgba(255, 159, 10, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
}

.action-pill-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #F5F5F7;
  font-size: 10.5px;
  font-family: inherit;
  padding: 3px 8px;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.action-pill-btn:hover {
  background: rgba(255, 255, 255, 0.18);
}

.action-pill-switch {
  background: rgba(10, 132, 255, 0.15);
  border: 1px solid rgba(10, 132, 255, 0.3);
  color: #79C0FF;
  font-size: 10.5px;
  font-family: inherit;
  padding: 3px 8px;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.action-pill-switch:hover {
  background: rgba(10, 132, 255, 0.25);
  color: #FFFFFF;
}

.apple-vault-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  transition: all 0.2s ease;
}

.apple-vault-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
}

.vault-owner-tag {
  font-size: 9.5px;
  background: rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  padding: 1px 6px;
  border-radius: 999px;
}

.regex-code {
  font-family: SFMono-Regular, Consolas, Monaco, monospace;
  font-size: 11px;
  color: #64D2FF;
  background: rgba(0, 0, 0, 0.4);
  padding: 2px 6px;
  border-radius: 4px;
}

.guard-sandbox-card {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.sample-token-chip {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #8E8E93;
  font-size: 11px;
  font-family: inherit;
  padding: 3px 10px;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.sample-token-chip:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #F5F5F7;
}

.sandbox-input {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 8px 12px;
  color: #FFFFFF;
  font-size: 12px;
  outline: none;
}

.sandbox-input:focus {
  border-color: #0A84FF;
}

.sandbox-result-box {
  font-size: 12px;
}

.result-blocked {
  background: rgba(255, 69, 58, 0.12);
  border: 1px solid rgba(255, 69, 58, 0.35);
  color: #FF453A;
}

.result-sanitized {
  background: rgba(48, 209, 88, 0.12);
  border: 1px solid rgba(48, 209, 88, 0.35);
  color: #30D158;
}

.apple-pill-refresh {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  font-size: 11px;
  font-family: inherit;
  padding: 4px 10px;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.apple-pill-refresh:hover {
  color: #FFFFFF;
  background: rgba(255, 255, 255, 0.12);
}

.apple-pill-primary {
  background: #0A84FF;
  border: none;
  color: #FFFFFF;
  font-size: 12px;
  font-weight: 600;
  font-family: inherit;
  padding: 6px 14px;
  border-radius: 9999px;
  transition: all 0.2s ease;
}

.apple-pill-primary:hover:not(:disabled) {
  background: #0071E3;
}

.apple-btn-white {
  background: #F5F5F7;
  color: #000000;
  border: none;
  border-radius: 9999px;
  padding: 8px 20px;
  font-size: 13px;
  font-family: inherit;
  font-weight: 600;
  transition: all 0.2s ease;
}

.apple-btn-white:hover {
  background: #FFFFFF;
}

.btn-spinning {
  animation: spin 1s infinite linear;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
