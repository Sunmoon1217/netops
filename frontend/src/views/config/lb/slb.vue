<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import DeviceFilter from '@/ui/DeviceFilter.vue'
import { getLtmVirtualServers, getLtmPools } from '@/api/config'

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

watch(filterDevice, fetchData)
onMounted(fetchData)
</script>

<template>
  <PageLayout title="负载均衡管理">
    <template #actions>
      <DeviceFilter v-model="filterDevice" />
    </template>
    <el-tabs v-model="activeTab" class="page-tabs">
      <el-tab-pane label="Virtual Server" name="vs">
        <DataTable :data="virtualServers" :loading="loading" size="small">
          <el-table-column prop="device_hostname" label="设备" width="140" sortable />
          <el-table-column prop="name" label="名称" width="180" sortable />
          <el-table-column prop="vs_address" label="虚拟地址" width="140" />
          <el-table-column prop="vs_port" label="端口" width="80" />
          <el-table-column prop="protocol" label="协议" width="80" />
          <el-table-column prop="pool" label="关联池" width="140" />
          <el-table-column prop="snat_type" label="SNAT" width="100" />
          <el-table-column prop="persist" label="会话保持" width="100" />
        </DataTable>
      </el-tab-pane>
      <el-tab-pane label="Pool" name="pool">
        <DataTable :data="pools" :loading="loading" size="small">
          <el-table-column prop="device_hostname" label="设备" width="140" sortable />
          <el-table-column prop="name" label="名称" width="180" sortable />
          <el-table-column prop="mode" label="负载模式" width="120" />
          <el-table-column prop="monitors" label="监控" min-width="200">
            <template #default="{ row }">
              <el-tag v-for="m in (row.monitors || [])" :key="m" size="small" style="margin-right: 4px">{{ m }}</el-tag>
              <span v-if="!row.monitors?.length" style="color: #c0c4cc">-</span>
            </template>
          </el-table-column>
        </DataTable>
      </el-tab-pane>
    </el-tabs>
  </PageLayout>
</template>

<style scoped>
.page-tabs { flex: 1; min-height: 0; }
</style>
