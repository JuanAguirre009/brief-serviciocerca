<script setup lang="ts">
import { useNetwork } from '~/composables/useNetwork'


const { network, loading, errorMessage, refresh } = useNetwork()
</script>



<template>
  <main class="container">
    <header class="page-header">
      <div>
        <p class="eyebrow">
          ServicioCerca
        </p>

        <h1>Red de cobertura</h1>

        <p>
          Configura bases, zonas, técnicos y conexiones
          operativas.
        </p>
      </div>

      <button
        class="secondary"
        :disabled="loading"
        @click="refresh"
      >
        Actualizar red
      </button>
    </header>


    <div
      v-if="errorMessage"
      class="alert error"
    >
      {{ errorMessage }}
    </div>


    <section class="forms-grid">
      <CoverageNodeForm @created="refresh" />

      <CoverageTechnicianForm
        :nodes="network.nodes"
        @created="refresh"
      />

      <CoverageConnectionForm
        :nodes="network.nodes"
        @created="refresh"
      />
    </section>


    <p
      v-if="loading"
      class="loading"
    >
      Cargando red...
    </p>

    <CoverageNetworkList
      v-else
      :network="network"
    />
  </main>
</template>
