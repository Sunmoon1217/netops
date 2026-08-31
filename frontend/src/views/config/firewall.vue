<script setup lang="ts">
import { getPolicies, getNatRules, getAddressBooks, getServices } from '@/api/config'
import { getDevices } from '@/api/devices'

const devices = ref<any[]>([])
const policies = ref<any[]>([])
const natRules = ref<any[]>([])
const addressBooks = ref<any[]>([])
const services = ref<any[]>([])
const loading = ref(false)
const filterDevice = ref<number | ''>('')
const activeTab = ref('policy')

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {}
    if (filterDevice.value) params.device = filterDevice.value
    const [pRes, nRes, aRes, sRes] = await Promise.all([
      getPolicies(params), getNatRules(params), getAddressBooks(params), getServices(params),
    ])
    policies.value = pRes.data.results || pRes.data || []
    natRules.value = nRes.data.results || nRes.data || []
    addressBooks.value = aRes.data.results || aRes.data || []
    services.value = sRes.data.results || sRes.data || []
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const fetchDevices = async () => {
  try {
    const res = await getDevices()
    devices.value = res.data.results || res.data || []
  } catch { /* ignore */ }
}

onMounted(() => { fetchDevices(); fetchData() })
</script>

<template>
  <div class="page">
    <div class="page-header">
      <h2>防火墙策略管理</h2>
      <div class="header-actions">
        <el-select v-model="filterDevice" placeholder="设备" clearable style="width: 160px" @change="fetchData">
          <el-option v-for="d in devices" :key="d.id" :label="d.hostname" :value="d.id" />
        </el-select>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="page-tabs">
      <el-tab-pane label="安全策略" name="policy">
        <el-table v-loading="loading" :data="policies" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="130" sortable />
          <el-table-column prop="policy_id" label="策略ID" width="100" />
          <el-table-column prop="order" label="顺序" width="70" />
          <el-table-column prop="name" label="策略名称" width="160" />
          <el-table-column prop="action" label="动作" width="80">
            <template #default="{ row }">
              <el-tag :type="row.action === 'allow' ? 'success' : 'danger'" size="small">{{ row.action }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="log" label="日志" width="60" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.log" type="warning" size="small">开</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="NAT 规则" name="nat">
        <el-table v-loading="loading" :data="natRules" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="130" sortable />
          <el-table-column prop="order" label="顺序" width="70" />
          <el-table-column prop="name" label="规则名称" width="160" />
          <el-table-column prop="nat_type" label="转换类型" width="110">
            <template #default="{ row }">
              <el-tag size="small">{{ row.nat_type }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="enabled" label="启用" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.enabled ? 'success' : 'info'" size="small">{{ row.enabled ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="地址簿" name="addr">
        <el-table v-loading="loading" :data="addressBooks" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="130" sortable />
          <el-table-column prop="name" label="名称" width="160" />
          <el-table-column prop="address_type" label="类型" width="100" />
          <el-table-column prop="ip_address" label="地址" width="150" />
          <el-table-column prop="ip_netmask" label="掩码" width="80" />
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="服务" name="service">
        <el-table v-loading="loading" :data="services" stripe border size="small" height="100%">
          <el-table-column prop="device_hostname" label="设备" width="130" sortable />
          <el-table-column prop="name" label="名称" width="160" />
          <el-table-column prop="protocol" label="协议" width="90" />
          <el-table-column prop="port" label="端口" width="100" />
          <el-table-column prop="port2" label="结束端口" width="100" />
          <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style scoped>
.page { display: flex; flex-direction: column; height: 100%; padding: 20px; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; flex-shrink: 0; }
.page-header h2 { margin: 0; font-size: 1.2rem; font-weight: 600; }
.header-actions { display: flex; gap: 8px; }
.page-tabs { flex: 1; min-height: 0; }
</style>
