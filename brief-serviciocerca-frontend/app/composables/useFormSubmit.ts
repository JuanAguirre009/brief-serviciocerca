import { ref } from 'vue'
import { formatApiError } from '~/utils/formatApiError'

export interface UseFormSubmitOptions<T, R> {
  onSubmit: (payload: T) => Promise<R>
  successMessage: string
  reset: () => void
}

export function useFormSubmit<T, R>(options: UseFormSubmitOptions<T, R>) {
  const loading = ref(false)
  const errorMessage = ref('')
  const successMessage = ref('')

  async function submit(payload: T): Promise<R | undefined> {
    loading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    try {
      const result = await options.onSubmit(payload)
      successMessage.value = options.successMessage
      options.reset()
      return result
    }
    catch (error: any) {
      errorMessage.value = formatApiError(error)
      return undefined
    }
    finally {
      loading.value = false
    }
  }

  function clearMessages() {
    errorMessage.value = ''
    successMessage.value = ''
  }

  return {
    loading,
    errorMessage,
    successMessage,
    submit,
    clearMessages,
  }
}
