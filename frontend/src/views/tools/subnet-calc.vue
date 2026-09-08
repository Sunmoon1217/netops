<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'

const input = ref('10.0.0.0/24')
const splitCount = ref<number | null>(null)
const results = ref<any[]>([])
const error = ref('')

const ipVersion = computed(() => input.value.includes(':') ? 6 : 4)

function calculate() {
  error.value = ''
  results.value = []
  try {
    if (ipVersion.value === 6) {
      calcIPv6()
    } else {
      calcIPv4()
    }
  } catch (e: any) {
    error.value = e.message || '计算错误'
  }
}

function calcIPv4() {
  const parts = input.value.trim().split('/')
  if (parts.length !== 2) { error.value = '格式: IP/CIDR (如 10.0.0.0/24)'; return }
  const ip = parts[0]
  const prefix = parseInt(parts[1])
  if (isNaN(prefix) || prefix < 0 || prefix > 32) { error.value = 'IPv4 CIDR 范围: 0-32'; return }

  const ipNum = ipv4ToNum(ip)
  if (ipNum === null) { error.value = '无效 IPv4 地址'; return }

  const mask = prefix === 0 ? 0 : (~0 << (32 - prefix)) >>> 0
  const network = (ipNum & mask) >>> 0
  const broadcast = (network | ~mask) >>> 0
  const totalHosts = broadcast - network + 1
  const usable = totalHosts >= 2 ? totalHosts - 2 : totalHosts

  results.value.push(
    { label: '版本', value: 'IPv4' },
    { label: '网络地址', value: numToIPv4(network) },
    { label: '广播地址', value: numToIPv4(broadcast) },
    { label: '子网掩码', value: numToIPv4(mask) },
    { label: 'CIDR 前缀', value: `/${prefix}` },
    { label: '总 IP 数', value: totalHosts.toLocaleString() },
    { label: '可用 IP 数', value: usable.toLocaleString() },
    { label: 'IP 范围', value: totalHosts >= 2 ? `${numToIPv4(network + 1)} - ${numToIPv4(broadcast - 1)}` : numToIPv4(network) },
  )

  if (splitCount.value && splitCount.value > 1) {
    const newPrefix = prefix + Math.ceil(Math.log2(splitCount.value))
    if (newPrefix > 32) { error.value = '拆分数超出 CIDR 范围'; return }
    const blockSize = Math.pow(2, 32 - newPrefix)
    results.value.push({ label: '', value: '', isDivider: true })
    results.value.push({ label: `拆分为 ${splitCount.value} 个 /${newPrefix} 子网`, value: '', isHeader: true })
    for (let i = 0; i < Math.min(splitCount.value, 16); i++) {
      const subNet = (network + i * blockSize) >>> 0
      const subBcast = (subNet + blockSize - 1) >>> 0
      results.value.push({ label: `${numToIPv4(subNet)}/${newPrefix}`, value: `${numToIPv4(subNet + 1)} - ${numToIPv4(subBcast - 1)} (${(blockSize - 2).toLocaleString()} 可用)`, isSplit: true })
    }
  }
}

function calcIPv6() {
  const parts = input.value.trim().split('/')
  if (parts.length !== 2) { error.value = '格式: IPv6/CIDR (如 2001:db8::/32)'; return }
  const prefix = parseInt(parts[1])
  if (isNaN(prefix) || prefix < 0 || prefix > 128) { error.value = 'IPv6 CIDR 范围: 0-128'; return }

  const addr = expandIPv6(parts[0])
  if (!addr) { error.value = '无效 IPv6 地址'; return }

  const hostBits = 128 - prefix
  const totalHosts = hostBits <= 53 ? BigInt(2) ** BigInt(hostBits) : null

  results.value.push(
    { label: '版本', value: 'IPv6' },
    { label: '地址', value: parts[0] },
    { label: '展开格式', value: addr },
    { label: 'CIDR 前缀', value: `/${prefix}` },
    { label: '主机位数', value: hostBits.toString() },
    { label: '总 IP 数', value: totalHosts ? totalHosts.toLocaleString() : `2^${hostBits} (过大)` },
  )
}

function ipv4ToNum(ip: string): number | null {
  const parts = ip.split('.')
  if (parts.length !== 4) return null
  let num = 0
  for (const p of parts) {
    const n = parseInt(p)
    if (isNaN(n) || n < 0 || n > 255) return null
    num = (num << 8 | n) >>> 0
  }
  return num
}

function numToIPv4(num: number): string {
  return [(num >>> 24) & 0xff, (num >>> 16) & 0xff, (num >>> 8) & 0xff, num & 0xff].join('.')
}

function expandIPv6(ip: string): string | null {
  try {
    // 展开 :: 并补零
    let expanded = ip
    if (expanded.includes('::')) {
      const parts = expanded.split('::')
      const left = parts[0] ? parts[0].split(':') : []
      const right = parts[1] ? parts[1].split(':') : []
      const missing = 8 - left.length - right.length
      expanded = [...left, ...Array(missing).fill('0'), ...right].join(':')
    }
    // 补齐每组前导零
    return expanded.split(':').map(g => g.padStart(4, '0')).join(':')
  } catch {
    return null
  }
}

onMounted(calculate)
</script>

<template>
  <PageLayout title="子网计算器">
    <template #actions>
      <el-input v-model="input" placeholder="IP/CIDR (IPv4 或 IPv6)" style="width: 220px" @keyup.enter="calculate" />
      <el-input-number v-if="ipVersion === 4" v-model="splitCount" :min="2" :max="256" placeholder="拆分数" controls-position="right" style="width: 120px" />
      <el-button type="primary" @click="calculate">计算</el-button>
    </template>
    <div class="calc-body">
      <el-alert v-if="error" type="error" :closable="false" style="margin-bottom: 12px;">{{ error }}</el-alert>
      <div v-if="results.length" class="result-grid">
        <template v-for="item in results" :key="item.label">
          <div v-if="item.isDivider" class="divider" />
          <div v-else-if="item.isHeader" class="result-header">{{ item.label }}</div>
          <template v-else>
            <div class="result-label" :class="{ 'split-label': item.isSplit }">{{ item.label }}</div>
            <div class="result-value" :class="{ 'split-value': item.isSplit }">{{ item.value }}</div>
          </template>
        </template>
      </div>
    </div>
  </PageLayout>
</template>

<style scoped>
.calc-body { background: #fff; border-radius: 8px; padding: 24px; max-width: 640px; }
.result-grid { display: grid; grid-template-columns: 120px 1fr; gap: 8px 16px; }
.result-label { font-size: 13px; color: var(--el-text-color-secondary); font-family: monospace; }
.result-value { font-size: 13px; font-weight: 600; font-family: monospace; }
.divider { grid-column: 1 / -1; height: 1px; background: var(--el-border-color-lighter); margin: 8px 0; }
.result-header { grid-column: 1 / -1; font-size: 13px; font-weight: 600; color: var(--el-color-primary); }
.split-label { font-size: 12px; }
.split-value { font-size: 12px; font-weight: 400; }
</style>
