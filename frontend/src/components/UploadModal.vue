<template>
  <q-dialog v-model="isOpen" persistent>
    <div class="apple-modal-card column q-pa-lg">
      <!-- Modal Header -->
      <div class="row items-center justify-between q-pb-md border-bottom-hairline">
        <div>
          <div class="text-h6 text-weight-bold text-white tracking-tight" style="font-size: 18px;">
            Add Knowledge Document
          </div>
          <div class="text-caption text-secondary" style="font-size: 12px; margin-top: 2px;">
            Natively parses and vectorizes multi-format files into enterprise storage.
          </div>
        </div>
        <button class="apple-circle-close cursor-pointer" :disabled="isUploading" @click="isOpen = false">
          <q-icon name="close" size="14px" />
        </button>
      </div>

      <!-- Modal Body -->
      <div class="q-py-md column q-gutter-y-md">
        <!-- 1. Admin & Department Owner Authorization Banner -->
        <div v-if="authStore.isPlatformAdmin" class="clearance-banner banner-admin row items-center justify-between q-pa-sm rounded-borders">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="shield" size="20px" color="blue-4" />
            <div>
              <div class="text-white text-caption text-weight-bold">Platform Admin Clearance</div>
              <div class="text-secondary" style="font-size: 11px;">
                {{ authStore.currentUser.full_name }} • Universal ingestion clearance across all enterprise vaults.
              </div>
            </div>
          </div>
          <span class="admin-badge">ADMIN</span>
        </div>

        <div v-else-if="authStore.isDepartmentOwner" class="clearance-banner banner-owner row items-center justify-between q-pa-sm rounded-borders">
          <div class="row items-center q-gutter-x-sm">
            <q-icon name="verified" size="20px" color="positive" />
            <div>
              <div class="text-white text-caption text-weight-bold">Approved Department Owner</div>
              <div class="text-secondary" style="font-size: 11px;">
                {{ authStore.currentUser.full_name }} ({{ authStore.currentUser.role_title }}) • Authorized for {{ authStore.currentUser.department }} vault.
              </div>
            </div>
          </div>
          <span class="owner-badge">OWNER</span>
        </div>

        <div v-else class="clearance-banner banner-restricted column q-pa-md rounded-borders">
          <div class="row items-start q-gutter-x-sm no-wrap">
            <q-icon name="lock" size="22px" color="red-4" class="q-mt-xs" />
            <div>
              <div class="text-weight-bold text-white" style="font-size: 13px;">
                Document Ingestion Restricted
              </div>
              <div class="text-secondary q-mt-xs" style="font-size: 11.5px; line-height: 1.45;">
                You are signed in as <strong>{{ authStore.currentUser.full_name }}</strong> ({{ authStore.currentUser.role_title }}).
                To protect data integrity, only <strong>Platform Admins</strong> or <strong>Approved Department Owners</strong> can upload documents into enterprise repositories.
              </div>
            </div>
          </div>
          <div class="row items-center q-gutter-x-xs q-mt-md">
            <button class="apple-pill-btn-switch cursor-pointer" @click="switchToAdmin">
              Switch to Ananya (Platform Admin)
            </button>
            <button class="apple-pill-btn-switch cursor-pointer" @click="switchToLead">
              Switch to Department Owner
            </button>
          </div>
        </div>

        <!-- 2. Target Vault Selection -->
        <div :class="{ 'opacity-disabled': !canUploadCurrent }">
          <label class="apple-field-label">Target Repository</label>
          <q-select
            v-model="targetDepartment"
            :options="filteredDepartmentOptions"
            outlined
            dense
            dark
            emit-value
            map-options
            :disabled="!canUploadCurrent"
            class="apple-select q-mt-xs"
            @update:model-value="onTargetDeptChange"
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

        <!-- 3. File Upload Dropzone -->
        <div :class="{ 'opacity-disabled': !canUploadCurrent }">
          <label class="apple-field-label">Document File</label>
          <q-file
            v-model="selectedFile"
            outlined
            dense
            dark
            :disabled="!canUploadCurrent"
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

        <!-- 4. Who Can View / Clearance Matrix -->
        <div class="clearance-matrix-card q-pa-sm" :class="{ 'opacity-disabled': !canUploadCurrent }">
          <div class="row items-center justify-between q-mb-xs">
            <span class="apple-field-label q-ma-none">Department Clearance</span>
            <button
              class="apple-ai-suggest-btn cursor-pointer row items-center no-wrap"
              :disabled="!selectedFile || isSuggesting || !canUploadCurrent"
              @click="triggerAiSuggestion"
            >
              <q-icon name="auto_awesome" size="12px" class="q-mr-xs" />
              <span>Suggest by AI</span>
            </button>
          </div>

          <!-- Team Pill Toggles -->
          <div class="row q-gutter-xs wrap items-center q-mt-xs">
            <button
              v-for="dept in availableTeams"
              :key="dept.value"
              class="team-toggle-pill cursor-pointer"
              :class="{ 'team-pill-active': selectedTeams.includes(dept.value) }"
              :disabled="!canUploadCurrent"
              @click="toggleTeam(dept.value)"
            >
              <span>{{ dept.label }}</span>
            </button>
          </div>

          <!-- AI Recommendation Note -->
          <div v-if="aiSuggestionNotice" class="ai-recommendation-box q-mt-sm text-caption">
            <q-icon name="smart_toy" size="14px" class="q-mr-xs" />
            <span>{{ aiSuggestionNotice }}</span>
          </div>
        </div>

        <!-- Progress Spinner -->
        <div v-if="isUploading" class="text-center q-py-sm">
          <q-spinner-dots color="blue-4" size="28px" />
          <div class="text-caption text-secondary q-mt-xs">Indexing partitions into vector engine...</div>
        </div>

        <!-- Conflict or Success Alert Banner -->
        <div v-if="uploadResult" class="q-mt-xs">
          <div
            class="result-alert-box q-pa-sm rounded-borders"
            :class="uploadResult.conflicts_detected > 0 ? 'alert-radar' : 'alert-success'"
          >
            <div class="row items-center q-gutter-x-xs text-weight-medium">
              <q-icon :name="uploadResult.conflicts_detected > 0 ? 'radar' : 'check_circle'" size="16px" />
              <span>{{ uploadResult.conflicts_detected > 0 ? 'Radar Divergence Detected' : 'Document Ingested' }}</span>
            </div>
            <div class="text-caption q-mt-xs" style="font-size: 11.5px; opacity: 0.9;">
              Indexed {{ uploadResult.chunks_indexed }} chunks into {{ uploadResult.department }}.
              <span v-if="uploadResult.conflicts_detected > 0">
                {{ uploadResult.conflicts_detected }} semantic policy/data clashes flagged in Radar.
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="row items-center justify-end q-gutter-x-sm border-top-hairline q-pt-md">
        <button class="apple-btn-ghost cursor-pointer" :disabled="isUploading" @click="isOpen = false">
          Cancel
        </button>
        <button
          class="apple-btn-white cursor-pointer"
          :disabled="!selectedFile || isUploading || !canUploadCurrent"
          @click="submitUpload"
        >
          {{ canUploadCurrent ? 'Ingest Document' : 'Ingestion Restricted' }}
        </button>
      </div>
    </div>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useFoldersStore } from '../stores/folders'
