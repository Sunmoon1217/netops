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
    if (ipVersion.value === 6) calcIPv6()
    else calcIPv4()
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
  const wildcard = (~mask) >>> 0
  const network = (ipNum & mask) >>> 0
  const broadcast = (network | ~mask) >>> 0
  const totalHosts = broadcast - network + 1
  const usable = totalHosts >= 2 ? totalHosts - 2 : totalHosts

  results.value.push(
    { label: '版本', value: 'IPv4' },
    { label: '地址类型', value: ipv4Type(ipNum) },
    { label: '网络地址', value: numToIPv4(network) },
    { label: '广播地址', value: numToIPv4(broadcast) },
    { label: '子网掩码', value: numToIPv4(mask) },
    { label: '通配符掩码', value: numToIPv4(wildcard), hint: 'ACL 用' },
    { label: 'CIDR 前缀', value: `/${prefix}` },
    { label: '总 IP 数', value: totalHosts.toLocaleString() },
    { label: '可用 IP 数', value: usable.toLocaleString() },
    { label: 'IP 范围', value: totalHosts >= 2 ? `${numToIPv4(network + 1)} — ${numToIPv4(broadcast - 1)}` : numToIPv4(network) },
    { label: '二进制掩码', value: numToBinary(mask) },
  )

  // 子网拆分
  if (splitCount.value && splitCount.value > 1) {
    const newPrefix = prefix + Math.ceil(Math.log2(splitCount.value))
    if (newPrefix > 32) { error.value = '拆分数超出 CIDR 范围'; return }
    const blockSize = Math.pow(2, 32 - newPrefix)
    results.value.push({ isDivider: true })
    results.value.push({ isHeader: true, label: `拆分为 ${splitCount.value} 个 /${newPrefix} 子网` })
    for (let i = 0; i < Math.min(splitCount.value, 32); i++) {
      const subNet = (network + i * blockSize) >>> 0
      const subBcast = (subNet + blockSize - 1) >>> 0
      results.value.push({
        isSplit: true,
        label: `${numToIPv4(subNet)}/${newPrefix}`,
        value: `${numToIPv4(subNet + 1)} — ${numToIPv4(subBcast - 1)}`,
        extra: `${(blockSize - 2).toLocaleString()} 可用`,
      })
    }
  }
}

function calcIPv6() {
  const parts = input.value.trim().split('/')
  if (parts.length !== 2) { error.value = '格式: IPv6/CIDR (如 2001:db8::/32)'; return }
  const ip = parts[0]
  const prefix = parseInt(parts[1])
  if (isNaN(prefix) || prefix < 0 || prefix > 128) { error.value = 'IPv6 CIDR 范围: 0-128'; return }

  const expanded = expandIPv6(ip)
  if (!expanded) { error.value = '无效 IPv6 地址'; return }

  const hostBits = 128 - prefix
  const totalHosts = hostBits <= 53 ? (BigInt(2) ** BigInt(hostBits)).toLocaleString() : `2^${hostBits}`
  const usable = hostBits >= 2 && hostBits <= 53 ? (BigInt(2) ** BigInt(hostBits) - 2n).toLocaleString() : totalHosts

  // 计算网络地址
  const addrBigInt = ipv6ToBigInt(expanded)
  const maskBigInt = prefix === 0 ? 0n : ((1n << 128n) - (1n << BigInt(128 - prefix)))
  const networkBigInt = addrBigInt & maskBigInt
  const networkAddr = bigIntToIPv6(networkBigInt)

  results.value.push(
    { label: '版本', value: 'IPv6' },
    { label: '地址类型', value: ipv6Type(ip) },
    { label: '输入地址', value: ip },
    { label: '展开格式', value: expanded },
    { label: '网络地址', value: networkAddr },
    { label: 'CIDR 前缀', value: `/${prefix}` },
    { label: '主机位数', value: hostBits.toString() },
    { label: '总 IP 数', value: totalHosts },
    { label: '可用 IP 数', value: usable },
  )
}

// --- IPv4 工具函数 ---

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

function numToBinary(num: number): string {
  return [(num >>> 24) & 0xff, (num >>> 16) & 0xff, (num >>> 8) & 0xff, num & 0xff]
    .map(b => b.toString(2).padStart(8, '0'))
    .join('.')
}

function ipv4Type(num: number): string {
  const a = (num >>> 24) & 0xff
  const b = (num >>> 16) & 0xff
  if (a === 127) return '环回地址 (Loopback)'
  if (a === 10) return '私有地址 (A类)'
  if (a === 172 && b >= 16 && b <= 31) return '私有地址 (B类)'
  if (a === 192 && b === 168) return '私有地址 (C类)'
  if (a === 169 && b === 254) return '链路本地 (Link-local)'
  if (a >= 224 && a <= 239) return '组播地址 (Multicast)'
  if (a >= 240) return '保留地址'
  return '公网地址'
}

