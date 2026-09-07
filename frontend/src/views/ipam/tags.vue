<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import { useCrudApi } from '@/composables/useCrudApi'
import { getTags, createTag, updateTag, deleteTag } from '@/api/ipam'

const { data: tags, loading, fetchData, handleSave, handleDelete } = useCrudApi()
const editVisible = ref(false)
const editForm = ref<any>(null)
const isNew = ref(false)

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

const save = () => {
  if (!editForm.value?.name) { ElMessage.warning('请输入标签名称'); return }
  const fn = isNew.value
    ? () => createTag(editForm.value)
    : () => updateTag(editForm.value.id, editForm.value)
  handleSave(fn, () => { editVisible.value = false; fetchData(getTags) })
}

const remove = (row: any) => {
  handleDelete(row.name, () => deleteTag(row.id), () => fetchData(getTags))
}

onMounted(() => fetchData(getTags))
</script>

<template>
  <PageLayout title="标签管理">
    <template #actions>
      <el-button type="primary" @click="openAdd">新增标签</el-button>
    </template>
    <div class="table-wrapper">
      <DataTable :data="tags" :loading="loading">
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
            <el-button size="small" link type="danger" @click="remove(row)">删除</el-button>
          </template>
        </el-table-column>
      </DataTable>
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
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </PageLayout>
</template>

<style scoped>
.table-wrapper { flex: 1; min-height: 0; background: #fff; border-radius: 8px; overflow: hidden; }
</style>
