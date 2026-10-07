<script setup lang="ts">
import type {
  CoverageNetwork,
} from '~/types/coverage'

import { useCoverageApi } from '~/composables/useCoverageApi'


const coverageApi = useCoverageApi()


const network = ref<CoverageNetwork>({
  nodes: [],
  technicians: [],
  connections: [],
})


const loading = ref(true)
const errorMessage = ref('')


async function loadNetwork() {
  loading.value = true
  errorMessage.value = ''

  try {
    network.value = await coverageApi.getNetwork()
  }
  catch {
    errorMessage.value =
      'No fue posible consultar la red de cobertura.'
  }
  finally {
    loading.value = false
  }
}


onMounted(() => {
  loadNetwork()
})
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
        @click="loadNetwork"
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
      <CoverageNodeForm
        @created="loadNetwork"
      />

      <CoverageTechnicianForm
        :nodes="network.nodes"
        @created="loadNetwork"
      />

      <CoverageConnectionForm
        :nodes="network.nodes"
        @created="loadNetwork"
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
