import { apiClient } from '../../../shared/api/client';
import type { DepartamentoItem, CiudadItem } from './types';

export async function listarDepartamentosApi(): Promise<DepartamentoItem[]> {
  const { data } = await apiClient.get<{ did: number; pid: number; departamento: string }[]>(
    '/ubicaciones/departamentos',
  );
  return data.map((dep) => ({ did: dep.did, departamento: dep.departamento }));
}

export async function listarCiudadesApi(did: number): Promise<CiudadItem[]> {
  const { data } = await apiClient.get<CiudadItem[]>(`/ubicaciones/ciudades/${did}`);
  return data;
}
