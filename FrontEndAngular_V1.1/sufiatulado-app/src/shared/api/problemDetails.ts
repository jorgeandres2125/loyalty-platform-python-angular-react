import { isApiError } from './apiError';

/**
 * RFC 7807 Problem Details (formato que emite FastAPI / Starlette para HTTPException
 * y para errores de validación Pydantic). Discriminated por el campo `type`.
 *
 * Pydantic `ValidationError` (422) viene como un sub-shape: `detail` es un array
 * de `{loc, msg, type, ...}`. El campo `errors` lo normaliza por nombre de campo.
 */
export interface ProblemDetails {
  type?: string;
  title?: string;
  status?: number;
  detail?: string | unknown;
  instance?: string;
  errors?: Record<string, string[]>;
}

export function isProblemDetails(value: unknown): value is ProblemDetails {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  const hasShape: boolean =
    typeof obj.title === 'string' ||
    typeof obj.detail === 'string' ||
    typeof obj.detail === 'object' ||
    typeof obj.errors === 'object';
  return hasShape;
}

/**
 * Extrae el ProblemDetails del payload de un ApiError, o null si la respuesta
 * no tiene esa forma (timeout, network error, 5xx con HTML, etc.).
 */
export function extractProblemDetails(err: unknown): ProblemDetails | null {
  if (!isApiError(err)) return null;
  const data: unknown = err.response?.data;
  return isProblemDetails(data) ? data : null;
}

/**
 * Devuelve un mensaje legible para mostrar al usuario, derivado del error.
 * Prioriza ProblemDetails.detail (string) → title → fallback genérico.
 */
export function getProblemMessage(err: unknown, fallback: string = 'Ocurrió un error inesperado.'): string {
  const problem: ProblemDetails | null = extractProblemDetails(err);
  if (problem) {
    if (typeof problem.detail === 'string' && problem.detail.length > 0) return problem.detail;
    if (typeof problem.title === 'string' && problem.title.length > 0) return problem.title;
  }
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}
