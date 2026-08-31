<script setup lang="ts">
import { h } from 'vue'
import { useRouter } from 'vue-router'
import { getDevices } from '@/api/devices'
import { ElButton } from 'element-plus'

const router = useRouter()
const tableRef = ref<HTMLElement | null>(null)
const tableHeight = ref(600)
const tableWidth = ref(1200)

const devices = ref<any[]>([])
const loading = ref(false)
const search = ref('')

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
        <el-input v-model="search" placeholder="搜索..." clearable style="width: 220px" />
        <el-button type="primary">添加设备</el-button>
      </div>
    </div>

    <div ref="tableRef" class="table-wrapper">
      <el-table-v2
        v-loading="loading"
        :columns="[
          { key: 'hostname', title: '主机名', dataKey: 'hostname', width: 200 },
          { key: 'device_type', title: '类型', dataKey: 'device_type', width: 100 },
          { key: 'ip_address', title: '管理IP', dataKey: 'ip_address', width: 140 },
          { key: 'idc_name', title: '数据中心', dataKey: 'idc_name', width: 140 },
          { key: 'remark', title: '备注', dataKey: 'remark', width: 200 },
          { key: 'config', title: '操作', width: 100, fixed: true },
        ]"
        :data="filteredData"
        :height="tableHeight"
        :width="tableWidth"
        :fixed="true"
      >
        <template #header-cell="{ column }">
          <span style="font-weight: 600">{{ column.title }}</span>
        </template>
        <template #cell="{ column, rowData }">
          <template v-if="column.key === 'config'">
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
