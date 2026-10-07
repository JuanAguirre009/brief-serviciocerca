<script setup lang="ts">
import type {
  ConnectionCreatePayload,
  CoverageNode,
} from '~/types/coverage'

import { useCoverageApi } from '~/composables/useCoverageApi'

const props = defineProps<{
  nodes: CoverageNode[]
}>()


const emit = defineEmits<{
  created: []
}>()


const coverageApi = useCoverageApi()


const form = reactive<ConnectionCreatePayload>({
  origin_id: 0,
  destination_id: 0,
  estimated_minutes: 1,
  is_bidirectional: false,
})


const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')


async function submit() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await coverageApi.createConnection({
      ...form,
    })

    successMessage.value =
      'Conexión registrada correctamente.'

    form.origin_id = 0
    form.destination_id = 0
    form.estimated_minutes = 1
    form.is_bidirectional = false

    emit('created')
  }
  catch (error: any) {
    errorMessage.value =
      error?.data
        ? JSON.stringify(error.data)
        : 'No fue posible registrar la conexión.'
  }
  finally {
    loading.value = false
  }
}
</script>


<template>
  <section class="card">
    <h2>Registrar conexión</h2>

    <form
      class="form"
      @submit.prevent="submit"
    >
      <label>
        Origen

        <select
          v-model.number="form.origin_id"
          required
        >
          <option
            disabled
            :value="0"
          >
            Selecciona un nodo
          </option>

          <option
            v-for="node in nodes"
            :key="node.id"
            :value="node.id"
          >
            {{ node.code }} - {{ node.name }}
          </option>
        </select>
      </label>

      <label>
        Destino

        <select
          v-model.number="form.destination_id"
          required
        >
          <option
            disabled
            :value="0"
          >
            Selecciona un nodo
          </option>

          <option
            v-for="node in nodes"
            :key="node.id"
            :value="node.id"
          >
            {{ node.code }} - {{ node.name }}
          </option>
        </select>
      </label>

      <label>
        Tiempo estimado (minutos)

        <input
          v-model.number="form.estimated_minutes"
          type="number"
          min="1"
          required
        >
      </label>

      <label class="checkbox">
        <input
          v-model="form.is_bidirectional"
          type="checkbox"
        >

        Puede recorrerse en ambos sentidos
      </label>

      <button
        type="submit"
        :disabled="loading || nodes.length < 2"
      >
        {{ loading ? 'Guardando...' : 'Registrar conexión' }}
      </button>
    </form>

    <p
      v-if="nodes.length < 2"
      class="hint"
    >
      Debes registrar al menos dos nodos.
    </p>

    <p
      v-if="successMessage"
      class="success"
    >
      {{ successMessage }}
    </p>

    <p
      v-if="errorMessage"
      class="error"
    >
      {{ errorMessage }}
    </p>
  </section>
</template>