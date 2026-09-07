<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { ElTag } from 'element-plus'
import { getDevices } from '@/api/devices'

const devices = ref<any[]>([])
const policies = ref<any[]>([])
const loading = ref(false)
const filterDevice = ref<number | ''>('')
const search = ref('')

const filteredData = computed(() => {
  let data = policies.value
  if (filterDevice.value) data = data.filter((p: any) => p.device === filterDevice.value)
  if (search.value) {
    const kw = search.value.toLowerCase()
    data = data.filter((p: any) =>
      p.name?.toLowerCase().includes(kw) || p.policy_id?.toLowerCase().includes(kw)
    )
  }
  return data
})

const fetchData = async () => {
  loading.value = true
  try {
    const params = filterDevice.value ? `?device=${filterDevice.value}` : ''
    const res = await fetch(`/api/assets/policies/${params}`)
    const data = await res.json()
    policies.value = data.results || data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const fetchDevices = async () => {
  try {
    const res = await getDevices()
    devices.value = res.data.results || res.data || []
  } catch { /* ignore */ }
}

onMounted(() => { fetchDevices(); fetchData() })
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>访问策略</h2>
      <div class="header-actions">
        <el-select v-model="filterDevice" placeholder="设备" clearable style="width: 140px" @change="fetchData">
          <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
        </el-select>
        <el-input v-model="search" placeholder="搜索策略名称/ID" clearable style="width: 200px" />
      </div>
    </div>
    <div class="table-wrapper">
      <el-table v-loading="loading" :data="filteredData" stripe border height="100%">
        <el-table-column prop="device_name" label="设备" width="140" />
        <el-table-column prop="policy_id" label="策略ID" width="100" />
        <el-table-column prop="order" label="顺序" width="70" />
        <el-table-column prop="name" label="策略名称" width="160" />
        <el-table-column prop="action" label="动作" width="80">
          <template #default="{ row }">
            <el-tag :type="row.action === 'allow' ? 'success' : 'danger'" size="small">{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="log" label="日志" width="60" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.log" type="warning" size="small">开</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 1.2rem; font-weight: 600; }
.header-actions { display: flex; gap: 8px; }
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
