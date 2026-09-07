<script setup lang="ts">
import { h } from 'vue'
import { useRouter } from 'vue-router'
import { getDevices } from '@/api/devices'
import api from '@/api/index'
import { ElButton } from 'element-plus'
import { FixedDir } from 'element-plus/es/components/table-v2/src/constants'
import ImportDevice from './components/ImportDevice.vue'
import PageLayout from '@/ui/PageLayout.vue'
import { useCrudApi } from '@/composables/useCrudApi'
import { useTableHeight } from '@/composables/useTableHeight'

const router = useRouter()
const { tableRef, tableHeight, tableWidth } = useTableHeight()
const { data: devices, loading, search, filteredData, fetchData, handleSave } = useCrudApi(['hostname', 'ip_address'])

const importDialogVisible = ref(false)
const editDialogVisible = ref(false)
const editForm = ref<any>(null)

const goToConfig = (row: any) => router.push(`/devices/${row.id}/config`)
const goToHistory = (row: any) => router.push(`/devices/${row.id}/history`)

const openEdit = (row: any) => {
  editForm.value = { ...row }
  editDialogVisible.value = true
}

const saveEdit = () => {
  if (!editForm.value) return
  handleSave(
    () => api.put(`/api/assets/devices/${editForm.value.id}/`, editForm.value),
    () => { editDialogVisible.value = false; fetchData(getDevices) }
  )
}

const columns = [
  { key: 'hostname', title: '主机名', dataKey: 'hostname', width: 180 },
  { key: 'device_type', title: '类型', dataKey: 'device_type', width: 100 },
  { key: 'ip_address', title: '管理IP', dataKey: 'ip_address', width: 140 },
  { key: 'idc_name', title: '数据中心', dataKey: 'idc_name', width: 140 },
  { key: 'remark', title: '备注', dataKey: 'remark', width: 200 },
  { key: 'operation', title: '操作', width: 200, fixed: FixedDir.RIGHT },
]

onMounted(() => fetchData(getDevices))
</script>

<template>
  <PageLayout title="设备列表">
    <template #actions>
      <el-input v-model="search" placeholder="搜索主机名 / IP" clearable style="width: 220px" />
      <el-button @click="importDialogVisible = true">导入</el-button>
      <el-button type="primary">添加设备</el-button>
    </template>
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
    <ImportDevice v-model:visible="importDialogVisible" @success="() => fetchData(getDevices)" />
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
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<style scoped>
.table-wrapper { flex: 1; min-height: 0; }
</style>
