import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../boot/axios'
import { useAuthStore } from './auth'

export interface FileNode {
  name: string
  type: 'file' | 'folder'
  department: string
  accessible: boolean
  file_type?: string
  size_bytes?: number
  path: string
  children?: FileNode[]
  file_count?: number
}

export const useFoldersStore = defineStore('folders', () => {
  const tree = ref<FileNode[]>([])
  const isLoading = ref(false)

  async function fetchTree() {
    const authStore = useAuthStore()
    isLoading.value = true
    try {
      const res = await api.get('/api/folders/tree', {
        params: { username: authStore.currentUser.username }
      })
      if (res.data?.tree) {
        tree.value = res.data.tree
      }
    } catch (err) {
      console.error('Failed to fetch folder tree:', err)
    } finally {
      isLoading.value = false
    }
  }

  async function syncAndReindex() {
    isLoading.value = true
    try {
      const res = await api.post('/api/sync/reindex')
      await fetchTree()
      return res.data
    } catch (err) {
      console.error('Failed to reindex repositories:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    tree,
    isLoading,
    fetchTree,
    syncAndReindex,
  }
})
