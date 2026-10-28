<script setup lang="ts">
import { MapPin } from 'lucide-vue-next'
import { Handle, Position } from '@vue-flow/core'
defineProps<{ data: { code: string; name: string; state?: string } }>()
const states: Record<string, string> = {
  visited: 'Visitado',
  path: 'Ruta',
  origin: 'Origen',
  destination: 'Destino',
}
</script>
<template>
  <div
    class="graph-node"
    :class="`graph-node--${data.state ?? 'default'}`"
    :title="`${data.name} · ${data.code}${data.state && states[data.state] ? ' · ' + states[data.state] : ''}`"
  >
    <Handle
      id="in-left"
      type="target"
      :position="Position.Left"
      :connectable="false"
      class="graph-handle"
    />
    <Handle
      id="out-left"
      type="source"
      :position="Position.Left"
      :connectable="false"
      class="graph-handle"
    />
    <span class="node-icon"><MapPin :size="18" aria-hidden="true" /></span>
    <div class="node-copy">
      <span class="node-type"
        >ZONA<template v-if="data.state && states[data.state]">
          · {{ states[data.state] }}</template
        ></span
      >
      <strong>{{ data.name }}</strong
      ><small>{{ data.code }}</small>
    </div>
    <Handle
      id="in-right"
      type="target"
      :position="Position.Right"
      :connectable="false"
      class="graph-handle"
    />
    <Handle
      id="out-right"
      type="source"
      :position="Position.Right"
      :connectable="false"
      class="graph-handle"
    />
  </div>
</template>
