<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { getDevice, getDeviceConfigs } from '@/api/devices'

const route = useRoute()
const router = useRouter()
const deviceId = Number(route.params.id)

const device = ref<any>(null)
const configs = ref<any[]>([])
const loading = ref(false)
const selectedConfig = ref<any>(null)

const fetchDevice = async () => {
  try {
    const res = await getDevice(deviceId)
    device.value = res.data
  } catch {
    ElMessage.error('获取设备信息失败')
  }
}

const fetchConfigs = async () => {
  loading.value = true
  try {
    const res = await getDeviceConfigs({ device: deviceId })
    configs.value = res.data.results || res.data || []
    if (configs.value.length > 0) {
      selectedConfig.value = configs.value[0]
    }
  } catch {
    ElMessage.error('获取配置失败')
  } finally {
    loading.value = false
  }
}

const formatJson = (json: any) => {
  if (!json) return '暂无配置数据'
  return JSON.stringify(json, null, 2)
}

onMounted(() => {
  fetchDevice()
  fetchConfigs()
})
</script>

<template>
  <div class="config-page">
    <div class="config-header">
      <el-button text @click="router.back()">← 返回</el-button>
      <h2>{{ device?.hostname || '设备配置' }}</h2>
    </div>

    <div class="config-body">
      <div class="config-sidebar">
        <div class="sidebar-title">配置历史</div>
        <el-menu v-loading="loading">
          <el-menu-item
            v-for="cfg in configs"
            :key="cfg.id"
            :index="String(cfg.id)"
            :class="{ 'is-active': selectedConfig?.id === cfg.id }"
            @click="selectedConfig = cfg"
          >
            <div class="config-item">
              <span class="config-time">
                {{ new Date(cfg.collected_at).toLocaleString('zh-CN') }}
              </span>
              <span class="config-hash">{{ cfg.git_commit_hash?.slice(0, 8) }}</span>
            </div>
          </el-menu-item>
        </el-menu>
        <el-empty v-if="!loading && configs.length === 0" description="暂无配置" :image-size="60" />
      </div>

      <div class="config-content">
        <div class="content-header" v-if="selectedConfig">
          <span>采集时间: {{ new Date(selectedConfig.collected_at).toLocaleString('zh-CN') }}</span>
          <span>Commit: {{ selectedConfig.git_commit_hash }}</span>
          <span v-if="selectedConfig.parse_duration">
            解析耗时: {{ selectedConfig.parse_duration.toFixed(2) }}s
          </span>
        </div>
        <pre class="config-code">{{ formatJson(selectedConfig?.config_json) }}</pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.config-page {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.config-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-shrink: 0;
}
.config-header h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 600;
}
.config-body {
  display: flex;
  flex: 1;
  gap: 16px;
  min-height: 0;
}
.config-sidebar {
  width: 240px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 8px;
  overflow-y: auto;
}
.sidebar-title {
  padding: 12px 16px;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 1px solid #ebeef5;
}
.config-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.config-time {
  font-size: 13px;
}
.config-hash {
  font-size: 12px;
  color: #909399;
  font-family: monospace;
}
.config-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
}
.content-header {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  font-size: 13px;
  color: #606266;
  border-bottom: 1px solid #ebeef5;
  flex-shrink: 0;
}
.config-code {
  flex: 1;
  padding: 16px;
  margin: 0;
  overflow: auto;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  line-height: 1.5;
  background: #fafafa;
}
</style>
