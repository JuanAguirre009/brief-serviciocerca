/**
 * Transforms an API error payload into a human-readable string.
 *
 * Supports:
 * - DRF { detail: string }
 * - DRF { field: ["msg", ...] }
 * - DRF { field: "msg" }
 * - Plain strings
 */
export function formatApiError(error: any): string {
  if (!error?.data) {
    return 'Ocurrió un error inesperado. Inténtalo de nuevo.'
  }

  const data = error.data

  if (typeof data === 'string') {
    return data
  }

  if (data.detail) {
    return String(data.detail)
  }

  if (Array.isArray(data)) {
    return data.map(String).join('. ')
  }

  return Object.entries(data)
    .map(([field, messages]) => {
      const label = field === 'nonFieldErrors' ? 'Error' : field
      const text = Array.isArray(messages)
        ? messages.join('. ')
        : String(messages)
      return `${label}: ${text}`
    })
    .join('. ')
}
