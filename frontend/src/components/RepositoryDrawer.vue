<template>
  <div class="column full-height apple-sidebar-panel text-white">
    <!-- Header -->
    <div class="q-pa-md border-bottom-hairline">
      <div class="row items-center justify-between">
        <div class="row items-center q-gutter-x-xs">
          <span class="text-weight-semibold text-white" style="font-size: 14px; letter-spacing: -0.01em;">
            Knowledge Vaults
          </span>
        </div>
        <button
          class="apple-sync-btn cursor-pointer row items-center justify-center"
          :class="{ 'btn-spinning': foldersStore.isLoading }"
          @click="handleSync"
        >
          <q-icon name="sync" size="14px" />
          <q-tooltip class="bg-black text-caption">Live Vector Sync & Re-index</q-tooltip>
        </button>
      </div>

      <!-- Scope Indicator -->
      <div class="row items-center justify-between q-mt-xs text-caption text-secondary" style="font-size: 11px;">
        <span>Clearance:</span>
        <div class="row items-center q-gutter-x-xs no-wrap">
          <span class="scope-pill">{{ authStore.currentUser.department }}</span>
          <span
            class="mini-role-badge"
            :class="authStore.isPlatformAdmin ? 'mini-admin' : (authStore.isDepartmentOwner ? 'mini-owner' : 'mini-analyst')"
          >
            {{ authStore.isPlatformAdmin ? 'Admin' : (authStore.isDepartmentOwner ? 'Owner' : 'Analyst') }}
          </span>
        </div>
      </div>
    </div>

    <!-- Tree View Body -->
    <div class="col scroll q-pa-sm">
      <div v-if="foldersStore.isLoading" class="text-center q-pa-xl text-secondary">
        <q-spinner-dots size="24px" color="blue-4" />
        <div class="q-mt-sm text-caption">Scanning enterprise vaults...</div>
      </div>

      <div v-else-if="foldersStore.tree.length === 0" class="text-center q-pa-xl text-secondary">
        <q-icon name="folder_open" size="36px" />
        <div class="text-weight-medium text-white q-mt-sm" style="font-size: 13px;">No Files Indexed</div>
        <button
          class="apple-pill-secondary q-mt-md text-caption cursor-pointer"
          @click="handleSync"
        >
          Sync Now
        </button>
      </div>

      <div v-else class="q-gutter-y-xs">
        <template v-for="node in foldersStore.tree" :key="node.path">
          <TreeNode :node="node" />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useFoldersStore, FileNode } from '../stores/folders'
import { useAuthStore } from '../stores/auth'
import { Notify } from 'quasar'

defineEmits<{
  (e: 'open-upload'): void
}>()

const foldersStore = useFoldersStore()
const authStore = useAuthStore()

onMounted(() => {
  foldersStore.fetchTree()
})

async function handleSync() {
  try {
    const res = await foldersStore.syncAndReindex()
    if (res?.status === 'error') {
      Notify.create({
        type: 'warning',
        message: `Sync Warning: ${res.error || 'Check backend console'}`,
        icon: 'warning',
        timeout: 4000,
      })
      return
    }
    Notify.create({
      type: 'positive',
      message: `Sync Complete: ${res.total_chunks} chunks indexed across ${res.total_files} files in ${res.duration_seconds}s.`,
      icon: 'check_circle',
      timeout: 3000,
    })
  } catch (err: any) {
    let msg = 'Failed to sync repositories.'
    if (err.response?.data?.detail) {
      msg = err.response.data.detail
    } else if (err.code === 'ERR_NETWORK' || (err.message && (err.message.includes('Network Error') || err.message.includes('ECONNREFUSED')))) {
      msg = 'Backend connection unreachable on http://localhost:8010. Please ensure Uvicorn server is running.'
    } else if (err.message) {
      msg = `Sync notice: ${err.message}`
    }
    Notify.create({
      type: 'negative',
      message: msg,
      timeout: 4000,
    })
  }
}
</script>

<script lang="ts">
import { defineComponent, h, PropType } from 'vue'
import { QExpansionItem, QItem, QItemSection, QIcon, QTooltip } from 'quasar'
import { useViewerStore } from '../stores/viewer'

