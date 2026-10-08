import { Injectable, inject } from '@angular/core';
import {
  HttpClient,
  HttpErrorResponse,
  HttpHeaders,
  HttpParams,
  type HttpResponse,
} from '@angular/common/http';
import { firstValueFrom, timeout, TimeoutError } from 'rxjs';
import { API_BASE_URL } from '../config/constants';
import { ApiError } from './apiError';

export type ParamValue = string | number | boolean | null | undefined;

export interface RequestConfig {
  params?: Record<string, ParamValue> | URLSearchParams;
  responseType?: 'json' | 'blob';
  headers?: Record<string, string>;
}

/** Respuesta con la misma forma que la de Axios (`data`, `status`, `headers`). */
export interface ApiResponse<T> {
  data: T;
  status: number;
  headers: HttpHeaders;
}

const TIMEOUT_MS = 30_000;

/**
 * Cliente HTTP de la SPA (equivalente al `apiClient` de Axios del proyecto React).
 * Envuelve `HttpClient`: antepone `API_BASE_URL`, envía cookies (`withCredentials`),
 * aplica un timeout de 30 s y normaliza los errores a `ApiError`. La protección
 * CSRF, el limitador de ráfaga y el manejo de 401 viven en los interceptores
 * (ver `interceptors.ts`). Devuelve Promesas para integrarse con TanStack Query.
 */
@Injectable({ providedIn: 'root' })
export class ApiClient {
  private readonly http = inject(HttpClient);

  get<T>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('GET', url, undefined, config);
  }

  delete<T = unknown>(url: string, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('DELETE', url, undefined, config);
  }

  post<T = unknown>(url: string, body?: unknown, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('POST', url, body, config);
  }

  put<T = unknown>(url: string, body?: unknown, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('PUT', url, body, config);
  }

  patch<T = unknown>(url: string, body?: unknown, config?: RequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>('PATCH', url, body, config);
  }

  private async request<T>(
    method: string,
    url: string,
    body: unknown,
    config: RequestConfig | undefined,
  ): Promise<ApiResponse<T>> {
    const esFormData: boolean = typeof FormData !== 'undefined' && body instanceof FormData;
    let headers = new HttpHeaders(config?.headers ?? {});
    // Con FormData el navegador fija el boundary del multipart: no forzar Content-Type.
    if (esFormData) {
      headers = headers.delete('Content-Type');
    } else if (!headers.has('Content-Type') && body !== undefined) {
      headers = headers.set('Content-Type', 'application/json');
    }

    const obs$ = this.http.request(method, this.urlCompleta(url), {
      body: body ?? null,
      params: this.construirParams(config?.params),
      headers,
      withCredentials: true,
      observe: 'response',
      responseType: (config?.responseType ?? 'json') as 'json',
    });

    try {
      const resp = (await firstValueFrom(obs$.pipe(timeout(TIMEOUT_MS)))) as HttpResponse<T>;
      return { data: resp.body as T, status: resp.status, headers: resp.headers };
    } catch (err: unknown) {
      if (err instanceof HttpErrorResponse) {
        throw ApiError.desdeHttp(err, method);
      }
      if (err instanceof TimeoutError) {
        throw new ApiError(`timeout of ${TIMEOUT_MS}ms exceeded`, undefined, { url, method });
      }
      throw err;
    }
  }

  private urlCompleta(url: string): string {
    if (/^https?:\/\//i.test(url)) return url;
    const base: string = API_BASE_URL.replace(/\/+$/, '');
    return `${base}/${url.replace(/^\/+/, '')}`;
  }

  private construirParams(params: RequestConfig['params']): HttpParams | undefined {
    if (!params) return undefined;
    let httpParams = new HttpParams();
    if (params instanceof URLSearchParams) {
      params.forEach((valor, clave) => {
        httpParams = httpParams.append(clave, valor);
      });
      return httpParams;
    }
    // Igual que Axios: se omiten los valores null / undefined.
    for (const [clave, valor] of Object.entries(params)) {
      if (valor === null || valor === undefined) continue;
      httpParams = httpParams.set(clave, String(valor));
    }
    return httpParams;
  }
}
