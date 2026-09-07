<script setup lang="ts">
import { useLayoutStore } from '@/stores/layout'
import { useThemeStore } from '@/stores/theme'
import { IconLayoutTop, IconLayoutSide, IconSun, IconMoon } from './menu-icons'
import { computed } from 'vue'

const layoutStore = useLayoutStore()
const themeStore = useThemeStore()
const isVertical = computed(() => layoutStore.mode === 'side')
</script>

<template>
  <div class="floating-actions">
    <el-tooltip :content="isVertical ? '切换为顶栏布局' : '切换为侧栏布局'" placement="left">
      <el-button :icon="isVertical ? IconLayoutSide : IconLayoutTop" circle size="small" @click="layoutStore.setMode(isVertical ? 'top' : 'side')" />
    </el-tooltip>
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
  display: flex;
  gap: 8px;
}
</style>
