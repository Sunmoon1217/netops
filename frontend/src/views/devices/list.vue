<script setup lang="ts">
import { h } from 'vue'
import { useRouter } from 'vue-router'
import { getDevices } from '@/api/devices'
import api from '@/api/index'
import { ElButton } from 'element-plus'
import { FixedDir } from 'element-plus/es/components/table-v2/src/constants'
import ImportDevice from './components/ImportDevice.vue'

const router = useRouter()
const tableRef = ref<HTMLElement | null>(null)
const tableHeight = ref(600)
const tableWidth = ref(1200)

const devices = ref<any[]>([])
const loading = ref(false)
const search = ref('')
const importDialogVisible = ref(false)
const editDialogVisible = ref(false)
const editForm = ref<any>(null)

const filteredData = computed(() => {
  if (!search.value) return devices.value
  const keyword = search.value.toLowerCase()
  return devices.value.filter(
    (item: any) =>
      item.hostname.toLowerCase().includes(keyword) ||
      item.ip_address?.toLowerCase().includes(keyword)
  )
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDevices()
    devices.value = res.data.results || res.data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const goToConfig = (row: any) => {
  router.push(`/devices/${row.id}/config`)
}

const goToHistory = (row: any) => {
  router.push(`/devices/${row.id}/history`)
}

const openEdit = (row: any) => {
  editForm.value = { ...row }
  editDialogVisible.value = true
}

const handleEditSave = async () => {
  if (!editForm.value) return
  try {
    await api.put(`/api/assets/devices/${editForm.value.id}/`, editForm.value)
    ElMessage.success('保存成功')
    editDialogVisible.value = false
    fetchData()
  } catch {
    ElMessage.error('保存失败')
  }
}

const columns = [
  { key: 'hostname', title: '主机名', dataKey: 'hostname', width: 180 },
  { key: 'device_type', title: '类型', dataKey: 'device_type', width: 100 },
  { key: 'ip_address', title: '管理IP', dataKey: 'ip_address', width: 140 },
  { key: 'idc_name', title: '数据中心', dataKey: 'idc_name', width: 140 },
  { key: 'remark', title: '备注', dataKey: 'remark', width: 200 },
  { key: 'operation', title: '操作', width: 200, fixed: FixedDir.RIGHT },
]

const updateSize = () => {
  if (tableRef.value) {
    tableHeight.value = tableRef.value.clientHeight
    tableWidth.value = tableRef.value.clientWidth
  }
}

onMounted(() => {
  fetchData()
  nextTick(updateSize)
  window.addEventListener('resize', updateSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateSize)
})
</script>

<template>
  <div class="device-list">
    <div class="list-header">
      <h2>设备列表</h2>
      <div class="list-actions">
        <el-input v-model="search" placeholder="搜索主机名 / IP" clearable style="width: 220px" />
        <el-button @click="importDialogVisible = true">导入</el-button>
        <el-button type="primary">添加设备</el-button>
      </div>
    </div>

    <div ref="tableRef" class="table-wrapper">
      <el-table-v2
        v-loading="loading"
        :columns="columns"
        :data="filteredData"
        :height="tableHeight"
        :width="tableWidth"
        :fixed="true"
      >
        <template #header-cell="{ column }">
          <span style="font-weight: 600">{{ column.title }}</span>
        </template>
        <template #cell="{ column, rowData }">
          <template v-if="column.key === 'operation'">
            <el-button size="small" link type="primary" @click="goToConfig(rowData)">配置</el-button>
            <el-button size="small" link type="info" @click="goToHistory(rowData)">历史</el-button>
            <el-button size="small" link type="warning" @click="openEdit(rowData)">编辑</el-button>
          </template>
          <template v-else>
            {{ rowData[column.dataKey!] ?? '-' }}
          </template>
        </template>
      </el-table-v2>
    </div>

    <ImportDevice v-model:visible="importDialogVisible" @success="fetchData" />

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialogVisible" title="编辑设备" width="500px">
      <el-form v-if="editForm" label-width="80px">
        <el-form-item label="主机名">
          <el-input v-model="editForm.hostname" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="editForm.device_type" style="width: 100%">
            <el-option label="防火墙" value="firewall" />
            <el-option label="交换机" value="switch" />
            <el-option label="负载均衡" value="loadbalancer" />
            <el-option label="路由器" value="router" />
            <el-option label="服务器" value="server" />
          </el-select>
        </el-form-item>
        <el-form-item label="管理IP">
          <el-input v-model="editForm.ip_address" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.device-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.list-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}
.list-actions {
  display: flex;
  gap: 8px;
}
.table-wrapper {
  flex: 1;
  min-height: 0;
}
</style>
