<script setup lang="ts">
import { useNetwork } from '~/composables/useNetwork'


const { network, loading, errorMessage, refresh } = useNetwork()
</script>



<template>
  <main class="container">
    <header class="page-header">
      <div>
        <p class="eyebrow">
          Configuración
        </p>

        <h1>Red de cobertura</h1>

        <p>
          Registra bases, zonas, técnicos y conexiones operativas.
        </p>
      </div>

      <button
        class="secondary"
        :disabled="loading"
        @click="refresh"
      >
        <span
          v-if="loading"
          class="spinner"
        />

        {{ loading ? 'Actualizando...' : 'Actualizar red' }}
      </button>
    </header>


    <div
      v-if="errorMessage"
      class="alert error"
    >
      {{ errorMessage }}
    </div>


    <div class="dashboard">
      <section class="dashboard-card">
        <div class="card-header">
          <h2>Registrar elementos</h2>

          <p>
            Completa los formularios para construir la red.
          </p>
        </div>

        <div class="forms-stack">
          <CoverageNodeForm @created="refresh" />

          <CoverageTechnicianForm
            :nodes="network.nodes"
            @created="refresh"
          />

          <CoverageConnectionForm
            :nodes="network.nodes"
            @created="refresh"
          />
        </div>
      </section>


      <section class="dashboard-card">
        <div class="card-header">
          <h2>Visualización de la red</h2>

          <p>
            Bases, zonas y conexiones operativas.
          </p>
        </div>

        <CoverageNetworkGraph :network="network" />
      </section>
    </div>


    <p
      v-if="loading"
      class="loading"
    >
      <span class="spinner" />

      Cargando red...
    </p>

    <CoverageNetworkList
      v-else
      :network="network"
    />
  </main>
</template>


<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  align-items: start;
  margin-bottom: 24px;
}

.dashboard-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  min-width: 0;
  overflow: hidden;
}

.dashboard-card:last-child {
  position: sticky;
  top: 90px;
  padding: 24px;
}

.card-header {
  padding: 24px 24px 0;
  margin-bottom: 20px;
}

.card-header h2 {
  margin: 0 0 4px;
  font-size: 1.25rem;
}

.card-header p {
  margin: 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.forms-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 0 24px 24px;
}

.forms-stack > :deep(.card) {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  box-shadow: none;
}

.forms-stack > :deep(.card) h2 {
  font-size: 1.1rem;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
  margin-right: 8px;
  vertical-align: middle;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .dashboard {
    grid-template-columns: 1fr;
  }

  .dashboard-card:last-child {
    position: static;
  }
}
</style>
