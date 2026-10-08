import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  cambiarEstadoComisionistaApi,
  cambiarEstadoUsuarioApi,
  emitirPasswordTemporalApi,
  listarUsuariosApi,
  type ProgramaAsesor,
} from './apiAdminUsuarios';
import type {
  EstadoCuentaPayload,
  PasswordTemporalResultado,
  UsuarioListItem,
  UsuarioListQuery,
  UsuarioListResponse,
} from './types';

const QK_LIST = 'admin-usuarios-list' as const;

export function useAdminUsuariosList(query: UsuarioListQuery) {
  return useQuery<UsuarioListResponse>({
    queryKey: [QK_LIST, query],
    queryFn: () => listarUsuariosApi(query),
    staleTime: 30_000,
  });
}

export function useCambiarEstadoUsuario() {
  const qc = useQueryClient();
  return useMutation<
    UsuarioListItem,
    Error,
    { uid: number; payload: EstadoCuentaPayload }
  >({
    mutationFn: ({ uid, payload }) => cambiarEstadoUsuarioApi(uid, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_LIST] });
    },
  });
}

/**
 * Acción reutilizada en las pantallas de asesor: deshabilita/habilita la cuenta
 * de un comisionista por número de documento.
 */
export function useCambiarEstadoComisionista() {
  return useMutation<
    UsuarioListItem,
    Error,
    { programa: ProgramaAsesor; numeroDocumento: string; payload: EstadoCuentaPayload }
  >({
    mutationFn: ({ programa, numeroDocumento, payload }) =>
      cambiarEstadoComisionistaApi(programa, numeroDocumento, payload),
  });
}

// AP-0047: emite una contrasena temporal; la clave en claro solo llega en esta respuesta.
export function useEmitirPasswordTemporal() {
  return useMutation<PasswordTemporalResultado, Error, { uid: number }>({
    mutationFn: ({ uid }) => emitirPasswordTemporalApi(uid),
  });
}
