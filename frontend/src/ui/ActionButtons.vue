<script setup lang="ts">
defineProps<{
  editRoute?: string
  editLabel?: string
  showEdit?: boolean
  showDelete?: boolean
}>()

const emit = defineEmits<{ (e: 'edit'): void; (e: 'delete'): void }>()
</script>

<template>
  <span class="action-buttons">
    <el-button v-if="showEdit !== false" size="small" link type="primary" @click="editRoute ? null : emit('edit')">
      <router-link v-if="editRoute" :to="editRoute" class="action-link">{{ editLabel || '编辑' }}</router-link>
      <template v-else>{{ editLabel || '编辑' }}</template>
    </el-button>
    <el-button v-if="showDelete !== false" size="small" link type="danger" @click="emit('delete')">删除</el-button>
  </span>
</template>

<style scoped>
.action-buttons { display: inline-flex; gap: 4px; }
.action-link { color: inherit; text-decoration: none; }
</style>