// --- IPv6 工具函数 ---

function expandIPv6(ip: string): string | null {
  try {
    let expanded = ip
    if (expanded.includes('::')) {
      const parts = expanded.split('::')
      const left = parts[0] ? parts[0].split(':') : []
      const right = parts[1] ? parts[1].split(':') : []
      const missing = 8 - left.length - right.length
      expanded = [...left, ...Array(missing).fill('0'), ...right].join(':')
    }
    return expanded.split(':').map(g => g.padStart(4, '0')).join(':')
  } catch { return null }
}

function ipv6ToBigInt(expanded: string): bigint {
  const groups = expanded.split(':')
  let result = 0n
  for (const g of groups) {
    result = (result << 16n) | BigInt(parseInt(g, 16))
  }
  return result
}

function bigIntToIPv6(num: bigint): string {
  const groups: string[] = []
  for (let i = 7; i >= 0; i--) {
    groups.push(((num >> BigInt(i * 16)) & 0xffffn).toString(16).padStart(4, '0'))
  }
  return groups.join(':')
}

function ipv6Type(ip: string): string {
  const lower = ip.toLowerCase()
  if (lower.startsWith('::1')) return '环回地址 (Loopback)'
  if (lower.startsWith('fe80')) return '链路本地 (Link-local)'
  if (lower.startsWith('fc') || lower.startsWith('fd')) return '唯一本地 (ULA)'
  if (lower.startsWith('ff')) return '组播地址 (Multicast)'
  if (lower.startsWith('2001:db8')) return '文档地址 (Documentation)'
  if (lower.startsWith('::ffff:')) return 'IPv4 映射地址'
  return '全局单播 (Global Unicast)'
}

onMounted(calculate)
</script>

<template>
  <PageLayout title="子网计算器">
    <div class="calc-layout">
      <!-- 左侧输入区 -->
      <div class="calc-input">
        <el-input v-model="input" placeholder="IP/CIDR (IPv4 或 IPv6)" @keyup.enter="calculate" />
        <el-input-number v-if="ipVersion === 4" v-model="splitCount" :min="2" :max="32" placeholder="拆分数" controls-position="right" style="width: 100%;" />
        <el-button type="primary" style="width: 100%;" @click="calculate">计算</el-button>
        <el-alert v-if="error" type="error" :closable="false" style="margin-top: 8px;">{{ error }}</el-alert>
      </div>
      <!-- 右侧结果区 -->
      <div class="calc-result">
        <el-empty v-if="!results.length && !error" description="输入 IP/CIDR 后点击计算" />
        <div v-if="results.length" class="result-grid">
          <template v-for="(item, idx) in results" :key="idx">
            <div v-if="item.isDivider" class="divider" />
            <div v-else-if="item.isHeader" class="result-header">{{ item.label }}</div>
            <template v-else>
              <div class="result-label" :class="{ 'split-label': item.isSplit }">
                {{ item.label }}
                <span v-if="item.hint" class="hint">{{ item.hint }}</span>
              </div>
              <div class="result-value" :class="{ 'split-value': item.isSplit }">
                <span>{{ item.value }}</span>
                <span v-if="item.extra" class="extra">{{ item.extra }}</span>
              </div>
            </template>
          </template>
        </div>
      </div>
    </div>
  </PageLayout>
</template>

<style scoped>
.calc-layout { display: flex; gap: 20px; height: 100%; }
.calc-input { width: 260px; flex-shrink: 0; background: #fff; border-radius: 8px; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
.calc-result { flex: 1; min-width: 0; background: #fff; border-radius: 8px; padding: 24px; overflow: auto; }
.result-grid { display: grid; grid-template-columns: 120px 1fr; gap: 8px 16px; }
.result-label { font-size: 13px; color: var(--el-text-color-secondary); font-family: monospace; }
.result-value { font-size: 13px; font-weight: 600; font-family: monospace; }
.divider { grid-column: 1 / -1; height: 1px; background: var(--el-border-color-lighter); margin: 8px 0; }
.result-header { grid-column: 1 / -1; font-size: 13px; font-weight: 600; color: var(--el-color-primary); }
.split-label { font-size: 12px; }
.split-value { font-size: 12px; font-weight: 400; }
.hint { font-size: 11px; color: var(--el-text-color-placeholder); margin-left: 4px; }
.extra { font-size: 11px; color: var(--el-text-color-secondary); margin-left: 8px; font-weight: 400; }
</style>
