import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';

export interface Departamento {
  did: number;
  pid: number;
  departamento: string;
}

export interface Ciudad {
  cid: number;
  did: number;
  ciudad: string;
}

async function getDepartamentosApi(): Promise<Departamento[]> {
  const { data } = await apiClient.get<Departamento[]>('/ubicaciones/departamentos');
  return data;
}

async function getCiudadesApi(departamentoId: number): Promise<Ciudad[]> {
  const { data } = await apiClient.get<Ciudad[]>(`/ubicaciones/ciudades/${departamentoId}`);
  return data;
}

export function useDepartamentos() {
  return useQuery({
    queryKey: ['departamentos'],
    queryFn: getDepartamentosApi,
    staleTime: Infinity,
  });
}

export function useCiudades(departamentoId: number | null) {
  return useQuery({
    queryKey: ['ciudades', departamentoId],
    queryFn: () => getCiudadesApi(departamentoId!),
    enabled: departamentoId !== null,
    staleTime: Infinity,
  });
}
