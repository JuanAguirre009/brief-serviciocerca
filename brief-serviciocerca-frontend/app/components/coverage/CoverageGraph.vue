<script setup lang="ts">
import {
  computed,
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
  useId,
  watch,
} from 'vue'
import { MarkerType, VueFlow, useVueFlow } from '@vue-flow/core'
import type { Edge, Node } from '@vue-flow/core'
import {
  Background,
  Controls,
  MiniMap,
  PanelPosition,
} from '@vue-flow/additional-components'
import {
  LoaderCircle,
  Maximize,
  Minus,
  Network,
  Plus,
  RefreshCw,
} from 'lucide-vue-next'
import BaseNode from './BaseNode.vue'
import ZoneNode from './ZoneNode.vue'
import OperationalEdge from './OperationalEdge.vue'
import { layoutNetwork } from '~/utils/layoutNetwork'
import type { CoverageNetwork } from '~/types/coverage'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'

const props = defineProps<{
  network: CoverageNetwork
  loading?: boolean
  error?: string
  visitedNodeIds?: number[]
  pathNodeIds?: number[]
  originId?: number | null
  destinationId?: number | null
  resultKey?: number
}>()
const id = useId()
const shell = ref<HTMLElement>()
const ready = ref(false)
const { fitView, zoomIn, zoomOut, onNodesInitialized, onPaneReady } =
  useVueFlow(id)
