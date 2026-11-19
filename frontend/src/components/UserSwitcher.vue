<template>
  <div class="row items-center">
    <q-btn-dropdown
      dense
      flat
      no-caps
      class="apple-role-pill"
      dropdown-icon="expand_more"
    >
      <template #label>
        <div class="row items-center no-wrap q-gutter-x-xs">
          <span class="dept-dot" :style="{ backgroundColor: authStore.currentDeptColor }"></span>
          <span class="dept-name text-weight-medium">{{ authStore.currentUser.department }}</span>
          <span class="role-separator">•</span>
          <span class="user-name">{{ authStore.currentUser.full_name }}</span>
        </div>
      </template>

      <q-list class="apple-dropdown-menu q-py-xs">
        <div class="q-px-sm q-py-xs text-caption text-secondary text-weight-medium" style="font-size: 11px;">
          SWITCH ENTERPRISE IDENTITY
        </div>

        <q-item
          v-for="u in authStore.users"
          :key="u.username"
          clickable
          v-close-popup
          class="apple-dropdown-item"
          :class="{ 'apple-dropdown-item-active': u.username === authStore.currentUser.username }"
          @click="selectUser(u)"
        >
          <q-item-section avatar style="min-width: 28px;">
            <span class="dept-dot" :style="{ backgroundColor: authStore.departmentColors[u.department] || '#0A84FF' }"></span>
          </q-item-section>

          <q-item-section>
            <q-item-label class="text-weight-medium text-white text-caption">{{ u.full_name }}</q-item-label>
            <q-item-label caption class="text-secondary" style="font-size: 10.5px;">
              {{ u.role_title || u.department }}
            </q-item-label>
          </q-item-section>

          <q-item-section v-if="u.username === authStore.currentUser.username" side>
            <q-icon name="check" size="14px" color="blue-4" />
          </q-item-section>
        </q-item>
      </q-list>
    </q-btn-dropdown>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore, User } from '../stores/auth'
import { useFoldersStore } from '../stores/folders'

const authStore = useAuthStore()
const foldersStore = useFoldersStore()

function selectUser(user: User) {
  authStore.setUser(user)
  foldersStore.fetchTree()
}
</script>

<style scoped>
.apple-role-pill {
  background: rgba(255, 255, 255, 0.06) !important;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 4px 12px;
  font-size: 12px;
  letter-spacing: -0.01em;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-role-pill:hover {
  background: rgba(255, 255, 255, 0.10) !important;
  border-color: rgba(255, 255, 255, 0.16);
}

.dept-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dept-name {
  color: #F5F5F7;
  font-size: 12px;
}

.role-separator {
  color: rgba(255, 255, 255, 0.3);
  font-size: 10px;
}

.user-name {
  color: #8E8E93;
  font-size: 12px;
}

.apple-dropdown-menu {
  background: #1A1A1E !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  min-width: 240px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
}

.apple-dropdown-item {
  border-radius: 8px;
  margin: 1px 4px;
  transition: background 0.15s ease;
}

.apple-dropdown-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.apple-dropdown-item-active {
  background: rgba(10, 132, 255, 0.12) !important;
}
</style>
