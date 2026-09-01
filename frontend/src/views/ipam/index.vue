<script setup lang="ts">
import { getSubnets, createSubnet, updateSubnet, deleteSubnet } from '@/api/ipam'
import { getTags } from '@/api/ipam'

const subnets = ref<any[]>([])
const tags = ref<any[]>([])
const loading = ref(false)
const search = ref('')
const filterTag = ref<number | ''>('')
const editVisible = ref(false)
const editForm = ref<any>(null)
const isNew = ref(false)

const filteredData = computed(() => {
  if (!search.value) return subnets.value
  const kw = search.value.toLowerCase()
  return subnets.value.filter((s: any) =>
    s.network?.toLowerCase().includes(kw) || s.description?.toLowerCase().includes(kw)
  )
})

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterTag.value) params.tag = filterTag.value
    const res = await getSubnets(params)
    subnets.value = res.data.results || res.data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const fetchTags = async () => {
  try {
    const res = await getTags()
    tags.value = res.data.results || res.data || []
  } catch { /* ignore */ }
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

const handleSave = async () => {
  if (!editForm.value?.network) {
    ElMessage.warning('请输入网段')
    return
  }
  try {
    if (isNew.value) await createSubnet(editForm.value)
    else await updateSubnet(editForm.value.id, editForm.value)
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.network?.[0] || '保存失败')
  }
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除 ${row.network}？`, '提示', { type: 'warning' })
  await deleteSubnet(row.id)
  ElMessage.success('已删除')
  fetchData()
}

onMounted(() => { fetchTags(); fetchData() })
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>IP 管理</h2>
      <div class="header-actions">
        <el-select v-model="filterTag" placeholder="标签" clearable style="width: 120px" @change="fetchData">
          <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
        <el-input v-model="search" placeholder="搜索网段/描述" clearable style="width: 200px" />
        <el-button type="primary" @click="openAdd">新增网段</el-button>
      </div>
    </div>

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
            <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editVisible" :title="isNew ? '新增网段' : '编辑网段'" width="500px">
      <el-form v-if="editForm" label-width="80px">
        <el-form-item label="网段" required>
          <el-input v-model="editForm.network" placeholder="如 10.0.0.0/24" />
        </el-form-item>
        <el-form-item label="网关">
          <el-input v-model="editForm.gateway" placeholder="如 10.0.0.1" />
        </el-form-item>
        <el-form-item label="VLAN">
          <el-input v-model="editForm.vlan" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="editForm.tags" multiple filterable placeholder="选择标签" style="width: 100%">
            <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 1.2rem; font-weight: 600; }
.header-actions { display: flex; gap: 8px; }
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
