<script setup lang="ts">
import PageLayout from '@/ui/PageLayout.vue'

const ipVer = ref<'v4' | 'v6'>('v4')
const input = ref('10.0.0.0/24')
const splitCount = ref<number | null>(null)
const hostCount = ref<number | null>(null)
const maskInput = ref('')
const results = ref<any[]>([])
const maskResults = ref<any[]>([])
const hostResults = ref<any[]>([])
const error = ref('')

function calculate() {
  error.value = ''
  results.value = []
  try {
    if (ipVer.value === 'v6') calcIPv6()
    else calcIPv4()
  } catch (e: any) {
    error.value = e.message || '计算错误'
  }
}

function calcMask() {
  maskResults.value = []
  const val = maskInput.value.trim()
  if (!val) return
  if (val.startsWith('/')) {
    const prefix = parseInt(val.slice(1))
    if (isNaN(prefix) || prefix < 0 || prefix > 32) return
    const mask = prefix === 0 ? 0 : (~0 << (32 - prefix)) >>> 0
    maskResults.value.push(
      { label: 'CIDR', value: `/${prefix}` },
      { label: '点分十进制', value: numToIPv4(mask) },
      { label: '十六进制', value: '0x' + (mask >>> 0).toString(16).toUpperCase().padStart(8, '0') },
      { label: '二进制', value: numToBinary(mask) },
      { label: '可用主机数', value: (prefix >= 31 ? Math.pow(2, 32 - prefix) : Math.pow(2, 32 - prefix) - 2).toLocaleString() },
    )
  } else {
    const num = ipv4ToNum(val)
    if (num === null) return
    const binary = num.toString(2).padStart(32, '0')
    if (!/^1*0*$/.test(binary)) { maskResults.value.push({ label: '错误', value: '不是合法子网掩码' }); return }
    const prefix = binary.indexOf('0') === -1 ? 32 : binary.indexOf('0')
    maskResults.value.push(
      { label: '点分十进制', value: val },
      { label: 'CIDR', value: `/${prefix}` },
      { label: '十六进制', value: '0x' + (num >>> 0).toString(16).toUpperCase().padStart(8, '0') },
      { label: '二进制', value: numToBinary(num) },
      { label: '通配符掩码', value: numToIPv4((~num) >>> 0) },
      { label: '可用主机数', value: (prefix >= 31 ? Math.pow(2, 32 - prefix) : Math.pow(2, 32 - prefix) - 2).toLocaleString() },
    )
  }
}

function calcHosts() {
  hostResults.value = []
  if (!hostCount.value || hostCount.value < 1) return
  const needed = hostCount.value + 2
  const bits = Math.ceil(Math.log2(needed))
  const prefix = 32 - bits
  if (prefix < 0) { hostResults.value.push({ label: '错误', value: '超出 IPv4 范围' }); return }
  const available = Math.pow(2, bits) - 2
  const mask = prefix === 0 ? 0 : (~0 << (32 - prefix)) >>> 0
  hostResults.value.push(
    { label: '需要主机数', value: hostCount.value.toLocaleString() },
    { label: '推荐 CIDR', value: `/${prefix}` },
    { label: '子网掩码', value: numToIPv4(mask) },
    { label: '实际可用', value: available.toLocaleString() },
  )
}

function calcIPv4() {
  const parts = input.value.trim().split('/')
  if (parts.length !== 2) { error.value = '格式: IP/CIDR (如 10.0.0.0/24)'; return }
  const ip = parts[0]
  const prefix = parseInt(parts[1])
  if (isNaN(prefix) || prefix < 0 || prefix > 32) { error.value = 'CIDR 范围: 0-32'; return }
  const ipNum = ipv4ToNum(ip)
  if (ipNum === null) { error.value = '无效 IPv4 地址'; return }
  const mask = prefix === 0 ? 0 : (~0 << (32 - prefix)) >>> 0
  const wildcard = (~mask) >>> 0
  const network = (ipNum & mask) >>> 0
  const broadcast = (network | ~mask) >>> 0
  const totalHosts = broadcast - network + 1
  const usable = totalHosts >= 2 ? totalHosts - 2 : totalHosts
  results.value.push(
    { label: '地址类型', value: ipv4Type(ipNum) },
    { label: '网络地址', value: numToIPv4(network) },
    { label: '广播地址', value: numToIPv4(broadcast) },
    { label: '子网掩码', value: `${numToIPv4(mask)}  /${prefix}` },
    { label: '通配符掩码', value: numToIPv4(wildcard) },
    { label: '十六进制掩码', value: '0x' + (mask >>> 0).toString(16).toUpperCase().padStart(8, '0') },
    { label: '总 IP 数', value: totalHosts.toLocaleString() },
    { label: '可用 IP 数', value: usable.toLocaleString() },
    { label: '首可用 IP', value: totalHosts >= 2 ? numToIPv4(network + 1) : '-' },
    { label: '末可用 IP', value: totalHosts >= 2 ? numToIPv4(broadcast - 1) : '-' },
    { label: '二进制掩码', value: numToBinary(mask) },
  )
  if (splitCount.value && splitCount.value > 1) {
    const newPrefix = prefix + Math.ceil(Math.log2(splitCount.value))
    if (newPrefix > 32) { error.value = '拆分数超出 CIDR 范围'; return }
    const blockSize = Math.pow(2, 32 - newPrefix)
    results.value.push({ isDivider: true })
    results.value.push({ isHeader: true, label: `拆分为 ${splitCount.value} 个 /${newPrefix} 子网` })
    for (let i = 0; i < Math.min(splitCount.value, 32); i++) {
      const subNet = (network + i * blockSize) >>> 0
      const subBcast = (subNet + blockSize - 1) >>> 0
      results.value.push({ isSplit: true, label: `${numToIPv4(subNet)}/${newPrefix}`, value: `${numToIPv4(subNet + 1)} — ${numToIPv4(subBcast - 1)}`, extra: `${(blockSize - 2).toLocaleString()} 可用` })
    }
  }
}

