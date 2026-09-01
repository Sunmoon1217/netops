<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLayoutStore } from '@/stores/layout'
import AppNav from '@/ui/navigation/AppNav.vue'
import TopLayout from '@/layout/TopLayout.vue'
import SideLayout from '@/layout/SideLayout.vue'

const route = useRoute()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()

if (authStore.isAuthenticated) {
  authStore.fetchUser()
}
</script>

<template>
  <div v-if="route.name !== 'login'" class="app-root">
    <!-- 顶栏布局 -->
    <TopLayout v-if="layoutStore.mode === 'top'">
      <template #nav><AppNav /></template>
      <template #main><router-view /></template>
    </TopLayout>
    <!-- 侧栏布局 -->
    <SideLayout v-else>
      <template #nav><AppNav /></template>
      <template #main><router-view /></template>
    </SideLayout>
  </div>
  <router-view v-else />
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: var(--el-bg-color-page, #f5f7fa); }
</style>