export const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    node: {
      type: Object as PropType<FileNode>,
      required: true
    }
  },
  setup(props) {
    const viewerStore = useViewerStore()
    return () => {
      const { node } = props

      if (node.type === 'folder') {
        const isRestricted = !node.accessible

        return h(
          QExpansionItem,
          {
            defaultOpened: node.accessible,
            dense: true,
            denseToggle: true,
            headerClass: isRestricted
              ? 'folder-header-restricted'
              : 'folder-header',
          },
          {
            header: () => [
              h(QItemSection, { avatar: true, style: 'min-width: 24px;' }, () => [
                h(QIcon, {
                  name: isRestricted ? 'lock' : 'folder',
                  color: isRestricted ? 'red-4' : 'grey-5',
                  size: '15px'
                })
              ]),
              h(QItemSection, () => [
                h('div', { class: 'row items-center no-wrap' }, [
                  h('span', { class: isRestricted ? 'text-secondary text-caption' : 'text-white text-caption text-weight-medium' }, node.name),
                  isRestricted
                    ? h('span', { class: 'lock-badge q-ml-xs' }, 'Restricted')
                    : null
                ])
              ]),
              isRestricted
                ? h(QTooltip, { class: 'bg-black text-white text-caption' }, () =>
                    `🔒 Restricted: Role cannot view ${node.department} files.`
                  )
                : null
            ],
            default: () =>
              node.children && node.children.length > 0
                ? node.children.map(child => h(TreeNode, { node: child, key: child.path }))
                : h('div', { class: 'q-pa-xs text-caption text-secondary q-ml-lg' }, isRestricted ? '(Restricted by RBAC)' : 'Empty folder')
          }
        )
      } else {
        // File Node
        const isRestricted = !node.accessible
        const ext = (node.file_type || 'FILE').toUpperCase()

        return h(
          QItem,
          {
            dense: true,
            clickable: true,
            class: isRestricted ? 'file-row-restricted' : 'file-row q-ml-sm',
            onClick: () => {
              viewerStore.openPreview(node.name)
            }
          },
          () => [
            h(QItemSection, { avatar: true, style: 'min-width: 28px;' }, () => [
              h('span', { class: `file-tag tag-${ext.toLowerCase()}` }, ext)
            ]),
            h(QItemSection, () => [
              h('div', { class: isRestricted ? 'text-secondary text-caption ellipsis' : 'text-caption text-white ellipsis' }, node.name)
            ]),
            h(QItemSection, { side: true }, () => [
              isRestricted
                ? h(QIcon, { name: 'lock', size: '12px', color: 'red-4' })
                : h(QIcon, {
                    name: 'arrow_downward',
                    size: '13px',
                    color: 'grey-5',
                    class: 'cursor-pointer hover-white',
                    onClick: (e: Event) => {
                      e.stopPropagation()
                      viewerStore.downloadDoc(node.name)
                    }
                  })
            ]),
            isRestricted
              ? h(QTooltip, { class: 'bg-black text-white' }, () =>
                  `🔒 Restricted: ${node.department} file blocked by role clearance.`
                )
              : null
          ]
        )
      }
    }
  }
})
</script>

<style scoped>
.apple-sidebar-panel {
  background: transparent;
}

.border-bottom-hairline {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.apple-sync-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.apple-sync-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #F5F5F7;
}

.btn-spinning {
  animation: spin 1s infinite linear;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.scope-pill {
  background: rgba(255, 255, 255, 0.08);
  color: #F5F5F7;
  padding: 1px 6px;
  border-radius: 999px;
  font-size: 10.5px;
}

.mini-role-badge {
  font-size: 8.5px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 3px;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.mini-admin {
  background: rgba(10, 132, 255, 0.2);
  color: #0A84FF;
  border: 1px solid rgba(10, 132, 255, 0.4);
}

.mini-owner {
  background: rgba(48, 209, 88, 0.18);
  color: #30D158;
  border: 1px solid rgba(48, 209, 88, 0.35);
}

.mini-analyst {
  background: rgba(255, 255, 255, 0.08);
  color: #8E8E93;
}

:deep(.folder-header) {
  border-radius: 8px;
  margin: 1px 0;
  transition: background 0.15s ease;
}

:deep(.folder-header:hover) {
  background: rgba(255, 255, 255, 0.05);
}

:deep(.folder-header-restricted) {
  border-radius: 8px;
  opacity: 0.6;
  margin: 1px 0;
}

:deep(.file-row) {
  border-radius: 8px;
  margin: 1px 0;
  transition: all 0.15s ease;
}

:deep(.file-row:hover) {
  background: rgba(255, 255, 255, 0.06);
}

:deep(.file-row-restricted) {
  border-radius: 8px;
  opacity: 0.45;
}

:deep(.file-tag) {
  font-size: 8.5px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 4px;
  letter-spacing: 0.04em;
}

:deep(.tag-pptx) { background: rgba(191, 90, 242, 0.2); color: #BF5AF2; }
:deep(.tag-docx) { background: rgba(10, 132, 255, 0.2); color: #0A84FF; }
:deep(.tag-xlsx) { background: rgba(48, 209, 88, 0.2); color: #30D158; }
:deep(.tag-pdf)  { background: rgba(255, 69, 58, 0.2); color: #FF453A; }
:deep(.tag-md)   { background: rgba(255, 255, 255, 0.12); color: #8E8E93; }

:deep(.lock-badge) {
  font-size: 9px;
  background: rgba(255, 69, 58, 0.2);
  color: #FF453A;
  padding: 1px 4px;
  border-radius: 3px;
}

:deep(.hover-white:hover) {
  color: #FFFFFF !important;
}
</style>
