import { useQuery } from '@tanstack/react-query';
import { listarCiudadesApi, listarDepartamentosApi } from './apiUbicaciones';
import type { CiudadItem, DepartamentoItem } from './types';

export function useDepartamentos() {
  return useQuery<DepartamentoItem[]>({
    queryKey: ['departamentos'],
    queryFn: listarDepartamentosApi,
    staleTime: 10 * 60_000,
  });
}

export function useCiudades(did: number | null) {
  return useQuery<CiudadItem[]>({
    queryKey: ['ciudades', did],
    queryFn: () => listarCiudadesApi(did!),
    enabled: did !== null,
    staleTime: 5 * 60_000,
  });
}
