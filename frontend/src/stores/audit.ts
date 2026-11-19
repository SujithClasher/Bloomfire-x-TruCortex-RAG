import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../boot/axios'
import { Notify } from 'quasar'

export interface AuditLogEntry {
  id: number
  timestamp: string
  username: string
  department: string
  query_masked: string
  response_summary: string
  pii_blocked: number
  rbac_blocked: number
  feedback_rating?: 'up' | 'down' | null
  feedback_comment?: string | null
}

export const useAuditStore = defineStore('audit', () => {
  const logs = ref<AuditLogEntry[]>([])
  const isLoading = ref(false)

  async function fetchLogs() {
    isLoading.value = true
    try {
      const res = await api.get('/api/audit/logs', { params: { limit: 100 } })
      if (res.data?.logs) {
        logs.value = res.data.logs
      }
    } catch (err) {
      console.error('Failed to fetch audit logs:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function submitFeedback(auditId: number, rating: 'up' | 'down', comment: string = '') {
    try {
      await api.post(`/api/audit/feedback/${auditId}`, { rating, comment })
      const found = logs.value.find(l => l.id === auditId)
      if (found) {
        found.feedback_rating = rating
        found.feedback_comment = comment
      }
      Notify.create({
        type: 'positive',
        message: `Feedback recorded: ${rating === 'up' ? 'Helpful 👍' : 'Needs Improvement 👎'}`,
        icon: rating === 'up' ? 'thumb_up' : 'thumb_down',
      })
    } catch (err) {
      console.error('Failed to submit feedback:', err)
      Notify.create({
        type: 'negative',
        message: 'Could not record feedback.',
      })
    }
  }

  return {
    logs,
    isLoading,
    fetchLogs,
    submitFeedback,
  }
})

