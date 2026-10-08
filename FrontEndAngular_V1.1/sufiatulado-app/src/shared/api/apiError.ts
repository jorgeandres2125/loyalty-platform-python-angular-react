import { HttpErrorResponse, type HttpHeaders } from '@angular/common/http';

/**
 * Error HTTP normalizado de la SPA. Conserva la forma `error.response.{status,data}`
 * que usaba el cliente Axios del proyecto React, para que los helpers de mensajes
 * (extractError, getProblemMessage, graciaExpirada…) sigan funcionando sin cambios.
 */
export interface ApiErrorResponse {
  status: number;
  data: unknown;
  headers: HttpHeaders | null;
}

export class ApiError extends Error {
  readonly isApiError = true as const;
  readonly response: ApiErrorResponse | undefined;
  readonly config: { url: string; method: string };

  constructor(
    message: string,
    response: ApiErrorResponse | undefined,
    config: { url: string; method: string },
  ) {
    super(message);
    this.name = 'ApiError';
    this.response = response;
    this.config = config;
  }

  static desdeHttp(err: HttpErrorResponse, method: string): ApiError {
    // status 0 = error de red / CORS / abortado: no hay respuesta del servidor.
    const response: ApiErrorResponse | undefined =
      err.status === 0 ? undefined : { status: err.status, data: err.error, headers: err.headers };
    const message: string =
      err.status === 0 ? 'Network Error' : `Request failed with status code ${err.status}`;
    return new ApiError(message, response, { url: err.url ?? '', method });
  }
}

export function isApiError(value: unknown): value is ApiError {
  return (
    value instanceof ApiError ||
    (typeof value === 'object' && value !== null && (value as { isApiError?: unknown }).isApiError === true)
  );
}

export { HttpErrorResponse };
