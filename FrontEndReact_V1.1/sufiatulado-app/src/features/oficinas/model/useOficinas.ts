import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  actualizarOficinaApi,
  crearOficinaApi,
  listarOficinasActivasApi,
  listarOficinasApi,
  obtenerOficinaApi,
} from './apiOficinas';
import type {
  OficinaActivaItem,
  OficinaFormPayload,
  OficinaFormResponse,
  OficinaListQuery,
  OficinaListResponse,
} from './types';

export function useOficinas(query: OficinaListQuery) {
  return useQuery<OficinaListResponse>({
    queryKey: ['oficinas', query],
    queryFn: () => listarOficinasApi(query),
    staleTime: 30_000,
  });
}

export function useOficinasActivas() {
  return useQuery<OficinaActivaItem[]>({
    queryKey: ['oficinas-activas'],
    queryFn: listarOficinasActivasApi,
    staleTime: 5 * 60_000,
  });
}

export function useOficina(codOficinas: number | null) {
  return useQuery<OficinaFormResponse>({
    queryKey: ['oficina', codOficinas],
    queryFn: () => obtenerOficinaApi(codOficinas ?? 0),
    enabled: codOficinas !== null && codOficinas > 0,
    staleTime: 15_000,
  });
}

export function useCrearOficina() {
  const qc = useQueryClient();
  return useMutation<OficinaFormResponse, Error, OficinaFormPayload>({
    mutationFn: (payload) => crearOficinaApi(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['oficinas'] });
    },
  });
}

export function useActualizarOficina() {
  const qc = useQueryClient();
  return useMutation<
    OficinaFormResponse,
    Error,
    { codOficinas: number; payload: OficinaFormPayload }
  >({
    mutationFn: ({ codOficinas, payload }) => actualizarOficinaApi(codOficinas, payload),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ['oficinas'] });
      qc.invalidateQueries({ queryKey: ['oficina', data.cod_oficinas] });
    },
  });
}
