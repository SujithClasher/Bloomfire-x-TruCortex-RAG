<template>
  <q-dialog v-model="viewerStore.isOpen" maximized transition-show="slide-up" transition-hide="slide-down">
    <q-card class="column full-height bg-black text-white">
      <!-- Top Navigation & Action Header (Apple Frosted Nav) -->
      <div class="viewer-top-bar q-px-md q-py-sm apple-glass-nav text-white row items-center justify-between border-bottom-hairline shadow-2">
        <div class="row items-center q-gutter-x-sm">
          <button class="apple-circle-back cursor-pointer" @click="viewerStore.close">
            <q-icon name="arrow_back" size="16px" />
          </button>

          <span class="format-badge-apple" :class="'badge-' + formatClass">
            <q-icon :name="formatIcon" size="13px" class="q-mr-xs" />
            {{ viewerStore.currentDoc?.file_type || 'DOC' }}
          </span>

          <div>
            <div class="row items-center q-gutter-x-xs leading-none">
              <span class="text-weight-bold text-subtitle2 text-white" style="letter-spacing: -0.01em;">
                {{ viewerStore.currentDoc?.file_name || 'Document Inspector' }}
              </span>
              <span class="apple-dept-tag q-ml-xs">
                {{ viewerStore.currentDoc?.department }}
              </span>
            </div>
            <div class="text-caption text-secondary" style="font-size: 11px; margin-top: 2px;">
              {{ viewerStore.currentDoc?.total_sections || 0 }} parsed partitions • 
              {{ Math.round((viewerStore.currentDoc?.file_size_bytes || 0) / 1024) }} KB
            </div>
          </div>
        </div>

        <!-- Mode Toggle & Download Actions -->
        <div class="row items-center q-gutter-x-sm">
          <!-- View Mode Toggle for PDF -->
          <q-btn-toggle
            v-if="viewerStore.currentDoc?.file_type === 'PDF'"
            v-model="pdfViewMode"
            dense
            rounded
            unelevated
            toggle-color="blue-5"
            color="grey-9"
            text-color="grey-4"
            size="sm"
            :options="[
              { label: 'Native PDF', value: 'native', icon: 'picture_as_pdf' },
              { label: 'Parsed Chunks', value: 'parsed', icon: 'subject' }
            ]"
            class="q-mr-xs"
          />

          <!-- View Mode Toggle for PPTX -->
          <q-btn-toggle
            v-if="viewerStore.currentDoc?.file_type === 'PPTX'"
            v-model="pptxViewMode"
            dense
            rounded
            unelevated
            toggle-color="purple-5"
            color="grey-9"
            text-color="grey-4"
            size="sm"
            :options="[
              { label: 'Slide Deck View', value: 'deck', icon: 'slideshow' },
              { label: 'Parsed Chunks', value: 'parsed', icon: 'subject' }
            ]"
            class="q-mr-xs"
          />

          <button
            v-if="viewerStore.currentDoc"
            class="apple-pill-btn apple-pill-primary cursor-pointer row items-center no-wrap text-caption"
            @click="viewerStore.downloadDoc(viewerStore.currentDoc.file_name)"
          >
            <q-icon name="arrow_downward" size="14px" class="q-mr-xs" />
            <span>Download</span>
            <q-tooltip class="bg-black text-caption">Download original binary file from enterprise repository</q-tooltip>
          </button>

          <button class="apple-circle-close cursor-pointer" @click="viewerStore.close">
            <q-icon name="close" size="15px" />
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="viewerStore.isLoading" class="col column items-center justify-center text-slate-300">
        <q-spinner-cube color="cyan-4" size="52px" />
        <div class="text-weight-bold text-subtitle2 q-mt-md">Parsing & preparing visual presentation...</div>
      </div>

      <!-- RBAC Denial State -->
      <div v-else-if="viewerStore.rbacError" class="col column items-center justify-center q-pa-lg text-center">
        <div class="rbac-denial-card q-pa-xl bg-dark-card shadow-4 rounded-borders border-dark" style="max-width: 520px;">
          <q-avatar size="64px" color="red-10" text-color="rose-3" icon="lock" class="q-mb-md" />
          <div class="text-h6 text-weight-bolder text-rose-4">Access Restricted by RBAC Policy</div>
          <div class="text-body2 text-slate-300 q-mt-sm">
            {{ viewerStore.rbacError }}
          </div>
          <q-btn
            unelevated
            color="indigo-7"
            label="Close Inspector"
            class="q-mt-lg btn-pill"
            @click="viewerStore.close"
          />
        </div>
      </div>

      <!-- Main Viewer Body -->
      <div v-else-if="viewerStore.currentDoc" class="col row no-wrap overflow-hidden">
        <!-- MODE A: NATIVE PDF IFRAME VIEWER -->
        <div v-if="viewerStore.currentDoc.file_type === 'PDF' && pdfViewMode === 'native'" class="col full-height">
          <iframe
            :src="rawFileUrl"
            class="full-width full-height border-none"
            title="Native PDF Document Viewer"
          ></iframe>
        </div>

        <!-- MODE B: PPTX SLIDE DECK PRESENTATION VIEWER -->
        <div v-else-if="viewerStore.currentDoc.file_type === 'PPTX' && pptxViewMode === 'deck'" class="col row no-wrap full-height bg-dark-deep">
          <!-- Slide Thumbnails Bar -->
          <div class="slide-nav-sidebar col-2 bg-dark-drawer scroll q-pa-sm border-right-dark">
            <div class="text-caption text-weight-bold text-slate-400 q-mb-xs">SLIDES ({{ viewerStore.currentDoc.sections.length }})</div>
            <div class="q-gutter-y-sm">
              <div
                v-for="slide in viewerStore.currentDoc.sections"
                :key="slide.index"
                class="slide-thumb-card cursor-pointer q-pa-xs rounded-borders"
                :class="activeSectionIndex === slide.index ? 'active-thumb' : ''"
                @click="activeSectionIndex = slide.index"
              >
                <div class="row items-center justify-between text-caption text-slate-300 q-px-xs">
                  <span class="text-weight-bold">{{ slide.location }}</span>
                  <q-icon v-if="slide.is_highlighted" name="star" color="amber-4" size="14px" />
                </div>
                <div class="slide-thumb-preview bg-dark-surface rounded-borders q-pa-xs text-slate-200 ellipsis-2-lines text-caption border-dark" style="font-size: 10px; height: 48px;">
                  {{ slide.content.slice(0, 80) }}
                </div>
              </div>
            </div>
          </div>

          <!-- Main Slide Presentation Canvas (16:9 Aspect Ratio) -->
          <div class="col column items-center justify-center q-pa-lg scroll">
            <div class="pptx-slide-canvas bg-white text-dark shadow-6 column justify-between q-pa-xl">
              <!-- Slide Header -->
              <div>
                <div class="row items-center justify-between border-bottom q-pb-sm">
                  <span class="text-caption text-weight-bold text-indigo-7">
                    {{ viewerStore.currentDoc.file_name }}
                  </span>
                  <q-badge color="deep-purple-8" :label="activeSection?.location" class="text-bold" />
                </div>

                <div class="text-h5 text-weight-bolder text-slate-900 q-mt-md">
                  {{ extractSlideTitle(activeSection?.content || '') }}
                </div>
              </div>

              <!-- Slide Body -->
              <div class="col q-py-lg scroll text-body1 text-slate-800">
                <div v-for="(para, pIdx) in extractSlideBody(activeSection?.content || '')" :key="pIdx" class="q-mb-sm row items-start">
                  <q-icon name="arrow_right" size="20px" color="indigo-7" class="q-mr-xs q-mt-xs" />
                  <div class="col">{{ para }}</div>
                </div>
              </div>

              <!-- Speaker Notes & Footer Callout -->
              <div v-if="extractSpeakerNotes(activeSection?.content || '')" class="speaker-notes-box q-pa-sm rounded-borders bg-amber-1 border-amber text-caption text-amber-10">
                <q-icon name="record_voice_over" size="16px" class="q-mr-xs" />
                <strong>Speaker Notes:</strong> {{ extractSpeakerNotes(activeSection?.content || '') }}
              </div>
            </div>

            <!-- Slide Navigation Controls -->
            <div class="row items-center q-gutter-x-md q-mt-md">
              <q-btn
                round
                dense
                unelevated
                color="indigo-7"
                icon="chevron_left"
                :disable="activeSectionIndex <= 1"
                @click="activeSectionIndex--"
              />
              <span class="text-caption text-white text-bold">
                Slide {{ activeSectionIndex }} of {{ viewerStore.currentDoc.sections.length }}
              </span>
              <q-btn
                round
                dense
                unelevated
                color="indigo-7"
                icon="chevron_right"
                :disable="activeSectionIndex >= viewerStore.currentDoc.sections.length"
                @click="activeSectionIndex++"
              />
            </div>
          </div>
        </div>

        <!-- MODE C: STRUCTURED OUTLINE / SPREADSHEET / DOCUMENT READER -->
        <div v-else class="col row no-wrap full-height bg-dark-deep">
          <!-- Sections Sidebar -->
          <div class="sections-sidebar col-3 bg-dark-drawer border-right-dark scroll q-pa-sm">
            <div class="text-caption text-weight-bolder text-slate-400 q-mb-xs q-px-xs">
              DOCUMENT OUTLINE ({{ viewerStore.currentDoc.sections.length }} ITEMS)
            </div>

            <q-list dense class="q-gutter-y-xs">
              <q-item
                v-for="sec in viewerStore.currentDoc.sections"
                :key="sec.index"
                clickable
                v-ripple
                :active="activeSectionIndex === sec.index"
                active-class="active-section-item"
                class="section-nav-item rounded-borders"
                @click="activeSectionIndex = sec.index"
              >
                <q-item-section avatar style="min-width: 32px;">
                  <q-badge
                    :color="sec.is_highlighted ? 'amber-8' : 'slate-8'"
                    :text-color="sec.is_highlighted ? 'dark' : 'slate-2'"
                    :label="`${sec.index}`"
                    class="text-bold"
                  />
                </q-item-section>

                <q-item-section>
                  <q-item-label class="text-weight-bold text-caption ellipsis text-slate-200">
                    {{ sec.location }}
                  </q-item-label>
                  <q-item-label caption class="ellipsis text-slate-400" style="font-size: 10.5px;">
                    {{ sec.content.slice(0, 50) }}...
                  </q-item-label>
                </q-item-section>

                <q-item-section v-if="sec.is_highlighted" side>
                  <q-icon name="star" color="amber-4" size="14px" />
                </q-item-section>
              </q-item>
            </q-list>
          </div>

          <!-- Reader Pane -->
          <div class="col scroll q-pa-lg bg-dark-deep">
            <div class="reader-pane-wrapper" style="max-width: 900px; margin: 0 auto;">
              <!-- Section Banner -->
              <div class="row items-center justify-between q-mb-md bg-dark-surface q-pa-md rounded-borders shadow-1 border-dark">
                <div class="row items-center q-gutter-x-sm">
                  <q-avatar size="32px" color="indigo-9" text-color="indigo-2" icon="menu_book" />
                  <div>
                    <div class="text-subtitle1 text-weight-bolder text-white">
                      {{ activeSection?.location }}
                    </div>
                    <div class="text-caption text-slate-400">
                      Partition {{ activeSection?.index }} of {{ viewerStore.currentDoc.total_sections }}
                    </div>
                  </div>
                </div>

                <q-badge
                  v-if="activeSection?.is_highlighted"
                  color="amber-9"
                  text-color="dark"
                  class="q-pa-xs text-bold"
                >
                  <q-icon name="stars" size="14px" class="q-mr-xs" />
                  Cited Grounded Chunk
                </q-badge>
              </div>

              <!-- Content Display Card -->
              <q-card flat bordered class="q-pa-lg bg-dark-card shadow-2 rounded-borders border-dark">
                <!-- Table for spreadsheets or pipe-formatted content -->
                <div v-if="isTableContent(activeSection?.content || '')" class="q-my-xs overflow-auto">
                  <table class="parsed-content-table full-width">
                    <tbody>
                      <tr v-for="(row, rIdx) in parseTableRows(activeSection?.content || '')" :key="rIdx">
                        <td
                          v-for="(cell, cIdx) in row"
                          :key="cIdx"
                          :class="rIdx === 0 ? 'text-weight-bold bg-dark-surface text-cyan-3' : 'text-slate-200'"
                        >
                          {{ cell }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <!-- Paragraphs -->
                <div v-else class="content-text-body text-body1 text-slate-200">
                  <p
                    v-for="(paragraph, pIdx) in (activeSection?.content || '').split('\n')"
                    :key="pIdx"
                    class="q-mb-sm"
                  >
                    {{ paragraph }}
                  </p>
                </div>
              </q-card>
            </div>
          </div>
        </div>
      </div>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useViewerStore, DocSection } from '../stores/viewer'
