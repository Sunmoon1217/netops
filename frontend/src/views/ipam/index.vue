<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import { useCrudApi } from '@/composables/useCrudApi'
import { getSubnets, createSubnet, updateSubnet, deleteSubnet, getTags } from '@/api/ipam'

const { data: subnets, loading, search, filteredData, fetchData, handleSave, handleDelete } = useCrudApi(['network', 'description'])
const filterTag = ref<number | ''>('')
const editVisible = ref(false)
const editForm = ref<any>(null)
const isNew = ref(false)
const tags = ref<any[]>([])

const fetchAll = () => {
  const params: Record<string, any> = {}
  if (filterTag.value) params.tag = filterTag.value
  fetchData(() => getSubnets(params))
}

const openAdd = () => {
  editForm.value = { network: '', gateway: '', vlan: '', description: '', tags: [] }
  isNew.value = true
  editVisible.value = true
}

const openEdit = (row: any) => {
  editForm.value = { ...row, tags: row.tags || [] }
  isNew.value = false
  editVisible.value = true
}

const save = () => {
  if (!editForm.value?.network) { ElMessage.warning('请输入网段'); return }
  const fn = isNew.value
    ? () => createSubnet(editForm.value)
    : () => updateSubnet(editForm.value.id, editForm.value)
  handleSave(fn, () => { editVisible.value = false; fetchAll() })
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
      <el-button type="primary" @click="openAdd">新增网段</el-button>
    </template>
    <div class="table-wrapper">
      <el-table v-loading="loading" :data="filteredData" stripe border height="100%">
        <el-table-column prop="network" label="网段" width="160" sortable />
        <el-table-column prop="gateway" label="网关" width="140" />
        <el-table-column prop="vlan" label="VLAN" width="80" />
        <el-table-column prop="tag_names" label="标签" width="150">
          <template #default="{ row }">
            <el-tag v-for="t in row.tag_names" :key="t" size="small" style="margin-right: 4px">{{ t }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_ips" label="总IP" width="80" />
        <el-table-column prop="used_ips" label="已用" width="70" />
        <el-table-column prop="utilization" label="使用率" width="90">
          <template #default="{ row }">
            <el-progress :percentage="row.utilization || 0" :stroke-width="14" :text-inside="true" style="width: 70px" />
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <el-dialog v-model="editVisible" :title="isNew ? '新增网段' : '编辑网段'" width="500px">
      <el-form v-if="editForm" label-width="80px">
        <el-form-item label="网段" required><el-input v-model="editForm.network" placeholder="如 10.0.0.0/24" /></el-form-item>
        <el-form-item label="网关"><el-input v-model="editForm.gateway" placeholder="如 10.0.0.1" /></el-form-item>
        <el-form-item label="VLAN"><el-input v-model="editForm.vlan" /></el-form-item>
        <el-form-item label="标签">
          <el-select v-model="editForm.tags" multiple filterable placeholder="选择标签" style="width: 100%">
            <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述"><el-input v-model="editForm.description" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<style scoped>
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
