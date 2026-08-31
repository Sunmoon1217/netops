<script setup lang="ts">
import { h } from 'vue'
import { useRouter } from 'vue-router'
import { getDevices, importDevices } from '@/api/devices'
import { ElButton, ElMessageBox, ElMessage } from 'element-plus'
import { FixedDir } from 'element-plus/es/components/table-v2/src/constants'

const router = useRouter()
const tableRef = ref<HTMLElement | null>(null)
const tableHeight = ref(600)
const tableWidth = ref(1200)

const devices = ref<any[]>([])
const loading = ref(false)
const search = ref('')
const importDialogVisible = ref(false)
const importFile = ref<File | null>(null)
const importLoading = ref(false)

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

const handleImport = async () => {
  if (!importFile.value) {
    ElMessage.warning('请选择文件')
    return
  }
  importLoading.value = true
  try {
    const res = await importDevices(importFile.value)
    const data = res.data
    ElMessage.success(`导入完成: 新增 ${data.created}, 更新 ${data.updated}`)
    if (data.errors?.length) {
      ElMessage.warning(`${data.errors.length} 条导入失败`)
    }
    importDialogVisible.value = false
    importFile.value = null
    fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.error || '导入失败')
  } finally {
    importLoading.value = false
  }
}

const handleFileChange = (file: any) => {
  importFile.value = file.raw
}

const columns = [
  { key: 'hostname', title: '主机名', dataKey: 'hostname', width: 180 },
  { key: 'device_type', title: '类型', dataKey: 'device_type', width: 100 },
  { key: 'ip_address', title: '管理IP', dataKey: 'ip_address', width: 140 },
  { key: 'idc_name', title: '数据中心', dataKey: 'idc_name', width: 140 },
  { key: 'remark', title: '备注', dataKey: 'remark', width: 200 },
  { key: 'operation', title: '操作', width: 100, fixed: FixedDir.RIGHT },
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
            <el-button size="small" link type="primary" @click="goToConfig(rowData)">
              配置
            </el-button>
          </template>
          <template v-else>
            {{ rowData[column.dataKey!] ?? '-' }}
          </template>
        </template>
      </el-table-v2>
    </div>

    <!-- 导入弹窗 -->
    <el-dialog v-model="importDialogVisible" title="导入设备" width="480px">
      <div style="margin-bottom: 12px; color: #606266; font-size: 14px">
        上传 Excel 文件，Sheet 名需包含「设备」，列顺序：
        <br />
        <code>主机名 | 类型 | 管理IP | 数据中心 | 备注</code>
      </div>
      <el-upload
        drag
        :auto-upload="false"
        :limit="1"
        accept=".xlsx,.xls"
        :on-change="handleFileChange"
        :on-exceed="() => ElMessage.warning('只能上传一个文件')"
      >
        <el-icon style="font-size: 40px; color: #c0c4cc; margin-bottom: 8px">
          <UploadFilled />
        </el-icon>
        <div>将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div style="color: #909399; font-size: 12px">支持 .xlsx / .xls 格式</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="importLoading" @click="handleImport">
          确认导入
        </el-button>
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
