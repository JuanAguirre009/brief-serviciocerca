<script setup lang="ts">
import { computed } from 'vue'
import {
  Activity,
  GitBranch,
  Info,
  LoaderCircle,
  Network,
  Route,
} from 'lucide-vue-next'

import CoverageGraph from '~/components/coverage/CoverageGraph.vue'
import RouteComparison from '~/components/routes/RouteComparison.vue'

import type {
  CoverageCheckResult,
  CoverageNetwork,
  RouteSegment,
  ShortestRouteResult,
} from '~/types/coverage'

const props = defineProps<{
  network: CoverageNetwork
  result: ShortestRouteResult
  bfs: CoverageCheckResult | null
  bfsMinutes: number | null
  comparison: {
    difference: number
    savingPercent: number | null
  } | null
  comparisonLoading: boolean
  comparisonError: string
  activeRoute: 'dijkstra' | 'bfs'
  pathNodeIds: number[]
  visitedNodeIds: number[]
  highlightedSegments?: RouteSegment[]
  resultKey: number
}>()

const emit = defineEmits<{
  (event: 'compare'): void
  (
    event: 'switch-route',
    mode: 'dijkstra' | 'bfs'
  ): void
}>()

const currentRouteLabel = computed(() =>
  props.activeRoute === 'bfs'
    ? 'Recorrido BFS'
    : 'Recorrido recomendado'
)

const explorationNodes = computed(
  () => props.result.traversal_order
)
</script>

<template>
  <div class="deep-analysis">

    <div class="deep-analysis__intro">
      <div>
        <span class="eyebrow">Información complementaria</span>
        <h3>Detalles de la operación</h3>
        <p>
          Revisa cómo se obtuvo el recorrido recomendado
          y analiza la conectividad de la red.
        </p>
      </div>
    </div>

    <section class="deep-analysis__network">
      <div class="deep-analysis__heading">
        <div>
          <h4>
            <Network :size="18" aria-hidden="true" />
            Visualización de la red
          </h4>
          <p>
            {{ network.nodes.length }} nodos ·
            {{ network.connections.length }} conexiones
          </p>
        </div>

        <span class="badge">
          {{ currentRouteLabel }}
        </span>
      </div>

      <p v-if="!result.reachable" class="hint">
        No existe una ruta disponible para esta consulta.
        Se muestra la red para facilitar su análisis.
      </p>

      <div class="deep-analysis__graph">
        <ClientOnly>
          <CoverageGraph
            :network="network"
            :path-node-ids="pathNodeIds"
            :visited-node-ids="visitedNodeIds"
            :path-segments="highlightedSegments"
            :origin-id="result.origin.id"
            :destination-id="result.destination.id"
            :result-key="resultKey"
          />

          <template #fallback>
            <div class="deep-analysis__fallback">
              <LoaderCircle
                :size="22"
                class="spinning"
              />
              Preparando visualización…
            </div>
          </template>
        </ClientOnly>
      </div>

      <p class="deep-analysis__hint">
        El grafo es una representación técnica
        complementaria. El recorrido recomendado
        se encuentra en el resultado rápido superior.
      </p>
    </section>

    <section class="deep-analysis__bfs">
      <div class="deep-analysis__heading">
        <div>
          <h4>
            <GitBranch :size="18" aria-hidden="true" />
            Análisis de cobertura
          </h4>
          <p>
            Compara el recorrido recomendado con
            la consulta de cobertura mediante BFS.
          </p>
        </div>

        <button
          class="button"
          type="button"
          :disabled="comparisonLoading"
          @click="emit('compare')"
        >
          <LoaderCircle
            v-if="comparisonLoading"
            :size="16"
            class="spinning"
          />
          <GitBranch v-else :size="16" />

          {{
            comparisonLoading
              ? 'Consultando BFS…'
              : bfs
                ? 'Actualizar análisis BFS'
                : 'Analizar cobertura con BFS'
          }}
        </button>
      </div>

      <p
        v-if="comparisonError"
        class="alert error"
        role="alert"
      >
        {{ comparisonError }}
      </p>

      <template v-if="bfs">
        <div
          class="deep-analysis__switch"
          role="group"
          aria-label="Recorrido visualizado"
        >
          <button
            type="button"
            :aria-pressed="activeRoute === 'dijkstra'"
            @click="emit('switch-route', 'dijkstra')"
          >
            <Route :size="15" />
            Ver recorrido recomendado
          </button>

          <button
            type="button"
            :aria-pressed="activeRoute === 'bfs'"
            @click="emit('switch-route', 'bfs')"
          >
            <GitBranch :size="15" />
            Ver recorrido BFS
          </button>
        </div>

        <RouteComparison
          :dijkstra="result"
          :bfs="bfs"
          :bfs-minutes="bfsMinutes"
          :comparison="comparison"
        />
      </template>

      <p v-else class="deep-analysis__hint">
        La comparación es opcional. Utiliza el botón
        para consultar el algoritmo BFS sobre
        el mismo origen y destino.
      </p>
    </section>

    <section
      class="deep-analysis__exploration"
      aria-labelledby="exploration-title"
    >
      <div class="deep-analysis__heading">
        <div>
          <h4 id="exploration-title">
            <Activity :size="18" aria-hidden="true" />
            Cómo se encontró el recorrido
          </h4>
          <p>
            Exploración realizada por Dijkstra.
          </p>
        </div>

        <span class="badge">
          {{ result.visited_count }}
          nodos procesados
        </span>
      </div>

      <p class="deep-analysis__explanation">
        <Info :size="16" aria-hidden="true" />
        Estos nodos fueron confirmados por Dijkstra
        durante la búsqueda. Su orden no necesariamente
        corresponde al recorrido final recomendado.
      </p>

      <ol
        v-if="explorationNodes.length"
        class="deep-analysis__nodes"
        aria-label="Orden de procesamiento de Dijkstra"
      >
        <li
          v-for="(node, index) in explorationNodes"
          :key="`${index}-${node.id}`"
        >
          <span class="deep-analysis__number">
            {{ index + 1 }}
          </span>

          <div>
            <strong>{{ node.name }}</strong>
            <small>{{ node.code }}</small>
          </div>
        </li>
      </ol>

      <p v-else class="hint">
        No se registraron nodos procesados
        para esta consulta.
      </p>
    </section>

  </div>
