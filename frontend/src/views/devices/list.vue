<script setup lang="ts">
const datacenters = ref<any[]>([])
const loading = ref(false)
const search = ref('')

const filteredData = computed(() => {
  if (!search.value) return datacenters.value
  const keyword = search.value.toLowerCase()
  return datacenters.value.filter(
    (item: any) =>
      item.name.toLowerCase().includes(keyword) ||
      item.address.toLowerCase().includes(keyword)
  )
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await fetch('/api/dcim/datacenters/')
    const data = await res.json()
    datacenters.value = data.results || data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const handleDelete = (row: any) => {
  ElMessage.warning(`删除: ${row.name}`)
}

onMounted(() => {
  fetchData()
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

    <el-table-v2
      v-loading="loading"
      :columns="[
        { key: 'name', title: '名称', dataKey: 'name', width: 200 },
        { key: 'address', title: '地址', dataKey: 'address', width: 250 },
        { key: 'contact', title: '联系人', dataKey: 'contact', width: 120 },
        { key: 'phone', title: '电话', dataKey: 'phone', width: 140 },
        { key: 'room_count', title: '机房数', dataKey: 'room_count', width: 80 },
        { key: 'cabinet_count', title: '机柜数', dataKey: 'cabinet_count', width: 80 },
        { key: 'created_at', title: '创建时间', dataKey: 'created_at', width: 180 },
      ]"
      :data="filteredData"
      :width="1200"
      :height="600"
      :fixed="true"
    >
      <template #header-cell="{ column }">
        <span style="font-weight: 600">{{ column.title }}</span>
      </template>
      <template #cell="{ column, rowData }">
        <template v-if="column.key === 'created_at'">
          {{ new Date(rowData[column.dataKey!]).toLocaleDateString('zh-CN') }}
        </template>
        <template v-else>
          {{ rowData[column.dataKey!] ?? '-' }}
        </template>
      </template>
    </el-table-v2>
  </div>
</template>

<style scoped>
.device-list {
  padding: 20px;
}
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
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
</style>
