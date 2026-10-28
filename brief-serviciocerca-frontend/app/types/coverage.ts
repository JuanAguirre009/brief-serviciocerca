export type NodeType = 'BASE' | 'ZONE'

export interface CoverageNode {
  id: number
  code: string
  name: string
  type: NodeType
  created_at: string
  updated_at: string
}

export interface Technician {
  id: number
  code: string
  name: string
  base: CoverageNode
  is_available: boolean
  created_at: string
  updated_at: string
}

export interface Connection {
  id: number
  origin: CoverageNode
  destination: CoverageNode
  estimated_minutes: number
  is_bidirectional: boolean
  created_at: string
  updated_at: string
}

export interface CoverageNetwork {
  nodes: CoverageNode[]
  technicians: Technician[]
  connections: Connection[]
}

export interface NodeCreatePayload {
  code: string
  name: string
  type: NodeType
}

export interface TechnicianCreatePayload {
  code: string
  name: string
  base_id: number | null
  is_available: boolean
}

export interface ConnectionCreatePayload {
  origin_id: number | null
  destination_id: number | null
  estimated_minutes: number
  is_bidirectional: boolean
}

export interface ReachabilityNode {
  id: number
  code: string
  name: string
  type: NodeType
}

export interface CoverageCheckResult {
  mode: 'check'
  covered: boolean
  origin: ReachabilityNode
  destination: ReachabilityNode
  path: ReachabilityNode[]
  traversal_order: ReachabilityNode[]
  visited_count: number
  message: string
}

export interface CoverageReachabilityResult {
  mode: 'reachability'
  origin: ReachabilityNode
  reachable_count: number
  reachable_nodes: ReachabilityNode[]
  traversal_order: ReachabilityNode[]
  visited_count: number
  message: string
}

export type CoverageQueryResult =
  | CoverageCheckResult
  | CoverageReachabilityResult