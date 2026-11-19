<template>
  <div class="admin-page-container full-height column text-white select-none">
    <!-- Top Sub-Bar for Admin Dashboard -->
    <div class="admin-dashboard-header q-px-lg q-py-md row items-center justify-between border-bottom-hairline">
      <div class="row items-center q-gutter-x-md">
        <div class="admin-shield-icon-box row items-center justify-center">
          <q-icon name="admin_panel_settings" size="22px" color="blue-4" />
        </div>
        <div>
          <div class="row items-center q-gutter-x-xs leading-none">
            <span class="text-h6 text-weight-bold text-white tracking-tight" style="font-size: 18px;">
              Enterprise Ingestion & Impact Radar Admin Panel
            </span>
            <span class="admin-portal-tag q-ml-xs">MASTER CLEARANCE</span>
          </div>
          <div class="text-caption text-secondary" style="font-size: 11.5px; margin-top: 3px;">
            Authorized Document Ingestion, Cross-Department Conflict Radar, and Knowledge Vault Governance
          </div>
        </div>
      </div>

      <!-- Right Action: Return to Chat Workspace -->
      <div class="row items-center q-gutter-x-sm">
        <div class="admin-auth-pill row items-center q-gutter-x-xs">
          <span class="status-pulse-emerald"></span>
          <span class="text-caption text-white text-weight-medium">
            {{ authStore.currentUser.full_name }}
          </span>
          <span class="text-secondary" style="font-size: 10px;">({{ authStore.currentUser.role_title || 'Platform Admin' }})</span>
        </div>

        <button
          class="apple-pill-secondary cursor-pointer row items-center no-wrap text-caption"
          @click="$emit('switch-to-chat')"
        >
          <q-icon name="arrow_back" size="13px" class="q-mr-xs" />
          <span>Back to Chat</span>
        </button>
      </div>
    </div>

    <!-- Main Scrollable Dashboard Canvas -->
    <div class="col scroll q-pa-lg admin-canvas-scroll">
      <div class="admin-layout-wrapper">
        <!-- Top Metrics Row -->
        <div class="row q-col-gutter-md q-mb-lg">
          <div class="col-12 col-sm-3">
            <div class="apple-metric-card q-pa-md">
              <div class="metric-eyebrow text-secondary">Active Conflicts</div>
              <div class="metric-number text-amber-5 text-weight-bold">{{ conflictsStore.activeCount }}</div>
              <div class="metric-caption text-secondary">Cross-Vault Divergences</div>
            </div>
          </div>
          <div class="col-12 col-sm-3">
            <div class="apple-metric-card q-pa-md">
              <div class="metric-eyebrow text-secondary">Indexed Partitions</div>
              <div class="metric-number text-blue-4 text-weight-bold">{{ totalIndexedChunks }}</div>
              <div class="metric-caption text-secondary">Across Enterprise Repositories</div>
            </div>
          </div>
          <div class="col-12 col-sm-3">
            <div class="apple-metric-card q-pa-md">
              <div class="metric-eyebrow text-secondary">Ingestion Authority</div>
              <div class="metric-number text-positive text-weight-bold">Active</div>
              <div class="metric-caption text-secondary">Platform Admin Clearance</div>
            </div>
          </div>
          <div class="col-12 col-sm-3">
            <div class="apple-metric-card q-pa-md">
              <div class="metric-eyebrow text-secondary">GuardLLM Security</div>
              <div class="metric-number text-purple-4 text-weight-bold">Zero-PII</div>
              <div class="metric-caption text-secondary">Regex PAN/Aadhaar Gate</div>
            </div>
          </div>
        </div>

        <!-- 2-Column Split: LEFT = Ingestion Suite (Add Docs) | RIGHT = Impact Radar -->
        <div class="row q-col-gutter-lg items-start">
          <!-- ======================================================== -->
          <!-- LEFT COLUMN: Document Ingestion Suite (Add Docs)       -->
          <!-- ======================================================== -->
          <div class="col-12 col-lg-5">
            <div class="apple-panel-card q-pa-lg column q-gutter-y-md">
              <!-- Card Header -->
              <div class="row items-center justify-between border-bottom-hairline q-pb-sm">
                <div class="row items-center q-gutter-x-xs">
                  <q-icon name="cloud_upload" size="18px" color="blue-4" />
                  <span class="text-weight-bold text-white text-subtitle2" style="letter-spacing: -0.01em;">
                    Add Enterprise Document
                  </span>
                </div>
                <span class="panel-section-badge">ADMIN ONLY</span>
              </div>

              <!-- 1. Target Repository -->
              <div>
                <label class="apple-field-label">Target Knowledge Repository</label>
                <q-select
                  v-model="targetDepartment"
                  :options="departmentOptions"
                  outlined
                  dense
                  dark
                  emit-value
                  map-options
                  class="apple-select q-mt-xs"
                >
                  <template #selected-item="scope">
                    <span class="text-white text-caption text-weight-medium">{{ scope.opt.label }}</span>
                  </template>
                  <template #option="scope">
                    <q-item v-bind="scope.itemProps" class="apple-select-item">
                      <q-item-section>
                        <q-item-label class="text-weight-medium text-white text-caption">{{ scope.opt.label }}</q-item-label>
                        <q-item-label caption class="text-secondary" style="font-size: 11px;">{{ scope.opt.description }}</q-item-label>
                      </q-item-section>
                    </q-item>
                  </template>
                </q-select>
              </div>

              <!-- 2. File Upload Dropzone -->
              <div>
                <label class="apple-field-label">Document Payload</label>
                <q-file
                  v-model="selectedFile"
                  outlined
                  dense
                  dark
                  accept=".pptx,.docx,.xlsx,.pdf,.md,.txt"
                  class="apple-file-input q-mt-xs"
                  @update:model-value="onFileSelected"
                >
                  <template #prepend>
                    <q-icon name="attach_file" size="18px" color="blue-4" />
                  </template>
                  <template #default>
                    <span v-if="!selectedFile" class="text-secondary text-caption">Choose PowerPoint, Word, Excel, or PDF</span>
                  </template>
                </q-file>
              </div>

              <!-- 3. Department Clearance Matrix -->
              <div class="clearance-matrix-box q-pa-sm rounded-borders">
                <div class="row items-center justify-between q-mb-xs">
                  <span class="apple-field-label q-ma-none">View Clearance</span>
                  <button
                    class="apple-ai-suggest-btn cursor-pointer row items-center no-wrap"
                    :disabled="!selectedFile || isSuggesting"
                    @click="triggerAiSuggestion"
                  >
                    <q-icon name="auto_awesome" size="12px" class="q-mr-xs" />
                    <span>Suggest by AI</span>
                  </button>
                </div>

                <!-- Teams Toggle Pills -->
                <div class="row q-gutter-xs wrap items-center q-mt-xs">
                  <button
                    v-for="dept in availableTeams"
                    :key="dept.value"
                    class="team-toggle-pill cursor-pointer"
                    :class="{ 'team-pill-active': selectedTeams.includes(dept.value) }"
                    @click="toggleTeam(dept.value)"
                  >
                    <span>{{ dept.label }}</span>
                  </button>
                </div>

                <!-- AI Suggestion Notice -->
                <div v-if="aiSuggestionNotice" class="ai-recommendation-box q-mt-sm text-caption">
                  <q-icon name="smart_toy" size="14px" class="q-mr-xs" />
                  <span>{{ aiSuggestionNotice }}</span>
                </div>
              </div>

              <!-- Upload Action Button -->
              <div class="q-pt-xs">
                <button
                  class="apple-btn-white full-width cursor-pointer"
                  :disabled="!selectedFile || isUploading"
                  @click="submitUpload"
                >
                  <q-spinner-dots v-if="isUploading" size="16px" class="q-mr-xs" />
                  <span>{{ isUploading ? 'Vectorizing & Checking Radar...' : 'Ingest Document into Repository' }}</span>
                </button>
              </div>

              <!-- Upload Result Banner -->
              <div v-if="uploadResult" class="q-mt-xs">
                <div
                  class="result-alert-box q-pa-sm rounded-borders"
                  :class="uploadResult.conflicts_detected > 0 ? 'alert-radar' : 'alert-success'"
                >
                  <div class="row items-center q-gutter-x-xs text-weight-bold">
                    <q-icon :name="uploadResult.conflicts_detected > 0 ? 'radar' : 'check_circle'" size="16px" />
                    <span>{{ uploadResult.conflicts_detected > 0 ? 'Radar Divergence Detected' : 'Document Ingested' }}</span>
                  </div>
                  <div class="text-caption q-mt-xs" style="font-size: 11.5px; opacity: 0.95;">
                    Indexed {{ uploadResult.chunks_indexed }} chunks into {{ uploadResult.department }}.
                    <span v-if="uploadResult.conflicts_detected > 0">
                      {{ uploadResult.conflicts_detected }} cross-department policy/data clash(es) flagged in Radar on the right!
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ======================================================== -->
          <!-- RIGHT COLUMN: Impact & Conflict Radar (PROMINENT!)       -->
          <!-- ======================================================== -->
          <div class="col-12 col-lg-7">
            <div class="apple-panel-card q-pa-lg column full-height">
              <!-- Radar Header -->
              <div class="row items-center justify-between border-bottom-hairline q-pb-sm q-mb-md">
                <div class="row items-center q-gutter-x-xs">
                  <q-icon name="radar" size="20px" color="amber-5" />
                  <span class="text-weight-bold text-white text-subtitle2" style="letter-spacing: -0.01em;">
                    Impact & Conflict Radar
                  </span>
                  <span v-if="conflictsStore.activeCount > 0" class="radar-live-count-badge q-ml-xs">
                    {{ conflictsStore.activeCount }} ACTIVE CLASHES
                  </span>
                </div>

                <div class="row items-center q-gutter-x-xs">
                  <button
                    class="apple-pill-secondary cursor-pointer row items-center no-wrap text-caption"
                    :disabled="conflictsStore.isLoading"
                    @click="conflictsStore.triggerScan"
                  >
                    <q-icon name="search" size="13px" class="q-mr-xs" />
                    <span>Run Deep Scan</span>
                  </button>
                </div>
              </div>

              <!-- Radar Status Explainer -->
              <div class="radar-status-bar q-pa-sm rounded-borders q-mb-md row items-center justify-between">
                <div class="row items-center q-gutter-x-xs text-caption text-secondary" style="font-size: 11.5px;">
                  <q-icon name="info" size="14px" color="amber-5" />
                  <span>Cross-checks incoming and modified documents against other departments' ChromaDB vectors (>0.65 similarity).</span>
                </div>
                <div class="row items-center q-gutter-x-xs">
                  <button
                    class="filter-tab-pill cursor-pointer"
                    :class="{ 'filter-tab-active': statusFilter === 'all' }"
                    @click="statusFilter = 'all'"
                  >
                    All ({{ conflictsStore.conflicts.length }})
                  </button>
                  <button
                    class="filter-tab-pill cursor-pointer"
                    :class="{ 'filter-tab-active': statusFilter === 'active' }"
                    @click="statusFilter = 'active'"
                  >
                    Active ({{ conflictsStore.activeCount }})
                  </button>
                </div>
              </div>

              <!-- Conflicts List Area -->
              <div class="col radar-cards-scroll q-gutter-y-md">
                <!-- Loading State -->
                <div v-if="conflictsStore.isLoading" class="text-center q-pa-xl text-secondary">
                  <q-spinner-dots size="28px" color="amber-5" />
                  <div class="text-caption q-mt-sm">Evaluating cross-departmental embeddings in ChromaDB...</div>
                </div>

                <!-- Empty State -->
                <div v-else-if="filteredConflicts.length === 0" class="text-center q-pa-xl">
                  <q-icon name="check_circle" size="38px" color="green-4" />
                  <div class="text-weight-semibold text-white q-mt-sm" style="font-size: 14px;">Radar Clear</div>
                  <div class="text-caption text-secondary q-mt-xs" style="font-size: 12px;">
                    No policy or rate divergences detected across active vaults.
                  </div>
                </div>

                <!-- Live Conflict Cards -->
                <div
                  v-for="item in filteredConflicts"
                  :key="item.id"
                  class="apple-conflict-card rounded-borders"
                  :class="{ 'card-confirmed': item.status === 'impact_confirmed', 'card-dismissed': item.status === 'dismissed' }"
                >
                  <!-- Card Top Row: Type & Similarity -->
                  <div class="row items-center justify-between q-mb-xs">
                    <div class="row items-center q-gutter-x-xs">
                      <span class="conflict-type-pill" :class="getConflictClass(item.conflict_type)">
                        {{ formatConflictType(item.conflict_type) }}
                      </span>
                      <span
                        class="status-indicator-tag"
                        :class="item.status === 'impact_confirmed' ? 'status-confirmed-tag' : (item.status === 'dismissed' ? 'status-dismissed-tag' : 'status-active-tag')"
                      >
                        {{ item.status === 'impact_confirmed' ? '✓ IMPACT CONFIRMED' : (item.status === 'dismissed' ? 'DISMISSED' : 'ACTIVE CLASH') }}
                      </span>
                    </div>

                    <span class="similarity-score-text text-secondary text-caption text-weight-medium">
                      {{ Math.round(item.similarity * 100) }}% semantic overlap
                    </span>
                  </div>

                  <!-- Discrepancy Highlight Box -->
                  <div v-if="item.discrepancy_summary" class="discrepancy-summary-callout q-mb-sm rounded-borders">
                    <div class="row items-center q-gutter-x-xs text-amber-4 text-weight-bold" style="font-size: 11px; letter-spacing: 0.03em;">
                      <q-icon name="warning" size="13px" />
                      <span>CROSS-DEPARTMENT POLICY / DATA DIVERGENCE</span>
                    </div>
                    <div class="text-white text-caption text-weight-medium q-mt-xs" style="font-size: 12.5px; line-height: 1.45;">
                      {{ item.discrepancy_summary }}
                    </div>
                  </div>

                  <!-- Side-by-side Dual Column Clash Quotes -->
                  <div class="row q-col-gutter-sm items-stretch q-my-xs">
                    <!-- Left Column: Source Document -->
                    <div class="col-12 col-md-6 column">
                      <div class="clash-quote-box quote-source col rounded-borders">
                        <div class="row items-center justify-between no-wrap q-mb-xs">
                          <div class="row items-center no-wrap ellipsis text-blue-4 text-weight-bold" style="font-size: 11.5px;">
                            <q-icon name="description" size="13px" class="q-mr-xs" />
                            <span class="ellipsis">{{ item.source_file }}</span>
                          </div>
                          <span class="dept-badge-mini dept-source">{{ item.source_dept }}</span>
                        </div>
                        <div v-if="item.source_location" class="location-label text-caption text-secondary q-mb-xs" style="font-size: 10.5px;">
                          📍 {{ item.source_location }}
                        </div>
                        <div class="conflict-snippet-text">
                          “{{ item.source_chunk }}”
                        </div>
                      </div>
                    </div>

                    <!-- Right Column: Conflicting Document -->
                    <div class="col-12 col-md-6 column">
                      <div class="clash-quote-box quote-conflicting col rounded-borders">
                        <div class="row items-center justify-between no-wrap q-mb-xs">
                          <div class="row items-center no-wrap ellipsis text-red-4 text-weight-bold" style="font-size: 11.5px;">
                            <q-icon name="warning_amber" size="13px" class="q-mr-xs" />
                            <span class="ellipsis">{{ item.conflicting_file }}</span>
                          </div>
                          <span class="dept-badge-mini dept-clash">{{ item.conflicting_dept }}</span>
                        </div>
                        <div v-if="item.conflicting_location" class="location-label text-caption text-secondary q-mb-xs" style="font-size: 10.5px;">
                          📍 {{ item.conflicting_location }}
                        </div>
                        <div class="conflict-snippet-text conflicting-snippet">
                          “{{ item.conflicting_chunk }}”
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Action Buttons (Confirm Impact / Dismiss / Reopen) -->
                  <div v-if="item.status === 'active'" class="row items-center justify-between q-mt-sm q-pt-xs border-top-hairline">
                    <div class="text-caption text-secondary" style="font-size: 11px;">
                      Action: Governance Review Required
                    </div>
                    <div class="row items-center q-gutter-x-sm">
                      <button
                        class="apple-card-action-btn btn-dismiss cursor-pointer"
                        @click="conflictsStore.takeAction(item.id, 'dismiss')"
                      >
                        ✕ Dismiss Divergence
                      </button>
                      <button
                        class="apple-card-action-btn btn-confirm cursor-pointer"
                        @click="conflictsStore.takeAction(item.id, 'confirm_impact')"
                      >
                        ✓ Confirm Impact
                      </button>
                    </div>
                  </div>

                  <!-- Impact Confirmed State -->
                  <div v-else-if="item.status === 'impact_confirmed'" class="row items-center justify-between q-mt-sm q-pt-xs border-top-hairline">
                    <div class="row items-center q-gutter-x-xs text-positive text-caption text-weight-medium">
                      <q-icon name="verified" size="15px" />
                      <span>✓ Impact Confirmed: Escalated for Risk Audit & Executive Alignment</span>
                    </div>
                    <button
                      class="apple-card-action-btn btn-reopen cursor-pointer"
                      @click="conflictsStore.takeAction(item.id, 'reopen')"
                    >
                      Reopen
                    </button>
                  </div>

                  <!-- Dismissed State -->
                  <div v-else class="row items-center justify-between q-mt-sm q-pt-xs border-top-hairline">
                    <div class="row items-center q-gutter-x-xs text-secondary text-caption">
                      <q-icon name="visibility_off" size="13px" />
                      <span>Dismissed as acceptable divergence / false positive</span>
                    </div>
                    <button
                      class="apple-card-action-btn btn-reopen cursor-pointer"
                      @click="conflictsStore.takeAction(item.id, 'reopen')"
                    >
                      Reopen
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ======================================================== -->
        <!-- BOTTOM SECTION: Enterprise Vaults Inventory             -->
        <!-- ======================================================== -->
        <div class="q-mt-xl">
          <div class="row items-center justify-between q-mb-md">
            <div>
              <div class="text-weight-bold text-white text-subtitle1" style="letter-spacing: -0.01em;">
                Enterprise Knowledge Vaults Directory
              </div>
              <div class="text-caption text-secondary" style="font-size: 11.5px;">
                Physical repositories stored in <code>/data_repositories/</code> with verified RBAC locks.
              </div>
            </div>

            <button
              class="apple-pill-secondary cursor-pointer row items-center no-wrap text-caption"
              :disabled="foldersStore.isLoading"
              @click="handleSyncAll"
            >
              <q-icon name="sync" size="13px" class="q-mr-xs" :class="{ 'btn-spinning': foldersStore.isLoading }" />
              <span>Sync All Vaults</span>
            </button>
          </div>

          <!-- Vaults Grid -->
          <div class="row q-col-gutter-sm">
            <div v-for="vault in vaultCards" :key="vault.name" class="col-12 col-sm-6 col-md-4">
              <div class="apple-vault-card-alt q-pa-md rounded-borders">
                <div class="row items-center justify-between q-mb-xs">
                  <div class="row items-center q-gutter-x-xs">
                    <q-icon :name="vault.icon" size="18px" :color="vault.color" />
                    <span class="text-weight-bold text-white text-caption">{{ vault.name }}</span>
                  </div>
                  <span class="vault-owner-chip">{{ vault.department }}</span>
                </div>
                <div class="text-caption text-secondary q-mb-sm" style="font-size: 11px;">
                  {{ vault.description }}
                </div>
                <div class="row items-center justify-between text-caption text-secondary border-top-hairline q-pt-xs" style="font-size: 10.5px;">
                  <span>Files:</span>
                  <span class="text-white">{{ vault.files }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useConflictsStore } from '../stores/conflicts'
