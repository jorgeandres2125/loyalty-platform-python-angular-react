import { useMutation, useQuery } from '@tanstack/react-query';
import type { AsesorConsumoFiltros } from './types';
import {
  finalizarConsumoApi,
  getAsesorConsumoListApi,
  getDetalleAsesorConsumoApi,
  getSubprogramasConsumoApi,
  postWizardPaso1ConsumoApi,
  postWizardPaso3ConsumoApi,
  verificarAsesorConsumoApi,
} from './apiAsesorConsumo';

export function useAsesorConsumoList(page: number, size: number, filtros?: AsesorConsumoFiltros) {
  return useQuery({
    queryKey: ['asesor-consumo-list', page, size, filtros],
    queryFn: () => getAsesorConsumoListApi(page, size, filtros),
  });
}

export function useVerificarAsesorConsumo(documento: string) {
  return useQuery({
    queryKey: ['asesor-consumo-verificar', documento],
    queryFn: () => verificarAsesorConsumoApi(documento),
    enabled: documento.length >= 5 && /^\d+$/.test(documento),
    retry: false,
  });
}

export function useDetalleAsesorConsumo(documento: string | null) {
  return useQuery({
    queryKey: ['asesor-consumo-detalle', documento],
    queryFn: () => getDetalleAsesorConsumoApi(documento!),
    enabled: !!documento && documento.length >= 3,
  });
}

export function useSubprogramasConsumo(cpid: number) {
  return useQuery({
    queryKey: ['asesor-consumo-subprogramas', cpid],
    queryFn: () => getSubprogramasConsumoApi(cpid),
    enabled: cpid > 0,
  });
}

export function useWizardPaso1Consumo() {
  return useMutation({ mutationFn: postWizardPaso1ConsumoApi });
}

export function useWizardPaso3Consumo() {
  return useMutation({ mutationFn: postWizardPaso3ConsumoApi });
}

export function useFinalizarConsumo() {
  return useMutation({ mutationFn: finalizarConsumoApi });
}
