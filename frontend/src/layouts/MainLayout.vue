<template>
  <q-layout view="hHh lpR fFf" class="full-height apple-canvas-ambient">
    <!-- Minimalist Apple Top Navigation Bar (58px height) -->
    <q-header class="apple-glass-nav text-white">
      <div class="row items-center justify-between no-wrap q-px-md" style="height: 58px;">
        <!-- Left: Logo + Title -->
        <div class="row items-center no-wrap cursor-pointer" @click="leftDrawerOpen = !leftDrawerOpen">
          <img src="/icon.png" alt="TruCortex Logo" class="nav-logo q-mr-sm" />
          <img src="/logo.svg" alt="TransUnion CIBIL" class="cibil-nav-logo" />
          <span class="apple-brand-separator q-mx-sm">/</span>
          <span class="apple-brand-sub">TruCortex x Bloomfire KMP</span>
          <q-tooltip class="bg-black text-caption">Toggle Knowledge Explorer</q-tooltip>
        </div>

        <!-- Center: View Switcher (Platform Admin Only) -->
        <div class="row items-center justify-center">
          <div v-if="authStore.isPlatformAdmin" class="apple-segmented-toggle row items-center">
            <button
              type="button"
              class="segmented-toggle-btn cursor-pointer row items-center no-wrap"
              :class="{ 'segmented-toggle-active': authStore.activeView === 'chat' }"
              @click="authStore.activeView = 'chat'"
            >
              <q-icon name="chat" size="13px" class="q-mr-xs text-blue-4" />
              <span>Intelligence Chat</span>
            </button>
            <button
              type="button"
              class="segmented-toggle-btn cursor-pointer row items-center no-wrap"
              :class="{ 'segmented-toggle-active': authStore.activeView === 'admin' }"
              @click="authStore.activeView = 'admin'"
            >
              <q-icon name="admin_panel_settings" size="14px" class="q-mr-xs text-amber-5" />
              <span>Enterprise Admin</span>
            </button>
          </div>
        </div>

        <!-- Right: Role / Department Identity Pill Badge -->
        <div class="row items-center no-wrap">
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
                <span class="user-name text-secondary">{{ authStore.currentUser.full_name }}</span>
              </div>
            </template>

            <!-- Role Switcher Dropdown (Apple Frosted Style) -->
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
                @click="switchUser(u)"
              >
                <q-item-section avatar style="min-width: 28px;">
                  <span class="dept-dot" :style="{ backgroundColor: authStore.departmentColors[u.department] || '#0A84FF' }"></span>
                </q-item-section>
                <q-item-section>
                  <div class="row items-center justify-between no-wrap">
                    <q-item-label class="text-weight-medium text-white text-caption">
                      {{ u.full_name }}
                    </q-item-label>
                    <span
                      class="mini-role-badge q-ml-xs"
                      :class="u.is_admin ? 'mini-admin' : (u.is_owner ? 'mini-owner' : 'mini-analyst')"
                    >
                      {{ u.is_admin ? 'Admin' : (u.is_owner ? 'Owner' : 'Analyst') }}
                    </span>
                  </div>
                  <q-item-label caption class="text-secondary" style="font-size: 10.5px;">
                    {{ u.role_title || u.department }}
                  </q-item-label>
                </q-item-section>
                <q-item-section v-if="u.username === authStore.currentUser.username" side>
                  <q-icon name="check" size="14px" color="blue-4" />
                </q-item-section>
              </q-item>

              <q-separator dark class="q-my-xs" style="opacity: 0.1;" />
              <q-item
                v-if="authStore.isPlatformAdmin"
                clickable
                v-close-popup
                class="apple-dropdown-item"
                @click="authStore.activeView = 'admin'"
              >
                <q-item-section avatar style="min-width: 28px;">
                  <q-icon name="admin_panel_settings" size="16px" color="blue-4" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-caption text-blue-4 text-weight-medium">Open Admin Dashboard</q-item-label>
                </q-item-section>
              </q-item>
              <q-item clickable v-close-popup class="apple-dropdown-item" @click="authStore.logout()">
                <q-item-section avatar style="min-width: 28px;">
                  <q-icon name="logout" size="16px" color="grey-5" />
                </q-item-section>
                <q-item-section>
                  <q-item-label class="text-caption text-secondary">Sign Out</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-btn-dropdown>
        </div>
      </div>
    </q-header>

    <!-- Left Drawer: Subtle Knowledge Repository Explorer -->
    <q-drawer
      v-model="leftDrawerOpen"
      bordered
      :width="300"
      side="left"
      class="apple-sidebar"
    >
      <RepositoryDrawer @open-upload="handleUploadClick" />
    </q-drawer>

    <!-- Main Content Area: Switches between Dedicated Admin Dashboard (Admin Only) and Intelligence Chat -->
    <q-page-container class="full-height">
      <!-- Dedicated Standalone Admin Panel with Ingestion Suite + Impact Radar (Platform Admin Only) -->
      <AdminPage
        v-if="authStore.isPlatformAdmin && authStore.activeView === 'admin'"
        @switch-to-chat="authStore.activeView = 'chat'"
      />

      <!-- Primary Apple-Grade Intelligence Extractive Chat (For Normal Users and Chat Mode) -->
      <ChatPage
        v-else
        @open-upload="handleUploadClick"
        @open-admin="authStore.activeView = 'admin'"
      />
    </q-page-container>

    <!-- Interactive Document Viewer Modal -->
    <DocumentViewerModal />

    <!-- Fallback Upload Knowledge Document Dialog (For non-admin owners) -->
    <UploadModal v-model="showUploadModal" />

    <!-- Enterprise Admin Console Quick Dialog -->
    <AdminPanelModal v-model="showAdminModal" />
  </q-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import RepositoryDrawer from '../components/RepositoryDrawer.vue'
