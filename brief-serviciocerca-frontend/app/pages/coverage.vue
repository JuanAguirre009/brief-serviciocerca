<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  ArrowRight,
  CheckCircle2,
  CircleOff,
  LoaderCircle,
  Network,
  Radar,
  RefreshCw,
  Route,
  Search,
} from 'lucide-vue-next'
import CoverageGraph from '~/components/coverage/CoverageGraph.vue'
import { useCoverageApi } from '~/composables/useCoverageApi'
import { useNetwork } from '~/composables/useNetwork'
import { formatApiError } from '~/utils/formatApiError'
import type { CoverageQueryResult } from '~/types/coverage'

const api = useCoverageApi()
const {
  network,
  loading: networkLoading,
  errorMessage: networkError,
  refresh,
} = useNetwork()
const originId = ref<number | null>(null)
const destinationId = ref<number | null>(null)
const queryLoading = ref(false)
const queryError = ref('')
const result = ref<CoverageQueryResult | null>(null)
const resultKey = ref(0)
let requestVersion = 0
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
function clearResult() {
  requestVersion++
  queryLoading.value = false
  result.value = null
  queryError.value = ''
  resultKey.value++
}
watch([originId, destinationId], clearResult)
watch(network, clearResult)
const visitedNodeIds = computed(
  () => result.value?.traversal_order.map((node) => node.id) ?? [],
)
const pathNodeIds = computed(() =>
  result.value?.mode === 'check' && result.value.covered
    ? result.value.path.map((node) => node.id)
    : [],
)
const highlightedDestination = computed(() =>
  result.value?.mode === 'reachability' ? null : destinationId.value,
)
const canQuery = computed(
  () =>
    !queryLoading.value &&
    !networkLoading.value &&
    !networkError.value &&
    originId.value !== null,
)
async function query(mode: 'check' | 'reachability') {
  if (!canQuery.value || (mode === 'check' && destinationId.value === null))
    return
  const version = ++requestVersion
  queryLoading.value = true
  queryError.value = ''
  result.value = null
  try {
    const response = await api.getReachability(
      originId.value!,
      mode === 'check' ? destinationId.value! : undefined,
    )
    if (version === requestVersion) {
      result.value = response
      resultKey.value++
    }
  } catch (error) {
    if (version === requestVersion) queryError.value = formatApiError(error)
  } finally {
    if (version === requestVersion) queryLoading.value = false
  }
}
async function refreshNetwork() {
  clearResult()
  await refresh()
}
</script>
<template>
  <div class="page coverage-page">
    <header class="page-heading">
      <div>
        <span class="eyebrow">COBERTURA TÉCNICA</span>
        <h2>Consulta de cobertura</h2>
        <p>
          Comprueba el servicio desde una base y explora el resultado sobre la
          red.
        </p>
      </div>
      <button
        class="button"
        :disabled="networkLoading || queryLoading"
        @click="refreshNetwork"
      >
        <RefreshCw :size="16" :class="{ spinning: networkLoading }" />
        Actualizar red
      </button>
    </header>
    <p v-if="networkError" class="alert error" role="alert">
      {{ networkError }} Los datos anteriores, si existen, se conservan.
    </p>
    <section class="coverage-workspace">
      <aside class="query-panel" aria-label="Consulta y resultado de cobertura">
        <div class="panel-heading">
          <span class="panel-icon"><Radar :size="20" /></span>
          <div>
            <span class="eyebrow">NUEVA CONSULTA</span>
            <h3>Evaluar cobertura</h3>
          </div>
        </div>
        <form class="query-form" @submit.prevent="query('check')">
          <div class="form-field">
            <label for="origin">Base de origen</label
            ><select
              id="origin"
              v-model="originId"
              :disabled="networkLoading || queryLoading || !bases.length"
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
            <label for="destination">Zona solicitada</label
            ><select
              id="destination"
              v-model="destinationId"
              :disabled="networkLoading || queryLoading || !zones.length"
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
            class="button button--primary"
            type="submit"
            :disabled="!canQuery || destinationId === null"
          >
            <LoaderCircle
              v-if="queryLoading"
              :size="16"
              class="spinning"
            /><Search v-else :size="16" />{{
              queryLoading ? 'Consultando…' : 'Consultar cobertura'
            }}
          </button>
          <button
            class="button"
            type="button"
            :disabled="!canQuery"
            @click="query('reachability')"
          >
            <Route :size="16" /> Ver alcance completo
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
              ? 'Agrega una base para consultar cobertura.'
              : 'Agrega una zona para consultar un destino. Puedes explorar el alcance de la base.'
          }}
          <NuxtLink to="/network">Configurar red</NuxtLink>
        </p>
        <p v-if="queryError" class="error" role="alert">{{ queryError }}</p>
        <div :aria-busy="queryLoading" aria-live="polite" aria-atomic="true">
          <p v-if="queryLoading" class="query-hint">
            Consultando el motor de cobertura…
          </p>
          <div v-else-if="result" class="result-block">
            <div
              v-if="result.mode === 'check'"
              class="result-status"
              :class="result.covered ? 'success' : 'error'"
            >
              <CheckCircle2 v-if="result.covered" :size="19" /><CircleOff
                v-else
                :size="19"
              /><strong>{{
                result.covered ? 'Cobertura disponible' : 'Sin cobertura'
              }}</strong>
            </div>
            <div v-else class="result-status success">
              <Radar :size="19" /><strong
                >{{ result.reachable_count }} zonas alcanzables desde
                {{ result.origin.name }}</strong
              >
            </div>
            <p class="result-message">{{ result.message }}</p>
            <p class="visited-count">
              <strong>{{ result.visited_count }}</strong> nodos visitados
            </p>
            <div
              v-if="result.mode === 'check' && result.path.length"
              class="route-result"
            >
              <span class="eyebrow">RUTA ENCONTRADA</span>
              <ol class="route-chips">
                <li v-for="(node, index) in result.path" :key="node.id">
                  <ArrowRight v-if="index" :size="13" aria-hidden="true" /><span
                    :title="node.code"
                    >{{ node.name }}</span
                  >
                </li>
              </ol>
            </div>
            <details class="trace" open>
              <summary>
                TRAZA BFS <span>{{ result.traversal_order.length }}</span>
              </summary>
              <ol>
                <li
                  v-for="(node, index) in result.traversal_order"
                  :key="node.id"
                >
                  <span class="trace-index">{{ index + 1 }}</span>
                  <div>
                    <strong>{{ node.name }}</strong
                    ><small>{{ node.code }}</small>
                  </div>
                </li>
              </ol>
            </details>
            <button
              class="button button--quiet clear-button"
              @click="clearResult"
            >
              Limpiar resultado
            </button>
          </div>
          <div v-else-if="!queryError" class="query-idle">
            <Route :size="19" aria-hidden="true" />
            <p>
              Selecciona el origen y el destino para consultar cobertura, o
              explora el alcance completo de una base.
            </p>
          </div>
        </div>
      </aside>
      <section class="graph-panel" aria-label="Mapa de cobertura">
        <header class="graph-header">
          <div>
            <h3>Red operacional</h3>
            <span>{{
              networkLoading
                ? 'Sincronizando red…'
                : `${network.nodes.length} nodos · ${network.connections.length} conexiones`
            }}</span>
          </div>
          <span class="badge"><Network :size="13" /> Vista de red</span>
        </header>
        <div class="graph-body">
          <ClientOnly
            ><CoverageGraph
              :network="network"
              :loading="networkLoading"
              :error="networkError"
              :visited-node-ids="visitedNodeIds"
              :path-node-ids="pathNodeIds"
              :origin-id="originId"
              :destination-id="highlightedDestination"
              :result-key="resultKey"
            /><template #fallback
              ><div class="empty-state">
                <LoaderCircle :size="24" class="spinning" />
                <p>Preparando mapa de cobertura…</p>
              </div></template
            ></ClientOnly
          >
        </div>
        <footer class="graph-footer">
          <div class="graph-legend">
            <span><i class="legend-visited" />Visitado</span
            ><span><i class="legend-path" />Ruta encontrada</span
            ><span>→ Dirección · ↔ Doble sentido</span>
          </div>
          <span class="graph-tip"
            >Arrastra para mover · Usa los controles para ampliar</span
          >
        </footer>
      </section>
    </section>
  </div>
