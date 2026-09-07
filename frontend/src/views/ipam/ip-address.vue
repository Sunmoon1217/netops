<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import { useCrudApi } from '@/composables/useCrudApi'
import { getIpAddresses, createIpAddress, updateIpAddress, deleteIpAddress } from '@/api/ipam'
import { getDevices } from '@/api/devices'

const { data: ipList, loading, search, filteredData, fetchData, handleSave, handleDelete } = useCrudApi(['ip_address', 'description'])
const filterStatus = ref('')
const editVisible = ref(false)
const editForm = ref<any>(null)
const isNew = ref(false)
const devices = ref<any[]>([])

const statusOptions = [
  { label: '已使用', value: 'used' },
  { label: '预留', value: 'reserved' },
  { label: '可用', value: 'available' },
]

const displayed = computed(() => {
  if (!filterStatus.value) return filteredData.value
  return filteredData.value.filter((i: any) => i.status === filterStatus.value)
})

const fetchAll = () => {
  const params: Record<string, any> = {}
  if (filterStatus.value) params.status = filterStatus.value
  fetchData(() => getIpAddresses(params))
}

const openAdd = () => {
  editForm.value = { ip_address: '', status: 'used', description: '' }
  isNew.value = true
  editVisible.value = true
}

const openEdit = (row: any) => {
  editForm.value = { ...row }
  isNew.value = false
  editVisible.value = true
}

const save = () => {
  if (!editForm.value?.ip_address) { ElMessage.warning('请输入 IP 地址'); return }
  const fn = isNew.value
    ? () => createIpAddress(editForm.value)
    : () => updateIpAddress(editForm.value.id, editForm.value)
  handleSave(fn, () => { editVisible.value = false; fetchAll() })
}

const remove = (row: any) => {
  handleDelete(row.ip_address, () => deleteIpAddress(row.id), fetchAll)
}

const statusTag = (s: string) => {
  const map: Record<string, string> = { used: 'danger', reserved: 'warning', available: 'success' }
  return (map[s] || 'info') as any
}

onMounted(async () => {
  fetchAll()
  try { const res = await getDevices(); devices.value = res.data.results || res.data || [] } catch {}
})
</script>

<template>
  <PageLayout title="IP 地址管理">
    <template #actions>
      <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 110px" @change="fetchAll">
        <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
      </el-select>
      <el-input v-model="search" placeholder="搜索 IP/描述" clearable style="width: 200px" />
      <el-button type="primary" @click="openAdd">新增 IP</el-button>
    </template>
    <div class="table-wrapper">
      <DataTable :data="displayed" :loading="loading">
        <el-table-column prop="ip_address" label="IP 地址" width="150" sortable />
        <el-table-column prop="subnet_network" label="所属网段" width="140" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTag(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device_hostname" label="关联设备" width="140" />
        <el-table-column prop="interface" label="接口" width="120" />
        <el-table-column prop="security_zone_name" label="安全区" width="100" />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </DataTable>
    </div>
    <el-dialog v-model="editVisible" :title="isNew ? '新增 IP 地址' : '编辑 IP 地址'" width="500px">
      <el-form v-if="editForm" label-width="90px">
        <el-form-item label="IP 地址" required><el-input v-model="editForm.ip_address" placeholder="如 10.0.1.1" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status" style="width: 100%">
            <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关联设备">
          <el-select v-model="editForm.device" clearable filterable placeholder="选择设备" style="width: 100%">
            <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="接口"><el-input v-model="editForm.interface" /></el-form-item>
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
