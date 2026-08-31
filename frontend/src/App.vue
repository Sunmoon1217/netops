<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NavBar from '@/layout/NavBar.vue'

const route = useRoute()
const authStore = useAuthStore()

if (authStore.isAuthenticated) {
  authStore.fetchUser()
}
</script>

<template>
  <div v-if="route.name !== 'login'" class="app-layout">
    <NavBar />
    <main class="app-main">
      <router-view />
    </main>
  </div>
  <router-view v-else />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
html, body, #app {
  height: 100%;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
}
</style>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}
.app-main {
  flex: 1;
  overflow: hidden;
  padding: 16px;
}
</style>
