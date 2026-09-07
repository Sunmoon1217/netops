<script setup lang="ts">
import { useThemeStore } from '@/stores/theme'
import { IconSun, IconMoon } from './menu-icons'

const themeStore = useThemeStore()
</script>

<template>
  <div class="floating-actions">
    <el-tooltip :content="themeStore.isDark ? '切换为亮色模式' : '切换为暗色模式'" placement="left">
      <el-button :icon="themeStore.isDark ? IconMoon : IconSun" circle size="small" @click="themeStore.toggleDark()" />
    </el-tooltip>
  </div>
</template>

<style scoped>
.floating-actions {
  position: fixed;
  top: 12px;
  right: 16px;
  z-index: 2000;
}
</style>