import { useFoldersStore } from '../stores/folders'
import { api } from '../boot/axios'
import { Notify } from 'quasar'

defineEmits<{
  (e: 'switch-to-chat'): void
}>()

const authStore = useAuthStore()
const conflictsStore = useConflictsStore()
const foldersStore = useFoldersStore()

const statusFilter = ref<'all' | 'active'>('active')

const selectedFile = ref<File | null>(null)
const targetDepartment = ref('Product')
const isUploading = ref(false)
const isSuggesting = ref(false)
const uploadResult = ref<any>(null)
const aiSuggestionNotice = ref<string | null>(null)

const selectedTeams = ref<string[]>(['Product', 'Technical', 'Operations'])

const totalIndexedChunks = ref(172)

onMounted(async () => {
  await conflictsStore.fetchConflicts()
  await foldersStore.fetchTree()
})

const filteredConflicts = computed(() => {
  if (statusFilter.value === 'active') {
    return conflictsStore.conflicts.filter(c => c.status === 'active')
  }
  return conflictsStore.conflicts
})

const availableTeams = [
  { label: 'Product', value: 'Product' },
  { label: 'Technical', value: 'Technical' },
  { label: 'Sales', value: 'Sales' },
  { label: 'Operations', value: 'Operations' },
  { label: 'Infosec', value: 'Infosec' },
  { label: 'Finance', value: 'Finance' },
]

