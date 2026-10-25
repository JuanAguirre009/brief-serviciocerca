<script setup lang="ts">
import type { CoverageNode, NodeCreatePayload } from '~/types/coverage'

import { useCoverageApi } from '~/composables/useCoverageApi'
import { useFormSubmit } from '~/composables/useFormSubmit'


const emit = defineEmits<{
  created: [node: CoverageNode]
}>()


const coverageApi = useCoverageApi()


function createEmptyForm(): NodeCreatePayload {
  return {
    code: '',
    name: '',
    type: 'BASE',
  }
}


const form = reactive<NodeCreatePayload>(createEmptyForm())


const { loading, errorMessage, successMessage, submit } = useFormSubmit<NodeCreatePayload, CoverageNode>({
  onSubmit: payload => coverageApi.createNode(payload),
  successMessage: 'Nodo registrado correctamente.',
  reset: () => Object.assign(form, createEmptyForm()),
})


async function handleSubmit() {
  const node = await submit(form)
  if (node) {
    emit('created', node)
  }
}
</script>


<template>
  <section class="card">
    <h2>Registrar nodo</h2>

    <form
      class="form"
      @submit.prevent="handleSubmit"
    >
      <label>
        Código

        <input
          v-model="form.code"
          required
          maxlength="50"
          placeholder="BASE-NORTE"
        >
      </label>

      <label>
        Nombre

        <input
          v-model="form.name"
          required
          maxlength="150"
          placeholder="Base Norte"
        >
      </label>

      <label>
        Tipo

        <select
          v-model="form.type"
          required
        >
          <option value="BASE">
            Base
          </option>

          <option value="ZONE">
            Zona
          </option>
        </select>
      </label>

      <button
        type="submit"
        :disabled="loading"
      >
        {{ loading ? 'Guardando...' : 'Registrar nodo' }}
      </button>
    </form>

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
