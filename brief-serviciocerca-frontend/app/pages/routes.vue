<script setup lang="ts">
import {
  CheckCircle2,
  CircleOff,
  Clock3,
  GitBranch,
  Info,
  LoaderCircle,
  Network,
  RefreshCw,
  Route,
  Search,
} from 'lucide-vue-next'
import CoverageGraph from '~/components/coverage/CoverageGraph.vue'
import RouteComparison from '~/components/routes/RouteComparison.vue'
import RoutePath from '~/components/routes/RoutePath.vue'
import { useRoutePlanning } from '~/composables/useRoutePlanning'

useHead({ title: 'Rutas óptimas · ServicioCerca' })
const {
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
  bfsMinutes,
  comparison,
  pathNodeIds,
  visitedNodeIds,
  highlightedSegments,
  calculateRoute,
  compareWithBfs,
  clearResults,
  refreshNetwork,
} = useRoutePlanning()
</script>

<template>
  <div class="page routes-page">
    <header class="page-heading">
      <div>
        <span class="eyebrow">PLANIFICACIÓN DEL SERVICIO</span>
        <h2>Rutas óptimas</h2>
        <p>
          Encuentra el recorrido con menor tiempo estimado utilizando Dijkstra
        </p>
      </div>
      <button
        class="button"
        type="button"
        :disabled="networkLoading"
        @click="refreshNetwork"
      >
        <RefreshCw :size="16" :class="{ spinning: networkLoading }" />Actualizar
        red
      </button>
    </header>
    <p v-if="networkError" class="alert error" role="alert">
      {{ networkError }} Actualiza la red para volver a consultar.
    </p>

    <section class="routes-workspace">
      <aside class="route-query" aria-label="Consulta de ruta óptima">
        <div class="panel-heading">
          <span class="panel-icon"
            ><GitBranch :size="20" aria-hidden="true"
          /></span>
          <div>
            <span class="eyebrow">NUEVA CONSULTA</span>
            <h3>Planificar recorrido</h3>
          </div>
        </div>
        <form class="route-form" @submit.prevent="calculateRoute">
          <div class="form-field">
            <label for="route-origin">Base de origen</label
            ><select
              id="route-origin"
              v-model="originId"
              :disabled="networkLoading || !bases.length"
            >
              <option v-if="!bases.length" :value="null">
                {{
                  networkLoading
                    ? 'Cargando bases…'
                    : 'No hay bases registradas'
                }}
              </option>
              <option v-for="base in bases" :key="base.id" :value="base.id">
                {{ base.name }} · {{ base.code }}
              </option>
            </select>
          </div>
          <div class="form-field">
            <label for="route-destination">Zona de destino</label
            ><select
              id="route-destination"
              v-model="destinationId"
              :disabled="networkLoading || !zones.length"
            >
              <option v-if="!zones.length" :value="null">
                {{
                  networkLoading
                    ? 'Cargando zonas…'
                    : 'No hay zonas registradas'
                }}
              </option>
              <option v-for="zone in zones" :key="zone.id" :value="zone.id">
                {{ zone.name }} · {{ zone.code }}
              </option>
            </select>
          </div>
          <button
            class="button button--primary calculate-button"
            type="submit"
            :disabled="!canQuery"
          >
            <LoaderCircle
              v-if="queryLoading"
              :size="16"
              class="spinning"
            /><Search v-else :size="16" />{{
              queryLoading ? 'Calculando ruta…' : 'Calcular ruta óptima'
            }}
          </button>
        </form>
        <p
          v-if="
            !networkLoading && !networkError && (!bases.length || !zones.length)
          "
          class="hint"
        >
          {{
            !bases.length
              ? 'Agrega una base de origen para planificar un recorrido.'
              : 'Agrega una zona de destino para calcular una ruta.'
          }}
          <NuxtLink to="/network">Configurar red</NuxtLink>
        </p>
        <p v-if="queryError" class="error" role="alert">{{ queryError }}</p>

        <div
          class="query-feedback"
          :aria-busy="queryLoading"
          aria-live="polite"
          aria-atomic="true"
        >
          <div v-if="queryLoading" class="query-loading" role="status">
            <div class="skeleton" />
            <p>Consultando el tiempo mínimo del recorrido…</p>
          </div>
          <template v-else-if="result">
            <div v-if="result.reachable" class="route-summary">
              <div class="status-line success">
                <CheckCircle2 :size="18" /><strong
                  >Ruta óptima encontrada</strong
                >
              </div>
              <div class="total-time">
                <Clock3 :size="21" aria-hidden="true" /><strong
                  data-testid="total-minutes"
                  >{{ result.total_minutes }}</strong
                ><span>minutos</span>
              </div>
              <dl class="endpoints">
                <div>
                  <dt>Desde</dt>
                  <dd>{{ result.origin.name }}</dd>
                </div>
                <div>
                  <dt>Hasta</dt>
                  <dd>{{ result.destination.name }}</dd>
                </div>
              </dl>
              <div class="route-metrics">
                <div>
                  <strong>{{ result.segments.length }}</strong
                  ><span>{{
                    result.segments.length === 1 ? 'segmento' : 'segmentos'
                  }}</span>
                </div>
                <div>
                  <strong>{{ result.visited_count }}</strong
                  ><span>nodos procesados</span>
                </div>
              </div>
            </div>
            <div v-else class="no-route">
              <div class="status-line error">
                <CircleOff :size="18" /><strong
                  >No hay una ruta disponible</strong
                >
              </div>
              <p>
                No hay una conexión válida entre {{ result.origin.name }} y
                {{ result.destination.name }} en el sentido solicitado.
              </p>
            </div>
            <p class="backend-message">{{ result.message }}</p>
          </template>
          <div v-else-if="!queryError" class="query-idle">
            <Route :size="19" aria-hidden="true" />
            <p>
              Selecciona una base y una zona. La ruta y sus tiempos se mostrarán
              sobre la red operacional.
            </p>
          </div>
        </div>
        <div v-if="result" class="comparison-actions">
          <p class="comparison-description">
            Contrasta el menor tiempo con el menor número de conexiones.
          </p>
          <span v-if="comparisonLoading" class="sr-only" role="status"
            >Consultando la ruta BFS para el mismo origen y destino.</span
          >
          <button
            class="button button--quiet clear-button"
            type="button"
            @click="clearResults"
          >
            Limpiar resultados
          </button>
        </div>
      </aside>

      <section class="route-graph" aria-label="Mapa de rutas">
        <header class="graph-heading">
          <div>
            <h3>Red operacional</h3>
            <span>{{
              networkLoading
                ? 'Sincronizando red…'
                : `${network.nodes.length} nodos · ${network.connections.length} conexiones`
            }}</span>
          </div>
          <div class="graph-actions">
            <span class="badge"
              ><Network :size="13" aria-hidden="true" />{{
                activeRoute === 'bfs' ? 'BFS' : 'Dijkstra'
              }}</span
            >
            <button
              v-if="result"
              class="button compare-button"
              type="button"
              :disabled="comparisonLoading || networkLoading || !!networkError"
              @click="compareWithBfs"
            >
              <LoaderCircle
                v-if="comparisonLoading"
                :size="16"
                class="spinning"
              /><GitBranch v-else :size="16" />{{
                comparisonLoading
                  ? 'Comparando…'
                  : bfs
                    ? 'Actualizar comparación BFS'
                    : 'Comparar con BFS'
              }}
            </button>
          </div>
        </header>
        <p v-if="comparisonError" class="error comparison-error" role="alert">
          Comparación no disponible. {{ comparisonError }}
        </p>
        <div
          v-if="bfs && result"
          class="route-switch"
          role="group"
          aria-label="Ruta resaltada en el grafo"
        >
          <button
            type="button"
            :aria-pressed="activeRoute === 'dijkstra'"
            @click="activeRoute = 'dijkstra'"
          >
            Ver ruta Dijkstra</button
          ><button
            type="button"
            :aria-pressed="activeRoute === 'bfs'"
            @click="activeRoute = 'bfs'"
          >
            Ver ruta BFS
          </button>
        </div>
        <div class="route-canvas">
          <ClientOnly
            ><CoverageGraph
              :network="network"
              :loading="networkLoading"
              :error="networkError"
              :visited-node-ids="visitedNodeIds"
              :path-node-ids="pathNodeIds"
              :path-segments="highlightedSegments"
              :origin-id="originId"
              :destination-id="destinationId"
              :result-key="resultKey"
            /><template #fallback
              ><div class="empty-state">
                <LoaderCircle :size="24" class="spinning" />
                <p>Preparando mapa de rutas…</p>
              </div></template
            ></ClientOnly
          >
        </div>
        <footer class="graph-footer">
          <div class="graph-legend">
            <span
              ><i class="legend-path" />{{
                activeRoute === 'bfs' ? 'Ruta BFS' : 'Ruta Dijkstra'
              }}</span
            ><span
              ><i class="legend-visited" />{{
                activeRoute === 'bfs'
                  ? 'Visitado por BFS'
                  : 'Procesado por Dijkstra'
              }}</span
            ><span>→ Dirección · ↔ Doble sentido</span>
          </div>
        </footer>
      </section>
    </section>

    <RouteComparison
      v-if="result && bfs"
      class="route-comparison"
      :dijkstra="result"
      :bfs="bfs"
      :bfs-minutes="bfsMinutes"
      :comparison="comparison"
    />

    <div v-if="result" class="route-details">
      <section
        v-if="result.reachable"
        class="card segments-card"
        aria-labelledby="segments-title"
      >
        <header>
          <div>
            <span class="eyebrow">RECORRIDO FINAL</span>
            <h3 id="segments-title">Desglose de la ruta óptima</h3>
          </div>
          <span class="badge"
            >{{ result.segments.length }}
            {{ result.segments.length === 1 ? 'segmento' : 'segmentos' }}</span
          >
        </header>
        <RoutePath
          :nodes="result.path"
          label="Ubicaciones de la ruta óptima, en orden"
        />
        <ol class="segment-list" aria-label="Duración de cada segmento">
          <li v-for="(segment, index) in result.segments" :key="index">
            <span class="step-number">{{ index + 1 }}</span>
            <div>
              <strong
                >{{ segment.origin.name }} →
                {{ segment.destination.name }}</strong
              ><small
                >{{ segment.origin.code }} →
                {{ segment.destination.code }}</small
              >
            </div>
            <span class="segment-time"
              >{{ segment.estimated_minutes }} min</span
            >
          </li>
        </ol>
        <div class="segment-total">
          <span>Suma total del recorrido</span
          ><strong>{{ result.total_minutes }} minutos</strong>
        </div>
      </section>
      <section v-else class="card unavailable-detail">
        <CircleOff :size="24" aria-hidden="true" />
        <h3>Sin conexión válida para este recorrido</h3>
        <p>
          Prueba otra zona o revisa las conexiones dirigidas en la configuración
          de red.
        </p>
        <NuxtLink to="/network" class="button">Revisar conexiones</NuxtLink>
      </section>
      <section class="card exploration-card">
        <details class="exploration">
          <summary>
            <span>Exploración del algoritmo</span
            ><span class="badge">{{ result.visited_count }} nodos</span>
          </summary>
          <p>
            Estos nodos fueron confirmados por Dijkstra en orden de menor
            distancia acumulada.
          </p>
          <p class="trace-note">
            <Info :size="14" aria-hidden="true" />La exploración es distinta del
            recorrido físico final.
          </p>
          <ol
            class="exploration-list"
            aria-label="Nodos procesados por Dijkstra, en orden"
          >
            <li
              v-for="(node, index) in result.traversal_order"
              :key="`${index}-${node.id}`"
            >
              <span class="step-number">{{ index + 1 }}</span>
              <div>
                <strong>{{ node.name }}</strong
                ><small>{{ node.code }}</small>
              </div>
            </li>
          </ol>
          <p v-if="!result.traversal_order.length" class="hint">
            La API no devolvió nodos procesados para esta consulta.
          </p>
        </details>
      </section>
    </div>
  </div>
