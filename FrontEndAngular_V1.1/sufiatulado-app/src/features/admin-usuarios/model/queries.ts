import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminUsuariosApi, type ProgramaAsesor } from './apiAdminUsuarios';
import type {
  EstadoCuentaPayload,
  PasswordTemporalResultado,
  UsuarioListItem,
  UsuarioListQuery,
  UsuarioListResponse,
} from './types';

const QK_LIST = 'admin-usuarios-list' as const;

export function injectAdminUsuariosList(query: () => UsuarioListQuery) {
  const api = inject(AdminUsuariosApi);
  return injectQuery<UsuarioListResponse>(() => {
    const q = query();
    return {
      queryKey: [QK_LIST, q],
      queryFn: () => api.listar(q),
      staleTime: 30_000,
    };
  });
}

export function injectCambiarEstadoUsuario() {
  const api = inject(AdminUsuariosApi);
  const qc = inject(QueryClient);
  return injectMutation<UsuarioListItem, Error, { uid: number; payload: EstadoCuentaPayload }>(
    () => ({
      mutationFn: ({ uid, payload }) => api.cambiarEstadoUsuario(uid, payload),
      onSuccess: () => {
        void qc.invalidateQueries({ queryKey: [QK_LIST] });
      },
    }),
  );
}

/**
 * Acción reutilizada en las pantallas de asesor: deshabilita/habilita la cuenta
 * de un comisionista por número de documento.
 */
export function injectCambiarEstadoComisionista() {
  const api = inject(AdminUsuariosApi);
  return injectMutation<
    UsuarioListItem,
    Error,
    { programa: ProgramaAsesor; numeroDocumento: string; payload: EstadoCuentaPayload }
  >(() => ({
    mutationFn: ({ programa, numeroDocumento, payload }) =>
      api.cambiarEstadoComisionista(programa, numeroDocumento, payload),
  }));
}

// AP-0047: emite una contrasena temporal; la clave en claro solo llega en esta respuesta.
export function injectEmitirPasswordTemporal() {
  const api = inject(AdminUsuariosApi);
  return injectMutation<PasswordTemporalResultado, Error, { uid: number }>(() => ({
    mutationFn: ({ uid }) => api.emitirPasswordTemporal(uid),
  }));
}
