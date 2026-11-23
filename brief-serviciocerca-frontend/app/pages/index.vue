<script setup lang="ts">
import { computed } from 'vue'
import {
  Activity,
  ArrowRight,
  Building2,
  Clock3,
  GitBranch,
  MapPin,
  Network,
  Radar,
  RefreshCw,
  Route,
  UsersRound,
} from 'lucide-vue-next'

import { useNetwork } from '~/composables/useNetwork'

useHead({
  title: 'Resumen operacional · ServicioCerca',
})

const {
  network,
  loading,
  errorMessage,
  refresh,
} = useNetwork()

const bases = computed(
  () =>
    network.value.nodes.filter(
      (node) => node.type === 'BASE',
    ).length,
)

const zones = computed(
  () =>
    network.value.nodes.filter(
      (node) => node.type === 'ZONE',
    ).length,
)

const available = computed(
  () =>
    network.value.technicians.filter(
      (technician) => technician.is_available,
    ).length,
)

const networkReady = computed(
  () => bases.value > 0 && zones.value > 0,
)

const status = computed(() => {
  if (errorMessage.value) return 'Sin conexión'
  if (loading.value) return 'Actualizando'
  if (!networkReady.value) return 'Configuración pendiente'
  return 'Red registrada'
})

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
    helper: 'Destinos registrados',
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
    helper: 'Trayectos registrados',
    icon: Network,
  },
])
</script>

<template>
  <div class="page dashboard-page">

    <header class="page-heading">
      <div>
        <span class="eyebrow">RESUMEN OPERACIONAL</span>

        <h2>Tu operación, en un solo lugar</h2>

        <p>
          Planifica recorridos y consulta los recursos
          de tu red de servicio.
        </p>
      </div>

      <button
        class="button"
        type="button"
        :disabled="loading"
        @click="refresh"
      >
        <RefreshCw
          :size="16"
          :class="{ spinning: loading }"
          aria-hidden="true"
        />

        Actualizar datos
      </button>
    </header>

    <p
      v-if="errorMessage"
      class="alert error"
      role="alert"
    >
      {{ errorMessage }}
    </p>

    <!-- ACCIÓN OPERACIONAL PRINCIPAL -->
    <section
      class="card main-operation"
      aria-labelledby="main-operation-title"
    >
      <div class="main-operation__content">
        <span class="eyebrow">
          ACCIÓN PRINCIPAL
        </span>

        <h3 id="main-operation-title">
          ¿A dónde vamos y cuánto tardamos?
        </h3>

        <p class="main-operation__description">
          Encuentra el recorrido con menor tiempo estimado
          desde una base hasta una zona de servicio.
          Consulta las ubicaciones que debes recorrer
          y los minutos de cada conexión.
        </p>

        <div
          class="main-operation__benefits"
          aria-label="Información de la consulta"
        >
          <span>
            <Clock3 :size="17" aria-hidden="true" />
            Tiempo estimado
          </span>

          <span>
            <MapPin :size="17" aria-hidden="true" />
            Destino
          </span>

          <span>
            <Route :size="17" aria-hidden="true" />
            Zonas del recorrido
          </span>
        </div>

        <div class="main-operation__actions">
          <NuxtLink
            to="/operations"
            class="button button--primary main-operation__button"
          >
            Consultar mejor recorrido
            <ArrowRight :size="18" aria-hidden="true" />
          </NuxtLink>
        </div>

        <p class="main-operation__note">
          Los tiempos se calculan a partir de las conexiones
          registradas. No representan tráfico en tiempo real.
        </p>
      </div>

      <aside
        class="main-operation__steps"
        aria-label="Pasos para consultar un recorrido"
      >
        <span class="eyebrow">
          CONSULTA EN TRES PASOS
        </span>

        <ol>
          <li>
            <span class="step-number">1</span>

            <div>
              <strong>Selecciona una base</strong>
              <p>
                Define desde dónde partirá el recorrido.
              </p>
            </div>
          </li>

          <li>
            <span class="step-number">2</span>

            <div>
              <strong>Selecciona el destino</strong>
              <p>
                Elige la zona que necesitas atender.
              </p>
            </div>
          </li>

          <li>
            <span class="step-number">3</span>

            <div>
              <strong>Consulta el resultado</strong>
              <p>
                Obtén tiempo total y zonas de paso.
              </p>
            </div>
          </li>
        </ol>
      </aside>
    </section>

    <!-- ESTADO DE LA RED -->
    <section
      class="dashboard-network"
      aria-label="Estado de la red"
    >
      <div class="dashboard-section-heading">
        <div>
          <span class="eyebrow">INFRAESTRUCTURA</span>
          <h3>Estado de la red</h3>
        </div>

        <span
          class="badge"
          :class="{
            'badge--success':
              !loading &&
              !errorMessage &&
              networkReady,
          }"
        >
          <Activity :size="14" aria-hidden="true" />
          {{ status }}
        </span>
      </div>

      <div
        class="kpi-grid"
        :aria-busy="loading"
      >
        <article
          v-for="kpi in kpis"
          :key="kpi.label"
          class="card kpi"
        >
          <span class="kpi-icon">
            <component
              :is="kpi.icon"
              :size="20"
              aria-hidden="true"
            />
          </span>

          <div>
            <span class="kpi-label">
              {{ kpi.label }}
            </span>

            <strong>
              {{
                loading || errorMessage
                  ? '—'
                  : kpi.value
              }}
            </strong>

            <small>{{ kpi.helper }}</small>
          </div>
        </article>
      </div>
    </section>

    <!-- FUNCIONES COMPLEMENTARIAS -->
    <section
      class="secondary-actions"
      aria-label="Herramientas complementarias"
    >
      <article class="card secondary-action">
        <span class="secondary-action__icon">
          <Radar :size="21" aria-hidden="true" />
        </span>

        <div>
          <h3>Consultar cobertura</h3>

          <p>
            Comprueba si una zona es alcanzable
            desde una base mediante BFS.
          </p>
        </div>

        <NuxtLink
          to="/coverage"
          class="button"
        >
          Ver cobertura
          <ArrowRight :size="16" aria-hidden="true" />
        </NuxtLink>
      </article>

      <article class="card secondary-action">
        <span class="secondary-action__icon">
          <GitBranch :size="21" aria-hidden="true" />
        </span>

        <div>
          <h3>Rutas óptimas</h3>

          <p>
            Consulta la vista especializada de Dijkstra
            y los detalles de los recorridos.
          </p>
        </div>

        <NuxtLink
          to="/routes"
          class="button"
        >
          Explorar rutas
          <ArrowRight :size="16" aria-hidden="true" />
        </NuxtLink>
      </article>

      <article class="card secondary-action">
        <span class="secondary-action__icon">
          <Network :size="21" aria-hidden="true" />
        </span>

        <div>
          <h3>Configurar red</h3>

          <p>
            Administra bases, zonas, técnicos
            y conexiones operativas.
          </p>
        </div>

        <NuxtLink
          to="/network"
          class="button"
        >
          Configurar red
          <ArrowRight :size="16" aria-hidden="true" />
        </NuxtLink>
      </article>
    </section>

    <div
      v-if="!loading && !errorMessage && !networkReady"
      class="hint dashboard-hint"
    >
      Para consultar recorridos necesitas registrar al menos
      una base y una zona de servicio.

      Puedes hacerlo desde
      <NuxtLink to="/network">
        Configuración de red
      </NuxtLink>.
    </div>

  </div>
