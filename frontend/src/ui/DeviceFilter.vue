<script setup lang="ts">
import { getDevices } from '@/api/devices'

const props = defineProps<{ modelValue: number | '' }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: number | ''): void; (e: 'change', v: number | ''): void }>()

const devices = ref<any[]>([])

const handleChange = (v: number | '') => {
  emit('update:modelValue', v)
  emit('change', v)
}

onMounted(async () => {
  try {
    const res = await getDevices()
    devices.value = res.data.results || res.data || []
  } catch { /* ignore */ }
})
</script>

<template>
  <el-select :model-value="modelValue" placeholder="设备" clearable style="width: 140px" @update:model-value="handleChange">
    <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
  </el-select>
</template>
