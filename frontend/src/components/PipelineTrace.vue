<template>
  <div class="trace-wrapper q-my-sm">
    <div class="row items-center justify-between q-pb-xs">
      <div class="row items-center q-gutter-x-xs">
        <q-icon name="polyline" size="16px" color="indigo-7" />
        <span class="text-caption text-weight-bold text-slate-800">Orchestrator Pipeline Trace:</span>
        <span class="text-caption text-grey-6 gt-xs">({{ steps.length }} stages executed)</span>
      </div>
      <q-btn
        flat
        dense
        size="xs"
        no-caps
        color="primary"
        :icon-right="isExpanded ? 'expand_less' : 'expand_more'"
        :label="isExpanded ? 'Hide Trace Logs' : 'View Stage Details'"
        @click="isExpanded = !isExpanded"
      />
    </div>

    <!-- Stepper Pills Flow -->
    <div class="row items-center no-wrap scroll q-gutter-x-xs q-py-xs trace-pill-bar">
      <template v-for="(step, index) in steps" :key="step.step">
        <div
          class="row items-center no-wrap trace-step-pill cursor-pointer"
          :class="[getStepClass(step.status), selectedStep === step.step ? 'selected-step' : '']"
          @click="toggleStep(step.step)"
        >
          <q-icon :name="getStepIcon(step.status)" size="13px" class="q-mr-xs" />
          <span class="step-num">{{ step.step }}.</span>
          <span class="step-name">{{ step.name }}</span>
          <span v-if="step.latency_ms > 0" class="step-latency">
            {{ formatLatency(step.latency_ms) }}
          </span>
          <q-tooltip class="bg-slate-900 text-caption q-pa-xs">
            <div>Stage {{ step.step }}: <strong>{{ step.name }}</strong></div>
            <div>Status: {{ step.status.toUpperCase() }}</div>
            <div v-if="step.latency_ms > 0">Duration: {{ formatLatency(step.latency_ms) }}</div>
            <div class="q-mt-xs text-grey-4">{{ step.detail }}</div>
          </q-tooltip>
        </div>

        <!-- Connector Arrow -->
        <q-icon
          v-if="index < steps.length - 1"
          name="chevron_right"
          size="14px"
          color="grey-4"
          class="q-mx-none"
        />
      </template>
    </div>

    <!-- Expandable Log Detail Drawer -->
    <q-slide-transition>
      <div v-if="isExpanded || selectedStep !== null" class="trace-detail-card q-mt-xs">
        <div class="row items-center justify-between q-mb-xs">
          <span class="text-caption text-weight-bold text-grey-7">
            {{ selectedStep !== null ? `Stage ${selectedStep} Diagnostics:` : 'All Stage Logs:' }}
          </span>
          <q-btn v-if="selectedStep !== null" flat dense size="xs" label="Show All" @click="selectedStep = null" />
        </div>
        <div class="q-gutter-y-xs">
          <div
            v-for="s in displayedSteps"
            :key="s.step"
            class="detail-log-row row items-start q-gutter-x-sm"
          >
            <q-badge
              :color="s.status === 'blocked' ? 'negative' : 'positive'"
              class="text-weight-bold"
              style="font-size: 10px;"
            >
              {{ s.step }}
            </q-badge>
            <div class="col">
              <span class="text-weight-bold text-caption text-dark q-mr-xs">{{ s.name }}:</span>
              <span class="text-caption text-slate-700 mono-font">{{ s.detail }}</span>
            </div>
            <span class="text-caption text-grey-5 mono-font">
              {{ formatLatency(s.latency_ms) }}
            </span>
          </div>
        </div>
      </div>
    </q-slide-transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { TraceStep } from '../stores/chat'

const props = defineProps<{
  steps: TraceStep[]
}>()

const isExpanded = ref(false)
const selectedStep = ref<number | null>(null)

const displayedSteps = computed(() => {
  if (selectedStep.value !== null) {
    return props.steps.filter(s => s.step === selectedStep.value)
  }
  return props.steps
})

function toggleStep(stepNum: number) {
  if (selectedStep.value === stepNum) {
    selectedStep.value = null
  } else {
    selectedStep.value = stepNum
  }
}

function formatLatency(ms: number): string {
  if (!ms || ms === 0) return ''
  if (ms >= 1000) {
    return `${(ms / 1000).toFixed(1)}s`
  }
  if (ms < 1) {
    return `${ms.toFixed(2)}ms`
  }
  return `${ms.toFixed(1)}ms`
}

function getStepIcon(status: string): string {
  switch (status.toLowerCase()) {
    case 'done':
      return 'check'
    case 'blocked':
      return 'gpp_bad'
    case 'running':
      return 'sync'
    default:
      return 'schedule'
  }
}

function getStepClass(status: string): string {
  switch (status.toLowerCase()) {
    case 'done':
      return 'step-done'
    case 'blocked':
      return 'step-blocked'
    case 'running':
      return 'step-running'
    default:
      return 'step-pending'
  }
}
</script>

<style scoped>
.trace-wrapper {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 6px 12px;
}

.trace-pill-bar {
  padding-bottom: 2px;
}

.trace-step-pill {
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.1px;
  transition: all 0.15s ease-in-out;
  border: 1px solid transparent;
}

.trace-step-pill:hover {
  transform: translateY(-1px);
}

.step-num {
  font-weight: 700;
  margin-right: 3px;
}

.step-name {
  white-space: nowrap;
}

.step-latency {
  margin-left: 4px;
  font-size: 9.5px;
  opacity: 0.75;
  font-family: var(--font-mono);
}

.step-done {
  background: #ecfdf5;
  color: #065f46;
  border-color: #a7f3d0;
}

.step-blocked {
  background: #fef2f2;
  color: #991b1b;
  border-color: #fecaca;
  font-weight: 700;
}

.step-running {
  background: #eff6ff;
  color: #1e40af;
  border-color: #bfdbfe;
}

.step-pending {
  background: #f1f5f9;
  color: #64748b;
  border-color: #e2e8f0;
}

.selected-step {
  box-shadow: 0 0 0 2px #4f46e5;
}

.trace-detail-card {
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 11.5px;
}

.detail-log-row {
  padding: 3px 0;
  border-bottom: 1px dashed #f1f5f9;
}
.detail-log-row:last-child {
  border-bottom: none;
}
</style>
