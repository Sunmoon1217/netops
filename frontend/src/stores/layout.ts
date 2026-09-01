import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useLayoutStore = defineStore('layout', () => {
  const viewtitle = ref('默认标题')

  const mode = ref<'top' | 'side'>(
    (localStorage.getItem('layoutMode') as 'top' | 'side') || 'top',
  )

  const collapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true')

  const SIDEBAR_WIDTH = 180
  const SIDEBAR_COLLAPSED_WIDTH = 56

  const sidebarWidth = computed(() =>
    collapsed.value ? SIDEBAR_COLLAPSED_WIDTH : SIDEBAR_WIDTH,
  )

  const setMode = (m: 'top' | 'side') => {
    mode.value = m
    localStorage.setItem('layoutMode', m)
  }

  const toggleCollapsed = () => {
    collapsed.value = !collapsed.value
    localStorage.setItem('sidebarCollapsed', String(collapsed.value))
  }

  return { viewtitle, mode, collapsed, sidebarWidth, SIDEBAR_WIDTH, SIDEBAR_COLLAPSED_WIDTH, setMode, toggleCollapsed }
})
