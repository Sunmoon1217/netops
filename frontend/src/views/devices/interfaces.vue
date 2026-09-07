<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import DeviceFilter from '@/ui/DeviceFilter.vue'
import { useCrudApi } from '@/composables/useCrudApi'
import { getInterfaces, updateInterface } from '@/api/interfaces'

const { data: interfaces, loading, search, filteredData, fetchData, handleSave } = useCrudApi(['interface', 'ip_address', 'device_hostname'])
const filterDevice = ref<number | ''>('')
const filterMode = ref('')
const editVisible = ref(false)
const editForm = ref<any>(null)

const modeOptions = [
  { label: '三层接口', value: 'layer3' },
  { label: 'Access', value: 'access' },
  { label: 'Hybrid', value: 'hybrid' },
  { label: 'Trunk', value: 'trunk' },
]

const displayed = computed(() => {
  let d = filteredData.value
  if (filterDevice.value) d = d.filter((i: any) => i.device === filterDevice.value)
  if (filterMode.value) d = d.filter((i: any) => i.mode === filterMode.value)
  return d
})

const fetchAll = () => {
  const params: Record<string, any> = {}
  if (filterDevice.value) params.device = filterDevice.value
  if (filterMode.value) params.mode = filterMode.value
  fetchData(() => getInterfaces(params))
}

const openEdit = (row: any) => {
  editForm.value = { ...row }
  editVisible.value = true
}

const saveEdit = () => {
  if (!editForm.value) return
  handleSave(
    () => updateInterface(editForm.value.id, {
      mode: editForm.value.mode,
      ip_address: editForm.value.ip_address,
      subnet_mask: editForm.value.subnet_mask,
      description: editForm.value.description,
      enabled: editForm.value.enabled,
    }),
    () => { editVisible.value = false; fetchAll() }
  )
}

const modeTag = (mode: string) => {
  const map: Record<string, string> = { layer3: 'primary', access: 'success', hybrid: 'warning', trunk: '' }
  return (map[mode] || 'info') as any
}

watch(filterDevice, fetchAll)
watch(filterMode, fetchAll)
onMounted(fetchAll)
</script>

<template>
  <PageLayout title="接口管理">
    <template #actions>
      <DeviceFilter v-model="filterDevice" />
      <el-select v-model="filterMode" placeholder="接口模式" clearable style="width: 120px">
        <el-option v-for="m in modeOptions" :key="m.value" :label="m.label" :value="m.value" />
      </el-select>
      <el-input v-model="search" placeholder="搜索接口/IP/设备" clearable style="width: 200px" />
    </template>
    <div class="table-wrapper">
      <DataTable :data="displayed" :loading="loading">
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
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? 'Up' : 'Down' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="80" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
          </template>
        </el-table-column>
      </DataTable>
    </div>
    <el-dialog v-model="editVisible" title="编辑接口" width="500px">
      <el-form v-if="editForm" label-width="80px">
        <el-form-item label="设备"><el-input :model-value="editForm.device_hostname" disabled /></el-form-item>
        <el-form-item label="接口"><el-input :model-value="editForm.interface" disabled /></el-form-item>
        <el-form-item label="模式">
          <el-select v-model="editForm.mode" clearable style="width: 100%">
            <el-option v-for="m in modeOptions" :key="m.value" :label="m.label" :value="m.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="IP 地址"><el-input v-model="editForm.ip_address" placeholder="如 10.0.1.1" /></el-form-item>
        <el-form-item label="子网掩码"><el-input v-model="editForm.subnet_mask" placeholder="如 255.255.255.0" /></el-form-item>
        <el-form-item label="启用"><el-switch v-model="editForm.enabled" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="editForm.description" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<style scoped>
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
