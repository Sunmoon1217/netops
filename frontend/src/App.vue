<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useLayoutStore } from '@/stores/layout'
import AppNav from '@/ui/navigation/AppNav.vue'
import FloatingActions from '@/ui/navigation/FloatingActions.vue'
import TopLayout from '@/layout/TopLayout.vue'
import SideLayout from '@/layout/SideLayout.vue'
const Login = () => import('@/views/login/Login.vue')

const route = useRoute()
const authStore = useAuthStore()
const layoutStore = useLayoutStore()

const isLoginPage = computed(() => route.path === '/login')
const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentLayout = computed(() => layoutStore.mode === 'top' ? TopLayout : SideLayout)

onMounted(() => {
  if (authStore.isAuthenticated) {
    authStore.fetchUser()
  }
})
</script>

<template>
  <!-- 登录页 -->
  <Login v-if="isLoginPage" />

  <!-- 未认证：显示登录页 -->
  <Login v-else-if="!isAuthenticated" />

  <!-- 已认证：正常布局 -->
  <component v-else :is="currentLayout">
    <template #nav><AppNav /></template>
    <template #main><router-view /></template>
  </component>

  <!-- 浮动按钮（仅登录后显示） -->
  <FloatingActions v-if="isAuthenticated && !isLoginPage" />
</template>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, #app { height: 100%; width: 100%; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--el-bg-color-page, #f5f7fa);
}
</style>