</template>

<style scoped>
.dashboard-page {
  display: grid;
  gap: 22px;
}

.dashboard-page .page-heading {
  margin-bottom: 0;
}

.main-operation {
  display: grid;
  grid-template-columns:
    minmax(0, 1.4fr)
    minmax(280px, 0.6fr);
  gap: 28px;
  padding: 30px;
  border-top: 4px solid var(--primary);
}

.main-operation__content {
  min-width: 0;
}

.main-operation h3 {
  max-width: 680px;
  margin: 4px 0 14px;
  font-size: clamp(1.6rem, 2.6vw, 2.4rem);
  letter-spacing: -0.04em;
  line-height: 1.15;
}

.main-operation__description {
  max-width: 680px;
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.98rem;
  line-height: 1.75;
}

.main-operation__benefits {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.main-operation__benefits span {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 11px;
  border-radius: 8px;
  background: var(--bg-surface-soft);
  color: var(--text-primary);
  font-size: 0.82rem;
  font-weight: 600;
}

.main-operation__benefits svg {
  color: var(--primary);
}

.main-operation__actions {
  margin-top: 26px;
}

.main-operation__button {
  min-height: 48px;
  padding: 12px 20px;
  font-size: 0.96rem;
}

.main-operation__note {
  max-width: 600px;
  margin: 12px 0 0;
  color: var(--text-muted);
  font-size: 0.76rem;
  line-height: 1.55;
}

.main-operation__steps {
  align-self: stretch;
  padding: 22px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius);
  background: var(--bg-surface-soft);
}

.main-operation__steps ol {
  display: grid;
  gap: 19px;
  margin: 22px 0 0;
  padding: 0;
  list-style: none;
}

.main-operation__steps li {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.step-number {
  display: grid;
  place-items: center;
  flex: 0 0 30px;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary-hover);
  font-weight: 700;
}

.main-operation__steps strong {
  display: block;
  margin-bottom: 5px;
  font-size: 0.88rem;
}

.main-operation__steps li p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.8rem;
  line-height: 1.5;
}

.dashboard-section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 14px;
}

.dashboard-section-heading h3 {
  font-size: 1.1rem;
}

.kpi-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
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
  width: 36px;
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

.secondary-actions {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.secondary-action {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
}

.secondary-action__icon {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 9px;
  color: var(--primary-hover);
  background: var(--primary-soft);
}

.secondary-action h3 {
  margin: 0 0 8px;
  font-size: 1rem;
}

.secondary-action p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.6;
}

.secondary-action .button {
  margin-top: auto;
}

.dashboard-hint {
  margin: 0;
}

@media (max-width: 1200px) {
  .main-operation {
    grid-template-columns: 1fr;
  }

  .kpi-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .secondary-actions {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 650px) {
  .main-operation {
    padding: 20px;
  }

  .main-operation__benefits {
    display: grid;
  }

  .main-operation__button {
    width: 100%;
  }

  .kpi-grid,
  .secondary-actions {
    grid-template-columns: 1fr;
  }

  .kpi {
    align-items: center;
  }

  .main-operation__steps {
    padding: 16px;
  }
}
</style>
