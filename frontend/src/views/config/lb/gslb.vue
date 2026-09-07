<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import DeviceFilter from '@/ui/DeviceFilter.vue'
import { getGtmWideips, getGtmPools } from '@/api/config'

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

watch(filterDevice, fetchData)
onMounted(fetchData)
</script>

<template>
  <PageLayout title="域名解析管理">
    <template #actions>
      <DeviceFilter v-model="filterDevice" />
    </template>
    <el-tabs v-model="activeTab" class="page-tabs">
      <el-tab-pane label="Wide IP" name="wideip">
        <DataTable :data="wideips" :loading="loading" size="small">
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
        </DataTable>
      </el-tab-pane>
      <el-tab-pane label="Pool" name="pool">
        <DataTable :data="pools" :loading="loading" size="small">
          <el-table-column prop="device_hostname" label="设备" width="140" sortable />
          <el-table-column prop="name" label="名称" width="180" sortable />
          <el-table-column prop="lb_mode" label="负载模式" width="120" />
          <el-table-column prop="alternate_mode" label="备选模式" width="120" />
          <el-table-column prop="fallback_mode" label="回退模式" width="120" />
          <el-table-column prop="fallback_ip" label="回退IP" width="140" />
          <el-table-column prop="ttl" label="TTL" width="70" />
        </DataTable>
      </el-tab-pane>
    </el-tabs>
  </PageLayout>
</template>

<style scoped>
.page-tabs { flex: 1; min-height: 0; }
</style>
