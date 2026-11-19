<template>
  <div class="full-height apple-canvas-ambient">
    <!-- Authenticated Platform Interface -->
    <MainLayout v-if="authStore.isAuthenticated" />

    <!-- Startup Enterprise Login Screen -->
    <LoginPage v-else />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import MainLayout from './layouts/MainLayout.vue'
import LoginPage from './pages/LoginPage.vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(async () => {
  await authStore.fetchUsers()
})
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  background-color: #000000;
  color: #F5F5F7;
  overflow: hidden;
}
</style>
