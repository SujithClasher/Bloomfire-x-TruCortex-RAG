import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../boot/axios'
import { Notify } from 'quasar'

export interface ConflictItem {
  id: number
  source_file: string
  source_dept: string
  source_location?: string
  source_chunk: string
  conflicting_file: string
  conflicting_dept: string
  conflicting_location?: string
  conflicting_chunk?: string
  discrepancy_summary?: string
  similarity: number
  conflict_type: string
  status: 'active' | 'impact_confirmed' | 'dismissed'
  notes?: string
}

export const useConflictsStore = defineStore('conflicts', () => {
  const conflicts = ref<ConflictItem[]>([])
  const isLoading = ref(false)

  const activeCount = computed(() => {
    return conflicts.value.filter(c => c.status === 'active').length
  })

  async function fetchConflicts() {
    isLoading.value = true
    try {
      const res = await api.get('/api/conflicts/list', { params: { status_filter: '' } })
      if (res.data?.conflicts) {
        conflicts.value = res.data.conflicts
      }
    } catch (err) {
      console.error('Failed to fetch conflicts:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function triggerScan() {
    isLoading.value = true
    try {
      const res = await api.post('/api/conflicts/scan')
      await fetchConflicts()
      Notify.create({
        type: 'info',
        message: `Scan complete: ${res.data.scanned_files} files scanned, ${res.data.new_conflicts_found} cross-department overlaps detected.`,
        icon: 'radar',
      })
      return res.data
    } catch (err) {
      console.error('Failed to scan conflicts:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  async function takeAction(id: number, action: 'confirm_impact' | 'dismiss' | 'reopen', notes: string = '') {
    try {
      await api.post(`/api/conflicts/${id}/action`, { action, notes })
      const item = conflicts.value.find(c => c.id === id)
      if (item) {
        item.status = action === 'confirm_impact' ? 'impact_confirmed' : (action === 'dismiss' ? 'dismissed' : 'active')
        item.notes = notes
      }
      Notify.create({
        type: action === 'confirm_impact' ? 'positive' : (action === 'dismiss' ? 'info' : 'warning'),
        message: action === 'confirm_impact' ? '✓ Impact confirmed by governance officer.' : (action === 'dismiss' ? 'Conflict dismissed.' : 'Conflict reopened.'),
        icon: action === 'confirm_impact' ? 'verified' : (action === 'dismiss' ? 'visibility_off' : 'refresh'),
      })
    } catch (err) {
      console.error('Failed to take action on conflict:', err)
    }
  }

  function addConflicts(newItems: ConflictItem[]) {
    conflicts.value.unshift(...newItems)
  }

  return {
    conflicts,
    activeCount,
    isLoading,
    fetchConflicts,
    triggerScan,
    takeAction,
    addConflicts,
  }
})
