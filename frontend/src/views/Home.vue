<script setup lang="ts">
import { ref, onMounted, watch, markRaw } from 'vue'
import api from '@/api/index'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart, GaugeChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([PieChart, BarChart, GaugeChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const data = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const resp = await api.get('/api/assets/overview/')
    data.value = resp.data
  } finally {
    loading.value = false
  }
})

const COLORS = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#48b8d0']

function lookup(map: Record<string, string>, key: string, fallback = '未知'): string {
  return map[key] ?? fallback
}

function pieOpt(title: string, items: { name: string; value: number }[], radius = ['40%', '70%']) {
  return markRaw({
    title: { text: title, left: 'center', textStyle: { fontSize: 13, fontWeight: 600 } },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    color: COLORS,
    series: [{
      type: 'pie', radius, center: ['50%', '55%'],
      label: { fontSize: 11 },
      data: items.filter(i => i.value > 0),
    }],
  })
}

function barOpt(title: string, categories: string[], values: number[], horizontal = false) {
  const axis = horizontal
    ? { xAxis: { type: 'value' }, yAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } } }
    : { xAxis: { type: 'category', data: categories, axisLabel: { rotate: 30, fontSize: 10 } }, yAxis: { type: 'value' } }
  return markRaw({
    title: { text: title, left: 'center', textStyle: { fontSize: 13, fontWeight: 600 } },
    tooltip: { trigger: 'axis' },
    color: COLORS,
    grid: { top: 40, bottom: 50, left: horizontal ? 80 : 40, right: 20 },
    ...axis,
    series: [{ type: 'bar', data: values, barMaxWidth: 32, itemStyle: { borderRadius: [4, 4, 0, 0] } }],
  })
}

function gaugeOpt(title: string, value: number, max: number) {
  return markRaw({
    title: { text: title, left: 'center', textStyle: { fontSize: 13, fontWeight: 600 } },
    series: [{
      type: 'gauge', center: ['50%', '60%'], radius: '80%',
      progress: { show: true, width: 14 },
      axisLine: { lineStyle: { width: 14 } },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      detail: { valueAnimation: true, fontSize: 22, fontWeight: 700, offsetCenter: [0, '10%'], formatter: `{value}/${max}` },
      data: [{ value }],
      max,
    }],
  })
}

function mapItems(arr: { name: string; value: number }[]) {
  return arr.map(i => ({ name: i.name || '未知', value: i.value }))
}

const charts = ref<any[]>([])

watch(data, (val) => { if (val) buildCharts() })

function buildCharts() {
  const d = data.value
  const list: any[] = []

  // 基础设施
  if (d.cabinets_by_dc?.length)
    list.push({ title: '机柜 / 数据中心', option: barOpt('机柜 / 数据中心', d.cabinets_by_dc.map((i: any) => i.room__datacenter__name || '未知'), d.cabinets_by_dc.map((i: any) => i.count)) })

  if (d.cabinets_by_status?.length)
    list.push({ title: '机柜状态', option: pieOpt('机柜状态', mapItems(d.cabinets_by_status.map((i: any) => ({ name: i.status === 'active' ? '在用' : '空闲', value: i.count })))) })

  // 设备
  if (d.device_types?.length)
    list.push({ title: '设备类型', option: pieOpt('设备类型', mapItems(d.device_types.map((i: any) => ({ name: lookup({ firewall: '防火墙', switch: '交换机', loadbalancer: '负载均衡', router: '路由器', server: '服务器', dns: '域名解析', dwdm: '波分复用', internalac: '上网行为管理', wirelessac: '无线控制器' }, i.device_type, i.device_type), value: i.count })))) })

  if (d.devices_by_vendor?.length)
    list.push({ title: '设备 / 厂商', option: barOpt('设备 / 厂商', d.devices_by_vendor.map((i: any) => i.device_model__vendor__name || '未知'), d.devices_by_vendor.map((i: any) => i.count), true) })

  if (d.devices_by_zone?.length)
    list.push({ title: '设备 / 安全域', option: barOpt('设备 / 安全域', d.devices_by_zone.map((i: any) => i.security_zone__name || '未分配'), d.devices_by_zone.map((i: any) => i.count)) })

  // 接口
  list.push({ title: '接口状态', option: gaugeOpt('接口启用率', d.interface_up, d.interface_count || 1) })

  if (d.interface_modes?.length)
    list.push({ title: '接口模式', option: pieOpt('接口模式', mapItems(d.interface_modes.map((i: any) => ({ name: lookup({ layer3: '三层', access: 'Access', trunk: 'Trunk', hybrid: 'Hybrid' }, i.mode || '', '未设置'), value: i.count })))) })

  // 网络
  if (d.route_protocols?.length)
    list.push({ title: '路由协议', option: pieOpt('路由协议分布', mapItems(d.route_protocols.map((i: any) => ({ name: lookup({ static: '静态', connected: '直连', ospf: 'OSPF', bgp: 'BGP', rip: 'RIP', other: '其他' }, i.protocol, i.protocol), value: i.count })))) })

  if (d.routes_by_device?.length)
    list.push({ title: '路由 / 设备', option: barOpt('路由 / 设备 (Top 10)', d.routes_by_device.map((i: any) => i.vrf__device__hostname || '未知'), d.routes_by_device.map((i: any) => i.count), true) })

  // SLB
  if (d.vs_by_protocol?.length)
    list.push({ title: 'VS 协议', option: pieOpt('虚拟服务协议', mapItems(d.vs_by_protocol.map((i: any) => ({ name: (i.protocol || 'tcp').toUpperCase(), value: i.count })))) })

  if (d.pools_by_lb?.length)
    list.push({ title: '池 / LB设备', option: barOpt('池 / LB 设备', d.pools_by_lb.map((i: any) => i.device__hostname || '未知'), d.pools_by_lb.map((i: any) => i.count), true) })

  // 防火墙
  if (d.policies_by_action?.length)
    list.push({ title: '策略动作', option: pieOpt('安全策略动作', mapItems(d.policies_by_action.map((i: any) => ({ name: i.action === 'allow' ? '放行' : '拒绝', value: i.count })))) })

  if (d.nat_by_type?.length)
    list.push({ title: 'NAT 类型', option: pieOpt('NAT 规则类型', mapItems(d.nat_by_type.map((i: any) => ({ name: lookup({ snat: '源转换', dnat: '目的转换', dulnat: '双向转换' }, i.nat_type, i.nat_type), value: i.count })))) })

  if (d.address_books_by_type?.length)
    list.push({ title: '地址簿类型', option: pieOpt('地址簿类型', mapItems(d.address_books_by_type.map((i: any) => ({ name: lookup({ host: '主机', subnet: '子网', range: '范围', addressbook: '地址簿组' }, i.address_type, i.address_type), value: i.count })))) })

  if (d.services_by_protocol?.length)
    list.push({ title: '服务协议', option: pieOpt('服务协议分布', mapItems(d.services_by_protocol.map((i: any) => ({ name: (i.protocol || 'tcp').toUpperCase(), value: i.count })))) })

  // IPAM
  if (d.subnets_by_dc?.length)
    list.push({ title: '子网 / 数据中心', option: barOpt('子网 / 数据中心', d.subnets_by_dc.map((i: any) => i.datacenter__name || '未分配'), d.subnets_by_dc.map((i: any) => i.count)) })

  if (d.subnets_by_zone?.length)
    list.push({ title: '子网 / 安全域', option: barOpt('子网 / 安全域', d.subnets_by_zone.map((i: any) => i.security_zone__name || '未分配'), d.subnets_by_zone.map((i: any) => i.count), true) })

  charts.value = list
}
</script>

