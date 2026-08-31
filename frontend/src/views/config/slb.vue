<script setup lang="ts">
import { getLtmVirtualServers, getLtmPools } from '@/api/config'
import { getDevices } from '@/api/devices'

const devices = ref<any[]>([])
const virtualServers = ref<any[]>([])
const pools = ref<any[]>([])
const loading = ref(false)
const filterDevice = ref<number | ''>('')
const activeTab = ref('vs')

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterDevice.value) params.device = filterDevice.value
    const [vsRes, poolRes] = await Promise.all([getLtmVirtualServers(params), getLtmPools(params)])
    virtualServers.value = vsRes.data.results || vsRes.data || []
    pools.value = poolRes.data.results || poolRes.data || []
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
      <h2>负载均衡管理</h2>
      <div class="header-actions">
        <el-select v-model="filterDevice" placeholder="设备" clearable style="width: 160px" @change="fetchData">
          <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
        </el-select>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="page-tabs">
      <el-tab-pane label="Virtual Server" name="vs">
        <el-table v-loading="loading" :data="virtualServers" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="140" sortable />
          <el-table-column prop="name" label="名称" width="180" sortable />
          <el-table-column prop="vs_address" label="虚拟地址" width="140" />
          <el-table-column prop="vs_port" label="端口" width="80" />
          <el-table-column prop="protocol" label="协议" width="80" />
          <el-table-column prop="pool" label="关联池" width="140" />
          <el-table-column prop="snat_type" label="SNAT" width="100" />
          <el-table-column prop="persist" label="会话保持" width="100" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="Pool" name="pool">
        <el-table v-loading="loading" :data="pools" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="140" sortable />
          <el-table-column prop="name" label="名称" width="180" sortable />
          <el-table-column prop="mode" label="负载模式" width="120" />
          <el-table-column prop="monitors" label="监控" min-width="200">
            <template #default="{ row }">
              <el-tag v-for="m in (row.monitors || [])" :key="m" size="small" style="margin-right: 4px">{{ m }}</el-tag>
              <span v-if="!row.monitors?.length" style="color: #c0c4cc">-</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 1.2rem; font-weight: 600; }
.header-actions { display: flex; gap: 8px; }
.page-tabs { flex: 1; min-height: 0; }
</style>
