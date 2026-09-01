<script setup lang="ts">
import { h, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useLayoutStore } from '@/stores/layout'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import {
  IconOverview, IconDevices, IconDeviceList, IconBaseline, IconInterfaces,
  IconParsers, IconConfig, IconLoadBalancer, IconDns, IconPolicy,
  IconIp, IconSubnet, IconLayoutTop, IconLayoutSide, IconSun, IconMoon,
} from './menu-icons'

const router = useRouter()
const route = useRoute()
const layoutStore = useLayoutStore()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isVertical = computed(() => layoutStore.mode === 'side')

function renderIcon(icon: any) {
  return () => h('span', { class: 'menu-icon' }, [h(icon)])
}

interface MenuItem {
  index: string
  label: string
  icon?: () => any
  children?: MenuItem[]
}

const menuOptions: MenuItem[] = [
  { index: '/', label: '总览', icon: renderIcon(IconOverview) },
  {
    index: '/devices', label: '设备管理', icon: renderIcon(IconDevices),
    children: [
      { index: '/devices', label: '设备列表', icon: renderIcon(IconDeviceList) },
      { index: '/devices/interfaces', label: '接口管理', icon: renderIcon(IconInterfaces) },
      { index: '/devices/baseline', label: '基线管理', icon: renderIcon(IconBaseline) },
      { index: '/devices/parsers', label: '解析器模板', icon: renderIcon(IconParsers) },
    ],
  },
  {
    index: '/config', label: '配置管理', icon: renderIcon(IconConfig),
    children: [
      { index: '/config/slb', label: '负载均衡', icon: renderIcon(IconLoadBalancer) },
      { index: '/config/gslb', label: '域名解析', icon: renderIcon(IconDns) },
      { index: '/config/firewall', label: '防火墙策略', icon: renderIcon(IconPolicy) },
    ],
  },
  {
    index: '/ipam', label: 'IP 管理', icon: renderIcon(IconIp),
    children: [
      { index: '/ipam/subnets', label: '网段管理', icon: renderIcon(IconSubnet) },
      { index: '/ipam/ip-addresses', label: 'IP 地址', icon: renderIcon(IconIp) },
      { index: '/ipam/tags', label: '标签管理', icon: renderIcon(IconIp) },
    ],
  },
]

const handleMenuSelect = (index: string) => {
  if (index.startsWith('/')) router.push(index)
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-nav" :class="{ vertical: isVertical }">
    <div class="nav-logo">
      <span class="logo-text"><strong>Network Ops</strong></span>
    </div>

    <el-menu
      :mode="isVertical ? 'vertical' : 'horizontal'"
      :default-active="route.path"
      unique-opened
      class="app-menu"
      @select="handleMenuSelect"
    >
      <template v-for="item in menuOptions" :key="item.index">
        <el-sub-menu v-if="item.children" :index="item.index">
          <template #title>
            <el-icon><component :is="item.icon?.()?.children?.default" /></el-icon>
            <span>{{ item.label }}</span>
          </template>
          <el-menu-item v-for="child in item.children" :key="child.index" :index="child.index">
            <el-icon><component :is="child.icon?.()?.children?.default" /></el-icon>
            <span>{{ child.label }}</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :index="item.index">
          <el-icon><component :is="item.icon?.()?.children?.default" /></el-icon>
          <span>{{ item.label }}</span>
        </el-menu-item>
      </template>
    </el-menu>

    <div class="nav-actions">
      <el-tooltip :content="isVertical ? '切换为顶栏布局' : '切换为侧栏布局'" placement="bottom">
        <el-button :icon="isVertical ? IconLayoutSide : IconLayoutTop" size="small" text @click="layoutStore.setMode(isVertical ? 'top' : 'side')" />
      </el-tooltip>
      <el-tooltip :content="themeStore.isDark ? '切换为亮色模式' : '切换为暗色模式'" placement="bottom">
        <el-button :icon="themeStore.isDark ? IconMoon : IconSun" size="small" text @click="themeStore.toggleDark()" />
      </el-tooltip>
      <span class="nav-user">{{ authStore.user?.username }}</span>
      <el-button type="danger" text size="small" @click="handleLogout">退出</el-button>
    </div>
  </div>
</template>

<style scoped>
.app-nav {
  --nav-height: 3rem;
  display: flex;
  align-items: center;
  width: 100%;
  height: var(--nav-height);
  padding: 0 1.25rem;
  box-sizing: border-box;
  background: var(--el-fill-color-blank, #fff);
  border-bottom: 1px solid var(--el-border-color-lighter, #e4e7ed);
}
.app-nav.vertical {
  flex-direction: column;
  height: 100%;
  padding: 0;
  border-bottom: none;
  border-right: 1px solid var(--el-border-color-lighter, #e4e7ed);
}
.app-nav.vertical :deep(.el-menu) {
  width: 100%;
  flex: 1;
  border-right: none;
}
.nav-logo {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  height: var(--nav-height);
}
.app-nav:not(.vertical) .nav-logo { margin-right: 32px; }
.app-nav.vertical .nav-logo {
  width: 100%;
  justify-content: center;
  border-bottom: 1px solid var(--el-border-color-lighter, #e4e7ed);
}
.logo-text { font-size: 1rem; font-weight: 600; white-space: nowrap; color: var(--el-text-color-primary, #303133); }
.nav-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.app-nav.vertical .nav-actions {
  margin-left: 0;
  margin-top: auto;
  width: 100%;
  justify-content: center;
  padding: 8px;
  border-top: 1px solid var(--el-border-color-lighter, #e4e7ed);
}
.nav-user { font-size: 14px; color: var(--el-text-color-secondary, #909399); }
:deep(.el-menu) { border-right: none; border-bottom: none; height: var(--nav-height); line-height: var(--nav-height); }
:deep(.el-menu-item), :deep(.el-sub-menu__title) { height: var(--nav-height); line-height: var(--nav-height); }
.app-nav:not(.vertical) :deep(.el-menu) { white-space: nowrap; flex: 1; overflow: visible; }
.menu-icon { margin-right: 4px; }
</style>
