<script setup lang="ts">
import type { CoverageNetwork, CoverageNode, Connection } from '~/types/coverage'


interface Position {
  x: number
  y: number
}

interface ArrowMarker {
  x: number
  y: number
  angle: number
}


const props = defineProps<{
  network: CoverageNetwork
}>()


const WIDTH = 500
const BASE_X = 80
const ZONE_X = 420
const NODE_RADIUS = 28
const VERTICAL_GAP = 90
const TOP_PADDING = 60


function getNodePosition(node: CoverageNode): Position {
  const isBase = node.type === 'BASE'
  const sameTypeNodes = props.network.nodes.filter(
    n => n.type === node.type,
  )
  const index = sameTypeNodes.findIndex(n => n.id === node.id)
  const count = sameTypeNodes.length
  const totalHeight = (count - 1) * VERTICAL_GAP
  const startY = (HEIGHT.value - totalHeight) / 2

  return {
    x: isBase ? BASE_X : ZONE_X,
    y: startY + index * VERTICAL_GAP,
  }
}


const HEIGHT = computed(() => {
  const maxCount = Math.max(
    props.network.nodes.filter(n => n.type === 'BASE').length,
    props.network.nodes.filter(n => n.type === 'ZONE').length,
    1,
  )
  return Math.max(300, TOP_PADDING * 2 + (maxCount - 1) * VERTICAL_GAP)
})


const nodePositions = computed(() => {
  const positions = new Map<number, Position>()
  props.network.nodes.forEach((node) => {
    positions.set(node.id, getNodePosition(node))
  })
  return positions
})


function getConnectionPath(connection: Connection): string {
  const origin = nodePositions.value.get(connection.origin.id)
  const destination = nodePositions.value.get(connection.destination.id)

  if (!origin || !destination) {
    return ''
  }

  return `M ${origin.x} ${origin.y} L ${destination.x} ${destination.y}`
}


function buildArrow(
  from: Position,
  to: Position,
): ArrowMarker | null {
  const dx = to.x - from.x
  const dy = to.y - from.y
  const distance = Math.sqrt(dx * dx + dy * dy)

  if (distance === 0) {
    return null
  }

  const ratio = (distance - NODE_RADIUS - 6) / distance
  const x = from.x + dx * ratio
  const y = from.y + dy * ratio
  const angle = Math.atan2(dy, dx) * (180 / Math.PI)

  return { x, y, angle }
}


function getArrowMarkers(connection: Connection): ArrowMarker[] {
  const origin = nodePositions.value.get(connection.origin.id)
  const destination = nodePositions.value.get(connection.destination.id)

  if (!origin || !destination) {
    return []
  }

  const markers: ArrowMarker[] = []

  const forward = buildArrow(origin, destination)
  if (forward) {
    markers.push(forward)
  }

  if (connection.is_bidirectional) {
    const backward = buildArrow(destination, origin)
    if (backward) {
      markers.push(backward)
    }
  }

  return markers
}


const hasNodes = computed(() => props.network.nodes.length > 0)
</script>


<template>
  <section class="graph-card">
    <div
      v-if="!hasNodes"
      class="empty-graph"
    >
      <p class="empty">
        No hay nodos registrados para visualizar.
      </p>

      <p class="hint">
        Registra al menos una base y una zona para ver el grafo.
      </p>
    </div>

    <svg
      v-else
      class="network-graph"
      :viewBox="`0 0 ${WIDTH} ${HEIGHT}`"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- Connections -->
      <g class="connections">
        <path
          v-for="connection in network.connections"
          :key="`connection-${connection.id}`"
          :d="getConnectionPath(connection)"
          class="connection-line"
          :class="{ bidirectional: connection.is_bidirectional }"
        />

        <g
          v-for="connection in network.connections"
          :key="`arrow-${connection.id}`"
          class="connection-arrow"
        >
          <polygon
            v-for="(marker, index) in getArrowMarkers(connection)"
            :key="index"
            points="0,-5 10,0 0,5"
            :transform="`translate(${marker.x}, ${marker.y}) rotate(${marker.angle})`"
            :class="{ bidirectional: connection.is_bidirectional }"
          />
        </g>
      </g>

      <!-- Nodes -->
      <g
        v-for="node in network.nodes"
        :key="`node-${node.id}`"
        class="node"
        :transform="`translate(${nodePositions.get(node.id)?.x}, ${nodePositions.get(node.id)?.y})`"
      >
        <circle
          :r="NODE_RADIUS"
          :class="['node-circle', node.type.toLowerCase()]"
        />

        <text
          class="node-code"
          dy="-2"
        >
          {{ node.code }}
        </text>

        <text
          class="node-type"
          dy="14"
        >
          {{ node.type === 'BASE' ? 'Base' : 'Zona' }}
        </text>
      </g>

      <!-- Legend -->
      <g
        class="legend"
        :transform="`translate(20, 20)`"
      >
        <circle
          r="8"
          class="node-circle base"
        />

        <text
          x="16"
          y="4"
          class="legend-text"
        >
          Base
        </text>

        <circle
          r="8"
          cx="70"
          class="node-circle zone"
        />

        <text
          x="86"
          y="4"
          class="legend-text"
        >
          Zona
        </text>
      </g>
    </svg>
  </section>
</template>


<style scoped>
.graph-card {
  width: 100%;
}

.empty-graph {
  text-align: center;
  padding: 48px 20px;
}

.network-graph {
  width: 100%;
  height: auto;
  max-height: 600px;
  background: #f9fafb;
  border-radius: 8px;
}

.connection-line {
  stroke: #6b7280;
  stroke-width: 2;
  fill: none;
}

.connection-line.bidirectional {
  stroke: #3b82f6;
}

.connection-arrow polygon {
  fill: #6b7280;
}

.connection-arrow polygon.bidirectional {
  fill: #3b82f6;
}

.node {
  cursor: pointer;
}

.node-circle {
  stroke: white;
  stroke-width: 3;
}

.node-circle.base {
  fill: #111827;
}

.node-circle.zone {
  fill: #3b82f6;
}

.node-code {
  fill: white;
  font-size: 10px;
  font-weight: 700;
  text-anchor: middle;
}

.node-type {
  fill: rgba(255, 255, 255, 0.8);
  font-size: 8px;
  text-anchor: middle;
}

.legend-text {
  font-size: 12px;
  fill: #4b5563;
}
</style>