const departmentOptions = [
  { label: 'Product Vault (Models & Roadmap)', value: 'Product', description: 'Internal score algorithms (TSM-2026), covariate matrices, roadmaps' },
  { label: 'Operations Vault (Dispute SOPs & KYC)', value: 'Operations', description: 'Resolution protocols, KYC workflows, bureau correction turnarounds' },
  { label: 'Technical Specs (APIs & mTLS Gateway)', value: 'Technical', description: 'REST endpoints, mTLS architecture, and gateway schemas' },
  { label: 'Sales Vault (Pitch & Commercial Tiers)', value: 'Sales', description: 'Commercial pitch decks, rank scale rules, and enablement' },
  { label: 'Governance & Risk (Statutory Compliance)', value: 'Governance_Risk', description: 'Mandatory data retention protocols and Zero-PII policies' },
  { label: 'Finance (Rate Cards & Billing)', value: 'Finance', description: 'Bureau pricing tiers, discount structures, and volume meters' },
]

const vaultCards = [
  {
    name: 'Product Vault',
    department: 'Product',
    description: 'Internal score methodology (TSM-2026 GBDT), covariate matrices, roadmaps.',
    files: '2 Files (.pptx, .docx)',
    icon: 'category',
    color: 'blue-4',
  },
  {
    name: 'Operations Vault',
    department: 'Operations',
    description: 'Customer dispute resolution SOPs, KYC mismatch escalation, and bureau correction protocols.',
    files: '3 Files (.docx, .pdf, .md)',
    icon: 'support_agent',
    color: 'green-4',
  },
  {
    name: 'Technical Architecture',
    department: 'Technical',
    description: 'API Gateway endpoints schema, CIR v5.0 mTLS transport security specs.',
    files: '2 Files (.pdf, .xlsx)',
    icon: 'terminal',
    color: 'cyan-4',
  },
  {
    name: 'Sales Enablement',
    department: 'Sales',
    description: 'CreditVision CMR commercial pitch decks and rank scale governance rules.',
    files: '1 File (.pptx)',
    icon: 'trending_up',
    color: 'amber-5',
  },
  {
    name: 'Governance & Risk',
    department: 'Governance_Risk',
    description: 'Statutory data retention schedules, Zero-PII scrubbing and audit rules.',
    files: '1 File (.docx)',
    icon: 'policy',
    color: 'purple-4',
  },
  {
    name: 'Finance Rate Cards',
    department: 'Finance',
    description: 'Bureau pricing rate cards, volume discount tiers (₹22 - ₹45), and billing meters.',
    files: '1 File (.xlsx)',
    icon: 'payments',
    color: 'yellow-5',
  },
]

