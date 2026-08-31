<script setup lang="ts">
import {
  getSnmpConfigs, createSnmpConfig, updateSnmpConfig, deleteSnmpConfig,
  getNtpConfigs, createNtpConfig, updateNtpConfig, deleteNtpConfig,
  getSyslogConfigs, createSyslogConfig, updateSyslogConfig, deleteSyslogConfig,
} from '@/api/baseline'
import { getDevices } from '@/api/devices'

const activeTab = ref('snmp')
const devices = ref<any[]>([])
const loading = ref(false)

// SNMP
const snmpData = ref<any[]>([])
const snmpEditVisible = ref(false)
const snmpForm = ref<any>({})
const snmpIsNew = ref(false)

// NTP
const ntpData = ref<any[]>([])
const ntpEditVisible = ref(false)
const ntpForm = ref<any>({})
const ntpIsNew = ref(false)

// Syslog
const syslogData = ref<any[]>([])
const syslogEditVisible = ref(false)
const syslogForm = ref<any>({})
const syslogIsNew = ref(false)

const fetchDevices = async () => {
  try {
    const res = await getDevices()
    devices.value = res.data.results || res.data || []
  } catch { /* ignore */ }
}

const fetchData = async () => {
  loading.value = true
  try {
    const [snmp, ntp, syslog] = await Promise.all([
      getSnmpConfigs(), getNtpConfigs(), getSyslogConfigs(),
    ])
    snmpData.value = snmp.data.results || snmp.data || []
    ntpData.value = ntp.data.results || ntp.data || []
    syslogData.value = syslog.data.results || syslog.data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const getDeviceName = (id: number) => devices.value.find((d) => d.id === id)?.hostname || id

// SNMP
const addSnmp = () => {
  snmpForm.value = { device: '', version: 'v2c', port: 161, trap_port: 162, enabled: true }
  snmpIsNew.value = true
  snmpEditVisible.value = true
}
const editSnmp = (row: any) => {
  snmpForm.value = { ...row }
  snmpIsNew.value = false
  snmpEditVisible.value = true
}
const saveSnmp = async () => {
  try {
    if (snmpIsNew.value) await createSnmpConfig(snmpForm.value)
    else await updateSnmpConfig(snmpForm.value.id, snmpForm.value)
    ElMessage.success('保存成功')
    snmpEditVisible.value = false
    fetchData()
  } catch { ElMessage.error('保存失败') }
}
const removeSnmp = async (id: number) => {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await deleteSnmpConfig(id)
  ElMessage.success('已删除')
  fetchData()
}

// NTP
const addNtp = () => {
  ntpForm.value = { device: '', server1: '', timezone: 'UTC', sync_interval: 64, enabled: true }
  ntpIsNew.value = true
  ntpEditVisible.value = true
}
const editNtp = (row: any) => {
  ntpForm.value = { ...row }
  ntpIsNew.value = false
  ntpEditVisible.value = true
}
const saveNtp = async () => {
  try {
    if (ntpIsNew.value) await createNtpConfig(ntpForm.value)
    else await updateNtpConfig(ntpForm.value.id, ntpForm.value)
    ElMessage.success('保存成功')
    ntpEditVisible.value = false
    fetchData()
  } catch { ElMessage.error('保存失败') }
}
const removeNtp = async (id: number) => {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await deleteNtpConfig(id)
  ElMessage.success('已删除')
  fetchData()
}

// Syslog
const addSyslog = () => {
  syslogForm.value = { device: '', port: 514, facility: 'local7', level: 'informational', enabled: true }
  syslogIsNew.value = true
  syslogEditVisible.value = true
}
const editSyslog = (row: any) => {
  syslogForm.value = { ...row }
  syslogIsNew.value = false
  syslogEditVisible.value = true
}
const saveSyslog = async () => {
  try {
    if (syslogIsNew.value) await createSyslogConfig(syslogForm.value)
    else await updateSyslogConfig(syslogForm.value.id, syslogForm.value)
    ElMessage.success('保存成功')
    syslogEditVisible.value = false
    fetchData()
  } catch { ElMessage.error('保存失败') }
}
const removeSyslog = async (id: number) => {
  await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
  await deleteSyslogConfig(id)
  ElMessage.success('已删除')
  fetchData()
}

onMounted(() => {
  fetchDevices()
  fetchData()
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>基线管理</h2>
    </div>

    <el-tabs v-model="activeTab" class="page-tabs">
      <!-- SNMP -->
      <el-tab-pane label="SNMP" name="snmp">
        <div class="tab-toolbar">
          <el-button type="primary" size="small" @click="addSnmp">新增</el-button>
        </div>
        <el-table v-loading="loading" :data="snmpData" stripe border size="small">
          <el-table-column prop="device_hostname" label="设备" width="150" />
          <el-table-column prop="version" label="版本" width="80" />
          <el-table-column prop="community_read" label="读社区" width="120" show-overflow-tooltip />
          <el-table-column prop="community_write" label="写社区" width="120" show-overflow-tooltip />
          <el-table-column prop="port" label="端口" width="80" />
          <el-table-column prop="trap_enabled" label="Trap" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.trap_enabled ? 'success' : 'info'" size="small">
                {{ row.trap_enabled ? '开' : '关' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-switch v-model="row.enabled" size="small" @change="updateSnmpConfig(row.id, { enabled: row.enabled })" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" link type="primary" @click="editSnmp(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="removeSnmp(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- NTP -->
      <el-tab-pane label="NTP" name="ntp">
        <div class="tab-toolbar">
          <el-button type="primary" size="small" @click="addNtp">新增</el-button>
        </div>
        <el-table v-loading="loading" :data="ntpData" stripe border size="small">
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
              <el-button size="small" link type="primary" @click="editNtp(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="removeNtp(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- Syslog -->
      <el-tab-pane label="Syslog" name="syslog">
        <div class="tab-toolbar">
          <el-button type="primary" size="small" @click="addSyslog">新增</el-button>
        </div>
        <el-table v-loading="loading" :data="syslogData" stripe border size="small">
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
              <el-button size="small" link type="primary" @click="editSyslog(row)">编辑</el-button>
              <el-button size="small" link type="danger" @click="removeSyslog(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- SNMP 编辑弹窗 -->
    <el-dialog v-model="snmpEditVisible" :title="snmpIsNew ? '新增 SNMP 配置' : '编辑 SNMP 配置'" width="500px">
      <el-form v-if="snmpForm" label-width="90px">
        <el-form-item label="设备" required>
          <el-select v-model="snmpForm.device" filterable style="width: 100%">
            <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="SNMP 版本">
          <el-select v-model="snmpForm.version" style="width: 100%">
            <el-option label="v1" value="v1" /><el-option label="v2c" value="v2c" /><el-option label="v3" value="v3" />
          </el-select>
        </el-form-item>
        <el-form-item label="读社区"><el-input v-model="snmpForm.community_read" /></el-form-item>
        <el-form-item label="写社区"><el-input v-model="snmpForm.community_write" /></el-form-item>
        <el-form-item label="端口"><el-input-number v-model="snmpForm.port" :min="1" :max="65535" /></el-form-item>
        <el-form-item label="启用 Trap"><el-switch v-model="snmpForm.trap_enabled" /></el-form-item>
        <el-form-item label="Trap 服务器" v-if="snmpForm.trap_enabled"><el-input v-model="snmpForm.trap_server" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="snmpEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSnmp">保存</el-button>
      </template>
    </el-dialog>

    <!-- NTP 编辑弹窗 -->
    <el-dialog v-model="ntpEditVisible" :title="ntpIsNew ? '新增 NTP 配置' : '编辑 NTP 配置'" width="500px">
      <el-form v-if="ntpForm" label-width="90px">
        <el-form-item label="设备" required>
          <el-select v-model="ntpForm.device" filterable style="width: 100%">
            <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="NTP 服务器1" required><el-input v-model="ntpForm.server1" /></el-form-item>
        <el-form-item label="NTP 服务器2"><el-input v-model="ntpForm.server2" /></el-form-item>
        <el-form-item label="NTP 服务器3"><el-input v-model="ntpForm.server3" /></el-form-item>
        <el-form-item label="时区"><el-input v-model="ntpForm.timezone" /></el-form-item>
        <el-form-item label="同步间隔"><el-input-number v-model="ntpForm.sync_interval" :min="1" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="ntpEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNtp">保存</el-button>
      </template>
    </el-dialog>

    <!-- Syslog 编辑弹窗 -->
    <el-dialog v-model="syslogEditVisible" :title="syslogIsNew ? '新增 Syslog 配置' : '编辑 Syslog 配置'" width="500px">
      <el-form v-if="syslogForm" label-width="90px">
        <el-form-item label="设备" required>
          <el-select v-model="syslogForm.device" filterable style="width: 100%">
            <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="日志服务器1" required><el-input v-model="syslogForm.server1" /></el-form-item>
        <el-form-item label="日志服务器2"><el-input v-model="syslogForm.server2" /></el-form-item>
        <el-form-item label="端口"><el-input-number v-model="syslogForm.port" :min="1" :max="65535" /></el-form-item>
        <el-form-item label="Facility">
          <el-select v-model="syslogForm.facility" style="width: 100%">
            <el-option v-for="i in 8" :key="i" :label="`local${i-1}`" :value="`local${i-1}`" />
          </el-select>
        </el-form-item>
        <el-form-item label="日志级别">
          <el-select v-model="syslogForm.level" style="width: 100%">
            <el-option v-for="l in ['emergency','alert','critical','error','warning','notice','informational','debugging']" :key="l" :label="l" :value="l" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="syslogEditVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSyslog">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page {
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
.page-tabs {
  flex: 1;
  min-height: 0;
}
.tab-toolbar {
  margin-bottom: 12px;
}
</style>
