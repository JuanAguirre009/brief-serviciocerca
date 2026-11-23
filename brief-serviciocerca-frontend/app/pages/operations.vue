<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  ChevronDown,
  ChevronUp,
  GitBranch,
  LoaderCircle,
  MapPin,
  Search,
} from 'lucide-vue-next'

import OperationalRoute from '~/components/operations/OperationalRoute.vue'
import QuickResult from '~/components/operations/QuickResult.vue'
import DeepAnalysis from '~/components/operations/DeepAnalysis.vue'

import { useRoutePlanning } from '~/composables/useRoutePlanning'

useHead({
  title: 'Consola de operación · ServicioCerca',
})

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
  refreshNetwork,
} = useRoutePlanning()

const analysisOpen = ref(false)

watch(
  [originId, destinationId, result],
  () => {
    analysisOpen.value = false
  },
)

function switchRoute(
  mode: 'dijkstra' | 'bfs',
) {
  activeRoute.value = mode
}
</script>

<template>
  <div class="page operations-page">

    <header class="page-heading">
      <div>
        <span class="eyebrow">
          OPERACIONES
        </span>

        <h2>Consola de operación</h2>

        <p>
          Consulta una zona de servicio y encuentra
          el recorrido con menor tiempo estimado.
        </p>
      </div>

      <button
        class="button"
        type="button"
        :disabled="networkLoading"
        @click="refreshNetwork"
      >
        <LoaderCircle
          :size="16"
          :class="{ spinning: networkLoading }"
        />
        {{
          networkLoading
            ? 'Actualizando…'
            : 'Actualizar red'
        }}
      </button>
    </header>

    <p
      v-if="networkError"
      class="alert error"
      role="alert"
    >
      {{ networkError }}

      <button
        class="button button--quiet"
        type="button"
        @click="refreshNetwork"
      >
        Reintentar
      </button>
    </p>

    <div class="operations-workspace">

      <section
        class="operations-query card"
        aria-label="Consulta de recorrido"
      >
        <div class="operations-query__heading">
          <span class="eyebrow">
            NUEVA CONSULTA
          </span>

          <h3>Planificar recorrido</h3>
        </div>

        <form
          class="operations-form"
          @submit.prevent="calculateRoute"
        >
          <div class="form-field">
            <label for="operation-origin">
              Base de origen
            </label>

            <select
              id="operation-origin"
              v-model="originId"
              :disabled="networkLoading || !bases.length"
            >
              <option
                v-if="!bases.length"
                :value="null"
              >
                {{
                  networkLoading
                    ? 'Cargando bases…'
                    : 'No hay bases registradas'
                }}
              </option>

              <option
                v-for="base in bases"
                :key="base.id"
                :value="base.id"
              >
                {{ base.name }} · {{ base.code }}
              </option>
            </select>
          </div>

          <div class="form-field">
            <label for="operation-destination">
              Zona de destino
            </label>

            <select
              id="operation-destination"
              v-model="destinationId"
              :disabled="networkLoading || !zones.length"
            >
              <option
                v-if="!zones.length"
                :value="null"
              >
                {{
                  networkLoading
                    ? 'Cargando zonas…'
                    : 'No hay zonas registradas'
                }}
              </option>

              <option
                v-for="zone in zones"
                :key="zone.id"
                :value="zone.id"
              >
                {{ zone.name }} · {{ zone.code }}
              </option>
            </select>
          </div>

          <button
            class="button button--primary operations-form__submit"
            type="submit"
            :disabled="!canQuery"
          >
            <LoaderCircle
              v-if="queryLoading"
              :size="16"
              class="spinning"
            />

            <Search
              v-else
              :size="16"
            />

            {{
              queryLoading
                ? 'Consultando…'
                : 'Consultar mejor recorrido'
            }}
          </button>
        </form>

        <p
          v-if="
            !networkLoading &&
            !networkError &&
            (!bases.length || !zones.length)
          "
          class="hint"
        >
          {{
            !bases.length
              ? 'Agrega una base de origen para planificar un recorrido.'
              : 'Agrega una zona de destino para calcular una ruta.'
          }}

          <NuxtLink to="/network">
            Configurar red
          </NuxtLink>
        </p>
      </section>

      <section
        class="operations-result card"
        aria-label="Resultado de la consulta"
      >
        <div class="operations-result__heading">
          <MapPin
            :size="18"
            aria-hidden="true"
          />

          <div>
            <span class="eyebrow">
              RESULTADO RÁPIDO
            </span>

            <h3>Tiempo y recorrido</h3>
          </div>
        </div>

        <QuickResult
          :result="result"
          :loading="queryLoading"
          :error="queryError"
        />

        <div
          v-if="result?.reachable"
          class="operations-route"
        >
          <h4 class="operations-route__title">
            Recorrido operacional
          </h4>

          <OperationalRoute
            :segments="result.segments"
          />
        </div>
      </section>

    </div>

    <section
      v-if="result"
      class="operations-analysis"
      aria-label="Análisis profundo"
    >
      <button
        type="button"
        class="operations-analysis__toggle"
        :aria-expanded="analysisOpen"
        aria-controls="operations-deep-content"
        @click="analysisOpen = !analysisOpen"
      >
        <span class="operations-analysis__toggle-content">
          <span class="operations-analysis__icon">
            <GitBranch :size="20" />
          </span>

          <span>
            <strong>Análisis profundo</strong>

            <small>
              Consulta el grafo, la exploración de
              Dijkstra y la cobertura con BFS.
            </small>
          </span>
        </span>

        <ChevronUp
          v-if="analysisOpen"
          :size="20"
        />

        <ChevronDown
          v-else
          :size="20"
        />
      </button>

      <div
        v-if="analysisOpen"
        id="operations-deep-content"
        class="operations-analysis__content"
      >
        <DeepAnalysis
          :network="network"
          :result="result"
          :bfs="bfs"
          :bfs-minutes="bfsMinutes"
          :comparison="comparison"
          :comparison-loading="comparisonLoading"
          :comparison-error="comparisonError"
          :active-route="activeRoute"
          :path-node-ids="pathNodeIds"
          :visited-node-ids="visitedNodeIds"
          :highlighted-segments="highlightedSegments"
          :result-key="resultKey"
          @compare="compareWithBfs"
          @switch-route="switchRoute"
        />
      </div>
    </section>

  </div>
