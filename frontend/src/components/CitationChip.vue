<template>
  <button class="apple-citation-pill row items-center no-wrap cursor-pointer" @click="handleClick">
    <q-icon :name="formatIcon" size="14px" class="q-mr-xs citation-icon" />
    <span class="citation-filename ellipsis" style="max-width: 220px;">
      {{ citation.file_name }}
    </span>
    <span v-if="citation.page_or_slide" class="citation-loc q-ml-xs text-secondary">
      · {{ formatLocation(citation.page_or_slide) }}
    </span>

    <q-tooltip class="apple-citation-tooltip bg-black text-white q-pa-sm shadow-6" max-width="320px">
      <div class="text-weight-bold text-caption text-white">{{ citation.file_name }}</div>
      <div class="text-caption text-secondary q-mt-xs">
        <strong>Section:</strong> {{ citation.page_or_slide }}
      </div>
      <div class="text-caption text-secondary">
        <strong>Repository:</strong> {{ citation.department }}
      </div>
    </q-tooltip>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Citation } from '../stores/chat'
import { useViewerStore } from '../stores/viewer'

const viewerStore = useViewerStore()

const props = defineProps<{
  citation: Citation
}>()

function handleClick() {
  viewerStore.openPreview(props.citation.file_name, props.citation.page_or_slide)
}

function formatLocation(loc: string): string {
  return loc.replace(/^(Section|Slide|Sheet|Page)\s*:\s*/i, '$1 ')
}

const formatIcon = computed(() => {
  const t = props.citation.file_type?.toUpperCase()
  switch (t) {
    case 'PPTX': return 'slideshow'
    case 'DOCX': return 'article'
    case 'XLSX': return 'table_chart'
    case 'PDF': return 'picture_as_pdf'
    case 'MD': return 'code'
    default: return 'description'
  }
})
</script>

<style scoped>
.apple-citation-pill {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 5px 12px;
  color: #F5F5F7;
  font-size: 12px;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
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
  letter-spacing: -0.01em;
}

.citation-loc {
  font-size: 11px;
}

.apple-citation-tooltip {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
