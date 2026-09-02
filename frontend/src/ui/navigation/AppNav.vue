<script setup lang="ts">
import { h, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElIcon } from 'element-plus'
import type { Component } from 'vue'
import { useLayoutStore } from '@/stores/layout'
import {
  IconOverview, IconDevices, IconDeviceList, IconBaseline, IconInterfaces,
  IconParsers, IconConfig, IconLoadBalancer, IconDns, IconPolicy,
  IconIp, IconSubnet,
} from './menu-icons'

const router = useRouter()
const route = useRoute()
const layoutStore = useLayoutStore()

const isVertical = computed(() => layoutStore.mode === 'side')
const isCollapsed = computed(() => layoutStore.collapsed)

function renderIcon(icon: Component) {
  return () => h(ElIcon, null, { default: () => h(icon) })
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
</script>

<template>
  <div class="app-nav" :class="{ vertical: isVertical, collapsed: isVertical && isCollapsed }">
    <div class="nav-logo">
      <span v-if="!isVertical || !isCollapsed" class="logo-text"><strong>Network Ops</strong></span>
      <span v-else class="logo-icon"><strong>N</strong></span>
    </div>

    <el-menu
      :mode="isVertical ? 'vertical' : 'horizontal'"
      :default-active="route.path"
      :collapse="isVertical && isCollapsed"
      unique-opened
      :collapse-transition="true"
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
  </div>
</template>

<style lang="css" scoped>
.app-nav {
  --nav-height: 3rem;
  display: flex;
  align-items: center;
  width: 100%;
  height: var(--nav-height);
  padding: 0 1.25rem;
  box-sizing: border-box;
  background: var(--el-fill-color-blank);
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.app-nav.vertical {
  flex-direction: column;
  height: 100%;
  padding: 0;
  border-bottom: none;
}
.app-nav.vertical :deep(.el-menu) {
  width: 100%;
  flex: 1;
  border-right: none;
}
.nav-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  height: var(--nav-height);
  box-sizing: border-box;
}
.app-nav:not(.vertical) .nav-logo { margin-right: 32px; }
.app-nav.vertical .nav-logo {
  width: 100%;
  border-bottom: 1px solid var(--el-border-color-lighter);
}
.logo-text { font-size: 1rem; font-weight: 600; white-space: nowrap; color: var(--el-text-color-primary); }
.logo-icon { font-size: 1.2rem; color: var(--el-color-primary); }
:deep(.el-menu) { border-right: none; border-bottom: none; height: var(--nav-height); line-height: var(--nav-height); }
:deep(.el-menu-item) { height: var(--nav-height); line-height: var(--nav-height); font-size: 14px; padding: 0 0.75rem; }
:deep(.el-sub-menu) { height: var(--nav-height); }
:deep(.el-sub-menu__title) { height: var(--nav-height) !important; line-height: var(--nav-height) !important; padding: 0 0.75rem !important; }
.app-nav:not(.vertical) :deep(.el-menu) { white-space: nowrap; flex: 1; overflow: visible; }
:deep(.el-menu-item:hover) { background-color: var(--el-fill-color-light); }
:deep(.el-menu-item.is-active) { color: var(--el-color-primary); }

</style>
