<script setup lang="ts">
import { computed } from 'vue'
import type { CSSProperties } from 'vue'
import { BaseEdge, Position, getSmoothStepPath } from '@vue-flow/core'
const props = defineProps<{
  id: string
  sourceX: number
  sourceY: number
  targetX: number
  targetY: number
  sourcePosition: Position
  targetPosition: Position
  data: { lane: number }
  label?: unknown
  style?: CSSProperties
  markerStart?: string
  markerEnd?: string
  labelStyle?: CSSProperties
  labelBgStyle?: CSSProperties
  labelBgPadding?: [number, number]
  labelBgBorderRadius?: number
}>()
const geometry = computed(() => {
  const {
    sourceX: sx,
    sourceY: sy,
    targetX: tx,
    targetY: ty,
    sourcePosition,
    targetPosition,
  } = props
  const lane = props.data.lane
  if (!lane)
    return getSmoothStepPath({
      sourceX: sx,
      sourceY: sy,
      targetX: tx,
      targetY: ty,
      sourcePosition,
      targetPosition,
      borderRadius: 12,
    })
  // Separate reciprocal / parallel records so each duration stays readable.
  const bend = Math.max(35, Math.abs(tx - sx) * 0.5)
  const c1x = sx + (sourcePosition === Position.Left ? -bend : bend)
  const c2x = tx + (targetPosition === Position.Left ? -bend : bend)
  return [
    `M ${sx},${sy} C ${c1x},${sy + lane} ${c2x},${ty + lane} ${tx},${ty}`,
    (sx + 3 * c1x + 3 * c2x + tx) / 8,
    (sy + ty) / 2 + lane * 0.75,
  ]
})
</script>
<template>
  <BaseEdge
    :id="id"
    :path="String(geometry[0])"
    :label="label"
    :label-x="Number(geometry[1])"
    :label-y="Number(geometry[2])"
    :style="style"
    :marker-start="markerStart"
    :marker-end="markerEnd"
    :label-style="labelStyle"
    :label-bg-style="labelBgStyle"
    :label-bg-padding="labelBgPadding"
    :label-bg-border-radius="labelBgBorderRadius"
  />
</template>
