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

  const loading = ref(false)
  const errorMessage = ref('')

  async function refresh() {
    loading.value = true
    errorMessage.value = ''

    try {
      network.value = await coverageApi.getNetwork()
    }
    catch {
      errorMessage.value = 'No fue posible consultar la red de cobertura.'
    }
    finally {
      loading.value = false
    }
  }

  onMounted(() => {
    refresh()
  })

  return {
    network,
    loading,
    errorMessage,
    refresh,
  }
}
