<script setup lang="ts">
import { ref } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { useNetwork } from '~/composables/useNetwork'
import NodeForm from '~/components/coverage/NodeForm.vue'
import TechnicianForm from '~/components/coverage/TechnicianForm.vue'
import ConnectionForm from '~/components/coverage/ConnectionForm.vue'
import NetworkList from '~/components/coverage/NetworkList.vue'
import CoverageGraph from '~/components/coverage/CoverageGraph.vue'
const { network, loading, errorMessage, refresh } = useNetwork()
const active = ref('nodes')
const sections = [
  { id: 'nodes', label: 'Nodos' },
  { id: 'technicians', label: 'Técnicos' },
  { id: 'connections', label: 'Conexiones' },
]
</script>
<template>
  <div class="page">
    <header class="page-heading">
      <div>
        <span class="eyebrow">CONFIGURACIÓN</span>
        <h2>Red de cobertura</h2>
        <p>Administra bases, zonas, técnicos y conexiones operativas.</p>
      </div>
      <button class="button" :disabled="loading" @click="refresh">
        <RefreshCw :size="16" :class="{ spinning: loading }" />Actualizar red
      </button>
    </header>
    <p v-if="errorMessage" class="alert error" role="alert">
      {{ errorMessage }}
    </p>
    <div class="network-workspace">
      <section class="card configuration">
        <h3>Registrar elementos</h3>
        <p class="configuration-description">
          Selecciona el recurso que deseas agregar.
        </p>
        <div class="segmented" role="group" aria-label="Tipo de recurso">
          <button
            v-for="section in sections"
            :key="section.id"
            :aria-pressed="active === section.id"
            :class="{ selected: active === section.id }"
            :aria-controls="`form-${section.id}`"
            @click="active = section.id"
          >
            {{ section.label }}
          </button>
        </div>
        <div id="form-nodes" v-show="active === 'nodes'">
          <NodeForm @created="refresh" />
        </div>
        <div id="form-technicians" v-show="active === 'technicians'">
          <TechnicianForm :nodes="network.nodes" @created="refresh" />
        </div>
        <div id="form-connections" v-show="active === 'connections'">
          <ConnectionForm :nodes="network.nodes" @created="refresh" />
        </div>
      </section>
      <section class="card network-map">
        <header>
          <h3>Visualización de la red</h3>
          <span class="badge"
            >{{ network.nodes.length }} nodos ·
            {{ network.connections.length }} conexiones</span
          >
        </header>
        <div class="map-canvas">
          <ClientOnly
            ><CoverageGraph
              :network="network"
              :loading="loading"
              :error="errorMessage"
            /><template #fallback
              ><div class="empty-state">Preparando red…</div></template
            ></ClientOnly
          >
        </div>
      </section>
    </div>
    <p v-if="loading" class="hint" role="status">
      Sincronizando los recursos de la red…
    </p>
    <NetworkList :network="network" />
  </div>
</template>
<style scoped>
.network-workspace {
  display: grid;
  grid-template-columns: 350px minmax(0, 1fr);
  align-items: start;
  gap: 18px;
}
.configuration-description {
  font-size: 0.83rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 7px 0 18px;
}
.segmented {
  display: flex;
  gap: 3px;
  padding: 4px;
  background: var(--bg-sidebar);
  border-radius: 8px;
  margin-bottom: 22px;
}
.segmented button {
  flex: 1;
  min-width: 0;
  padding: 9px 5px;
  border: 0;
  border-radius: 5px;
  color: var(--text-secondary);
  background: transparent;
  font-size: 0.8rem;
  font-weight: 600;
}
.segmented button.selected {
  color: var(--primary-hover);
  background: var(--bg-surface);
  box-shadow: var(--shadow);
}
.configuration :deep(.card) {
  padding: 0;
  border: 0;
  box-shadow: none;
}
.configuration :deep(h2) {
  font-size: 1rem;
}
.network-map {
  padding: 0;
  overflow: hidden;
}
.network-map header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 18px;
  border-bottom: 1px solid var(--border);
}
.map-canvas {
  height: 520px;
}
@media (max-width: 1050px) {
  .network-workspace {
    grid-template-columns: 1fr;
  }
  .configuration {
    max-width: 100%;
  }
  .map-canvas {
    height: 430px;
  }
}
</style>