import DocumentViewerModal from '../components/DocumentViewerModal.vue'
import UploadModal from '../components/UploadModal.vue'
import AdminPanelModal from '../components/AdminPanelModal.vue'
import ChatPage from '../pages/ChatPage.vue'
import AdminPage from '../pages/AdminPage.vue'
import { useConflictsStore } from '../stores/conflicts'
import { useAuthStore, User } from '../stores/auth'
import { useFoldersStore } from '../stores/folders'

const leftDrawerOpen = ref(false)
const showUploadModal = ref(false)
const showAdminModal = ref(false)

const conflictsStore = useConflictsStore()
const authStore = useAuthStore()
const foldersStore = useFoldersStore()

onMounted(async () => {
  await authStore.fetchUsers()
  await conflictsStore.fetchConflicts()
  // Normal users strictly get normal chat access with zero admin clutter
  if (!authStore.isPlatformAdmin) {
    authStore.activeView = 'chat'
  }
})

function switchUser(u: User) {
  authStore.setUser(u)
  foldersStore.fetchTree()
  // Normal users strictly get normal chat access
  if (!u.is_admin && !['ananya', 'vikram'].includes(u.username)) {
    authStore.activeView = 'chat'
  }
}

function handleUploadClick() {
  if (authStore.isPlatformAdmin) {
    authStore.activeView = 'admin'
  }
}
</script>

<style scoped>
.nav-logo {
  width: 28px;
  height: 28px;
  object-fit: contain;
  border-radius: 6px;
  filter: drop-shadow(0 0 6px rgba(99, 179, 237, 0.5));
}

.cibil-nav-logo {
  height: 28px;
  width: auto;
  max-width: 150px;
  object-fit: contain;
  display: inline-block;
  vertical-align: middle;
  filter: drop-shadow(0 0 6px rgba(0, 166, 202, 0.45));
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.cibil-nav-logo:hover {
  transform: scale(1.02);
}

.apple-brand-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #F5F5F7;
}

.apple-brand-separator {
  color: rgba(255, 255, 255, 0.35);
  font-size: 15px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  user-select: none;
}

.apple-brand-sub {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: -0.015em;
  color: #D1D1D6;
  line-height: 1;
  display: inline-flex;
  align-items: center;
}

.apple-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #0A84FF;
  box-shadow: 0 0 10px #0A84FF;
}

/* Center Segmented View Switcher */
.apple-segmented-toggle {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 9999px;
  padding: 3px;
}

.segmented-toggle-btn {
  background: transparent;
  border: none;
  border-radius: 9999px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  color: #8E8E93;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.segmented-toggle-btn:hover {
  color: #F5F5F7;
}

.segmented-toggle-active {
  background: rgba(255, 255, 255, 0.12);
  color: #FFFFFF !important;
  font-weight: 600;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.radar-tag-pill {
  background: rgba(255, 159, 10, 0.25);
  color: #FF9F0A;
  font-size: 9.5px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 9999px;
  border: 1px solid rgba(255, 159, 10, 0.4);
}

/* Center Role Pill */
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

/* Right Navigation Buttons */
.apple-nav-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #F5F5F7;
  border-radius: 9999px;
  padding: 6px 14px;
  font-size: 12px;
  font-family: inherit;
  font-weight: 500;
  letter-spacing: -0.01em;
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.apple-nav-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.18);
  transform: scale(1.02);
}

.apple-nav-btn:active {
  transform: scale(0.98);
}

.btn-restricted {
  border-color: rgba(255, 69, 58, 0.3) !important;
  color: #8E8E93 !important;
}

.admin-active-btn {
  background: rgba(10, 132, 255, 0.12) !important;
  border-color: rgba(10, 132, 255, 0.35) !important;
  color: #FFFFFF !important;
}

.admin-dot-indicator {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #0A84FF;
  box-shadow: 0 0 6px #0A84FF;
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

.radar-active {
  border-color: rgba(255, 159, 10, 0.4);
}

.radar-count-pill {
  background: #FF9F0A;
  color: #000000;
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 999px;
  line-height: 1.2;
}

/* Sidebar & Drawer Styling */
.apple-sidebar {
  background: rgba(14, 14, 16, 0.88) !important;
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.apple-radar-drawer {
  background: rgba(16, 16, 18, 0.92) !important;
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  border-left: 1px solid rgba(255, 255, 255, 0.08);
}

.border-bottom-hairline {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.apple-close-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #8E8E93;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.apple-close-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #F5F5F7;
}

.apple-pill-secondary {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 6px;
  color: #F5F5F7;
}

/* Dropdown Menu */
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
