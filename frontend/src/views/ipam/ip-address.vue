<script setup lang="ts">
import { getIpAddresses, createIpAddress, updateIpAddress, deleteIpAddress } from '@/api/ipam'
import { getDevices } from '@/api/devices'

const ipList = ref<any[]>([])
const devices = ref<any[]>([])
const loading = ref(false)
const search = ref('')
const filterStatus = ref('')
const editVisible = ref(false)
const editForm = ref<any>(null)
const isNew = ref(false)

const statusOptions = [
  { label: '已使用', value: 'used' },
  { label: '预留', value: 'reserved' },
  { label: '可用', value: 'available' },
]

const filteredData = computed(() => {
  if (!search.value) return ipList.value
  const kw = search.value.toLowerCase()
  return ipList.value.filter((i: any) =>
    i.ip_address?.toLowerCase().includes(kw) || i.description?.toLowerCase().includes(kw)
  )
})

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterStatus.value) params.status = filterStatus.value
    const res = await getIpAddresses(params)
    ipList.value = res.data.results || res.data || []
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

const handleSave = async () => {
  if (!editForm.value?.ip_address) {
    ElMessage.warning('请输入 IP 地址')
    return
  }
  try {
    if (isNew.value) await createIpAddress(editForm.value)
    else await updateIpAddress(editForm.value.id, editForm.value)
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.ip_address?.[0] || '保存失败')
  }
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除 ${row.ip_address}？`, '提示', { type: 'warning' })
  await deleteIpAddress(row.id)
  ElMessage.success('已删除')
  fetchData()
}

const statusTag = (s: string) => {
  const map: Record<string, string> = { used: 'danger', reserved: 'warning', available: 'success' }
  return (map[s] || 'info') as any
}

onMounted(() => { fetchDevices(); fetchData() })
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>IP 地址管理</h2>
      <div class="header-actions">
        <el-select v-model="filterStatus" placeholder="状态" clearable style="width: 110px" @change="fetchData">
          <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
        </el-select>
        <el-input v-model="search" placeholder="搜索 IP/描述" clearable style="width: 200px" />
        <el-button type="primary" @click="openAdd">新增 IP</el-button>
      </div>
    </div>

    <div class="table-wrapper">
      <el-table v-loading="loading" :data="filteredData" stripe border height="100%">
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
            <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editVisible" :title="isNew ? '新增 IP 地址' : '编辑 IP 地址'" width="500px">
      <el-form v-if="editForm" label-width="90px">
        <el-form-item label="IP 地址" required>
          <el-input v-model="editForm.ip_address" placeholder="如 10.0.1.1" />
        </el-form-item>
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
        <el-form-item label="接口">
          <el-input v-model="editForm.interface" />
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