function calcIPv6() {
  const parts = input.value.trim().split('/')
  if (parts.length !== 2) { error.value = '格式: IPv6/CIDR (如 2001:db8::/32)'; return }
  const prefix = parseInt(parts[1])
  if (isNaN(prefix) || prefix < 0 || prefix > 128) { error.value = 'CIDR 范围: 0-128'; return }
  const expanded = expandIPv6(parts[0])
  if (!expanded) { error.value = '无效 IPv6 地址'; return }
  const hostBits = 128 - prefix
  const totalHosts = hostBits <= 53 ? (BigInt(2) ** BigInt(hostBits)).toLocaleString() : `2^${hostBits}`
  const addrBigInt = ipv6ToBigInt(expanded)
  const maskBigInt = prefix === 0 ? 0n : ((1n << 128n) - (1n << BigInt(128 - prefix)))
  const networkBigInt = addrBigInt & maskBigInt
  results.value.push(
    { label: '地址类型', value: ipv6Type(parts[0]) },
    { label: '展开格式', value: expanded },
    { label: '网络地址', value: bigIntToIPv6(networkBigInt) },
    { label: 'CIDR 前缀', value: `/${prefix}` },
    { label: '主机位数', value: hostBits.toString() },
    { label: '总 IP 数', value: totalHosts },
  )
}

function ipv4ToNum(ip: string): number | null {
  const parts = ip.split('.'); if (parts.length !== 4) return null
  let num = 0; for (const p of parts) { const n = parseInt(p); if (isNaN(n) || n < 0 || n > 255) return null; num = (num << 8 | n) >>> 0 }; return num
}
function numToIPv4(num: number): string { return [(num >>> 24) & 0xff, (num >>> 16) & 0xff, (num >>> 8) & 0xff, num & 0xff].join('.') }
function numToBinary(num: number): string { return [(num >>> 24) & 0xff, (num >>> 16) & 0xff, (num >>> 8) & 0xff, num & 0xff].map(b => b.toString(2).padStart(8, '0')).join('.') }
function ipv4Type(num: number): string {
  const a = (num >>> 24) & 0xff, b = (num >>> 16) & 0xff
  if (a === 127) return '环回地址'; if (a === 10) return 'A 类私有'; if (a === 172 && b >= 16 && b <= 31) return 'B 类私有'
  if (a === 192 && b === 168) return 'C 类私有'; if (a === 169 && b === 254) return '链路本地'
  if (a >= 224 && a <= 239) return '组播地址'; if (a >= 240) return '保留地址'; return '公网地址'
}
function expandIPv6(ip: string): string | null {
  try { let e = ip; if (e.includes('::')) { const p = e.split('::'); const l = p[0] ? p[0].split(':') : []; const r = p[1] ? p[1].split(':') : []; e = [...l, ...Array(8 - l.length - r.length).fill('0'), ...r].join(':') }; return e.split(':').map(g => g.padStart(4, '0')).join(':') } catch { return null }
}
function ipv6ToBigInt(e: string): bigint { let r = 0n; for (const g of e.split(':')) r = (r << 16n) | BigInt(parseInt(g, 16)); return r }
function bigIntToIPv6(n: bigint): string { const g: string[] = []; for (let i = 7; i >= 0; i--) g.push(((n >> BigInt(i * 16)) & 0xffffn).toString(16).padStart(4, '0')); return g.join(':') }
function ipv6Type(ip: string): string {
  const l = ip.toLowerCase()
  if (l.startsWith('::1')) return '环回地址'; if (l.startsWith('fe80')) return '链路本地'; if (l.startsWith('fc') || l.startsWith('fd')) return '唯一本地 (ULA)'
  if (l.startsWith('ff')) return '组播地址'; if (l.startsWith('2001:db8')) return '文档地址'; if (l.startsWith('::ffff:')) return 'IPv4 映射'; return '全局单播'
}

