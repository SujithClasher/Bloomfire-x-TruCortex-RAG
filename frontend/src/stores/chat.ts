import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../boot/axios'
import { useAuthStore } from './auth'
import { Notify } from 'quasar'

export interface Citation {
  file_name: string
  file_type: string
  page_or_slide: string
  owner: string
  department: string
  score_pct: string
}

export interface TraceStep {
  step: number
  name: string
  status: string
  detail: string
  latency_ms: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  pipelineTrace?: TraceStep[]
  piiBlocked?: boolean
  rbacBlocked?: boolean
  auditId?: number
  timestamp: string
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([
    {
      id: 'init-1',
      role: 'assistant',
      content: `### Welcome to the Integrated KMP + TruCortex + Bloomfire Platform 🧠\n\nThis system implements a production-grade **Multi-Format Folder-to-Vector-DB RAG Pipeline** with strict **Department RBAC**, **Regex PII GuardLLM**, and **Change & Conflict Radar** — with **Zero External LLMs** and **Zero API Keys**.\n\nTry testing departmental boundaries or PII leak attempts using the quick prompt chips below!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
  ])

  const isLoading = ref(false)

  async function sendMessage(text: string) {
    if (!text.trim() || isLoading.value) return

    const authStore = useAuthStore()
    const user = authStore.currentUser

    // 1. Add User Message
    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    messages.value.push(userMsg)

    isLoading.value = true

    try {
      const response = await api.post('/api/query/chat', {
        query: text,
        username: user.username,
      })

      const data = response.data
      const botMsg: Message = {
        id: `bot-${Date.now()}`,
        role: 'assistant',
        content: data.answer,
        citations: data.citations || [],
        pipelineTrace: data.pipeline_trace || [],
        piiBlocked: data.pii_blocked || false,
        rbacBlocked: data.rbac_blocked || false,
        auditId: data.audit_id,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      }
      messages.value.push(botMsg)

      if (data.rbac_blocked) {
        Notify.create({
          type: 'warning',
          message: `RBAC Restriction: ${user.department} cannot access requested department data.`,
          caption: 'Access Filtered',
          icon: 'lock',
        })
      }
    } catch (err: any) {
      console.error('Chat query error:', err)
      const detail = err.response?.data?.detail
      let errorContent = 'Unable to reach the enterprise RAG service. Please verify that the backend is running on http://localhost:8010.'
      let trace: TraceStep[] | undefined = undefined
      let piiBlocked = false
      let auditId: number | undefined = undefined

      if (typeof detail === 'object' && detail !== null) {
        errorContent = `> 🛑 **Security Interception (HTTP 422 - Unprocessable Entity)**\n\n${detail.message || JSON.stringify(detail)}`
        trace = detail.pipeline_trace
        piiBlocked = detail.pii_blocked || false
        auditId = detail.audit_id

        if (piiBlocked) {
          Notify.create({
            type: 'negative',
            message: 'GuardLLM PII Guardrail Triggered: Sensitive Identity Token Blocked!',
            caption: 'Zero-PII Enforcement',
            icon: 'gpp_bad',
          })
        }
      } else if (typeof detail === 'string') {
        errorContent = `### Notice\n${detail}`
      }

      messages.value.push({
        id: `err-${Date.now()}`,
        role: 'assistant',
        content: errorContent,
        pipelineTrace: trace,
        piiBlocked: piiBlocked,
        auditId: auditId,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      })
    } finally {
      isLoading.value = false
    }
  }

  function clearChat() {
    messages.value = []
  }

  return {
    messages,
    isLoading,
    sendMessage,
    clearChat,
  }
})