</template>

<style scoped>
.routes-workspace {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.route-query {
  padding: 20px;
  border-right: 1px solid var(--border);
  max-height: max(540px, calc(100dvh - 215px));
  overflow-y: auto;
}
.panel-heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 22px;
}
.panel-icon {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  color: var(--primary-hover);
  background: var(--primary-soft);
}
.panel-heading .eyebrow {
  font-size: 0.65rem;
  margin-bottom: 5px;
}
.route-form {
  display: grid;
  gap: 14px;
}
.query-feedback {
  margin-top: 22px;
}
.query-feedback p,
.comparison-description,
.backend-message,
.exploration p,
.unavailable-detail p {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 0.84rem;
}
.query-idle {
  display: flex;
  gap: 9px;
  padding-top: 18px;
  border-top: 1px solid var(--border-soft);
  color: var(--text-muted);
}
.query-idle svg {
  flex-shrink: 0;
  margin-top: 3px;
}
.query-idle p {
  margin: 0;
}
.status-line {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px;
  margin: 0;
}
.status-line svg {
  flex-shrink: 0;
}
.total-time {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 18px 0 16px;
  color: var(--primary-hover);
}
.total-time svg {
  align-self: center;
}
.total-time strong {
  font-size: 2.9rem;
  font-weight: 650;
  letter-spacing: -0.06em;
  line-height: 1;
}
.total-time span {
  color: var(--text-secondary);
  font-size: 0.9rem;
}
.endpoints {
  display: grid;
  gap: 9px;
  margin: 0 0 18px;
}
.endpoints div {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 8px;
  font-size: 0.83rem;
}
dt {
  color: var(--text-muted);
}
dd {
  margin: 0;
  font-weight: 600;
  overflow-wrap: anywhere;
}
.route-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 12px 0;
  border-top: 1px solid var(--border-soft);
  border-bottom: 1px solid var(--border-soft);
}
.route-metrics div {
  display: grid;
  gap: 4px;
}
.route-metrics strong {
  font-size: 1.1rem;
}
.route-metrics span {
  color: var(--text-muted);
  font-size: 0.75rem;
}
.comparison-actions {
  margin-top: 18px;
  padding-top: 16px;
  border-top: 1px solid var(--border-soft);
}
.clear-button {
  width: 100%;
}
.comparison-description {
  margin: 8px 0;
}
.route-graph {
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.graph-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  min-height: 64px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border-soft);
}
.graph-heading h3 {
  font-size: 0.94rem;
  margin-bottom: 5px;
}
.graph-heading > div:first-child > span {
  font-size: 0.77rem;
  color: var(--text-muted);
}
.graph-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.compare-button {
  min-height: 34px;
  padding: 7px 10px;
  font-size: 0.8rem;
}
.route-switch {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--border-soft);
}
.comparison-error {
  margin: 12px 16px;
}
.route-switch button {
  min-height: 34px;
  padding: 7px 12px;
  border: 1px solid transparent;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 600;
}
.route-switch button[aria-pressed='true'] {
  color: var(--primary-hover);
  background: var(--primary-soft);
  border-color: var(--bg-selected);
}
.route-canvas {
  height: max(430px, calc(100dvh - 325px));
  min-width: 0;
  flex: 1 0 auto;
}
.graph-footer {
  padding: 13px 16px;
  border-top: 1px solid var(--border-soft);
  color: var(--text-secondary);
  font-size: 0.72rem;
}
.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.graph-legend span {
  display: flex;
  align-items: center;
  gap: 6px;
}
.graph-legend i {
  display: inline-block;
  width: 12px;
  height: 9px;
  border-radius: 2px;
}
.legend-path {
  border: 2px solid var(--primary);
}
.legend-visited {
  border: 1px dashed var(--primary);
  background: var(--primary-soft);
}
.route-comparison {
  margin-top: 20px;
}
.route-details {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  align-items: start;
  gap: 20px;
  margin-top: 20px;
}
.segments-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
}
.segment-list,
.exploration-list {
  padding: 0;
  margin: 18px 0;
  list-style: none;
}
.segment-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-soft);
}
.segment-list li > div,
.exploration-list li > div {
  display: grid;
  gap: 4px;
  min-width: 0;
  overflow-wrap: anywhere;
}
.segment-list strong,
.exploration-list strong {
  font-size: 0.86rem;
  font-weight: 600;
}
.segment-list small,
.exploration-list small {
  color: var(--text-muted);
  font-size: 0.74rem;
}
.step-number {
  display: grid;
  place-items: center;
  flex: 0 0 25px;
  height: 25px;
  border: 1px solid var(--border);
  border-radius: 50%;
  color: var(--primary-hover);
  font-size: 0.75rem;
}
.segment-time {
  flex-shrink: 0;
  margin-left: auto;
  color: var(--primary-hover);
  background: var(--primary-soft);
  border-radius: 5px;
  padding: 4px 7px;
  font-size: 0.8rem;
  font-weight: 600;
}
.segment-total {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  color: var(--text-secondary);
  font-size: 0.86rem;
}
.segment-total strong {
  color: var(--text-primary);
}
.exploration summary {
  cursor: pointer;
  color: var(--text-primary);
  font-size: 0.92rem;
  font-weight: 600;
  line-height: 1.8;
}
.exploration summary .badge {
  margin-left: 6px;
  font-weight: 400;
}
.trace-note {
  display: flex;
  align-items: flex-start;
  gap: 7px;
}
.trace-note svg {
  flex-shrink: 0;
  margin-top: 3px;
}
.exploration-list {
  display: grid;
  gap: 14px;
  margin-bottom: 0;
}
.exploration-list li {
  display: flex;
  align-items: center;
  gap: 10px;
}
.unavailable-detail {
  display: grid;
  justify-items: start;
  gap: 12px;
  color: var(--text-secondary);
}
.unavailable-detail h3 {
  color: var(--text-primary);
}
.unavailable-detail p {
  margin: 0;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
@media (max-width: 1050px) {
  .routes-workspace {
    grid-template-columns: 1fr;
  }
  .route-query {
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }
  .route-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .calculate-button {
    grid-column: 1 / -1;
  }
  .route-canvas {
    height: 480px;
  }
}
@media (max-width: 760px) {
  .route-details {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 600px) {
  .route-form {
    grid-template-columns: 1fr;
  }
  .route-query {
    padding: 16px;
  }
  .route-canvas {
    height: 420px;
  }
  .segment-list li {
    flex-wrap: wrap;
  }
  .segment-list li > div {
    flex: 1;
  }
}
</style>
