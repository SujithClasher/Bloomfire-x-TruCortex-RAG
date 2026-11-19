import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../boot/axios'
import { Notify } from 'quasar'

export interface AdminUser {
  id: number
  username: string
  department: string
  full_name: string
  role_title: string
  is_admin: boolean
  is_owner: boolean
}

export interface GuardRule {
  rule_name: string
  pattern: string
  action: string
  severity: string
  description: string
}

export interface AdminOverview {
  status: string
  system: {
    name: string
    version: string
    port: number
    architecture: string
    vector_store: string
    database: string
  }
  metrics: {
    total_users: number
    platform_admins: number
    department_owners: number
    analysts: number
    total_audit_events: number
    pii_intercepts: number
    rbac_interceptions: number
  }
  users: AdminUser[]
  guard_rules: GuardRule[]
}

export const useAdminStore = defineStore('admin', () => {
  const isOpen = ref(false)
  const isLoading = ref(false)
  const overview = ref<AdminOverview | null>(null)
  const testInput = ref('')
  const testResult = ref<any>(null)
  const isTesting = ref(false)

  async function fetchOverview() {
    isLoading.value = true
    try {
      const res = await api.get('/api/admin/overview')
      overview.value = res.data
    } catch (err: any) {
      console.error('Failed to fetch admin overview:', err)
      Notify.create({
        type: 'negative',
        message: 'Could not load Admin Console overview.',
        icon: 'error',
      })
    } finally {
      isLoading.value = false
    }
  }

  async function updateUserRole(username: string, isAdmin: boolean, isOwner: boolean, roleTitle: string) {
    try {
      const res = await api.post('/api/admin/users/update-role', {
        username,
        is_admin: isAdmin,
        is_owner: isOwner,
        role_title: roleTitle,
      })
      Notify.create({
        type: 'positive',
        message: res.data.message || `Updated clearance for ${username}.`,
        icon: 'check_circle',
      })
      await fetchOverview()
      return res.data
    } catch (err: any) {
      console.error('Role update failed:', err)
      Notify.create({
        type: 'negative',
        message: err.response?.data?.detail || 'Failed to update user role.',
      })
    }
  }

  async function runGuardTest(text: string) {
    if (!text.trim()) return
    isTesting.value = true
    testResult.value = null
    try {
      const res = await api.post('/api/admin/test-guardllm', { text })
      testResult.value = res.data
    } catch (err: any) {
      console.error('Guard test error:', err)
    } finally {
      isTesting.value = false
    }
  }

  return {
    isOpen,
    isLoading,
    overview,
    testInput,
    testResult,
    isTesting,
    fetchOverview,
    updateUserRole,
    runGuardTest,
  }
})
