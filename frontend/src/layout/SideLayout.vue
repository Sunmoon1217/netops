<script setup lang="ts">
import { computed } from 'vue'
import { useLayoutStore } from '@/stores/layout'

const layoutStore = useLayoutStore()
const sidebarWidth = computed(() => layoutStore.sidebarWidth)
</script>

<template>
  <el-container class="side-layout" direction="horizontal">
    <el-aside :width="sidebarWidth + 'px'" class="side-aside">
      <slot name="nav" />
    </el-aside>
    <el-main class="side-main">
      <slot name="main" />
    </el-main>
  </el-container>
</template>

<style scoped>
.side-layout { height: 100vh; }
.side-aside {
  overflow-y: auto;
  overflow-x: hidden;
  transition: width 0.3s;
  background: var(--el-fill-color-blank, #fff);
  border-right: 1px solid var(--el-border-color, #dcdfe6);
}
.side-main {
  flex: 1;
  padding: 16px;
  overflow: auto;
  background: var(--el-bg-color-page, #f5f7fa);
}
</style>
