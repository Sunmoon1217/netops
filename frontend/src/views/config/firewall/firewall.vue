<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import DeviceFilter from '@/ui/DeviceFilter.vue'
import { useCrudApi } from '@/composables/useCrudApi'

const { data: natRules, loading, search, filteredData, fetchData } = useCrudApi(['name', 'source', 'destination'])
const filterDevice = ref<number | ''>('')

const displayed = computed(() => {
  if (!filterDevice.value) return filteredData.value
  return filteredData.value.filter((r: any) => r.device === filterDevice.value)
})

const fetchAll = () => {
  const params = filterDevice.value ? `?device=${filterDevice.value}` : ''
  fetchData(() => fetch(`/api/assets/nat-rules/${params}`).then(r => r.json()))
}

watch(filterDevice, fetchAll)
onMounted(fetchAll)
</script>

<template>
  <PageLayout title="NAT 规则">
    <template #actions>
      <DeviceFilter v-model="filterDevice" />
      <el-input v-model="search" placeholder="搜索规则名称" clearable style="width: 200px" />
    </template>
    <div class="table-wrapper">
      <DataTable :data="displayed" :loading="loading">
        <el-table-column prop="device_name" label="设备" width="140" />
        <el-table-column prop="order" label="顺序" width="70" />
        <el-table-column prop="name" label="规则名称" width="160" />
        <el-table-column prop="nat_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.nat_type === 'snat' ? 'primary' : row.nat_type === 'dnat' ? 'warning' : 'danger'" size="small">{{ row.nat_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="启用" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '是' : '否' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
      </DataTable>
    </div>
  </PageLayout>
</template>

<style scoped>
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
