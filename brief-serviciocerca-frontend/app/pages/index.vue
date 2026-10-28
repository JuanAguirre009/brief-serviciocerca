<script setup lang="ts">
import {
  ArrowRight,
  Building2,
  MapPin,
  Network,
  RefreshCw,
  UsersRound,
  Activity,
} from 'lucide-vue-next'
import { useNetwork } from '~/composables/useNetwork'
const { network, loading, errorMessage, refresh } = useNetwork()
const bases = computed(
  () => network.value.nodes.filter((n) => n.type === 'BASE').length,
)
const zones = computed(
  () => network.value.nodes.filter((n) => n.type === 'ZONE').length,
)
const available = computed(
  () => network.value.technicians.filter((t) => t.is_available).length,
)
const status = computed(() =>
  errorMessage.value
    ? 'Sin conexión'
    : loading.value
      ? 'Actualizando'
      : network.value.nodes.length
        ? 'Red disponible'
        : 'Sin configurar',
)
const kpis = computed(() => [
  {
    label: 'Bases operativas',
    value: bases.value,
    helper: 'Puntos de origen',
    icon: Building2,
  },
  {
    label: 'Zonas',
    value: zones.value,
    helper: 'Áreas registradas',
    icon: MapPin,
  },
  {
    label: 'Técnicos disponibles',
    value: available.value,
    helper: `${network.value.technicians.length} registrados`,
    icon: UsersRound,
  },
  {
    label: 'Conexiones',
    value: network.value.connections.length,
    helper: 'Enlaces de la red',
    icon: Network,
  },
])
</script>
<template>
  <div class="page">
    <header class="page-heading">
      <div>
        <span class="eyebrow">RESUMEN OPERACIONAL</span>
        <h2>Tu operación, en un solo lugar</h2>
        <p>
          Supervisa los recursos y consulta el alcance de tu red de servicio.
        </p>
      </div>
      <button class="button" :disabled="loading" @click="refresh">
        <RefreshCw :size="16" :class="{ spinning: loading }" /> Actualizar datos
      </button>
    </header>
    <p v-if="errorMessage" class="alert error" role="alert">
      {{ errorMessage }}
    </p>
    <section
      class="kpi-grid"
      aria-label="Indicadores de la red"
      :aria-busy="loading"
    >
      <article v-for="kpi in kpis" :key="kpi.label" class="card kpi">
        <span class="kpi-icon"
          ><component :is="kpi.icon" :size="20" aria-hidden="true"
        /></span>
        <div>
          <span class="kpi-label">{{ kpi.label }}</span
          ><strong>{{ loading || errorMessage ? '—' : kpi.value }}</strong
          ><small>{{ kpi.helper }}</small>
        </div>
      </article>
    </section>
    <section class="operations-grid">
      <article class="card coverage-action">
        <div>
          <span class="eyebrow">COBERTURA TÉCNICA</span>
          <h3>¿Podemos atender esta zona?</h3>
          <p>
            Selecciona una base y una zona para comprobar la cobertura y
            visualizar la ruta encontrada.
          </p>
        </div>
        <NuxtLink to="/coverage" class="button button--primary"
          >Consultar cobertura <ArrowRight :size="16"
        /></NuxtLink>
      </article>
      <article class="card network-action">
        <span class="eyebrow">INFRAESTRUCTURA</span>
        <h3>Red operacional</h3>
        <span
          class="badge"
          :class="{
            'badge--success':
              !loading && !errorMessage && network.nodes.length > 0,
          }"
          ><Activity :size="14" />{{ status }}</span
        >
        <p>
          Administra bases, zonas, técnicos y conexiones desde la configuración.
        </p>
        <NuxtLink to="/network" class="button"
          >Configurar red <ArrowRight :size="16"
        /></NuxtLink>
      </article>
    </section>
    <div v-if="!loading && !errorMessage && !network.nodes.length" class="hint">
      Todavía no hay una red configurada. Agrega tu primera base y las zonas de
      servicio desde <NuxtLink to="/network">Configuración de red</NuxtLink>.
    </div>
  </div>
</template>
<style scoped>
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}
.kpi {
  display: flex;
  gap: 12px;
  padding: 18px;
}
.kpi-icon {
  display: grid;
  place-items: center;
  flex: 0 0 36px;
  height: 36px;
  border-radius: 8px;
  color: var(--primary-hover);
  background: var(--primary-soft);
}
.kpi > div {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.kpi-label,
.kpi small {
  color: var(--text-secondary);
  font-size: 0.8rem;
}
.kpi strong {
  font-size: 2rem;
  line-height: 1;
  font-weight: 650;
  letter-spacing: -0.04em;
}
.operations-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(0, 1fr);
  gap: 16px;
  margin: 20px 0;
}
.coverage-action {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: space-between;
  gap: 25px;
  padding: 26px;
  border-top: 3px solid var(--primary);
}
.coverage-action h3 {
  font-size: 1.5rem;
  letter-spacing: -0.03em;
}
.operations-grid p {
  color: var(--text-secondary);
  line-height: 1.7;
  max-width: 560px;
}
.network-action .badge {
  margin-top: 16px;
}
@media (max-width: 1200px) {
  .kpi {
    padding: 14px;
    gap: 9px;
  }
  .kpi-icon {
    flex-basis: 28px;
    height: 28px;
  }
}
@media (max-width: 900px) {
  .kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 600px) {
  .operations-grid {
    grid-template-columns: 1fr;
  }
  .kpi {
    flex-direction: column;
    align-items: flex-start;
  }
  .coverage-action {
    padding: 20px;
  }
}
</style>
