<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getDevices } from '@/api/devices'

const devices = ref<any[]>([])
const routes = ref<any[]>([])
const loading = ref(false)
const filterDevice = ref<number | ''>('')
const filterProtocol = ref('')
const search = ref('')

const protocolOptions = [
  { label: '静态', value: 'static' },
  { label: '直连', value: 'connected' },
  { label: 'OSPF', value: 'ospf' },
  { label: 'BGP', value: 'bgp' },
]

const filteredData = computed(() => {
  let data = routes.value
  if (filterDevice.value) data = data.filter((r: any) => r.device_id === filterDevice.value)
  if (filterProtocol.value) data = data.filter((r: any) => r.protocol === filterProtocol.value)
  if (search.value) {
    const kw = search.value.toLowerCase()
    data = data.filter((r: any) =>
      r.destination?.toLowerCase().includes(kw) ||
      r.nexthop?.toLowerCase().includes(kw) ||
      r.interface?.toLowerCase().includes(kw)
    )
  }
  return data
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/trace/routes/')
    const data = await res.json()
    routes.value = data.routes || []
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

const protocolTag = (p: string) => {
  const map: Record<string, string> = { static: 'warning', connected: 'success', ospf: 'primary', bgp: 'danger' }
  return map[p] || 'info'
}

onMounted(() => { fetchDevices(); fetchData() })
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>路由表</h2>
      <div class="header-actions">
        <el-select v-model="filterDevice" placeholder="设备" clearable style="width: 140px" @change="fetchData">
          <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
        </el-select>
        <el-select v-model="filterProtocol" placeholder="协议" clearable style="width: 100px">
          <el-option v-for="p in protocolOptions" :key="p.value" :label="p.label" :value="p.value" />
        </el-select>
        <el-input v-model="search" placeholder="搜索" clearable style="width: 180px" />
      </div>
    </div>
    <div class="table-wrapper">
      <el-table v-loading="loading" :data="filteredData" stripe border height="100%">
        <el-table-column prop="device" label="设备" width="140" sortable />
        <el-table-column prop="vrf" label="VRF" width="100" />
        <el-table-column prop="destination" label="目的网段" width="160" />
        <el-table-column prop="nexthop" label="下一跳" width="140" />
        <el-table-column prop="interface" label="出接口" width="150" />
        <el-table-column prop="protocol" label="协议" width="90">
          <template #default="{ row }">
            <el-tag :type="protocolTag(row.protocol) as any" size="small">{{ row.protocol }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric" label="度量值" width="80" />
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
