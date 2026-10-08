import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarEjecutivoApi,
  crearEjecutivoApi,
  listarEjecutivosApi,
  obtenerEjecutivoApi,
} from './apiEjecutivos';
import type {
  EjecutivoFormPayload,
  EjecutivoFormResponse,
  EjecutivoListQuery,
  EjecutivoListResponse,
} from './types';

export function useEjecutivos(query: EjecutivoListQuery) {
  return useQuery<EjecutivoListResponse>({
    queryKey: ['ejecutivos', query],
    queryFn: () => listarEjecutivosApi(query),
    staleTime: 30_000,
  });
}

export function useEjecutivo(id: number | null) {
  return useQuery<EjecutivoFormResponse>({
    queryKey: ['ejecutivo', id],
    queryFn: () => obtenerEjecutivoApi(id ?? 0),
    enabled: id !== null && id > 0,
    staleTime: 15_000,
  });
}

export function useCrearEjecutivo() {
  const qc = useQueryClient();
  return useMutation<EjecutivoFormResponse, Error, EjecutivoFormPayload>({
    mutationFn: (payload) => crearEjecutivoApi(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ejecutivos'] });
    },
  });
}

export function useActualizarEjecutivo() {
  const qc = useQueryClient();
  return useMutation<
    EjecutivoFormResponse,
    Error,
    { id: number; payload: EjecutivoFormPayload }
  >({
    mutationFn: ({ id, payload }) => actualizarEjecutivoApi(id, payload),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['ejecutivos'] });
      qc.invalidateQueries({ queryKey: ['ejecutivo', data.id] });
    },
  });
}
