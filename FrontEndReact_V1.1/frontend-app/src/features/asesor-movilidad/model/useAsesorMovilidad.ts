import { useMutation, useQuery } from '@tanstack/react-query';
import type { AsesorMovilidadFiltros } from './types';
import {
  finalizarMovilidadApi,
  getAsesorMovilidadListApi,
  getDetalleAsesorMovilidadApi,
  getSubprogramasMovilidadApi,
  postWizardPaso1MovilidadApi,
  postWizardPaso2MovilidadApi,
  postWizardPaso3MovilidadApi,
  verificarAsesorMovilidadApi,
} from './apiAsesorMovilidad';

export function useAsesorMovilidadList(page: number, size: number, filtros?: AsesorMovilidadFiltros) {
  return useQuery({
    queryKey: ['asesor-movilidad-list', page, size, filtros],
    queryFn: () => getAsesorMovilidadListApi(page, size, filtros),
  });
}

export function useVerificarAsesorMovilidad(documento: string) {
  return useQuery({
    queryKey: ['asesor-movilidad-verificar', documento],
    queryFn: () => verificarAsesorMovilidadApi(documento),
    enabled: documento.length >= 5 && /^\d+$/.test(documento),
    retry: false,
  });
}

export function useDetalleAsesorMovilidad(documento: string | null) {
  return useQuery({
    queryKey: ['asesor-movilidad-detalle', documento],
    queryFn: () => getDetalleAsesorMovilidadApi(documento!),
    enabled: !!documento && documento.length >= 3,
  });
}

export function useSubprogramasMovilidad(cpid: number) {
  return useQuery({
    queryKey: ['asesor-movilidad-subprogramas', cpid],
    queryFn: () => getSubprogramasMovilidadApi(cpid),
    enabled: cpid > 0,
  });
}

export function useWizardPaso1Movilidad() {
  return useMutation({ mutationFn: postWizardPaso1MovilidadApi });
}

export function useWizardPaso2Movilidad() {
  return useMutation({ mutationFn: postWizardPaso2MovilidadApi });
}

export function useWizardPaso3Movilidad() {
  return useMutation({ mutationFn: postWizardPaso3MovilidadApi });
}

export function useFinalizarMovilidad() {
  return useMutation({ mutationFn: finalizarMovilidadApi });
}
