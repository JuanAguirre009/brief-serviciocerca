<script setup lang="ts">
import type { CoverageNode, Technician, TechnicianCreatePayload } from '~/types/coverage'

import { useCoverageApi } from '~/composables/useCoverageApi'
import { useFormSubmit } from '~/composables/useFormSubmit'


const props = defineProps<{
  nodes: CoverageNode[]
}>()


const emit = defineEmits<{
  created: [technician: Technician]
}>()


const coverageApi = useCoverageApi()


const bases = computed(() => {
  return props.nodes.filter(
    node => node.type === 'BASE',
  )
})


function createEmptyForm(): TechnicianCreatePayload {
  return {
    code: '',
    name: '',
    base_id: null,
    is_available: true,
  }
}


const form = reactive<TechnicianCreatePayload>(createEmptyForm())


const { loading, errorMessage, successMessage, submit } = useFormSubmit<TechnicianCreatePayload, Technician>({
  onSubmit: payload => coverageApi.createTechnician({
    ...payload,
    base_id: payload.base_id!,
  }),
  successMessage: 'Técnico registrado correctamente.',
  reset: () => Object.assign(form, createEmptyForm()),
})


const canSubmit = computed(() => {
  return form.base_id !== null
    && form.code.trim() !== ''
    && form.name.trim() !== ''
})


async function handleSubmit() {
  if (form.base_id === null) {
    return
  }

  const technician = await submit(form)
  if (technician) {
    emit('created', technician)
  }
}
</script>


<template>
  <section class="card">
    <h2>Registrar técnico</h2>

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
          placeholder="TEC-001"
        >
      </label>

      <label>
        Nombre

        <input
          v-model="form.name"
          required
          maxlength="150"
          placeholder="Carlos Pérez"
        >
      </label>

      <label>
        Base

        <select
          v-model.number="form.base_id"
          required
        >
          <option
            disabled
            :value="null"
          >
            Selecciona una base
          </option>

          <option
            v-for="base in bases"
            :key="base.id"
            :value="base.id"
          >
            {{ base.code }} - {{ base.name }}
          </option>
        </select>
      </label>

      <label class="checkbox">
        <input
          v-model="form.is_available"
          type="checkbox"
        >

        Disponible
      </label>

      <button
        type="submit"
        :disabled="loading || !canSubmit"
      >
        {{ loading ? 'Guardando...' : 'Registrar técnico' }}
      </button>
    </form>

    <p
      v-if="!bases.length"
      class="hint"
    >
      Primero debes registrar al menos una base.
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
