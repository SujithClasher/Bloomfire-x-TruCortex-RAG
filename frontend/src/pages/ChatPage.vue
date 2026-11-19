<template>
  <div class="chat-canvas-container full-height column relative-position">
    <!-- Messages Scroll Area -->
    <div ref="scrollContainer" class="col scroll messages-scroll-viewport">
      <!-- 1. Apple Hero Welcome State (When Chat is Empty / Starter State) -->
      <div v-if="isWelcomeState" class="hero-welcome-container column items-center justify-center">
        <!-- TruCortex x Bloomfire KMP Platform Badge -->
        <div class="kmp-platform-pill row items-center q-gutter-x-xs q-mb-sm">
          <span class="apple-status-dot-mini q-mr-xs"></span>
          <span class="text-weight-bold tracking-tight">TruCortex x Bloomfire KMP</span>
        </div>

        <!-- Logo Hero -->
        <div class="hero-logo-container q-mb-md">
          <img src="/icon.png" alt="TruCortex" class="hero-logo-img" />
        </div>

        <!-- Eyebrow label -->
        <div class="hero-eyebrow q-mb-xs">
          {{ heroEyebrow }}
        </div>

        <!-- Headline Greeting -->
        <h2 class="hero-headline q-ma-none text-center">
          How can I help today?
        </h2>
        <p class="hero-subheadline text-center q-mt-xs q-mb-xl">
          Unified enterprise intelligence across TruCortex models, Bloomfire SOPs, and multi-vault architectures.
        </p>

        <!-- 3 Sleek Starter Prompt Cards Tailored to Active Role -->
        <div class="starter-cards-grid full-width">
          <div
            v-for="(card, idx) in activeDepartmentPrompts"
            :key="idx"
            class="starter-prompt-card column justify-between cursor-pointer"
            @click="runPrompt(card.query)"
          >
            <div class="card-prompt-text text-weight-medium">
              {{ card.title }}
            </div>
            <div class="row items-center justify-between q-mt-sm">
              <span class="card-vault-tag text-caption">{{ card.vault }}</span>
              <q-icon name="arrow_forward" size="14px" class="card-arrow-icon" />
            </div>
          </div>
        </div>
      </div>

      <!-- 2. Apple Editorial Conversation Stream (Max Width 780px Centered) -->
      <div v-else class="conversation-stream-wrapper q-pa-md">
        <div v-for="msg in displayMessages" :key="msg.id" class="message-row q-mb-xl">
          <!-- User Message Bubble (Right-Aligned Apple Blue) -->
          <div v-if="msg.role === 'user'" class="row justify-end">
            <div class="apple-user-bubble">
              <div class="user-bubble-text">{{ msg.content }}</div>
            </div>
          </div>

          <!-- Assistant Response (Left-Aligned with Logo Avatar, like Claude) -->
          <div v-else class="assistant-response-container">
            <!-- Avatar + Label Row (like Claude's icon-per-response) -->
            <div class="row items-center no-wrap q-gutter-x-sm q-mb-sm">
              <div class="ai-avatar-bubble">
                <img src="/icon.png" alt="TruCortex" class="ai-avatar-icon" />
              </div>
              <div class="row items-center q-gutter-x-xs">
                <span
                  class="editorial-dot"
                  :class="msg.piiBlocked || msg.rbacBlocked ? 'dot-crimson' : 'dot-emerald'"
                ></span>
                <span class="editorial-label text-weight-medium">
                  {{ getAssistantLabel(msg) }}
                </span>
                <span v-if="hasPiiMask(msg.content)" class="pii-masked-pill q-ml-xs">
                  PII Masked
                </span>
              </div>
            </div>

            <!-- RBAC or GuardLLM Security Alert Card -->
            <div v-if="msg.rbacBlocked || msg.piiBlocked" class="apple-crimson-card q-pa-md q-my-sm">
              <div class="row items-center q-gutter-x-sm q-mb-xs">
                <q-icon name="lock" size="18px" color="red-4" />
                <span class="text-weight-semibold text-white" style="font-size: 14px;">
                  {{ msg.piiBlocked ? 'Security Interception (Zero-PII Guardrail)' : 'Access Restricted by Role Policy' }}
                </span>
              </div>
              <div class="crimson-card-body text-caption">
                {{ cleanErrorMessage(msg.content) }}
              </div>
            </div>

            <!-- Clean Editorial Markdown Content -->
            <div v-else class="apple-markdown q-mt-xs">
              <div v-html="renderMarkdown(msg.content)"></div>
            </div>

            <!-- Horizontal Tactile Citation Pills (No Match % Numbers) -->
            <div v-if="msg.citations && msg.citations.length > 0" class="citations-container q-mt-md">
              <div class="citations-label q-mb-xs">Sources</div>
              <div class="row q-gutter-xs wrap items-center">
                <button
                  v-for="(cit, cIdx) in msg.citations"
                  :key="cIdx"
                  class="apple-citation-pill row items-center no-wrap cursor-pointer"
                  @click="openDocumentPreview(cit.file_name, cit.page_or_slide)"
                >
                  <q-icon :name="getFileIcon(cit.file_type)" size="14px" class="q-mr-xs citation-icon" />
                  <span class="citation-filename ellipsis">{{ cit.file_name }}</span>
                  <span v-if="cit.page_or_slide" class="citation-loc q-ml-xs text-secondary">
                    · {{ formatLocation(cit.page_or_slide) }}
                  </span>
                </button>
              </div>
            </div>

            <!-- Subtle Feedback Action Icons (Bottom) -->
            <div v-if="!msg.rbacBlocked && !msg.piiBlocked" class="row items-center q-gutter-x-xs q-mt-sm feedback-tray">
              <button
                class="feedback-btn cursor-pointer"
                :class="{ 'feedback-active': ratedMap[msg.id] === 'up' }"
                @click="rateResponse(msg, 'up')"
              >
                <q-icon name="thumb_up" size="13px" />
                <q-tooltip class="bg-black text-caption">Helpful</q-tooltip>
              </button>
              <button
                class="feedback-btn cursor-pointer"
                :class="{ 'feedback-active': ratedMap[msg.id] === 'down' }"
                @click="rateResponse(msg, 'down')"
              >
                <q-icon name="thumb_down" size="13px" />
                <q-tooltip class="bg-black text-caption">Needs refinement</q-tooltip>
              </button>
            </div>
          </div>
        </div>

        <!-- Claude-Style Thinking Indicator -->
        <div v-if="chatStore.isLoading" class="assistant-response-container q-mb-xl">
          <div class="row items-center no-wrap q-gutter-x-sm q-mb-sm">
            <div class="ai-avatar-bubble ai-avatar-pulse">
              <img src="/icon.png" alt="TruCortex" class="ai-avatar-icon" />
            </div>
            <div class="row items-center q-gutter-x-xs">
              <span class="editorial-dot dot-emerald pulse-dot"></span>
              <span class="editorial-label text-weight-medium">TruCortex x Bloomfire</span>
            </div>
          </div>

          <!-- Minimal Claude-style thinking text -->
          <div class="claude-thinking-block q-mt-xs">
            <div class="claude-thinking-line">
              <span class="claude-thinking-icon">
                <span class="thinking-sparkle"></span>
              </span>
              <span class="claude-thinking-text">{{ currentThinkingStep.text }}</span>
              <span class="claude-thinking-cursor"></span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. Floating Bottom Composer (Pill Shape Docked at Bottom) -->
    <div class="floating-composer-dock row justify-center full-width">
      <div class="floating-composer-pill row items-center no-wrap">
        <!-- Ingestion shortcut (Platform Admin Only - Normal users see clean, calm input) -->
        <button
          v-if="authStore.isPlatformAdmin"
          class="composer-action-btn cursor-pointer"
          @click="$emit('open-upload')"
        >
          <q-icon
            name="cloud_upload"
            size="17px"
            color="grey-4"
          />
          <q-tooltip class="bg-black text-caption">
            Open Document Ingestion Suite
          </q-tooltip>
        </button>

        <!-- Borderless Text Input -->
        <input
          v-model="inputQuery"
          type="text"
          class="composer-input col"
          placeholder="Ask anything across enterprise repositories..."
          :disabled="chatStore.isLoading"
          @keyup.enter="handleSend"
        />

        <!-- Circular Upward-Arrow Submit Button (Illuminates white when populated) -->
        <button
          class="composer-submit-btn cursor-pointer row items-center justify-center"
          :class="{ 'submit-active': inputQuery.trim().length > 0 }"
          :disabled="!inputQuery.trim() || chatStore.isLoading"
          @click="handleSend"
        >
          <q-icon name="arrow_upward" size="16px" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch, onUnmounted } from 'vue'
