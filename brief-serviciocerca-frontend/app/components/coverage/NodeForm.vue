<script setup lang="ts">
import type {
  NodeCreatePayload,
  NodeType,
} from '~/types/coverage'


const emit = defineEmits<{
  created: []
}>()


const coverageApi = useCoverageApi()


const form = reactive<NodeCreatePayload>({
  code: '',
  name: '',
  type: 'BASE',
})


const loading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')


async function submit() {
  loading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    await coverageApi.createNode({
      code: form.code,
      name: form.name,
      type: form.type,
    })

    successMessage.value = 'Nodo registrado correctamente.'

    form.code = ''
    form.name = ''
    form.type = 'BASE'

    emit('created')
  }
  catch (error: any) {
    errorMessage.value =
      error?.data
        ? JSON.stringify(error.data)
        : 'No fue posible registrar el nodo.'
  }
  finally {
    loading.value = false
  }
}
</script>


<template>
  <section class="card">
    <h2>Registrar nodo</h2>

    <form
      class="form"
      @submit.prevent="submit"
    >
      <label>
        Código

        <input
          v-model="form.code"
          required
          placeholder="BASE-NORTE"
        >
      </label>

      <label>
        Nombre

        <input
          v-model="form.name"
          required
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