<template>
  <div v-loading="loading" class="dashboard">
    <template v-if="data">
      <!-- 概要数字 -->
      <div class="summary-row">
        <el-card v-for="s in [
          { label: '设备', value: data.device_count, color: '#5470c6' },
          { label: '接口', value: data.interface_count, color: '#91cc75' },
          { label: '路由', value: data.route_count, color: '#fac858' },
          { label: '策略', value: data.policy_count, color: '#ee6666' },
          { label: 'NAT', value: data.nat_rule_count, color: '#73c0de' },
          { label: '子网', value: data.subnet_count, color: '#3ba272' },
          { label: 'VS', value: data.vs_count, color: '#9a60b4' },
        ]" :key="s.label" class="summary-card" shadow="hover">
          <div class="summary-value" :style="{ color: s.color }">{{ s.value }}</div>
          <div class="summary-label">{{ s.label }}</div>
        </el-card>
      </div>

      <!-- 图表卡片网格 -->
      <div class="chart-grid">
        <el-card v-for="chart in charts" :key="chart.title" class="chart-card" shadow="hover">
          <v-chart :option="chart.option" autoresize style="height: 280px;" />
        </el-card>
      </div>

      <!-- 数字卡片组 -->
      <div class="count-grid">
        <el-card v-for="item in [
          { label: '数据中心', value: data.dc_count, icon: '🏢' },
          { label: '机房', value: data.room_count, icon: '🏠' },
          { label: '安全域', value: data.security_zone_count, icon: '🔒' },
          { label: '厂商', value: data.vendor_count, icon: '🏭' },
          { label: '设备型号', value: data.device_model_count, icon: '📦' },
          { label: 'VLAN', value: data.vlan_count, icon: '🔗' },
          { label: 'VRF', value: data.vrf_count, icon: '🌐' },
          { label: '地址簿', value: data.address_book_count, icon: '📋' },
          { label: '服务', value: data.service_count, icon: '⚙️' },
          { label: 'GTM 域名', value: data.gtm_wideip_count, icon: '🌍' },
          { label: 'GTM 池', value: data.gtm_pool_count, icon: '🔄' },
          { label: 'GTM DC', value: data.gtm_dc_count, icon: '📡' },
        ]" :key="item.label" class="count-card" shadow="hover">
          <span class="count-icon">{{ item.icon }}</span>
          <div>
            <div class="count-value">{{ item.value }}</div>
            <div class="count-label">{{ item.label }}</div>
          </div>
        </el-card>
      </div>
    </template>
  </div>
</template>

<style scoped>
.dashboard { padding: 16px; display: flex; flex-direction: column; gap: 20px; }
.summary-row { display: flex; gap: 12px; flex-wrap: wrap; }
.summary-card { flex: 1; min-width: 110px; text-align: center; }
.summary-card :deep(.el-card__body) { padding: 14px 10px; }
.summary-value { font-size: 28px; font-weight: 700; font-family: 'SF Mono', 'Cascadia Code', monospace; line-height: 1.2; }
.summary-label { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 2px; }
.chart-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 16px; }
.chart-card :deep(.el-card__body) { padding: 12px; }
.count-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }
.count-card { display: flex; align-items: center; gap: 12px; }
.count-card :deep(.el-card__body) { display: flex; align-items: center; gap: 12px; padding: 14px 16px; }
.count-icon { font-size: 24px; }
.count-value { font-size: 20px; font-weight: 700; font-family: 'SF Mono', 'Cascadia Code', monospace; }
.count-label { font-size: 12px; color: var(--el-text-color-secondary); }
</style>