import { useChatStore, Message } from '../stores/chat'
import { useAuthStore } from '../stores/auth'
import { useViewerStore } from '../stores/viewer'
import { api } from '../boot/axios'
import { Notify } from 'quasar'

defineEmits<{
  (e: 'open-upload'): void
}>()

const chatStore = useChatStore()
const authStore = useAuthStore()
const viewerStore = useViewerStore()

const inputQuery = ref('')
const scrollContainer = ref<HTMLElement | null>(null)
const ratedMap = ref<Record<string, 'up' | 'down'>>({})

// ── Dynamic Progressive Thinking Analysis ──────────────────────────────────
const elapsedSeconds = ref(0)
let thinkingTimer: any = null

const currentThinkingStep = computed(() => {
  const sec = elapsedSeconds.value
  const dept = authStore.currentUser.department || 'Product'

  // Claude-style rotating analysis text — clean, minimal, professional
  const steps = [
    { at: 0,    text: `Searching ${dept} repositories...` },
    { at: 2.0,  text: 'Reading relevant documents...' },
    { at: 5.0,  text: 'Analyzing context and extracting key details...' },
    { at: 10.0, text: 'Reasoning through enterprise knowledge base...' },
    { at: 16.0, text: 'Synthesizing grounded response...' },
    { at: 24.0, text: 'Finalizing citations and structured output...' },
  ]

  let current = steps[0]
  for (const s of steps) {
    if (sec >= s.at) current = s
  }
  return current
})

