<template>
  <div class="column full-height apple-radar-panel text-white">
    <!-- Header Summary & Scan Trigger -->
    <div class="q-pa-md border-bottom-hairline">
      <div class="row items-center justify-between">
        <div>
          <div class="text-weight-semibold text-white" style="font-size: 14px; letter-spacing: -0.01em;">
            Active Cross-Department Discrepancies
          </div>
          <div class="text-caption text-secondary" style="font-size: 11.5px; margin-top: 1px;">
            Flags semantic divergence (>0.65 similarity) across repositories.
          </div>
        </div>
        <button
          class="apple-scan-btn cursor-pointer row items-center no-wrap"
          :disabled="conflictsStore.isLoading"
          @click="conflictsStore.triggerScan"
        >
          <q-icon name="search" size="13px" class="q-mr-xs" />
          <span>Scan All</span>
        </button>
      </div>
    </div>

    <!-- Conflict List -->
    <div class="col scroll q-pa-sm">
      <!-- Loading State -->
      <div v-if="conflictsStore.isLoading" class="text-center q-pa-xl text-secondary">
        <q-spinner-dots size="28px" color="amber-5" />
        <div class="text-caption q-mt-sm">Evaluating cross-departmental embeddings...</div>
      </div>

      <!-- Empty State -->
      <div v-else-if="conflictsStore.conflicts.length === 0" class="text-center q-pa-xl">
        <q-icon name="check_circle" size="36px" color="green-4" />
        <div class="text-weight-semibold text-white q-mt-sm" style="font-size: 14px;">Radar Clear</div>
        <div class="text-caption text-secondary q-mt-xs" style="font-size: 12px;">
          No active policy, version, or data divergences detected across departments.
        </div>
        <button
          class="apple-scan-btn q-mt-md cursor-pointer"
          @click="conflictsStore.triggerScan"
        >
          Run Deep Semantic Scan
        </button>
      </div>

      <!-- Conflicts Cards -->
      <div v-else class="q-gutter-y-sm">
        <div
          v-for="item in conflictsStore.conflicts"
          :key="item.id"
          class="apple-radar-card q-pa-md"
        >
          <!-- Top Row: Badge & Type -->
          <div class="row items-center justify-between q-mb-sm">
            <span class="radar-type-tag" :class="getConflictTypeClass(item.conflict_type)">
              {{ formatConflictType(item.conflict_type) }}
            </span>
            <span class="similarity-indicator text-secondary text-caption">
              {{ Math.round(item.similarity * 100) }}% semantic overlap
            </span>
          </div>

          <!-- Discrepancy Highlight Callout -->
          <div v-if="item.discrepancy_summary" class="discrepancy-drawer-callout q-pa-xs q-mb-sm rounded-borders text-caption">
            <span class="text-amber-4 text-weight-bold">⚠️ Core Discrepancy:</span>
            <span class="text-white q-ml-xs">{{ item.discrepancy_summary }}</span>
          </div>

          <!-- Dual Quote Comparison Block -->
          <div class="comparison-block q-pa-sm q-mb-sm q-gutter-y-xs">
            <div class="quote-box-mini quote-source-mini q-pa-xs rounded-borders text-caption">
              <div class="row items-center justify-between no-wrap q-mb-xs">
                <span class="compare-label text-blue-4 text-weight-bold ellipsis">
                  Source: {{ item.source_file }}
                  <span v-if="item.source_location" class="text-secondary">({{ item.source_location }})</span>
                </span>
                <span class="dept-pill">{{ item.source_dept }}</span>
              </div>
              <div class="drawer-snippet-text">
                "{{ item.source_chunk }}"
              </div>
            </div>

            <div v-if="item.conflicting_chunk" class="quote-box-mini quote-conflicting-mini q-pa-xs rounded-borders text-caption">
              <div class="row items-center justify-between no-wrap q-mb-xs">
                <span class="compare-label text-red-4 text-weight-bold ellipsis">
                  Contradicts: {{ item.conflicting_file }}
                  <span v-if="item.conflicting_location" class="text-secondary">({{ item.conflicting_location }})</span>
                </span>
                <span class="dept-pill">{{ item.conflicting_dept }}</span>
              </div>
              <div class="drawer-snippet-text conflicting-snippet-text">
                "{{ item.conflicting_chunk }}"
              </div>
            </div>
          </div>

          <!-- Action Buttons (Pill Format: Confirm Impact / Dismiss) -->
          <div v-if="item.status === 'active'" class="row items-center justify-end q-gutter-x-xs q-pt-xs">
            <button
              class="apple-card-action-btn btn-dismiss cursor-pointer"
              @click="conflictsStore.takeAction(item.id, 'dismiss')"
            >
              Dismiss
            </button>
            <button
              class="apple-card-action-btn btn-confirm cursor-pointer"
              @click="conflictsStore.takeAction(item.id, 'confirm_impact')"
            >
              Confirm Impact
            </button>
          </div>

          <!-- Status when resolved -->
          <div v-else class="text-caption text-secondary text-right q-pt-xs" style="font-size: 11px;">
            Status: <span class="text-white">{{ item.status === 'impact_confirmed' ? '⚠️ Impact Confirmed' : '✓ Dismissed' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useConflictsStore } from '../stores/conflicts'

const conflictsStore = useConflictsStore()

onMounted(() => {
  conflictsStore.fetchConflicts()
})

function formatConflictType(type: string): string {
  switch (type) {
    case 'pricing_mismatch': return 'Pricing Floor Mismatch'
    case 'sla_architecture_clash': return 'SLA & Architecture Clash'
    case 'confidentiality_breach': return 'Proprietary Disclosure Clash'
    case 'version_mismatch': return 'Version Mismatch'
    case 'policy_conflict': return 'Policy Divergence'
    case 'data_overlap': return 'Data Metric Clash'
    default: return 'Semantic Divergence'
  }
}

function getConflictTypeClass(type: string): string {
  switch (type) {
    case 'pricing_mismatch':
    case 'data_overlap': return 'tag-purple'
    case 'sla_architecture_clash':
    case 'policy_conflict': return 'tag-crimson'
    case 'confidentiality_breach': return 'tag-amber'
    case 'version_mismatch': return 'tag-amber'
    default: return 'tag-amber'
  }
}
</script>

<style scoped>
.apple-radar-panel {
  background: transparent;
}

.border-bottom-hairline {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.apple-scan-btn {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #F5F5F7;
  border-radius: 999px;
  font-size: 11.5px;
  font-family: inherit;
  padding: 4px 12px;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-scan-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: scale(1.02);
}

.apple-radar-card {
  background: #161618;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-radar-card:hover {
  background: #1C1C1F;
  border-color: rgba(255, 255, 255, 0.15);
}

.radar-type-tag {
  font-size: 10px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.tag-amber {
  background: rgba(255, 159, 10, 0.15);
  color: #FF9F0A;
  border: 1px solid rgba(255, 159, 10, 0.3);
}

.tag-crimson {
  background: rgba(255, 69, 58, 0.15);
  color: #FF453A;
  border: 1px solid rgba(255, 69, 58, 0.3);
}

.tag-purple {
  background: rgba(191, 90, 242, 0.15);
  color: #BF5AF2;
  border: 1px solid rgba(191, 90, 242, 0.3);
}

.similarity-indicator {
  font-size: 11px;
}

.discrepancy-drawer-callout {
  background: rgba(255, 159, 10, 0.12);
  border: 1px solid rgba(255, 159, 10, 0.3);
  font-size: 11px;
  line-height: 1.35;
  padding: 5px 8px;
}

.quote-box-mini {
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.04);
  padding: 5px 7px;
}

.quote-source-mini {
  border-left: 2px solid #0A84FF;
}

.quote-conflicting-mini {
  border-left: 2px solid #FF453A;
}

.drawer-snippet-text {
  font-style: italic;
  font-size: 11px;
  color: #D1D1D6;
  padding-left: 4px;
}

.conflicting-snippet-text {
  color: #FFB3AD !important;
}

.comparison-block {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.compare-label {
  font-weight: 600;
  min-width: 50px;
}

.dept-pill {
  background: rgba(255, 255, 255, 0.1);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 10px;
  color: #8E8E93;
}

.snippet-preview {
  color: #8E8E93;
  font-style: italic;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.apple-card-action-btn {
  font-family: inherit;
  font-size: 11.5px;
  font-weight: 500;
  border-radius: 999px;
  padding: 4px 12px;
  border: none;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.btn-dismiss {
  background: rgba(255, 255, 255, 0.06);
  color: #8E8E93;
}

.btn-dismiss:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #F5F5F7;
}

.btn-confirm {
  background: rgba(255, 159, 10, 0.2);
  color: #FF9F0A;
  border: 1px solid rgba(255, 159, 10, 0.35);
}

.btn-confirm:hover {
  background: #FF9F0A;
  color: #000000;
}
</style>
