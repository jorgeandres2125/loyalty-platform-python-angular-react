import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  cerrarOtrasSesionesApi,
  cerrarSesionApi,
  listarMisSesionesApi,
} from './apiSesiones';
import type { SesionActiva } from './types';

const QK_SESIONES = 'sesiones-activas' as const;

// AP-0130: sesiones concurrentes propias (informar + cierre remoto).
export function useMisSesiones() {
  return useQuery<SesionActiva[]>({
    queryKey: [QK_SESIONES],
    queryFn: listarMisSesionesApi,
    staleTime: 15_000,
  });
}

export function useCerrarSesion() {
  const qc = useQueryClient();
  return useMutation<void, Error, string>({
    mutationFn: (sid) => cerrarSesionApi(sid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_SESIONES] });
    },
  });
}

export function useCerrarOtrasSesiones() {
  const qc = useQueryClient();
  return useMutation<void, Error, void>({
    mutationFn: () => cerrarOtrasSesionesApi(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [QK_SESIONES] });
    },
  });
}