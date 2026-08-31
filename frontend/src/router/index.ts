import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue')
    },
    {
      path: '/devices',
      component: () => import('@/views/devices/index.vue'),
      children: [
        {
          path: '',
          name: 'device-list',
          component: () => import('@/views/devices/list.vue')
        }
      ]
    }
  ]
})

export default router
