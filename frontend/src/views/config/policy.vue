<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import DeviceFilter from '@/ui/DeviceFilter.vue'
import { useCrudApi } from '@/composables/useCrudApi'

const { data: policies, loading, search, filteredData, fetchData } = useCrudApi(['name', 'policy_id'])
const filterDevice = ref<number | ''>('')

const displayed = computed(() => {
  if (!filterDevice.value) return filteredData.value
  return filteredData.value.filter((p: any) => p.device === filterDevice.value)
})

const fetchAll = () => {
  const params = filterDevice.value ? `?device=${filterDevice.value}` : ''
  fetchData(() => fetch(`/api/assets/policies/${params}`).then(r => r.json()))
}

watch(filterDevice, () => fetchAll())
onMounted(fetchAll)
</script>

<template>
  <PageLayout title="访问策略">
    <template #actions>
      <DeviceFilter v-model="filterDevice" />
      <el-input v-model="search" placeholder="搜索策略名称/ID" clearable style="width: 200px" />
    </template>
    <div class="table-wrapper">
      <DataTable :data="displayed" :loading="loading">
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
      </DataTable>
    </div>
  </PageLayout>
</template>

<style scoped>
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