watch(() => chatStore.isLoading, (loading) => {
  if (loading) {
    elapsedSeconds.value = 0
    if (thinkingTimer) clearInterval(thinkingTimer)
    thinkingTimer = setInterval(() => {
      elapsedSeconds.value = +(elapsedSeconds.value + 0.1).toFixed(1)
    }, 100)
  } else {
    if (thinkingTimer) {
      clearInterval(thinkingTimer)
      thinkingTimer = null
    }
  }
}, { immediate: true })

onUnmounted(() => {
  if (thinkingTimer) {
    clearInterval(thinkingTimer)
    thinkingTimer = null
  }
})

// Filter out initial welcome placeholder if user starts fresh conversation
const displayMessages = computed(() => {
  return chatStore.messages.filter(m => m.id !== 'init-1')
})

const isWelcomeState = computed(() => {
  return displayMessages.value.length === 0
})

const heroEyebrow = computed(() => {
  const dept = authStore.currentUser.department?.toUpperCase() || 'ENTERPRISE'
  return `${dept} INTELLIGENCE`
})

// Department-tailored starter prompt cards (3 cards per role)
const promptMatrix: Record<string, Array<{ title: string; query: string; vault: string }>> = {
  Product: [
    {
      title: 'What is CIBIL Microfinance Score (MFI Score) and its scoring range?',
      query: 'What is CIBIL Microfinance Score and its scoring range?',
      vault: 'Product Vault'
    },
    {
      title: 'Explain Grameen Score and CreditVision Commercial Rank (CV CMR)',
      query: 'Explain Grameen Score and CreditVision Commercial Rank.',
      vault: 'Product Vault'
    },
    {
      title: 'Inspect dispute resolution SOP and bureau SLAs',
      query: 'What is the step-by-step SOP for customer dispute resolution and bureau verification?',
      vault: 'Operations SOPs'
    }
  ],
  Operations: [
    {
      title: 'What is the mandatory 4-step dispute resolution SOP?',
      query: 'What is the step-by-step SOP for customer dispute resolution and bureau verification?',
      vault: 'Operations SOPs'
    },
    {
      title: 'What are customer turnaround times mandated under RBI & FCRA?',
      query: 'What are the resolution SLAs and customer turnaround times under RBI guidelines?',
      vault: 'Operations Policy'
    },
    {
      title: 'How are biometric and identity mismatches verified?',
      query: 'How does the KYC fuzzy biometric match API work for customer verification?',
      vault: 'Technical Specs'
    }
  ],
  Sales: [
    {
      title: 'What is the enterprise rate card and volume discount tiers?',
      query: 'What is the enterprise rate card and unit price for CreditVision CMR?',
      vault: 'Finance Rate Card'
    },
    {
      title: 'Show CreditVision CMR executive pitch deck highlights',
      query: 'What are the key client pitch enablement points for CreditVision CMR v2.1?',
      vault: 'Sales Decks'
    },
    {
      title: 'Review customer dispute handling for commercial accounts',
      query: 'What is the step-by-step SOP for customer dispute resolution and bureau verification?',
      vault: 'Operations SOPs'
    }
  ],
  Technical: [
    {
      title: 'What are the internal API Gateway endpoints and rate limits?',
      query: 'What are the internal API Gateway endpoints, auth headers, and rate limits?',
      vault: 'Technical Specs'
    },
    {
      title: 'What transport security & mTLS ciphers are required?',
      query: 'What are the mTLS transport security cipher and payload requirements for CIR v5.0?',
      vault: 'API Architecture'
    },
    {
      title: 'What is the dispute registration schema and SLA?',
      query: 'What is the step-by-step SOP for customer dispute resolution and bureau verification?',
      vault: 'Bloomfire SOPs'
    }
  ],
  Governance_Risk: [
    {
      title: 'What are the mandatory data retention periods for bureau records?',
      query: 'What are the mandatory data retention periods for bureau records and audit logs?',
      vault: 'Governance Policy'
    },
    {
      title: 'What are the Zero-PII scrubbing & PAN masking protocols?',
      query: 'Explain the PII protection policy and national identity regex guardrails.',
      vault: 'Compliance Spec'
    },
    {
      title: 'Inspect enterprise pricing tiers and commercial contracts',
      query: 'What is the enterprise rate card and unit price for CreditVision CMR?',
      vault: 'Finance Vault'
    }
  ],
  Finance: [
    {
      title: 'What is the volume discount tier for CreditVision CMR?',
      query: 'What is the enterprise rate card and unit price for CreditVision CMR?',
      vault: 'Rate Card v4.0'
    },
    {
      title: 'What is the flat fee structure for the Dispute Gateway?',
      query: 'What is the pricing for Dispute Resolution Gateway and biometric verification?',
      vault: 'Pricing Matrix'
    },
    {
      title: 'Review customer dispute resolution turnaround requirements',
      query: 'What is the step-by-step SOP for customer dispute resolution and bureau verification?',
      vault: 'Bloomfire SOPs'
    }
  ]
}