function onFileSelected(file: File | null) {
  if (file) {
    triggerAiSuggestion()
  }
}

function toggleTeam(val: string) {
  if (selectedTeams.value.includes(val)) {
    selectedTeams.value = selectedTeams.value.filter(t => t !== val)
  } else {
    selectedTeams.value.push(val)
  }
}

async function triggerAiSuggestion() {
  if (!selectedFile.value) return
  isSuggesting.value = true
  try {
    const res = await api.post('/api/upload/suggest-permissions', {
      file_name: selectedFile.value.name,
      target_department: targetDepartment.value,
      content_snippet: selectedFile.value.name,
    })

    if (res.data?.suggested_departments) {
      selectedTeams.value = Array.from(new Set([...res.data.suggested_departments, 'Product']))
      aiSuggestionNotice.value = res.data.reason
    }
  } catch (err) {
    console.warn('AI suggestion note:', err)
  } finally {
    isSuggesting.value = false
  }
}

async function submitUpload() {
  if (!selectedFile.value) return

  isUploading.value = true
  uploadResult.value = null

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('username', authStore.currentUser.username)
  formData.append('target_department', targetDepartment.value)
  formData.append('allowed_departments', selectedTeams.value.join(','))

  try {
    const res = await api.post('/api/upload/document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    uploadResult.value = res.data
    await foldersStore.fetchTree()
    await conflictsStore.fetchConflicts()

    Notify.create({
      type: res.data.conflicts_detected > 0 ? 'warning' : 'positive',
      message: res.data.conflicts_detected > 0 ? 'Document Ingested — Radar Divergence Flagged!' : 'Document Ingested Successfully',
      icon: res.data.conflicts_detected > 0 ? 'radar' : 'check_circle',
      timeout: 3500,
    })
  } catch (err: any) {
    const msg = err.response?.data?.detail || 'Failed to ingest file.'
    Notify.create({
      type: 'negative',
      message: msg,
    })
  } finally {
    isUploading.value = false
  }
}

async function handleSyncAll() {
  try {
    const res = await foldersStore.syncAndReindex()
    Notify.create({
      type: 'positive',
      message: `Vault Sync Complete: ${res.total_chunks} chunks indexed across ${res.total_files} files in ${res.duration_seconds}s.`,
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

function formatConflictType(type: string): string {
  if (type === 'pricing_mismatch' || type === 'data_overlap') return 'Pricing Floor Mismatch'
  if (type === 'sla_architecture_clash' || type === 'policy_conflict') return 'SLA & Architecture Clash'
  if (type === 'confidentiality_breach') return 'Proprietary Disclosure Clash'
  if (type === 'version_mismatch') return 'Version Mismatch'
  return type
}

function getConflictClass(type: string): string {
  if (type === 'pricing_mismatch' || type === 'data_overlap') return 'type-pricing'
  if (type === 'sla_architecture_clash' || type === 'policy_conflict') return 'type-sla'
  if (type === 'confidentiality_breach') return 'type-confidential'
  return 'type-version'
}
</script>

<style scoped>
.admin-page-container {
  background: #000000;
  overflow: hidden;
}

.admin-dashboard-header {
  height: 64px;
  background: rgba(22, 22, 24, 0.85);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
}

.border-bottom-hairline {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.border-top-hairline {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.admin-shield-icon-box {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(10, 132, 255, 0.12);
  border: 1px solid rgba(10, 132, 255, 0.3);
}

.admin-portal-tag {
  font-size: 9.5px;
  font-weight: 700;
  background: rgba(10, 132, 255, 0.2);
  color: #0A84FF;
  border: 1px solid rgba(10, 132, 255, 0.4);
  padding: 1px 6px;
  border-radius: 4px;
}

.admin-auth-pill {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 9999px;
}

.status-pulse-emerald {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #30D158;
  box-shadow: 0 0 8px #30D158;
}

.apple-btn-white {
  background: #F5F5F7;
  color: #000000;
  border: none;
  border-radius: 9999px;
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-btn-white:hover:not(:disabled) {
  background: #FFFFFF;
  transform: scale(1.02);
}

.apple-btn-white:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.admin-canvas-scroll {
  overflow-y: auto;
}

.admin-layout-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* Metric Cards */
.apple-metric-card {
  background: rgba(22, 22, 24, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  transition: all 0.2s ease;
}

.apple-metric-card:hover {
  background: rgba(22, 22, 24, 0.95);
  border-color: rgba(255, 255, 255, 0.15);
}

.metric-eyebrow {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-number {
  font-size: 26px;
  letter-spacing: -0.02em;
  margin: 2px 0;
}

.metric-caption {
  font-size: 11px;
}

/* Panel Cards */
.apple-panel-card {
  background: rgba(22, 22, 24, 0.78);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 22px;
}

.panel-section-badge {
  font-size: 9px;
  font-weight: 700;
  background: rgba(10, 132, 255, 0.18);
  color: #0A84FF;
  padding: 2px 6px;
  border-radius: 4px;
}

.apple-field-label {
  font-size: 11.5px;
  font-weight: 600;
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  display: block;
}

.clearance-matrix-box {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.team-toggle-pill {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  font-size: 11.5px;
  padding: 4px 10px;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.team-toggle-pill:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #F5F5F7;
}

.team-pill-active {
  background: rgba(10, 132, 255, 0.18) !important;
  border-color: #0A84FF !important;
  color: #F5F5F7 !important;
}

.apple-ai-suggest-btn {
  background: rgba(10, 132, 255, 0.12);
  border: 1px solid rgba(10, 132, 255, 0.28);
  color: #79C0FF;
  border-radius: 999px;
  font-size: 11px;
  padding: 2px 8px;
  transition: all 0.2s ease;
}

.ai-recommendation-box {
  background: rgba(10, 132, 255, 0.08);
  border: 1px solid rgba(10, 132, 255, 0.2);
  border-radius: 8px;
  padding: 6px 10px;
  color: #D1E7FF;
}

.result-alert-box {
  font-size: 12px;
}

.alert-success {
  background: rgba(48, 209, 88, 0.12);
  border: 1px solid rgba(48, 209, 88, 0.3);
  color: #30D158;
}

.alert-radar {
  background: rgba(255, 159, 10, 0.15);
  border: 1px solid rgba(255, 159, 10, 0.4);
  color: #FF9F0A;
}

/* Radar Styles */
.radar-live-count-badge {
  font-size: 9.5px;
  font-weight: 700;
  background: rgba(255, 159, 10, 0.2);
  color: #FF9F0A;
  border: 1px solid rgba(255, 159, 10, 0.4);
  padding: 2px 7px;
  border-radius: 999px;
  letter-spacing: 0.03em;
}

.radar-status-bar {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.filter-tab-pill {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 999px;
  transition: all 0.2s ease;
}

.filter-tab-active {
  background: rgba(255, 255, 255, 0.16) !important;
  color: #FFFFFF !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
}

.radar-cards-scroll {
  overflow-y: auto;
  max-height: 640px;
  padding-right: 4px;
}

.radar-cards-scroll::-webkit-scrollbar {
  width: 5px;
}

.radar-cards-scroll::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 999px;
}

.apple-conflict-card {
  background: rgba(22, 22, 24, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 14px 16px;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-conflict-card:hover {
  background: rgba(30, 30, 34, 0.95);
  border-color: rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}

.card-confirmed {
  border-left: 4px solid #30D158 !important;
  background: rgba(48, 209, 88, 0.05) !important;
}

.card-dismissed {
  opacity: 0.55;
  border-left: 4px solid #636366 !important;
}

.conflict-type-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.type-policy,
.type-sla { background: rgba(255, 69, 58, 0.2); color: #FF453A; border: 1px solid rgba(255, 69, 58, 0.4); }
.type-data,
.type-pricing { background: rgba(255, 159, 10, 0.2); color: #FF9F0A; border: 1px solid rgba(255, 159, 10, 0.4); }
.type-version,
.type-confidential { background: rgba(191, 90, 242, 0.2); color: #BF5AF2; border: 1px solid rgba(191, 90, 242, 0.4); }

.status-indicator-tag {
  font-size: 9.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
}

.status-active-tag {
  background: rgba(255, 159, 10, 0.15);
  color: #FF9F0A;
  border: 1px solid rgba(255, 159, 10, 0.3);
}

.status-confirmed-tag {
  background: rgba(48, 209, 88, 0.18);
  color: #30D158;
  border: 1px solid rgba(48, 209, 88, 0.35);
}

.status-dismissed-tag {
  background: rgba(255, 255, 255, 0.08);
  color: #8E8E93;
}

.discrepancy-summary-callout {
  background: rgba(255, 159, 10, 0.10);
  border: 1px solid rgba(255, 159, 10, 0.28);
  border-radius: 10px;
  padding: 10px 12px;
}

.clash-quote-box {
  background: rgba(0, 0, 0, 0.48);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 10px 12px;
  height: 100%;
}

.quote-source {
  border-left: 3px solid #0A84FF;
}

.quote-conflicting {
  border-left: 3px solid #FF453A;
}

.dept-badge-mini {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
}

.dept-source {
  background: rgba(10, 132, 255, 0.16);
  color: #79C0FF;
  border: 1px solid rgba(10, 132, 255, 0.3);
}

.dept-clash {
  background: rgba(255, 69, 58, 0.16);
  color: #FF857D;
  border: 1px solid rgba(255, 69, 58, 0.3);
}

.conflict-snippet-text {
  font-style: italic;
  font-size: 11.5px;
  line-height: 1.5;
  color: #E5E5EA;
}

.conflicting-snippet {
  color: #FFD1CD !important;
}

.apple-card-action-btn {
  font-size: 11.5px;
  font-family: inherit;
  padding: 6px 16px;
  border-radius: 9999px;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  letter-spacing: -0.01em;
}

.btn-confirm {
  background: #30D158 !important;
  color: #000000 !important;
  border: none !important;
  box-shadow: 0 2px 10px rgba(48, 209, 88, 0.35);
}

.btn-confirm:hover {
  background: #34E061 !important;
  box-shadow: 0 4px 16px rgba(48, 209, 88, 0.55);
  transform: translateY(-1px);
}

.btn-dismiss {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.18) !important;
  color: #E5E5EA !important;
}

.btn-dismiss:hover {
  background: rgba(255, 255, 255, 0.16) !important;
  color: #FFFFFF !important;
  transform: translateY(-1px);
}

.btn-reopen {
  background: transparent !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  color: #8E8E93 !important;
  font-size: 11px !important;
  padding: 4px 12px !important;
}

.btn-reopen:hover {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #FFFFFF !important;
}

.apple-pill-secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #F5F5F7;
  padding: 5px 12px;
  border-radius: 9999px;
  font-family: inherit;
  transition: all 0.2s ease;
}

.apple-pill-secondary:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.15);
}

.apple-vault-card-alt {
  background: rgba(22, 22, 24, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s ease;
}

.apple-vault-card-alt:hover {
  background: rgba(22, 22, 24, 0.85);
  border-color: rgba(255, 255, 255, 0.14);
}

.vault-owner-chip {
  font-size: 9.5px;
  background: rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  padding: 1px 6px;
  border-radius: 4px;
}

.btn-spinning {
  animation: spin 1s infinite linear;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

:deep(.apple-select .q-field__control),
:deep(.apple-file-input .q-field__control) {
  background: rgba(255, 255, 255, 0.04) !important;
  border: 1px solid rgba(255, 255, 255, 0.10) !important;
  border-radius: 12px !important;
  min-height: 42px;
  color: #F5F5F7;
}

:deep(.apple-select .q-field__control:hover),
:deep(.apple-file-input .q-field__control:hover) {
  border-color: rgba(255, 255, 255, 0.20) !important;
}

:deep(.apple-select-item) {
  border-radius: 8px;
  margin: 2px 4px;
}

:deep(.apple-select-item:hover) {
  background: rgba(255, 255, 255, 0.08);
}
</style>
