/** Extrae un mensaje legible del error de Axios/FastAPI (detail string o lista). */
export function extractError(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
  if (Array.isArray(detail)) return detail.join('; ');
  if (typeof detail === 'string') return detail;
  if (err instanceof Error) return err.message;
  return fallback;
}
