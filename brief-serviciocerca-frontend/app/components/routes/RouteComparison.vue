<script setup lang="ts">
import { ArrowDown, Equal, Info } from 'lucide-vue-next'
import RoutePath from './RoutePath.vue'
import type { CoverageCheckResult, ShortestRouteResult } from '~/types/coverage'
defineProps<{
  dijkstra: ShortestRouteResult
  bfs: CoverageCheckResult
  bfsMinutes: number | null
  comparison: { difference: number; savingPercent: number | null } | null
}>()
const numberFormat = new Intl.NumberFormat('es-CO', {
  maximumFractionDigits: 1,
})
</script>

<template>
  <section class="card comparison-card" aria-labelledby="comparison-title">
    <header>
      <div>
        <span class="eyebrow">DOS CRITERIOS, LA MISMA SOLICITUD</span>
        <h3 id="comparison-title">BFS vs. Dijkstra</h3>
      </div>
      <span
        v-if="comparison && comparison.difference > 0"
        class="badge badge--success"
        ><ArrowDown :size="14" />{{ comparison.difference }} min menos con
        Dijkstra<template v-if="comparison.savingPercent !== null">
          · {{ numberFormat.format(comparison.savingPercent) }} % de
          ahorro</template
        ></span
      >
      <span v-else-if="comparison && comparison.difference === 0" class="badge"
        ><Equal :size="14" />Sin diferencia de tiempo</span
      >
    </header>
    <div class="comparison-routes">
      <article>
        <div class="algorithm-heading">
          <strong>BFS</strong
          ><span class="algorithm-time" data-testid="bfs-minutes">{{
            !bfs.covered
              ? 'Sin ruta'
              : bfsMinutes === null
                ? 'Tiempo no disponible'
                : `${bfsMinutes} min`
          }}</span>
        </div>
        <p>Camino con menor número de conexiones.</p>
        <RoutePath
          v-if="bfs.covered"
          :nodes="bfs.path"
          label="Ruta encontrada por BFS"
        />
        <p v-else>{{ bfs.message }}</p>
        <small v-if="bfs.covered"
          >{{ Math.max(0, bfs.path.length - 1) }}
          {{ bfs.path.length === 2 ? 'segmento' : 'segmentos' }}</small
        >
      </article>
      <article>
        <div class="algorithm-heading">
          <strong>Dijkstra</strong
          ><span class="algorithm-time" data-testid="dijkstra-minutes">{{
            dijkstra.total_minutes === null
              ? 'Sin ruta'
              : `${dijkstra.total_minutes} min`
          }}</span>
        </div>
        <p>Camino con menor suma de minutos.</p>
        <RoutePath
          v-if="dijkstra.reachable"
          :nodes="dijkstra.path"
          label="Ruta encontrada por Dijkstra"
        />
        <p v-else>{{ dijkstra.message }}</p>
        <small v-if="dijkstra.reachable"
          >{{ dijkstra.segments.length }}
          {{ dijkstra.segments.length === 1 ? 'segmento' : 'segmentos' }}</small
        >
      </article>
    </div>
    <p v-if="bfs.covered && bfsMinutes === null" class="hint comparison-note">
      <Info :size="16" />Tiempo no disponible: algún tramo BFS no corresponde
      inequívocamente a una conexión de la red. No se calcula ahorro ni se
      resaltan conexiones ambiguas.
    </p>
    <p
      v-else-if="comparison && comparison.difference < 0"
      class="hint comparison-note"
    >
      <Info :size="16" />Los datos consultados muestran un tiempo BFS menor al
      de Dijkstra. Actualiza la red y vuelve a calcular para comparar el mismo
      estado de la red.
    </p>
    <p v-else-if="!comparison" class="hint comparison-note">
      <Info :size="16" />Comparación de tiempos no disponible: ambas consultas
      deben devolver una ruta con duración conocida.
    </p>
    <p v-else-if="comparison.difference === 0" class="comparison-note">
      Ambos caminos tienen el mismo tiempo estimado; no existe ahorro de
      minutos.
    </p>
  </section>
</template>

<style scoped>
header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px;
}
.comparison-routes {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}
article {
  min-width: 0;
  padding: 16px;
  background: var(--bg-surface-soft);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
}
.algorithm-heading {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}
.algorithm-time {
  color: var(--text-primary);
  font-weight: 700;
}
p,
small {
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.6;
}
small {
  display: block;
  margin-top: 12px;
}
.comparison-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 16px 0 0;
}
.comparison-note svg {
  flex-shrink: 0;
  margin-top: 2px;
}
@media (max-width: 650px) {
  .comparison-routes {
    grid-template-columns: 1fr;
  }
}
</style>
