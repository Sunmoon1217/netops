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
        {
          path: '',
          name: 'device-list',
          component: () => import('@/views/devices/list.vue'),
        },
        {
          path: ':id/config',
          name: 'device-config',
          component: () => import('@/views/devices/config.vue'),
        },
        {
          path: 'parsers',
          name: 'device-parsers',
          component: () => import('@/views/devices/parsers.vue'),
        },
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
