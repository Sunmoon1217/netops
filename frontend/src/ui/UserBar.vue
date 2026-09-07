<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { IconSun, IconMoon } from '@/ui/navigation/menu-icons'

const authStore = useAuthStore()
const themeStore = useThemeStore()
const searchQuery = ref('')

const handleLogout = async () => {
  await authStore.logout()
  window.location.href = '/login'
}
</script>

<template>
  <div class="user-bar">
    <div class="bar-left">
      <el-input
        v-model="searchQuery"
        placeholder="全局搜索"
        clearable
        prefix-icon="Search"
        style="width: 280px;"
        size="small"
      />
    </div>
    <div class="bar-right">
      <el-tooltip :content="themeStore.isDark ? '亮色模式' : '暗色模式'" placement="bottom">
        <el-button :icon="themeStore.isDark ? IconMoon : IconSun" size="small" @click="themeStore.toggleDark()" />
      </el-tooltip>
      <span class="username">{{ authStore.user?.username || 'admin' }}</span>
      <el-divider direction="vertical" />
      <el-button link type="danger" size="small" @click="handleLogout">登出</el-button>
    </div>
  </div>
</template>

<style scoped>
.user-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 42px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-bg-color);
  flex-shrink: 0;
}
.bar-left, .bar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.username {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
