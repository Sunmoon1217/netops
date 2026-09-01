<script setup lang="ts">
import { getTags, createTag, updateTag, deleteTag } from '@/api/ipam'

const tags = ref<any[]>([])
const loading = ref(false)
const editVisible = ref(false)
const editForm = ref<any>(null)
const isNew = ref(false)

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getTags()
    tags.value = res.data.results || res.data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const openAdd = () => {
  editForm.value = { name: '', color: '#3b82f6' }
  isNew.value = true
  editVisible.value = true
}

const openEdit = (row: any) => {
  editForm.value = { ...row }
  isNew.value = false
  editVisible.value = true
}

const handleSave = async () => {
  if (!editForm.value?.name) {
    ElMessage.warning('请输入标签名称')
    return
  }
  try {
    if (isNew.value) await createTag(editForm.value)
    else await updateTag(editForm.value.id, editForm.value)
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchData()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.name?.[0] || '保存失败')
  }
}

const handleDelete = async (row: any) => {
  await ElMessageBox.confirm(`确认删除标签 ${row.name}？`, '提示', { type: 'warning' })
  await deleteTag(row.id)
  ElMessage.success('已删除')
  fetchData()
}

onMounted(fetchData)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>标签管理</h2>
      <el-button type="primary" @click="openAdd">新增标签</el-button>
    </div>

    <div class="table-wrapper">
      <el-table v-loading="loading" :data="tags" stripe border height="100%">
        <el-table-column prop="name" label="标签名称" width="200" sortable />
        <el-table-column prop="color" label="颜色" width="100">
          <template #default="{ row }">
            <span :style="{ display: 'inline-block', width: '16px', height: '16px', borderRadius: '3px', background: row.color, verticalAlign: 'middle', marginRight: '6px' }" />
            {{ row.color }}
          </template>
        </el-table-column>
        <el-table-column prop="subnet_count" label="关联网段" width="100" />
        <el-table-column label="操作" width="120" fixed="right" align="center">
          <template #default="{ row }">
            <el-button size="small" link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog v-model="editVisible" :title="isNew ? '新增标签' : '编辑标签'" width="400px">
      <el-form v-if="editForm" label-width="70px">
        <el-form-item label="名称" required>
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="editForm.color" />
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
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