</template>
<style scoped>
.coverage-workspace {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
  overflow: hidden;
  box-shadow: var(--shadow);
}
.query-panel {
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
.query-form {
  display: grid;
  gap: 14px;
}
.query-form .button + .button {
  margin-top: -6px;
}
.result-block {
  border-top: 1px solid var(--border-soft);
  margin-top: 22px;
  padding-top: 18px;
}
.result-status {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 11px;
  margin: 0;
}
.result-status svg {
  flex-shrink: 0;
}
.result-message {
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.6;
}
.visited-count {
  font-size: 0.83rem;
  color: var(--text-secondary);
}
.visited-count strong {
  color: var(--text-primary);
}
.route-result {
  margin-top: 20px;
}
.route-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 0;
  margin: 0;
  list-style: none;
}
.route-chips li {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  max-width: 100%;
}
.route-chips li span {
  padding: 5px 8px;
  background: var(--primary-soft);
  color: var(--primary-hover);
  border-radius: 5px;
  font-size: 0.78rem;
  overflow-wrap: anywhere;
}
.trace {
  margin-top: 20px;
}
.trace summary {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 4px 0;
}
.trace summary span {
  margin-left: 6px;
  font-weight: 400;
}
.trace ol {
  display: grid;
  gap: 10px;
  padding: 0;
  margin: 14px 0;
  list-style: none;
}
.trace li {
  display: flex;
  gap: 10px;
  align-items: center;
}
.trace-index {
  display: grid;
  place-items: center;
  flex: 0 0 24px;
  height: 24px;
  border: 1px solid var(--border);
  border-radius: 50%;
  color: var(--primary-hover);
  font-size: 0.74rem;
}
.trace li div {
  display: grid;
  gap: 3px;
  min-width: 0;
  overflow-wrap: anywhere;
}
.trace strong {
  font-size: 0.82rem;
  font-weight: 600;
}
.trace small {
  color: var(--text-muted);
  font-size: 0.74rem;
}
.clear-button {
  width: 100%;
  margin-top: 8px;
}
.query-idle {
  display: flex;
  gap: 9px;
  margin-top: 24px;
  border-top: 1px solid var(--border-soft);
  padding-top: 18px;
  color: var(--text-muted);
}
.query-idle svg {
  flex-shrink: 0;
  margin-top: 3px;
}
.query-idle p,
.query-hint {
  margin: 0;
  line-height: 1.6;
  font-size: 0.82rem;
  color: var(--text-secondary);
}
.query-hint {
  margin-top: 20px;
}
.graph-panel {
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.graph-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 64px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border-soft);
}
.graph-header h3 {
  font-size: 0.94rem;
  margin-bottom: 5px;
}
.graph-header div > span {
  font-size: 0.77rem;
  color: var(--text-muted);
}
.graph-body {
  height: max(430px, calc(100dvh - 325px));
  min-width: 0;
}
.graph-footer {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  padding: 13px 16px;
  border-top: 1px solid var(--border-soft);
  font-size: 0.72rem;
  color: var(--text-secondary);
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
.legend-visited {
  background: var(--primary-soft);
  border: 1px dashed var(--primary);
}
.legend-path {
  border: 2px solid var(--primary);
}
.graph-tip {
  color: var(--text-muted);
}
@media (max-width: 1200px) {
  .graph-tip {
    display: none;
  }
}
@media (max-width: 1050px) {
  .coverage-workspace {
    grid-template-columns: 1fr;
  }
  .query-panel {
    max-height: none;
    border-right: 0;
    border-bottom: 1px solid var(--border);
  }
  .query-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .query-form .button + .button {
    margin: 0;
  }
  .query-idle {
    margin-top: 16px;
  }
  .graph-body {
    height: 480px;
  }
}
@media (max-width: 600px) {
  .query-form {
    grid-template-columns: 1fr;
  }
  .query-panel {
    padding: 16px;
  }
  .graph-header .badge {
    display: none;
  }
  .graph-body {
    height: 420px;
  }
}
</style>