import { useConflictsStore } from '../stores/conflicts'
import { api } from '../boot/axios'
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

const authStore = useAuthStore()
const foldersStore = useFoldersStore()
const conflictsStore = useConflictsStore()

const canUploadCurrent = computed(() => {
  return authStore.canUploadDocuments
})

const selectedFile = ref<File | null>(null)
const targetDepartment = ref(authStore.currentUser.department || 'Product')
const isUploading = ref(false)
const isSuggesting = ref(false)
const uploadResult = ref<any>(null)
const aiSuggestionNotice = ref<string | null>(null)

const selectedTeams = ref<string[]>(['Product', authStore.currentUser.department || 'Operations'])

const availableTeams = [
  { label: 'Product', value: 'Product' },
  { label: 'Technical', value: 'Technical' },
  { label: 'Sales', value: 'Sales' },
  { label: 'Operations', value: 'Operations' },
  { label: 'Infosec', value: 'Infosec' },
  { label: 'Finance', value: 'Finance' },
]

const departmentOptions = [
  { label: 'Product Vault (Models & Specs)', value: 'Product', description: 'Internal score algorithms, roadmaps, and PRDs' },
  { label: 'Operations & Bloomfire (SOPs)', value: 'Operations', description: 'Resolution protocols & customer workflows' },
  { label: 'Technical Specs (APIs & Gateways)', value: 'Technical', description: 'REST endpoints, mTLS, and gateway schemas' },
  { label: 'Sales Vault (Pitch & Enablement)', value: 'Sales', description: 'Commercial pitch decks and market enablement' },
  { label: 'Governance & Risk (Compliance)', value: 'Governance_Risk', description: 'Mandatory retention and Zero-PII protocols' },
  { label: 'Finance (Rate Cards & Billing)', value: 'Finance', description: 'Pricing tiers and volume discount matrices' },
  { label: 'Bloomfire SOPs (Cross-Functional)', value: 'Bloomfire', description: 'Shared dispute adjudication workflows' },
]

const filteredDepartmentOptions = computed(() => {
  if (authStore.isPlatformAdmin) {
    return departmentOptions
  }
  if (authStore.isDepartmentOwner) {
    const userDept = authStore.currentUser.department
    if (userDept === 'Operations') {
      return departmentOptions.filter(d => ['Operations', 'Bloomfire'].includes(d.value))
    }
    return departmentOptions.filter(d => [userDept, 'Bloomfire'].includes(d.value))
  }
  return []
})

