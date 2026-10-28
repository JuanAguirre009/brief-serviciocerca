import { useRuntimeConfig } from '#app'
import type {
  Connection,
  ConnectionCreatePayload,
  CoverageNetwork,
  CoverageNode,
  NodeCreatePayload,
  Technician,
  TechnicianCreatePayload,
  CoverageCheckResult,
  CoverageReachabilityResult,
} from '~/types/coverage'


export function useCoverageApi() {
  const config = useRuntimeConfig()

  const apiBase = config.public.apiBase


  function getNodes() {
    return $fetch<CoverageNode[]>(
      `${apiBase}/nodes/`,
    )
  }


  function createNode(
    payload: NodeCreatePayload,
  ) {
    return $fetch<CoverageNode>(
      `${apiBase}/nodes/`,
      {
        method: 'POST',
        body: payload,
      },
    )
  }


  function getTechnicians() {
    return $fetch<Technician[]>(
      `${apiBase}/technicians/`,
    )
  }


  function createTechnician(
    payload: TechnicianCreatePayload,
  ) {
    return $fetch<Technician>(
      `${apiBase}/technicians/`,
      {
        method: 'POST',
        body: payload,
      },
    )
  }


  function getConnections() {
    return $fetch<Connection[]>(
      `${apiBase}/connections/`,
    )
  }


  function createConnection(
    payload: ConnectionCreatePayload,
  ) {
    return $fetch<Connection>(
      `${apiBase}/connections/`,
      {
        method: 'POST',
        body: payload,
      },
    )
  }


  function getNetwork() {
    return $fetch<CoverageNetwork>(
      `${apiBase}/network/`,
    )
  }

  function getReachability(
    originId: number,
    destinationId?: number,
  ) {
    const query: Record<string, number> = {
      origin_id: originId,
    }

    if (destinationId !== undefined) {
      query.destination_id = destinationId
    }

    return $fetch<
      CoverageCheckResult | CoverageReachabilityResult
    >(
      `${apiBase}/reachability/`,
      {
        query,
      },
    )
  }


  return {
    getNodes,
    createNode,

    getTechnicians,
    createTechnician,

    getConnections,
    createConnection,
    getReachability,

    getNetwork,
  }
}
