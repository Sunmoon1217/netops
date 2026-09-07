import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export function useCrudApi<T extends Record<string, any> = any>(searchFields: string[] = []) {
  const data = ref<T[]>([]) as any
  const loading = ref(false)
  const search = ref('')

  const filteredData = computed(() => {
    if (!search.value || !searchFields.length) return data.value
    const kw = search.value.toLowerCase()
    return data.value.filter((item: any) =>
      searchFields.some(f => String(item[f] ?? '').toLowerCase().includes(kw))
    )
  })

  async function fetchData(apiFn: () => Promise<any>) {
    loading.value = true
    try {
      const res = await apiFn()
      data.value = res.data?.results ?? res.data ?? res.results ?? res ?? []
    } catch {
      ElMessage.error('加载失败')
    } finally {
      loading.value = false
    }
  }

  async function handleSave(apiFn: () => Promise<any>, onSuccess?: () => void) {
    try {
      await apiFn()
      ElMessage.success('保存成功')
      onSuccess?.()
    } catch (e: any) {
      ElMessage.error(e?.response?.data?.detail || e?.response?.data?.name?.[0] || '保存失败')
    }
  }

  async function handleDelete(name: string, apiFn: () => Promise<any>, onSuccess?: () => void) {
    await ElMessageBox.confirm(`确认删除 ${name}？`, '提示', { type: 'warning' })
    try {
      await apiFn()
      ElMessage.success('已删除')
      onSuccess?.()
    } catch {
      ElMessage.error('删除失败')
    }
  }

  return { data, loading, search, filteredData, fetchData, handleSave, handleDelete }
}
