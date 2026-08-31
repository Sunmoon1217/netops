<script setup lang="ts">
import { getParsers, getParserTemplates, getParserTemplate, updateParserTemplate } from '@/api/parsers'

const parsers = ref<any[]>([])
const templates = ref<any[]>([])
const selectedTemplate = ref<any>(null)
const templateContent = ref('')
const editContent = ref('')
const isEditing = ref(false)

const fetchParsers = async () => {
  try {
    const data = await getParsers()
    parsers.value = data.parsers || []
  } catch {
    ElMessage.error('获取解析器列表失败')
  }
}

const fetchTemplates = async () => {
  try {
    const data = await getParserTemplates()
    templates.value = data.templates || []
  } catch {
    ElMessage.error('获取模板列表失败')
  }
}

const handleParserClick = (row: any) => {
  const tpl = templates.value.find((t) => t.name === row.template_name)
  if (tpl) handleTemplateClick(tpl)
}

const handleTemplateClick = async (row: any) => {
  selectedTemplate.value = row
  isEditing.value = false
  try {
    const data = await getParserTemplate(row.name)
    templateContent.value = data.content
    editContent.value = data.content
  } catch {
    ElMessage.error('获取模板内容失败')
  }
}

const saveTemplate = async () => {
  if (!selectedTemplate.value) return
  try {
    await updateParserTemplate(selectedTemplate.value.name, editContent.value)
    templateContent.value = editContent.value
    isEditing.value = false
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  }
}

const cancelEdit = () => {
  editContent.value = templateContent.value
  isEditing.value = false
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return `${bytes} B`
  return `${(bytes / 1024).toFixed(1)} KB`
}

onMounted(() => {
  fetchParsers()
  fetchTemplates()
})
</script>

<template>
  <div class="parsers-page">
    <div class="page-header">
      <h2>解析器模板管理</h2>
    </div>

    <div class="parsers-body">
      <!-- 左侧：解析器列表 -->
      <div class="parsers-sidebar">
        <div class="sidebar-title">解析器列表</div>
        <el-table :data="parsers" size="small" highlight-current-row @row-click="handleParserClick">
          <el-table-column prop="vendor" label="厂商" width="80" />
          <el-table-column prop="device_type" label="类型" width="80" />
          <el-table-column prop="template_name" label="模板" show-overflow-tooltip />
        </el-table>
      </div>

      <!-- 右侧：模板预览/编辑 -->
      <div class="parsers-main">
        <div class="template-header">
          <span class="template-name">{{ selectedTemplate?.name || '请选择模板' }}</span>
          <div v-if="selectedTemplate" class="template-actions">
            <el-button v-if="!isEditing" size="small" @click="isEditing = true">编辑</el-button>
            <el-button v-if="isEditing" size="small" type="primary" @click="saveTemplate">保存</el-button>
            <el-button v-if="isEditing" size="small" @click="cancelEdit">取消</el-button>
          </div>
        </div>
        <div class="template-content">
          <el-input
            v-if="isEditing"
            v-model="editContent"
            type="textarea"
            :autosize="{ minRows: 20, maxRows: 40 }"
            style="font-family: monospace"
          />
          <pre v-else class="template-preview">{{ templateContent || '请选择模板查看内容' }}</pre>
        </div>
      </div>
    </div>

    <!-- 底部：模板文件列表 -->
    <div class="template-files">
      <div class="files-title">模板文件</div>
      <el-table :data="templates" size="small" highlight-current-row @row-click="handleTemplateClick">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.size) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.parsers-page {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}
.page-header {
  flex-shrink: 0;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}
.parsers-body {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
}
.parsers-sidebar {
  width: 300px;
  flex-shrink: 0;
}
.sidebar-title, .files-title {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
  margin-bottom: 8px;
}
.parsers-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.template-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  flex-shrink: 0;
}
.template-name {
  font-size: 14px;
  font-weight: 600;
  color: #606266;
}
.template-actions {
  display: flex;
  gap: 8px;
}
.template-content {
  flex: 1;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  overflow: auto;
}
.template-preview {
  margin: 0;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
.template-files {
  margin-top: 16px;
  flex-shrink: 0;
}
</style>
