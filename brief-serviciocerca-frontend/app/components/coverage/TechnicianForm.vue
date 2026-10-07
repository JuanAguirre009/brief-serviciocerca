<script setup lang="ts">
import type {
  CoverageNode,
  TechnicianCreatePayload,
} from '~/types/coverage'


const props = defineProps<{
  nodes: CoverageNode[]
}>()


const emit = defineEmits<{
  created: []
}>()


const coverageApi = useCoverageApi()


const form = reactive<TechnicianCreatePayload>({
  code: '',
  name: '',
  base_id: 0,
  is_available: true,
})


const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')


const bases = computed(() => {
  return props.nodes.filter(
    node => node.type === 'BASE',
  )
})


async function submit() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await coverageApi.createTechnician({
      ...form,
    })

    successMessage.value =
      'Técnico registrado correctamente.'

    form.code = ''
    form.name = ''
    form.base_id = 0
    form.is_available = true

    emit('created')
  }
  catch (error: any) {
    errorMessage.value =
      error?.data
        ? JSON.stringify(error.data)
        : 'No fue posible registrar el técnico.'
  }
  finally {
    loading.value = false
  }
}
</script>


<template>
  <section class="card">
    <h2>Registrar técnico</h2>

    <form
      class="form"
      @submit.prevent="submit"
    >
      <label>
        Código

        <input
          v-model="form.code"
          required
          placeholder="TEC-001"
        >
      </label>

      <label>
        Nombre

        <input
          v-model="form.name"
          required
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
            :value="0"
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
        :disabled="loading || !bases.length"
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