const positions = computed(() => layoutNetwork(props.network))
const visited = computed(() => new Set(props.visitedNodeIds ?? []))
const path = computed(() => new Set(props.pathNodeIds ?? []))
function state(nodeId: number) {
  if (nodeId === props.originId) return 'origin'
  if (nodeId === props.destinationId) return 'destination'
  if (path.value.has(nodeId)) return 'path'
  return visited.value.has(nodeId) ? 'visited' : 'default'
}
const flowNodes = computed<Node[]>(() =>
  props.network.nodes.map((node) => ({
    id: String(node.id),
    type: node.type === 'BASE' ? 'base' : 'zone',
    position: positions.value.get(node.id) ?? { x: 0, y: 0 },
    data: { code: node.code, name: node.name, state: state(node.id) },
    draggable: false,
    connectable: false,
  })),
)
const pathPairs = computed(() => {
  const ids = props.pathNodeIds ?? []
  return new Set(ids.slice(1).map((nodeId, index) => `${ids[index]}-${nodeId}`))
})
const edgeLanes = computed(() => {
  const groups = new Map<string, number[]>()
  for (const connection of props.network.connections) {
    const key = [connection.origin.id, connection.destination.id]
      .sort((a, b) => a - b)
      .join('-')
    const group = groups.get(key) ?? []
    group.push(connection.id)
    groups.set(key, group)
  }
  const lanes = new Map<number, number>()
  for (const group of groups.values())
    group
      .sort((a, b) => a - b)
      .forEach((edgeId, index) =>
        lanes.set(edgeId, (index - (group.length - 1) / 2) * 70),
      )
  return lanes
})
const flowEdges = computed<Edge[]>(() =>
  props.network.connections.map((connection) => {
    const from = connection.origin.id
    const to = connection.destination.id
    const isPath =
      pathPairs.value.has(`${from}-${to}`) ||
      (connection.is_bidirectional && pathPairs.value.has(`${to}-${from}`))
    const backwards =
      (positions.value.get(from)?.x ?? 0) >= (positions.value.get(to)?.x ?? 0)
    const stroke = isPath ? '#356ae6' : '#9aacc1'
    return {
      id: `connection-${connection.id}`,
      source: String(from),
      target: String(to),
      sourceHandle: backwards ? 'out-left' : 'out-right',
      targetHandle: backwards ? 'in-right' : 'in-left',
      type: 'operational',
      animated: isPath,
      data: { lane: edgeLanes.value.get(connection.id) ?? 0 },
      markerEnd: { type: MarkerType.ArrowClosed, color: stroke },
      markerStart: connection.is_bidirectional
        ? {
            type: MarkerType.ArrowClosed,
            color: stroke,
            orient: 'auto-start-reverse',
          }
        : undefined,
      label: `${connection.estimated_minutes} min`,
      style: { stroke, strokeWidth: isPath ? 2.8 : 1.7 },
      labelStyle: {
        fill: isPath ? '#2859ca' : '#52647b',
        fontSize: 11,
        fontWeight: 600,
      },
      labelBgStyle: { fill: '#ffffff', fillOpacity: 0.97 },
      labelBgPadding: [5, 7],
      labelBgBorderRadius: 8,
    }
  }),
)
let frame = 0
function scheduleFit() {
  if (!import.meta.client) return
  cancelAnimationFrame(frame)
  void nextTick(() => {
    frame = requestAnimationFrame(() => {
      if (!ready.value || !props.network.nodes.length) return
      void fitView({
        padding: 0.12,
        minZoom: 0.05,
        maxZoom: 1.2,
        duration: window.matchMedia('(prefers-reduced-motion: reduce)').matches
          ? 0
          : 240,
      })
    })
  })
}
onPaneReady(() => {
  ready.value = true
  scheduleFit()
})
onNodesInitialized(scheduleFit)
watch(
  [
    () => props.network,
    () => props.visitedNodeIds,
    () => props.pathNodeIds,
    () => props.originId,
    () => props.destinationId,
    () => props.resultKey,
  ],
  scheduleFit,
  { deep: true, flush: 'post' },
)
let observer: ResizeObserver | undefined
onMounted(() => {
  observer = new ResizeObserver(scheduleFit)
  if (shell.value) observer.observe(shell.value)
})
onBeforeUnmount(() => {
  observer?.disconnect()
  cancelAnimationFrame(frame)
})
</script>
<template>
  <div
    ref="shell"
    class="graph-shell"
    :aria-busy="loading"
    aria-label="Red operacional de bases y zonas"
  >
    <div
      v-if="!network.nodes.length"
      class="empty-state graph-empty"
      role="status"
    >
      <template v-if="loading"
        ><LoaderCircle :size="26" class="spinning" /><strong
          >Cargando red operacional</strong
        >
        <div class="skeleton" style="width: 180px"
      /></template>
      <template v-else-if="error"
        ><Network :size="28" /><strong>No fue posible cargar la red</strong>
        <p>Vuelve a intentarlo con Actualizar red.</p></template
      >
      <template v-else
        ><Network :size="30" /><strong
          >No hay una red configurada todavía.</strong
        >
        <p>Agrega bases y zonas desde Configuración de red.</p>
        <NuxtLink to="/network" class="button"
          >Configurar red</NuxtLink
        ></template
      >
    </div>
    <template v-else>
      <VueFlow
        :id="id"
        :nodes="flowNodes"
        :edges="flowEdges"
        :min-zoom="0.05"
        :max-zoom="2"
        :nodes-draggable="false"
        :nodes-connectable="false"
        class="coverage-flow"
      >
        <Background pattern-color="#d7e0ec" :gap="20" :size="1" />
        <MiniMap
          :node-color="(node) => (node.type === 'base' ? '#356ae6' : '#a3b3c7')"
          :width="132"
          :height="88"
          :pannable="true"
          :zoomable="true"
          :position="PanelPosition.BottomRight"
        />
        <Controls
          :position="PanelPosition.BottomLeft"
          :show-interactive="false"
        >
          <template #control-zoom-in
            ><button
              type="button"
              class="vue-flow__controls-button vue-flow__controls-zoomin"
              aria-label="Ampliar red"
              title="Ampliar red"
              @click="zoomIn()"
            >
              <Plus :size="16" /></button
          ></template>
          <template #control-zoom-out
            ><button
              type="button"
              class="vue-flow__controls-button vue-flow__controls-zoomout"
              aria-label="Reducir red"
              title="Reducir red"
              @click="zoomOut()"
            >
              <Minus :size="16" /></button
          ></template>
          <template #control-fit-view
            ><button
              type="button"
              class="vue-flow__controls-button vue-flow__controls-fitview"
              aria-label="Ajustar red a la vista"
              title="Ajustar red a la vista"
              @click="scheduleFit"
            >
              <Maximize :size="16" /></button
          ></template>
        </Controls>
        <template #node-base="nodeProps"
          ><BaseNode v-bind="nodeProps"
        /></template>
        <template #node-zone="nodeProps"
          ><ZoneNode v-bind="nodeProps"
        /></template>
        <template #edge-operational="edgeProps"
          ><OperationalEdge v-bind="edgeProps"
        /></template>
      </VueFlow>
      <span v-if="loading" class="graph-loading" role="status"
        ><RefreshCw :size="13" class="spinning" /> Actualizando red</span
      >
    </template>
  </div>
</template>
<style scoped>
.graph-shell {
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 350px;
  position: relative;
  overflow: hidden;
  background: var(--bg-surface-soft);
}
.coverage-flow {
  width: 100%;
  height: 100%;
}
.graph-empty {
  height: 100%;
}
.graph-loading {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 6px;
  align-items: center;
  padding: 7px 10px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.78rem;
  color: var(--text-secondary);
}
:deep(.vue-flow__controls) {
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow);
}
:deep(.vue-flow__controls-button) {
  width: 30px;
  height: 30px;
  padding: 7px;
  border: 0;
  border-bottom: 1px solid var(--border-soft);
  color: var(--text-secondary);
  background: var(--bg-surface);
}
:deep(.vue-flow__controls-button:hover) {
  background: var(--primary-soft);
}
:deep(.vue-flow__minimap) {
  overflow: hidden;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fffffff0;
  box-shadow: none;
}
</style>
