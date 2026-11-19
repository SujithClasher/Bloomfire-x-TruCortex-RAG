import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../boot/axios'
import { useAuthStore } from './auth'
import { Notify } from 'quasar'

export interface DocSection {
  index: number
  location: string
  content: string
  is_highlighted: boolean
}

export interface DocPreview {
  file_name: string
  file_type: string
  department: string
  file_size_bytes: number
  total_sections: number
  sections: DocSection[]
  user_department: string
}

export const useViewerStore = defineStore('viewer', () => {
  const isOpen = ref(false)
  const isLoading = ref(false)
  const currentDoc = ref<DocPreview | null>(null)
  const targetLocation = ref<string | null>(null)
  const rbacError = ref<string | null>(null)

  async function openPreview(filePathOrName: string, location?: string) {
    const authStore = useAuthStore()
    isOpen.value = true
    isLoading.value = true
    currentDoc.value = null
    targetLocation.value = location || null
    rbacError.value = null

    try {
      const res = await api.get('/api/documents/preview', {
        params: {
          file_path: filePathOrName,
          username: authStore.currentUser.username,
          target_location: location || undefined,
        }
      })
      currentDoc.value = res.data
    } catch (err: any) {
      console.error('Failed to preview document:', err)
      const status = err.response?.status
      const detail = err.response?.data?.detail || 'Unable to open document preview.'

      if (status === 403) {
        rbacError.value = detail
        Notify.create({
          type: 'warning',
          message: 'Access Restricted by Department RBAC Policy',
          caption: detail,
          icon: 'lock',
        })
      } else {
        Notify.create({
          type: 'negative',
          message: detail,
          icon: 'error',
        })
        isOpen.value = false
      }
    } finally {
      isLoading.value = false
    }
  }

  function close() {
    isOpen.value = false
    currentDoc.value = null
    rbacError.value = null
  }

  function downloadDoc(fileName: string) {
    const authStore = useAuthStore()
    const url = `http://localhost:8010/api/documents/download?file_path=${encodeURIComponent(fileName)}&username=${encodeURIComponent(authStore.currentUser.username)}`
    window.open(url, '_blank')
    Notify.create({
      type: 'info',
      message: `Downloading ${fileName}...`,
      icon: 'download',
    })
  }

  return {
    isOpen,
    isLoading,
    currentDoc,
    targetLocation,
    rbacError,
    openPreview,
    close,
    downloadDoc,
  }
})

