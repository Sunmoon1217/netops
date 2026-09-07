<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AppNav from '@/ui/navigation/AppNav.vue'
import SideLayout from '@/layout/SideLayout.vue'
import Login from '@/views/login/Login.vue'

const route = useRoute()
const authStore = useAuthStore()

const isLoginPage = computed(() => route.path === '/login')
const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(() => {
  if (authStore.isAuthenticated) authStore.fetchUser()
})
</script>

<template>
  <Login v-if="isLoginPage" />
  <Login v-else-if="!isAuthenticated" />
  <SideLayout v-else>
    <template #nav><AppNav /></template>
    <template #main><router-view /></template>
  </SideLayout>
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; width: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--el-bg-color-page, #f5f7fa);
}
</style>
