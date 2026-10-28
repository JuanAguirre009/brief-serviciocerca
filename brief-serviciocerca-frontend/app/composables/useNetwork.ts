import { ref, onMounted } from 'vue'
import type { CoverageNetwork } from '~/types/coverage'
import { useCoverageApi } from '~/composables/useCoverageApi'

export function useNetwork() {
  const coverageApi = useCoverageApi()
  const network = ref<CoverageNetwork>({
    nodes: [],
    technicians: [],
    connections: [],
  })
  const loading = ref(true)
  const errorMessage = ref('')
  let pending: Promise<void> | undefined
  function refresh(): Promise<void> {
    if (pending) return pending
    loading.value = true
    errorMessage.value = ''
    pending = coverageApi
      .getNetwork()
      .then((value) => {
        network.value = value
      })
      .catch(() => {
        errorMessage.value = 'No fue posible consultar la red de cobertura.'
      })
      .finally(() => {
        loading.value = false
        pending = undefined
      })
    return pending
  }
  onMounted(refresh)
  return { network, loading, errorMessage, refresh }
}