</template>

<style scoped>
.deep-analysis {
  display: grid;
  gap: 20px;
  min-width: 0;
}

.deep-analysis__intro h3 {
  margin: 6px 0 8px;
  font-size: 1.1rem;
}

.deep-analysis__intro p,
.deep-analysis__heading p,
.deep-analysis__hint {
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 0.85rem;
  line-height: 1.6;
}

.deep-analysis__network,
.deep-analysis__bfs,
.deep-analysis__exploration {
  min-width: 0;
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
}

.deep-analysis__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 14px;
  margin-bottom: 16px;
}

.deep-analysis__heading h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
  font-size: 0.96rem;
}

.deep-analysis__heading h4 svg {
  color: var(--primary);
}

.deep-analysis__graph {
  height: 430px;
  min-width: 0;
  overflow: hidden;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
}

.deep-analysis__fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 100%;
  background: var(--bg-surface-soft);
  color: var(--text-secondary);
}

.deep-analysis__switch {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 14px 0 18px;
}

.deep-analysis__switch button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: 1px solid var(--border);
  border-radius: 7px;
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 0.83rem;
  font-weight: 600;
  cursor: pointer;
}

.deep-analysis__switch button[aria-pressed='true'] {
  border-color: var(--primary);
  background: var(--primary-soft);
  color: var(--primary-hover);
}

.deep-analysis__explanation {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 0.83rem;
  line-height: 1.6;
}

.deep-analysis__explanation svg {
  flex-shrink: 0;
  margin-top: 2px;
}

.deep-analysis__nodes {
  display: grid;
  gap: 10px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.deep-analysis__nodes li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  background: var(--bg-surface-soft);
}

.deep-analysis__number {
  display: grid;
  place-items: center;
  flex: 0 0 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary-hover);
  font-size: 0.8rem;
  font-weight: 700;
}

.deep-analysis__nodes li > div {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.deep-analysis__nodes strong {
  font-size: 0.84rem;
  overflow-wrap: anywhere;
}

.deep-analysis__nodes small {
  color: var(--text-muted);
  font-size: 0.76rem;
  overflow-wrap: anywhere;
}

@media (max-width: 600px) {
  .deep-analysis__network,
  .deep-analysis__bfs,
  .deep-analysis__exploration {
    padding: 14px;
  }

  .deep-analysis__graph {
    height: 370px;
  }

  .deep-analysis__heading {
    flex-direction: column;
  }
}
</style>