import { useAuthStore } from '../stores/auth'

const viewerStore = useViewerStore()
const authStore = useAuthStore()

const activeSectionIndex = ref(1)
const pdfViewMode = ref<'native' | 'parsed'>('native')
const pptxViewMode = ref<'deck' | 'parsed'>('deck')

watch(() => viewerStore.currentDoc, (newDoc) => {
  if (newDoc && newDoc.sections.length > 0) {
    const highlighted = newDoc.sections.find(s => s.is_highlighted)
    activeSectionIndex.value = highlighted ? highlighted.index : 1
    // Reset view modes to native / slide deck
    pdfViewMode.value = 'native'
    pptxViewMode.value = 'deck'
  }
})

const activeSection = computed<DocSection | undefined>(() => {
  return viewerStore.currentDoc?.sections.find(s => s.index === activeSectionIndex.value)
})

const rawFileUrl = computed(() => {
  if (!viewerStore.currentDoc) return ''
  return `http://localhost:8010/api/documents/raw?file_path=${encodeURIComponent(viewerStore.currentDoc.file_name)}&username=${encodeURIComponent(authStore.currentUser.username)}`
})

const formatClass = computed(() => {
  return (viewerStore.currentDoc?.file_type || 'doc').toLowerCase()
})

const formatIcon = computed(() => {
  const t = viewerStore.currentDoc?.file_type?.toUpperCase()
  switch (t) {
    case 'PPTX': return 'slideshow'
    case 'DOCX': return 'article'
    case 'XLSX': return 'table_view'
    case 'PDF': return 'picture_as_pdf'
    case 'MD': return 'code'
    default: return 'description'
  }
})

