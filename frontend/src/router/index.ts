import { createRouter, createWebHistory } from 'vue-router'
import { getToken } from '@/utils/token'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/login/Login.vue'),
    },
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/devices',
      component: () => import('@/views/devices/index.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'device-list', component: () => import('@/views/devices/list.vue') },
        { path: ':id/config', name: 'device-config', component: () => import('@/views/devices/config.vue') },
        { path: ':id/history', name: 'device-history', component: () => import('@/views/devices/history.vue') },
        { path: ':id/compare', name: 'device-compare', component: () => import('@/views/devices/compare.vue') },
        { path: 'interfaces', name: 'device-interfaces', component: () => import('@/views/devices/interfaces.vue') },
        { path: 'baseline', name: 'device-baseline', component: () => import('@/views/devices/baseline.vue') },
        { path: 'parsers', name: 'device-parsers', component: () => import('@/views/devices/parsers.vue') },
      ],
    },
    {
      path: '/config',
      component: () => import('@/views/devices/index.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/config/slb' },
        { path: 'slb', name: 'config-slb', component: () => import('@/views/config/slb.vue') },
        { path: 'gslb', name: 'config-gslb', component: () => import('@/views/config/gslb.vue') },
        { path: 'firewall', name: 'config-firewall', component: () => import('@/views/config/firewall.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !getToken()) {
    return { name: 'login' }
  }
})

export default router
