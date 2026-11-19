<template>
  <div class="column full-height bg-dark-drawer text-white">
    <!-- Header -->
    <div class="q-pa-md bg-dark-surface border-bottom-dark shadow-1">
      <div class="row items-center justify-between">
        <div class="row items-center q-gutter-x-xs">
          <q-icon name="fact_check" size="20px" color="teal-4" />
          <span class="text-subtitle2 text-weight-bolder text-white">
            Zero-PII Audit Trail
          </span>
        </div>
        <q-btn
          flat
          round
          dense
          icon="refresh"
          color="teal-3"
          :loading="auditStore.isLoading"
          @click="auditStore.fetchLogs"
        >
          <q-tooltip class="bg-slate-900 text-caption">Refresh Audit Log from SQLite</q-tooltip>
        </q-btn>
      </div>
      <div class="text-caption text-slate-400 q-mt-xs">
        Cryptographically scrubbed interaction logs stored in SQLite with Zero-PII masking.
      </div>
    </div>

    <!-- Logs List -->
    <div class="col scroll q-pa-sm bg-dark-drawer">
      <div v-if="auditStore.isLoading" class="text-center q-pa-xl text-slate-400">
        <q-spinner-dots size="32px" color="teal-4" />
        <div class="text-caption text-weight-medium q-mt-sm">Querying SQLite audit database...</div>
      </div>

      <div v-else-if="auditStore.logs.length === 0" class="text-center q-pa-xl text-slate-500">
        <q-icon name="history_toggle_off" size="44px" />
        <div class="text-body2 text-weight-bold q-mt-sm text-white">No audit records</div>
        <div class="text-caption text-slate-400">Submit queries in the chat to generate zero-PII audit records.</div>
      </div>

      <div v-else class="q-gutter-y-xs">
        <q-card
          v-for="log in auditStore.logs"
          :key="log.id"
          flat
          bordered
          class="audit-log-card bg-dark-card border-dark shadow-2"
        >
          <q-card-section class="q-pb-xs">
            <div class="row items-center justify-between">
              <span class="text-caption mono-font text-slate-400">
                #{{ log.id }} • {{ formatTime(log.timestamp) }}
              </span>
              <div class="row q-gutter-x-xs">
                <q-badge v-if="log.pii_blocked" color="negative" class="text-bold" label="PII BLOCKED" />
                <q-badge v-if="log.rbac_blocked" color="warning" text-color="dark" class="text-bold" label="RBAC BLOCKED" />
                <q-badge v-if="!log.pii_blocked && !log.rbac_blocked" color="positive" class="text-bold" label="AUTHORIZED" />
              </div>
            </div>

            <!-- User and Dept -->
            <div class="row items-center q-mt-xs">
              <strong class="text-indigo-3 text-body2 q-mr-xs">{{ log.username }}</strong>
              <q-badge color="slate-8" text-color="slate-2" class="text-bold">
                {{ log.department }}
              </q-badge>
            </div>

            <!-- Masked Query -->
            <div class="q-mt-xs text-body2 text-slate-200">
              <span class="text-slate-400">Query: </span>
              <span class="mono-font text-caption bg-dark-surface q-px-xs rounded-borders border-dark text-cyan-3">{{ log.query_masked }}</span>
            </div>

            <!-- Summary -->
            <div class="q-mt-xs text-caption text-slate-300 bg-dark-surface q-pa-xs rounded-borders border-dark ellipsis-2-lines">
              {{ log.response_summary }}
            </div>
          </q-card-section>

          <!-- Feedback Section -->
          <q-card-actions align="between" class="q-pt-none border-top-dark q-px-sm q-py-xs">
            <span class="text-caption text-slate-400" style="font-size: 11px;">Grounded evaluation:</span>
            <div class="row items-center q-gutter-x-xs">
              <q-btn
                flat
                dense
                round
                size="xs"
                :icon="log.feedback_rating === 'up' ? 'thumb_up' : 'thumb_up_off_alt'"
                :color="log.feedback_rating === 'up' ? 'positive' : 'slate-400'"
                @click="rate(log.id, 'up')"
              >
                <q-tooltip class="bg-slate-900 text-caption">Thumbs Up (Grounded & Accurate)</q-tooltip>
              </q-btn>
              <q-btn
                flat
                dense
                round
                size="xs"
                :icon="log.feedback_rating === 'down' ? 'thumb_down' : 'thumb_down_off_alt'"
                :color="log.feedback_rating === 'down' ? 'negative' : 'slate-400'"
                @click="rate(log.id, 'down')"
              >
                <q-tooltip class="bg-slate-900 text-caption">Thumbs Down (Needs Review)</q-tooltip>
              </q-btn>
            </div>
          </q-card-actions>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuditStore } from '../stores/audit'

const auditStore = useAuditStore()

onMounted(() => {
  auditStore.fetchLogs()
})

function formatTime(isoStr: string): string {
  try {
    const d = new Date(isoStr)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch {
    return isoStr
  }
}

function rate(id: number, rating: 'up' | 'down') {
  auditStore.submitFeedback(id, rating)
}
</script>

<style scoped>
.bg-dark-drawer {
  background-color: #0d1424;
}

.bg-dark-surface {
  background-color: #111a30;
}

.bg-dark-card {
  background-color: #15203b;
}

.border-bottom-dark {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.border-top-dark {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.border-dark {
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.audit-log-card {
  border-radius: 8px;
  transition: all 0.2s ease;
}

.audit-log-card:hover {
  border-color: rgba(255, 255, 255, 0.16);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
}
</style>