const activeDepartmentPrompts = computed(() => {
  const dept = authStore.currentUser.department || 'Product'
  return promptMatrix[dept] || promptMatrix.Product
})

function runPrompt(query: string) {
  inputQuery.value = query
  handleSend()
}

async function handleSend() {
  const text = inputQuery.value.trim()
  if (!text || chatStore.isLoading) return
  inputQuery.value = ''
  await chatStore.sendMessage(text)
  scrollToBottom()
}

function scrollToBottom() {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
}

watch(() => chatStore.messages.length, () => {
  scrollToBottom()
})

function isOperationsSop(content: string): boolean {
  return content.toLowerCase().includes('sop') || content.toLowerCase().includes('dispute')
}

function hasPiiMask(content: string): boolean {
  return content.includes('[PHONE_MASKED]') || content.includes('[EMAIL_MASKED]')
}

function getAssistantLabel(msg: Message): string {
  if (msg.piiBlocked) return 'Identity GuardLLM'
  if (msg.rbacBlocked) return 'Kernel RBAC Policy'
  return 'TruCortex x Bloomfire'
}

function cleanErrorMessage(content: string): string {
  return content.replace(/^>\s*(🛑|⚠️)?\s*\*\*.*?\*\*\s*/i, '').trim()
}

function getFileIcon(type?: string): string {
  const t = (type || '').toUpperCase()
  switch (t) {
    case 'PPTX': return 'slideshow'
    case 'DOCX': return 'article'
    case 'XLSX': return 'table_chart'
    case 'PDF': return 'picture_as_pdf'
    case 'MD': return 'code'
    default: return 'description'
  }
}

