<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'
import DataTable from '@/ui/DataTable.vue'
import {
  getSnmpConfigs, deleteSnmpConfig,
  getNtpConfigs, deleteNtpConfig,
  getSyslogConfigs, deleteSyslogConfig,
  updateSnmpConfig, updateNtpConfig, updateSyslogConfig,
} from '@/api/baseline'
import { useCrudApi } from '@/composables/useCrudApi'

const router = useRouter()
const activeTab = ref('snmp')
const loading = ref(false)

const snmp = useCrudApi()
const ntp = useCrudApi()
const syslog = useCrudApi()

const fetchAll = async () => {
  loading.value = true
  try {
    const [s, n, l] = await Promise.all([getSnmpConfigs(), getNtpConfigs(), getSyslogConfigs()])
    snmp.data.value = s.data.results || s.data || []
    ntp.data.value = n.data.results || n.data || []
    syslog.data.value = l.data.results || l.data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchAll)
</script>

<template>
  <PageLayout title="基线管理">
    <el-tabs v-model="activeTab" class="page-tabs">
      <el-tab-pane label="SNMP" name="snmp">
        <div class="tab-toolbar">
          <el-button type="primary" size="small" @click="router.push('/devices/baseline/snmp/create')">新增</el-button>
        </div>
        <DataTable :data="snmp.data.value" :loading="loading" size="small" height="">
          <el-table-column prop="device_hostname" label="设备" width="150" />
          <el-table-column prop="version" label="版本" width="80" />
          <el-table-column prop="community_read" label="读社区" width="120" show-overflow-tooltip />
          <el-table-column prop="community_write" label="写社区" width="120" show-overflow-tooltip />
          <el-table-column prop="port" label="端口" width="80" />
          <el-table-column prop="trap_enabled" label="Trap" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.trap_enabled ? 'success' : 'info'" size="small">{{ row.trap_enabled ? '开' : '关' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" size="small" @change="updateSnmpConfig(row.id, { enabled: row.enabled })" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="router.push(`/devices/baseline/snmp/${row.id}/edit`)">编辑</el-button>
              <el-button size="small" link type="danger" @click="snmp.handleDelete('SNMP配置', () => deleteSnmpConfig(row.id), fetchAll)">删除</el-button>
            </template>
          </el-table-column>
        </DataTable>
      </el-tab-pane>

      <el-tab-pane label="NTP" name="ntp">
        <div class="tab-toolbar">
          <el-button type="primary" size="small" @click="router.push('/devices/baseline/ntp/create')">新增</el-button>
        </div>
        <DataTable :data="ntp.data.value" :loading="loading" size="small" height="">
          <el-table-column prop="device_hostname" label="设备" width="150" />
          <el-table-column prop="server1" label="NTP服务器1" width="150" />
          <el-table-column prop="server2" label="NTP服务器2" width="150" />
          <el-table-column prop="server3" label="NTP服务器3" width="150" />
          <el-table-column prop="timezone" label="时区" width="100" />
          <el-table-column prop="sync_interval" label="同步间隔" width="90" />
          <el-table-column prop="enabled" label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" size="small" @change="updateNtpConfig(row.id, { enabled: row.enabled })" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="router.push(`/devices/baseline/ntp/${row.id}/edit`)">编辑</el-button>
              <el-button size="small" link type="danger" @click="ntp.handleDelete('NTP配置', () => deleteNtpConfig(row.id), fetchAll)">删除</el-button>
            </template>
          </el-table-column>
        </DataTable>
      </el-tab-pane>

      <el-tab-pane label="Syslog" name="syslog">
        <div class="tab-toolbar">
          <el-button type="primary" size="small" @click="router.push('/devices/baseline/syslog/create')">新增</el-button>
        </div>
        <DataTable :data="syslog.data.value" :loading="loading" size="small" height="">
          <el-table-column prop="device_hostname" label="设备" width="150" />
          <el-table-column prop="server1" label="日志服务器1" width="150" />
          <el-table-column prop="server2" label="日志服务器2" width="150" />
          <el-table-column prop="port" label="端口" width="80" />
          <el-table-column prop="facility" label="Facility" width="100" />
          <el-table-column prop="level" label="日志级别" width="120" />
          <el-table-column prop="enabled" label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" size="small" @change="updateSyslogConfig(row.id, { enabled: row.enabled })" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="router.push(`/devices/baseline/syslog/${row.id}/edit`)">编辑</el-button>
              <el-button size="small" link type="danger" @click="syslog.handleDelete('Syslog配置', () => deleteSyslogConfig(row.id), fetchAll)">删除</el-button>
            </template>
          </el-table-column>
        </DataTable>
      </el-tab-pane>
    </el-tabs>
  </PageLayout>
</template>

<style scoped>
.page-tabs { flex: 1; min-height: 0; }
.tab-toolbar { margin-bottom: 12px; }
</style>