</template>

<style scoped>
.operations-workspace {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.operations-query,
.operations-result {
  min-width: 0;
}

.operations-query__heading {
  margin-bottom: 20px;
}

.operations-query__heading .eyebrow {
  margin-bottom: 5px;
}

.operations-form {
  display: grid;
  gap: 16px;
}

.operations-form__submit {
  width: 100%;
}

.operations-result__heading {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.operations-result__heading svg {
  flex-shrink: 0;
  color: var(--primary);
}

.operations-result__heading .eyebrow {
  margin-bottom: 4px;
}

.operations-route {
  margin-top: 28px;
  padding-top: 24px;
  border-top: 1px solid var(--border-soft);
}

.operations-route__title {
  margin: 0 0 16px;
  font-size: 0.95rem;
  color: var(--text-secondary);
}

.operations-analysis {
  min-width: 0;
  margin-top: 22px;
}

.operations-analysis__toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  width: 100%;
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
  color: var(--text-primary);
  box-shadow: var(--shadow);
  text-align: left;
  cursor: pointer;
}

.operations-analysis__toggle-content {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.operations-analysis__toggle-content > span:last-child {
  display: grid;
  gap: 6px;
}

.operations-analysis__toggle-content strong {
  font-size: 0.95rem;
}

.operations-analysis__toggle-content small {
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
}

.operations-analysis__icon {
  display: grid;
  place-items: center;
  flex: 0 0 42px;
  width: 42px;
  height: 42px;
  border-radius: 9px;
  background: var(--primary-soft);
  color: var(--primary-hover);
}

.operations-analysis__content {
  min-width: 0;
  margin-top: 14px;
}

@media (max-width: 1000px) {
  .operations-workspace {
    grid-template-columns: 1fr;
  }

  .operations-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .operations-form__submit {
    grid-column: 1 / -1;
  }
}

@media (max-width: 600px) {
  .operations-form {
    grid-template-columns: 1fr;
  }

  .operations-analysis__toggle {
    padding: 14px;
  }
}
</style>
