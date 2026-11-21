<script setup lang="ts">
import {
  AlertCircle,
  CheckCircle2,
  CircleOff,
  Clock3,
  LoaderCircle,
  MapPin,
  Route,
} from 'lucide-vue-next'

import type { ShortestRouteResult } from '~/types/coverage'


interface Props {
  result: ShortestRouteResult | null
  loading: boolean
  error: string
}

const props = defineProps<Props>()


type ResultState = 'idle' | 'loading' | 'found' | 'unavailable' | 'error'


const state = computed<ResultState>(() => {
  if (props.loading) return 'loading'
  if (props.error) return 'error'
  if (!props.result) return 'idle'
  return props.result.reachable ? 'found' : 'unavailable'
})


const segmentCount = computed(() => {
  return props.result?.segments.length ?? 0
})


const nodeCount = computed(() => {
  return props.result?.path.length ?? 0
})
</script>


<template>
  <section
    class="quick-result"
    aria-live="polite"
    aria-atomic="true"
  >
    <!-- Idle -->
    <div
      v-if="state === 'idle'"
      class="quick-result__idle"
    >
      <Route :size="28" aria-hidden="true" />

      <p>
        Selecciona una base de origen y una zona de destino para consultar el
        mejor recorrido.
      </p>
    </div>

    <!-- Loading -->
    <div
      v-else-if="state === 'loading'"
      class="quick-result__loading"
      aria-busy="true"
    >
      <LoaderCircle :size="32" class="spinning" aria-hidden="true" />

      <p>Calculando el mejor recorrido…</p>
    </div>

    <!-- Error -->
    <div
      v-else-if="state === 'error'"
      class="quick-result__error"
      role="alert"
    >
      <AlertCircle :size="24" aria-hidden="true" />

      <p>{{ error }}</p>
    </div>

    <!-- Not available -->
    <div
      v-else-if="state === 'unavailable'"
      class="quick-result__unavailable"
    >
      <CircleOff :size="28" aria-hidden="true" />

      <h3>Ruta no disponible</h3>

      <p>
        No encontramos una ruta disponible entre
        <strong>{{ result?.origin.name }}</strong> y
        <strong>{{ result?.destination.name }}</strong>.
      </p>
    </div>

    <!-- Found -->
    <div
      v-else-if="state === 'found' && result"
      class="quick-result__found"
    >
      <div class="quick-result__header">
        <CheckCircle2 :size="22" aria-hidden="true" />

        <span>Ruta encontrada</span>
      </div>

      <div class="quick-result__time">
        <Clock3 :size="28" aria-hidden="true" />

        <strong>{{ result.total_minutes }}</strong>

        <span>minutos</span>
      </div>

      <dl class="quick-result__endpoints">
        <div>
          <dt>
            <MapPin :size="14" aria-hidden="true" />

            Salida
          </dt>

          <dd>{{ result.origin.name }}</dd>
        </div>

        <div>
          <dt>
            <MapPin :size="14" aria-hidden="true" />

            Destino
          </dt>

          <dd>{{ result.destination.name }}</dd>
        </div>
      </dl>

      <div class="quick-result__metrics">
        <div>
          <strong>{{ segmentCount }}</strong>

          <span>{{ segmentCount === 1 ? 'segmento' : 'segmentos' }}</span>
        </div>

        <div>
          <strong>{{ nodeCount }}</strong>

          <span>{{ nodeCount === 1 ? 'ubicación' : 'ubicaciones' }}</span>
        </div>
      </div>
    </div>
  </section>
</template>


<style scoped>
.quick-result {
  min-height: 260px;
}

.quick-result__idle,
.quick-result__loading,
.quick-result__error,
.quick-result__unavailable {
  display: grid;
  justify-items: center;
  align-content: center;
  gap: 14px;
  min-height: 260px;
  padding: 24px;
  text-align: center;
  border-radius: var(--radius);
  background: var(--bg-surface-soft);
  color: var(--text-secondary);
}

.quick-result__idle svg,
.quick-result__loading svg,
.quick-result__error svg,
.quick-result__unavailable svg {
  color: var(--text-muted);
}

.quick-result__idle p,
.quick-result__loading p,
.quick-result__error p,
.quick-result__unavailable p {
  max-width: 320px;
  margin: 0;
  line-height: 1.6;
}

.quick-result__error {
  color: var(--danger);
  background: var(--danger-soft);
}

.quick-result__error svg {
  color: var(--danger);
}

.quick-result__unavailable h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.1rem;
}

.quick-result__unavailable strong {
  color: var(--text-primary);
}

.quick-result__found {
  display: grid;
  gap: 18px;
}

.quick-result__header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--success);
  font-weight: 700;
  font-size: 0.9rem;
}

.quick-result__header svg {
  flex-shrink: 0;
}

.quick-result__time {
  display: flex;
  align-items: baseline;
  gap: 10px;
  padding: 16px 0;
  color: var(--primary-hover);
  border-top: 1px solid var(--border-soft);
  border-bottom: 1px solid var(--border-soft);
}

.quick-result__time svg {
  align-self: center;
  color: var(--primary);
}

.quick-result__time strong {
  font-size: 3.2rem;
  font-weight: 700;
  letter-spacing: -0.05em;
  line-height: 1;
}

.quick-result__time span {
  color: var(--text-secondary);
  font-size: 1rem;
  font-weight: 500;
}

.quick-result__endpoints {
  display: grid;
  gap: 12px;
  margin: 0;
}

.quick-result__endpoints div {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr);
  gap: 10px;
  align-items: baseline;
}

.quick-result__endpoints dt {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.quick-result__endpoints dd {
  margin: 0;
  font-weight: 600;
  color: var(--text-primary);
  overflow-wrap: anywhere;
}

.quick-result__metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.quick-result__metrics div {
  display: grid;
  gap: 4px;
  padding: 12px;
  border-radius: 8px;
  background: var(--bg-surface-soft);
  text-align: center;
}

.quick-result__metrics strong {
  font-size: 1.2rem;
  color: var(--text-primary);
}

.quick-result__metrics span {
  font-size: 0.78rem;
  color: var(--text-muted);
}

@media (max-width: 600px) {
  .quick-result__time strong {
    font-size: 2.6rem;
  }

  .quick-result__endpoints div {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>
