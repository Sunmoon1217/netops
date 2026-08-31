<script setup lang="ts">
import { getInterfaces, updateInterface } from '@/api/interfaces'
import { getDevices } from '@/api/devices'

const interfaces = ref<any[]>([])
const devices = ref<any[]>([])
const loading = ref(false)
const search = ref('')
const filterDevice = ref<number | ''>('')
const filterMode = ref('')

const modeOptions = [
  { label: '三层接口', value: 'layer3' },
  { label: 'Access', value: 'access' },
  { label: 'Hybrid', value: 'hybrid' },
  { label: 'Trunk', value: 'trunk' },
]

const editVisible = ref(false)
const editForm = ref<any>(null)

const filteredData = computed(() => {
  let data = interfaces.value
  if (search.value) {
    const kw = search.value.toLowerCase()
    data = data.filter((i: any) =>
      i.interface?.toLowerCase().includes(kw) ||
      i.ip_address?.toLowerCase().includes(kw) ||
      i.device_hostname?.toLowerCase().includes(kw)
    )
  }
  return data
})

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterDevice.value) params.device = filterDevice.value
    if (filterMode.value) params.mode = filterMode.value
    const res = await getInterfaces(params)
    interfaces.value = res.data.results || res.data || []
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

const openEdit = (row: any) => {
  editForm.value = { ...row }
  editVisible.value = true
}

const handleSave = async () => {
  if (!editForm.value) return
  try {
    await updateInterface(editForm.value.id, {
      mode: editForm.value.mode,
      ip_address: editForm.value.ip_address,
      subnet_mask: editForm.value.subnet_mask,
      description: editForm.value.description,
      enabled: editForm.value.enabled,
    })
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchData()
  } catch {
    ElMessage.error('保存失败')
  }
}

const modeTag = (mode: string) => {
  const map: Record<string, string> = { layer3: 'primary', access: 'success', hybrid: 'warning', trunk: '' }
  return (map[mode] || 'info') as any
}

onMounted(() => {
  fetchDevices()
  fetchData()
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>接口管理</h2>
      <div class="header-actions">
        <el-select v-model="filterDevice" placeholder="设备" clearable style="width: 160px" @change="fetchData">
          <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
        </el-select>
        <el-select v-model="filterMode" placeholder="接口模式" clearable style="width: 120px" @change="fetchData">
          <el-option v-for="m in modeOptions" :key="m.value" :label="m.label" :value="m.value" />
        </el-select>
        <el-input v-model="search" placeholder="搜索接口/IP/设备" clearable style="width: 200px" />
      </div>
    </div>

    <div class="table-wrapper">
      <el-table v-loading="loading" :data="filteredData" stripe border height="100%" style="width: 100%">
        <el-table-column prop="device_hostname" label="设备" width="150" sortable />
        <el-table-column prop="interface" label="接口" width="140" sortable />
        <el-table-column prop="mode" label="模式" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.mode" size="small" :type="modeTag(row.mode)">{{ row.mode }}</el-tag>
            <span v-else style="color: #c0c4cc">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP 地址" width="150" />
        <el-table-column prop="subnet_mask" label="子网掩码" width="130" />
        <el-table-column prop="vrf_name" label="VRF" width="120">
          <template #default="{ row }">
            <span v-if="row.vrf_name">{{ row.vrf_name }}</span>
            <span v-else style="color: #c0c4cc">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? 'Up' : 'Down' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="80" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editVisible" title="编辑接口" width="500px">
      <el-form v-if="editForm" label-width="80px">
        <el-form-item label="设备">
          <el-input :model-value="editForm.device_hostname" disabled />
        </el-form-item>
        <el-form-item label="接口">
          <el-input :model-value="editForm.interface" disabled />
        </el-form-item>
        <el-form-item label="模式">
          <el-select v-model="editForm.mode" clearable style="width: 100%">
            <el-option v-for="m in modeOptions" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址">
          <el-input v-model="editForm.ip_address" placeholder="如 10.0.1.1" />
        </el-form-item>
        <el-form-item label="子网掩码">
          <el-input v-model="editForm.subnet_mask" placeholder="如 255.255.255.0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="editForm.enabled" />
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
.page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.page-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.table-wrapper {
  flex: 1;
  min-height: 0;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}
</style>