function formatLocation(loc: string): string {
  return loc.replace(/^(Section|Slide|Sheet|Page)\s*:\s*/i, '$1 ')
}

function openDocumentPreview(fileName: string, location?: string) {
  viewerStore.openPreview(fileName, location)
}

async function rateResponse(msg: Message, rating: 'up' | 'down') {
  ratedMap.value[msg.id] = rating
  if (msg.auditId) {
    try {
      await api.post(`/api/audit/${msg.auditId}/feedback`, { rating })
      Notify.create({
        type: 'info',
        message: rating === 'up' ? 'Feedback recorded' : 'Marked for review',
        timeout: 1500,
        position: 'bottom',
      })
    } catch (err) {
      console.warn('Feedback submission note:', err)
    }
  }
}

function renderMarkdown(text: string): string {
  if (!text) return ''

  // Clean raw markdown output
  let html = text
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/`([^`]+)`/gim, '<code>$1</code>')
    .replace(/^\> (.*$)/gim, '<blockquote>$1</blockquote>')
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/^(?:[0-9]+\.) (.*$)/gim, '<li>$1</li>')

  // Wrap lists
  html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>')

  // Paragraph splits
  const paras = html.split(/\n\s*\n/)
  return paras
    .map(p => {
      p = p.trim()
      if (p.startsWith('<h') || p.startsWith('<blockquote') || p.startsWith('<ul')) return p
      return `<p>${p.replace(/\n/g, '<br/>')}</p>`
    })
    .join('')
}
</script>

<style scoped>
.chat-canvas-container {
  background: transparent;
  overflow: hidden;
}

.messages-scroll-viewport {
  padding-bottom: 120px; /* Space for floating composer */
}

/* Hero Welcome State */
.hero-welcome-container {
  min-height: calc(100vh - 200px);
  max-width: 740px;
  margin: 0 auto;
  padding: 40px 20px 80px;
}

.hero-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #0A84FF;
}

.kmp-platform-pill {
  background: rgba(10, 132, 255, 0.12);
  border: 1px solid rgba(10, 132, 255, 0.28);
  color: #79C0FF;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 11.5px;
  letter-spacing: -0.01em;
}

.apple-status-dot-mini {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #30D158;
  box-shadow: 0 0 8px #30D158;
}

.hero-headline {
  font-size: 38px;
  font-weight: 700;
  letter-spacing: -0.035em;
  color: #F5F5F7;
  line-height: 1.15;
}

.hero-subheadline {
  font-size: 15px;
  color: #8E8E93;
  letter-spacing: -0.015em;
  max-width: 500px;
}

.starter-cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

@media (max-width: 680px) {
  .starter-cards-grid {
    grid-template-columns: 1fr;
  }
}

.starter-prompt-card {
  background: #161618;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 16px;
  min-height: 110px;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.starter-prompt-card:hover {
  background: #222226;
  border-color: rgba(255, 255, 255, 0.16);
  transform: translateY(-2px);
}

.card-prompt-text {
  font-size: 13.5px;
  line-height: 1.4;
  color: #F5F5F7;
  letter-spacing: -0.015em;
}

.card-vault-tag {
  font-size: 11px;
  color: #8E8E93;
}

.card-arrow-icon {
  color: #636366;
  transition: transform 0.2s ease, color 0.2s ease;
}

.starter-prompt-card:hover .card-arrow-icon {
  color: #0A84FF;
  transform: translateX(2px);
}

/* Conversation Stream (Max Width 780px Centered) */
.conversation-stream-wrapper {
  max-width: 780px;
  margin: 0 auto;
  padding-top: 24px;
}

.message-row {
  animation: fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* User Bubble (Right-Aligned Apple Blue) */
.apple-user-bubble {
  background: #0A84FF;
  color: #F5F5F7;
  border-radius: 22px 22px 6px 22px;
  padding: 12px 18px;
  max-width: 82%;
  box-shadow: 0 4px 16px rgba(10, 132, 255, 0.25);
}

.user-bubble-text {
  font-size: 15px;
  line-height: 1.5;
  letter-spacing: -0.015em;
  word-break: break-word;
}

/* Assistant Response (Clean Editorial Layout) */
.assistant-response-container {
  padding-left: 4px;
}

.editorial-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}

.dot-emerald {
  background: #30D158;
  box-shadow: 0 0 8px #30D158;
}

.dot-amber {
  background: #FF9F0A;
  box-shadow: 0 0 8px #FF9F0A;
}

.dot-crimson {
  background: #FF453A;
  box-shadow: 0 0 8px #FF453A;
}

.editorial-label {
  font-size: 12px;
  color: #8E8E93;
  letter-spacing: -0.01em;
}

.pii-masked-pill {
  font-size: 10px;
  font-weight: 600;
  background: rgba(255, 159, 10, 0.15);
  color: #FF9F0A;
  border: 1px solid rgba(255, 159, 10, 0.3);
  padding: 1px 6px;
  border-radius: 999px;
}

/* Crimson Block Alert Card */
.apple-crimson-card {
  background: rgba(255, 69, 58, 0.08);
  border: 1px solid rgba(255, 69, 58, 0.28);
  border-radius: 18px;
}

.crimson-card-body {
  color: #FFB3AE;
  line-height: 1.5;
}

/* Citations Pills */
.citations-label {
  font-size: 11px;
  font-weight: 600;
  color: #636366;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.apple-citation-pill {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 5px 12px;
  color: #F5F5F7;
  font-size: 12px;
  font-family: inherit;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  max-width: 320px;
}

.apple-citation-pill:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.18);
  transform: scale(1.02);
}

.citation-icon {
  color: #0A84FF;
}

.citation-filename {
  font-weight: 500;
}

.citation-loc {
  font-size: 11px;
}

/* Feedback Tray */
.feedback-tray {
  opacity: 0.6;
  transition: opacity 0.2s ease;
}

.feedback-tray:hover {
  opacity: 1;
}

.feedback-btn {
  background: transparent;
  border: none;
  color: #8E8E93;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s ease;
}

.feedback-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #F5F5F7;
}

.feedback-active {
  color: #0A84FF !important;
}

/* Floating Bottom Composer */
.floating-composer-dock {
  position: absolute;
  bottom: 24px;
  left: 0;
  right: 0;
  pointer-events: none;
  z-index: 50;
  padding: 0 20px;
}

.floating-composer-pill {
  width: 100%;
  max-width: 740px;
  background: rgba(26, 26, 29, 0.85);
  backdrop-filter: blur(28px) saturate(190%);
  -webkit-backdrop-filter: blur(28px) saturate(190%);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 9999px;
  padding: 6px 8px 6px 14px;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.04);
  pointer-events: auto;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.floating-composer-pill:focus-within {
  border-color: rgba(10, 132, 255, 0.5);
  box-shadow: 0 20px 56px rgba(0, 0, 0, 0.8), 0 0 24px rgba(10, 132, 255, 0.2);
}

.composer-action-btn {
  background: transparent;
  border: none;
  color: #8E8E93;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  margin-right: 6px;
}

.composer-action-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #F5F5F7;
}

.composer-input {
  background: transparent;
  border: none;
  color: #F5F5F7;
  font-size: 14.5px;
  font-family: inherit;
  letter-spacing: -0.015em;
  outline: none;
  padding: 6px 8px;
}

.composer-input::placeholder {
  color: #636366;
}

.composer-submit-btn {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: #636366;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.submit-active {
  background: #F5F5F7 !important;
  color: #000000 !important;
  transform: scale(1.04);
}

.submit-active:hover {
  background: #FFFFFF !important;
  box-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
}

/* Thinking Pulse */
.dot-bounce {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #8E8E93;
  display: inline-block;
  animation: bounce 1.4s infinite ease-in-out both;
}

.d-1 { animation-delay: -0.32s; }
.d-2 { animation-delay: -0.16s; }
.d-3 { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.pulse-dot {
  animation: pulse-dot 2s infinite ease-in-out;
}

@keyframes pulse-dot {
  0% { transform: scale(0.95); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.95); opacity: 0.8; }
}

/* Apple Markdown Editorial Typography */
.apple-markdown {
  font-size: 14.5px;
  line-height: 1.6;
  color: #F5F5F7;
  letter-spacing: -0.01em;
}

.apple-markdown :deep(h1),
.apple-markdown :deep(h2),
.apple-markdown :deep(h3) {
  font-size: 15.5px;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: -0.02em;
  margin: 16px 0 8px 0;
}

.apple-markdown :deep(h3:first-child) {
  margin-top: 2px;
}

.apple-markdown :deep(p) {
  margin: 0 0 10px 0;
  line-height: 1.6;
}

.apple-markdown :deep(strong) {
  color: #FFFFFF;
  font-weight: 600;
}

.apple-markdown :deep(ul) {
  margin: 6px 0 12px 0;
  padding-left: 20px;
}

.apple-markdown :deep(li) {
  margin-bottom: 5px;
  line-height: 1.55;
  color: #E5E5EA;
}

.apple-markdown :deep(code) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 12.5px;
  color: #64D2FF;
}

.apple-markdown :deep(blockquote) {
  border-left: 3px solid #0A84FF;
  padding-left: 12px;
  margin: 10px 0;
  color: #8E8E93;
  font-style: italic;
}

/* ─── AI Avatar (Claude-style icon per response) ─────────────────────────── */
.ai-avatar-bubble {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(99, 179, 237, 0.1);
  border: 1px solid rgba(99, 179, 237, 0.25);
  box-shadow: 0 0 12px rgba(99, 179, 237, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: box-shadow 0.3s ease;
}

.ai-avatar-bubble:hover {
  box-shadow: 0 0 18px rgba(99, 179, 237, 0.4);
}

.ai-avatar-pulse {
  animation: avatar-glow 2s ease-in-out infinite;
}

@keyframes avatar-glow {
  0%, 100% { box-shadow: 0 0 10px rgba(99, 179, 237, 0.2); }
  50% { box-shadow: 0 0 22px rgba(99, 179, 237, 0.55); }
}

.ai-avatar-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
  border-radius: 2px;
}

/* ─── Hero Logo ───────────────────────────────────────────────────────────── */
.hero-logo-container {
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

.hero-logo-img {
  width: 48px;
  height: 48px;
  object-fit: contain;
  filter: drop-shadow(0 0 8px rgba(99, 179, 237, 0.4));
}

/* ─── Claude-Style Thinking Indicator ─────────────────────────────────────── */
.claude-thinking-block {
  padding-left: 2px;
  animation: think-appear 0.3s ease-out;
}

@keyframes think-appear {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.claude-thinking-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px 8px 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 20px;
  max-width: 420px;
}

.claude-thinking-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.thinking-sparkle {
  display: block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    rgba(10, 132, 255, 0.0),
    rgba(10, 132, 255, 0.6),
    rgba(100, 210, 255, 0.6),
    rgba(48, 209, 88, 0.4),
    rgba(10, 132, 255, 0.0)
  );
  animation: sparkle-spin 1.8s linear infinite;
}

@keyframes sparkle-spin {
  to { transform: rotate(360deg); }
}

.claude-thinking-text {
  font-size: 13.5px;
  color: #A1A1A6;
  letter-spacing: -0.01em;
  animation: text-shimmer 2.5s ease-in-out infinite;
}

@keyframes text-shimmer {
  0%, 100% { opacity: 0.65; }
  50% { opacity: 1; }
}

.claude-thinking-cursor {
  display: inline-block;
  width: 2px;
  height: 15px;
  background: #A1A1A6;
  border-radius: 1px;
  animation: cursor-blink 1s step-end infinite;
  flex-shrink: 0;
}

@keyframes cursor-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>