function switchToAdmin() {
  const adminUser = authStore.users.find(u => u.username === 'ananya')
  if (adminUser) {
    authStore.setUser(adminUser)
    targetDepartment.value = 'Product'
    Notify.create({
      type: 'positive',
      message: 'Active identity switched to Ananya Iyer (Platform Admin)',
      icon: 'shield',
      timeout: 2500,
    })
  }
}

function switchToLead() {
  const dept = authStore.currentUser.department
  const leadUser = authStore.users.find(u => u.department === dept && u.is_owner) || authStore.users.find(u => u.is_owner)
  if (leadUser) {
    authStore.setUser(leadUser)
    targetDepartment.value = leadUser.department
    Notify.create({
      type: 'positive',
      message: `Active identity switched to ${leadUser.full_name} (${leadUser.role_title})`,
      icon: 'verified',
      timeout: 2500,
    })
  }
}

function onTargetDeptChange(val: string) {
  if (!selectedTeams.value.includes(val)) {
    selectedTeams.value.push(val)
  }
}

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
      message: res.data.conflicts_detected > 0 ? 'Document Ingested — Radar Discrepancy Flagged' : 'Document Ingested Successfully',
      timeout: 3000,
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
</script>

<style scoped>
.clearance-banner {
  border-radius: 14px;
  transition: all 0.2s ease;
}

.banner-admin {
  background: rgba(10, 132, 255, 0.12);
  border: 1px solid rgba(10, 132, 255, 0.35);
}

.banner-owner {
  background: rgba(48, 209, 88, 0.1);
  border: 1px solid rgba(48, 209, 88, 0.3);
}

.banner-restricted {
  background: rgba(255, 69, 58, 0.1);
  border: 1px solid rgba(255, 69, 58, 0.3);
}

.admin-badge {
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
  background: rgba(10, 132, 255, 0.25);
  color: #0A84FF;
  border: 1px solid rgba(10, 132, 255, 0.45);
  padding: 2px 7px;
  border-radius: 999px;
}

.owner-badge {
  font-size: 9.5px;
  font-weight: 700;
  letter-spacing: 0.05em;
  background: rgba(48, 209, 88, 0.2);
  color: #30D158;
  border: 1px solid rgba(48, 209, 88, 0.4);
  padding: 2px 7px;
  border-radius: 999px;
}

.apple-pill-btn-switch {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
  font-size: 11px;
  font-weight: 500;
  padding: 5px 12px;
  border-radius: 999px;
  font-family: inherit;
  transition: all 0.2s ease;
}

.apple-pill-btn-switch:hover {
  background: rgba(255, 255, 255, 0.22);
}

.opacity-disabled {
  opacity: 0.35;
  pointer-events: none;
}

.apple-modal-card {
  width: 100%;
  max-width: 500px;
  background: rgba(22, 22, 24, 0.94);
  backdrop-filter: blur(32px) saturate(190%);
  -webkit-backdrop-filter: blur(32px) saturate(190%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  box-shadow: 0 32px 72px rgba(0, 0, 0, 0.85);
}

.border-bottom-hairline {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.border-top-hairline {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.apple-field-label {
  font-size: 11.5px;
  font-weight: 600;
  color: #8E8E93;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
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
  background: rgba(255, 255, 255, 0.15);
  color: #F5F5F7;
}

.clearance-matrix-card {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
}

.team-toggle-pill {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  font-size: 11.5px;
  font-family: inherit;
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
  font-family: inherit;
  transition: all 0.2s ease;
}

.apple-ai-suggest-btn:hover:not(:disabled) {
  background: rgba(10, 132, 255, 0.24);
  color: #FFFFFF;
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
  background: rgba(48, 209, 88, 0.1);
  border: 1px solid rgba(48, 209, 88, 0.3);
  color: #30D158;
}

.alert-radar {
  background: rgba(255, 159, 10, 0.1);
  border: 1px solid rgba(255, 159, 10, 0.3);
  color: #FF9F0A;
}

.apple-btn-ghost {
  background: transparent;
  border: none;
  color: #8E8E93;
  border-radius: 9999px;
  padding: 8px 18px;
  font-size: 13px;
  font-family: inherit;
  transition: color 0.2s ease;
}

.apple-btn-ghost:hover {
  color: #F5F5F7;
}

.apple-btn-white {
  background: #F5F5F7;
  color: #000000;
  border: none;
  border-radius: 9999px;
  padding: 8px 18px;
  font-size: 13px;
  font-family: inherit;
  font-weight: 600;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-btn-white:hover:not(:disabled) {
  background: #FFFFFF;
  transform: scale(1.02);
  box-shadow: 0 4px 14px rgba(255, 255, 255, 0.2);
}

.apple-btn-white:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
</style>
