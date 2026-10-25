<script setup lang="ts">
import type { Connection, ConnectionCreatePayload, CoverageNode } from '~/types/coverage'

import { useCoverageApi } from '~/composables/useCoverageApi'
import { useFormSubmit } from '~/composables/useFormSubmit'


const props = defineProps<{
  nodes: CoverageNode[]
}>()


const emit = defineEmits<{
  created: [connection: Connection]
}>()


const coverageApi = useCoverageApi()


function createEmptyForm(): ConnectionCreatePayload {
  return {
    origin_id: null,
    destination_id: null,
    estimated_minutes: 1,
    is_bidirectional: false,
  }
}


const form = reactive<ConnectionCreatePayload>(createEmptyForm())


const { loading, errorMessage, successMessage, submit } = useFormSubmit<ConnectionCreatePayload, Connection>({
  onSubmit: payload => coverageApi.createConnection({
    ...payload,
    origin_id: payload.origin_id!,
    destination_id: payload.destination_id!,
  }),
  successMessage: 'Conexión registrada correctamente.',
  reset: () => Object.assign(form, createEmptyForm()),
})


const validationError = computed(() => {
  if (form.origin_id === null || form.destination_id === null) {
    return ''
  }

  if (form.origin_id === form.destination_id) {
    return 'El origen y el destino deben ser diferentes.'
  }

  return ''
})


const canSubmit = computed(() => {
  return form.origin_id !== null
    && form.destination_id !== null
    && form.origin_id !== form.destination_id
    && form.estimated_minutes > 0
})


async function handleSubmit() {
  if (!canSubmit.value) {
    return
  }

  const connection = await submit(form)
  if (connection) {
    emit('created', connection)
  }
}
</script>


<template>
  <section class="card">
    <h2>Registrar conexión</h2>

    <form
      class="form"
      @submit.prevent="handleSubmit"
    >
      <label>
        Origen

        <select
          v-model.number="form.origin_id"
          required
        >
          <option
            disabled
            :value="null"
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
            :value="null"
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

      <p
        v-if="validationError"
        class="error"
      >
        {{ validationError }}
      </p>

      <button
        type="submit"
        :disabled="loading || !canSubmit"
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
