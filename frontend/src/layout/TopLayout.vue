<script setup lang="ts">
</script>

<template>
  <el-container class="top-layout" direction="vertical">
    <el-header class="top-header">
      <slot name="nav" />
    </el-header>
    <el-main class="top-main">
      <slot name="main" />
    </el-main>
  </el-container>
</template>

<style scoped>
.top-layout { height: 100vh; }
.top-header { width: 100%; display: flex; position: sticky; top: 0; z-index: 10; overflow: hidden; height: auto; padding: 0; }
.top-main { flex: 1; padding: 16px; overflow: auto; }
</style>