function resetResults() {
  results.value = []; maskResults.value = []; hostResults.value = []; error.value = ''
}

onMounted(calculate)
</script>

<template>
  <PageLayout title="子网计算器">
    <!-- 输入区 -->
    <div class="input-bar">
      <el-segmented v-model="ipVer" :options="[{ label: 'IPv4', value: 'v4' }, { label: 'IPv6', value: 'v6' }]" size="small" @change="resetResults" />
      <el-input v-model="input" :placeholder="ipVer === 'v4' ? '10.0.0.0/24' : '2001:db8::/32'" style="width: 220px" @keyup.enter="calculate" />
      <el-input-number v-if="ipVer === 'v4'" v-model="splitCount" :min="2" :max="32" placeholder="拆分数" controls-position="right" style="width: 110px" />
      <el-button type="primary" @click="calculate">计算</el-button>

      <el-divider v-if="ipVer === 'v4'" direction="vertical" />

      <template v-if="ipVer === 'v4'">
        <el-input v-model="maskInput" placeholder="掩码转换: /24 或 255.255.255.0" style="width: 230px" @keyup.enter="calcMask" />
        <el-button @click="calcMask">转换</el-button>
        <el-divider direction="vertical" />
        <el-input-number v-model="hostCount" :min="1" placeholder="主机数" controls-position="right" style="width: 110px" />
        <el-button @click="calcHosts">推荐</el-button>
      </template>
    </div>

    <el-alert v-if="error" type="error" :closable="false" style="margin-bottom: 12px;">{{ error }}</el-alert>

    <!-- 结果区 -->
    <template v-if="results.length || maskResults.length || hostResults.length">
      <!-- CIDR 结果 -->
      <div v-if="results.length" class="result-section">
        <div class="section-title">CIDR 计算结果</div>
        <div class="result-grid">
          <template v-for="(item, idx) in results" :key="idx">
            <div v-if="item.isDivider" class="divider" />
            <div v-else-if="item.isHeader" class="result-header">{{ item.label }}</div>
            <template v-else>
              <div class="result-label">{{ item.label }}</div>
              <div class="result-value">{{ item.value }}<span v-if="item.extra" class="extra">{{ item.extra }}</span></div>
            </template>
          </template>
        </div>
      </div>

      <!-- 掩码转换结果 -->
      <div v-if="maskResults.length" class="result-section">
        <div class="section-title">掩码转换</div>
        <div class="result-grid">
          <template v-for="(item, idx) in maskResults" :key="'m'+idx">
            <div class="result-label">{{ item.label }}</div>
            <div class="result-value">{{ item.value }}</div>
          </template>
        </div>
      </div>

      <!-- 主机数推荐结果 -->
      <div v-if="hostResults.length" class="result-section">
        <div class="section-title">主机数推荐掩码</div>
        <div class="result-grid">
          <template v-for="(item, idx) in hostResults" :key="'h'+idx">
            <div class="result-label">{{ item.label }}</div>
            <div class="result-value">{{ item.value }}</div>
          </template>
        </div>
      </div>
    </template>

    <el-empty v-if="!results.length && !maskResults.length && !hostResults.length && !error" description="输入参数后点击计算" />
  </PageLayout>
</template>

<style scoped>
.input-bar { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 16px; }
.result-section { margin-bottom: 20px; }
.section-title { font-size: 13px; font-weight: 600; color: var(--el-color-primary); margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px solid var(--el-border-color-lighter); }
.result-grid { display: grid; grid-template-columns: 120px 1fr; gap: 6px 16px; }
.result-label { font-size: 13px; color: var(--el-text-color-secondary); font-family: monospace; }
.result-value { font-size: 13px; font-weight: 600; font-family: monospace; word-break: break-all; }
.divider { grid-column: 1 / -1; height: 1px; background: var(--el-border-color-lighter); margin: 6px 0; }
.result-header { grid-column: 1 / -1; font-size: 13px; font-weight: 600; color: var(--el-color-primary); }
.extra { font-size: 11px; color: var(--el-text-color-secondary); margin-left: 8px; font-weight: 400; }
</style>
