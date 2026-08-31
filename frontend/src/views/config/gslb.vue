<script setup lang="ts">
import { getGtmWideips, getGtmPools } from '@/api/config'
import { getDevices } from '@/api/devices'

const devices = ref<any[]>([])
const wideips = ref<any[]>([])
const pools = ref<any[]>([])
const loading = ref(false)
const filterDevice = ref<number | ''>('')
const activeTab = ref('wideip')

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterDevice.value) params.device = filterDevice.value
    const [wRes, pRes] = await Promise.all([getGtmWideips(params), getGtmPools(params)])
    wideips.value = wRes.data.results || wRes.data || []
    pools.value = pRes.data.results || pRes.data || []
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
      <h2>域名解析管理</h2>
      <div class="header-actions">
        <el-select v-model="filterDevice" placeholder="设备" clearable style="width: 160px" @change="fetchData">
          <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
        </el-select>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="page-tabs">
      <el-tab-pane label="Wide IP" name="wideip">
        <el-table v-loading="loading" :data="wideips" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="140" sortable />
          <el-table-column prop="name" label="域名" width="220" sortable />
          <el-table-column prop="rtype" label="记录类型" width="100" />
          <el-table-column prop="lb_mode" label="负载模式" width="120" />
          <el-table-column prop="pools" label="关联池" min-width="200">
            <template #default="{ row }">
              <el-tag v-for="p in (row.pools || [])" :key="p" size="small" style="margin-right: 4px">{{ p }}</el-tag>
              <span v-if="!row.pools?.length" style="color: #c0c4cc">-</span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="Pool" name="pool">
        <el-table v-loading="loading" :data="pools" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="140" sortable />
          <el-table-column prop="name" label="名称" width="180" sortable />
          <el-table-column prop="lb_mode" label="负载模式" width="120" />
          <el-table-column prop="alternate_mode" label="备选模式" width="120" />
          <el-table-column prop="fallback_mode" label="回退模式" width="120" />
          <el-table-column prop="fallback_ip" label="回退IP" width="140" />
          <el-table-column prop="ttl" label="TTL" width="70" />
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
