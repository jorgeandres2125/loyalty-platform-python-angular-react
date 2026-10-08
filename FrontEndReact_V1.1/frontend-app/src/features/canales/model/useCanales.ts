import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarCanalApi,
  crearCanalApi,
  listarCanalesActivasApi,
  listarCanalesApi,
  obtenerCanalApi,
} from './apiCanales';
import type {
  CanalActivaItem,
  CanalFormPayload,
  CanalFormResponse,
  CanalListQuery,
  CanalListResponse,
} from './types';

export function useCanales(query: CanalListQuery) {
  return useQuery<CanalListResponse>({
    queryKey: ['canales', query],
    queryFn: () => listarCanalesApi(query),
    staleTime: 30_000,
  });
}

export function useCanalesActivas() {
  return useQuery<CanalActivaItem[]>({
    queryKey: ['canales-activas'],
    queryFn: listarCanalesActivasApi,
    staleTime: 5 * 60_000,
  });
}

export function useCanal(codCanales: number | null) {
  return useQuery<CanalFormResponse>({
    queryKey: ['canal', codCanales],
    queryFn: () => obtenerCanalApi(codCanales ?? 0),
    enabled: codCanales !== null && codCanales > 0,
    staleTime: 15_000,
  });
}

export function useCrearCanal() {
  const qc = useQueryClient();
  return useMutation<CanalFormResponse, Error, CanalFormPayload>({
    mutationFn: (payload) => crearCanalApi(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['canales'] });
    },
  });
}

export function useActualizarCanal() {
  const qc = useQueryClient();
  return useMutation<
    CanalFormResponse,
    Error,
    { codCanales: number; payload: CanalFormPayload }
  >({
    mutationFn: ({ codCanales, payload }) => actualizarCanalApi(codCanales, payload),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['canales'] });
      qc.invalidateQueries({ queryKey: ['canal', data.cod_canales] });
    },
  });
}
