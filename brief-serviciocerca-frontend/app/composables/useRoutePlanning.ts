import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useCoverageApi } from '~/composables/useCoverageApi'
import { useNetwork } from '~/composables/useNetwork'
import { formatApiError } from '~/utils/formatApiError'
import {
  compareRouteMinutes,
  resolvePathSegments,
} from '~/utils/routeComparison'
import type { CoverageCheckResult, ShortestRouteResult } from '~/types/coverage'

export function useRoutePlanning() {
  const api = useCoverageApi()
  const {
    network,
    loading: networkLoading,
    errorMessage: networkError,
    refresh,
  } = useNetwork()
  const originId = ref<number | null>(null)
  const destinationId = ref<number | null>(null)
  const result = ref<ShortestRouteResult | null>(null)
  const bfs = ref<CoverageCheckResult | null>(null)
  const queryLoading = ref(false)
  const comparisonLoading = ref(false)
  const queryError = ref('')
  const comparisonError = ref('')
  const activeRoute = ref<'dijkstra' | 'bfs'>('dijkstra')
  const resultKey = ref(0)
  let version = 0

  const bases = computed(() =>
    network.value.nodes.filter((node) => node.type === 'BASE'),
  )
  const zones = computed(() =>
    network.value.nodes.filter((node) => node.type === 'ZONE'),
  )
  watch(
    bases,
    (nodes) => {
      if (!nodes.some((node) => node.id === originId.value))
        originId.value = nodes[0]?.id ?? null
    },
    { immediate: true },
  )
  watch(
    zones,
    (nodes) => {
      if (!nodes.some((node) => node.id === destinationId.value))
        destinationId.value = nodes[0]?.id ?? null
    },
    { immediate: true },
  )

  function clearResults() {
    version++
    result.value = null
    bfs.value = null
    queryLoading.value = false
    comparisonLoading.value = false
    queryError.value = ''
    comparisonError.value = ''
    activeRoute.value = 'dijkstra'
    resultKey.value++
  }
  watch([originId, destinationId, network], clearResults, { flush: 'sync' })
  onBeforeUnmount(() => {
    version++
  })

  const canQuery = computed(
    () =>
      !networkLoading.value &&
      !networkError.value &&
      !queryLoading.value &&
      originId.value !== null &&
      destinationId.value !== null,
  )
  async function calculateRoute() {
    if (!canQuery.value) return
    const origin = originId.value!
    const destination = destinationId.value!
    clearResults()
    const request = version
    queryLoading.value = true
    try {
      const response = await api.getShortestRoute(origin, destination)
      if (request === version) {
        result.value = response
        resultKey.value++
      }
    } catch (error) {
      if (request === version) queryError.value = formatApiError(error)
    } finally {
      if (request === version) queryLoading.value = false
    }
  }

  async function compareWithBfs() {
    if (
      !result.value ||
      comparisonLoading.value ||
      networkLoading.value ||
      networkError.value
    )
      return
    const request = version
    const { origin, destination } = result.value
    bfs.value = null
    activeRoute.value = 'dijkstra'
    comparisonLoading.value = true
    comparisonError.value = ''
    try {
      const response = await api.getReachability(origin.id, destination.id)
      if (request !== version) return
      if (response.mode !== 'check') {
        comparisonError.value =
          'La respuesta BFS no corresponde a una consulta de origen y destino.'
        return
      }
      bfs.value = response
    } catch (error) {
      if (request === version) comparisonError.value = formatApiError(error)
    } finally {
      if (request === version) comparisonLoading.value = false
    }
  }

  async function refreshNetwork() {
    clearResults()
    await refresh()
  }
  const bfsSegments = computed(() =>
    bfs.value?.covered
      ? resolvePathSegments(bfs.value.path, network.value.connections)
      : null,
  )
  const bfsMinutes = computed(() =>
    bfsSegments.value === null
      ? null
      : bfsSegments.value.reduce(
          (total, segment) => total + segment.estimated_minutes,
          0,
        ),
  )
  const comparison = computed(() =>
    compareRouteMinutes(bfsMinutes.value, result.value?.total_minutes ?? null),
  )
  const activeResult = computed(() =>
    activeRoute.value === 'bfs' ? bfs.value : result.value,
  )
  const pathNodeIds = computed(() => {
    if (activeRoute.value === 'bfs')
      return bfs.value?.covered ? bfs.value.path.map((node) => node.id) : []
    return result.value?.reachable
      ? result.value.path.map((node) => node.id)
      : []
  })
  const visitedNodeIds = computed(
    () => activeResult.value?.traversal_order.map((node) => node.id) ?? [],
  )
  const highlightedSegments = computed(() => {
    if (activeRoute.value !== 'bfs') return result.value?.segments
    if (!bfs.value?.covered) return []
    const path = bfs.value.path
    return path
      .slice(1)
      .flatMap(
        (node, index) =>
          resolvePathSegments(
            [path[index]!, node],
            network.value.connections,
          ) ?? [],
      )
  })

  return {
    network,
    networkLoading,
    networkError,
    bases,
    zones,
    originId,
    destinationId,
    result,
    bfs,
    queryLoading,
    comparisonLoading,
    queryError,
    comparisonError,
    activeRoute,
    resultKey,
    canQuery,
    bfsSegments,
    bfsMinutes,
    comparison,
    pathNodeIds,
    visitedNodeIds,
    highlightedSegments,
    calculateRoute,
    compareWithBfs,
    clearResults,
    refreshNetwork,
  }
}