function extractSlideTitle(text: string): string {
  const lines = text.split('\n').filter(l => l.trim().length > 0)
  return lines[0] || 'Slide'
}

function extractSlideBody(text: string): string[] {
  const lines = text.split('\n').filter(l => l.trim().length > 0)
  return lines.slice(1).filter(l => !l.toLowerCase().includes('speaker notes'))
}

function extractSpeakerNotes(text: string): string {
  const match = text.match(/\[(?:Speaker\s+)?Notes:\s*(.*?)\]/i)
  return match ? match[1] : ''
}

function isTableContent(text: string): boolean {
  return text.includes('|') && text.includes(':')
}

function parseTableRows(text: string): string[][] {
  const lines = text.split('\n').filter(l => l.trim().length > 0)
  return lines.map(line => line.split('|').map(cell => cell.trim()))
}
</script>

<style scoped>
.bg-dark-deep {
  background-color: #090d16;
}

.bg-dark-surface {
  background-color: #111a30;
}

.bg-dark-drawer {
  background-color: #0d1424;
}

.bg-dark-card {
  background-color: #131c33;
}

.border-bottom-hairline {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.apple-circle-back, .apple-circle-close {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.apple-circle-back:hover, .apple-circle-close:hover {
  background: rgba(255, 255, 255, 0.14);
  color: #F5F5F7;
}

.format-badge-apple {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
}

.apple-dept-tag {
  font-size: 11px;
  background: rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  padding: 1px 6px;
  border-radius: 999px;
}

.viewer-top-bar {
  min-height: 52px;
}

.format-badge-lg {
  font-size: 11px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
}

.badge-pptx { background: rgba(147, 51, 234, 0.2); color: #c084fc; border: 1px solid rgba(147, 51, 234, 0.4); }
.badge-docx { background: rgba(37, 99, 235, 0.2); color: #60a5fa; border: 1px solid rgba(37, 99, 235, 0.4); }
.badge-xlsx { background: rgba(22, 163, 74, 0.2); color: #4ade80; border: 1px solid rgba(22, 163, 74, 0.4); }
.badge-pdf { background: rgba(220, 38, 38, 0.2); color: #f87171; border: 1px solid rgba(220, 38, 38, 0.4); }
.badge-md { background: rgba(100, 116, 139, 0.2); color: #94a3b8; border: 1px solid rgba(100, 116, 139, 0.4); }

.pptx-slide-canvas {
  width: 100%;
  max-width: 880px;
  aspect-ratio: 16 / 9;
  border-radius: 12px;
  border: 1px solid #cbd5e1;
}

.slide-thumb-card {
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: all 0.2s ease;
}

.slide-thumb-card:hover {
  background: rgba(255, 255, 255, 0.05);
}

.active-thumb {
  border: 2px solid #818cf8 !important;
  background: rgba(99, 102, 241, 0.2) !important;
}

.section-nav-item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.active-section-item {
  background: rgba(99, 102, 241, 0.2) !important;
  border-left: 3px solid #6366f1;
}

.parsed-content-table {
  border-collapse: collapse;
  width: 100%;
  font-size: 13px;
}

.parsed-content-table td {
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 8px 12px;
}

.content-text-body {
  line-height: 1.7;
  white-space: pre-wrap;
}

.speaker-notes-box {
  border-radius: 8px;
}

.border-none {
  border: none;
}
</style>
