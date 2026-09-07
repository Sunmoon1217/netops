<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import { useCrudApi } from '@/composables/useCrudApi'
import { getSubnets, deleteSubnet, getTags } from '@/api/ipam'

const router = useRouter()
const { data: subnets, loading, search, filteredData, fetchData, handleDelete } = useCrudApi(['network', 'description'])
const filterTag = ref<number | ''>('')
const tags = ref<any[]>([])

const fetchAll = () => {
  const params: Record<string, any> = {}
  if (filterTag.value) params.tag = filterTag.value
  fetchData(() => getSubnets(params))
}

const remove = (row: any) => {
  handleDelete(row.network, () => deleteSubnet(row.id), fetchAll)
}

onMounted(async () => {
  fetchAll()
  try { const res = await getTags(); tags.value = res.data.results || res.data || [] } catch {}
})
</script>

<template>
  <PageLayout title="IP 管理">
    <template #actions>
      <el-select v-model="filterTag" placeholder="标签" clearable style="width: 120px" @change="fetchAll">
        <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
      </el-select>
      <el-input v-model="search" placeholder="搜索网段/描述" clearable style="width: 200px" />
      <el-button type="primary" @click="router.push('/ipam/subnets/create')">新增网段</el-button>
    </template>
    <div class="table-wrapper">
      <DataTable :data="filteredData" :loading="loading">
        <el-table-column prop="network" label="网段" width="160" sortable />
        <el-table-column prop="gateway" label="网关" width="140" />
        <el-table-column prop="vlan" label="VLAN" width="80" />
        <el-table-column prop="tag_names" label="标签" width="150">
          <template #default="{ row }"><el-tag v-for="t in row.tag_names" :key="t" size="small" style="margin-right: 4px">{{ t }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="total_ips" label="总IP" width="80" />
        <el-table-column prop="used_ips" label="已用" width="70" />
        <el-table-column prop="utilization" label="使用率" width="90">
          <template #default="{ row }"><el-progress :percentage="row.utilization || 0" :stroke-width="14" :text-inside="true" style="width: 70px" /></template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="router.push(`/ipam/subnets/${row.id}/edit`)">编辑</el-button>
            <el-button size="small" link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </DataTable>
    </div>
  </PageLayout>
</template>

<style scoped>
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
