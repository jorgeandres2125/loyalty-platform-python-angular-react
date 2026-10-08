import { useCallback, useMemo } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../../entities/user/model/authStore';
import { putMiContacto, putMiEmocional, putMiTributario } from './apiPerfilSelf';
import { useMiContacto, useMiEmocional, useMiTributario } from './usePerfilSelf';
import type { PerfilContacto } from './types';

// Adaptadores self-service que replican la interfaz de los hooks de asesor
// (useDetalleAsesorMovilidad / useWizardPasoNMovilidad) para que la pagina del
// perfil propio (PerfilMovilidadPage) consuma los endpoints /me/perfil-* del
// propio comisionista, en vez de los endpoints de staff /asesor-movilidad/* que
// exigen el permiso MOVILIDAD_ASESORES_GESTIONAR (un comisionista no lo tiene:
// respondia 403). El backend resuelve el numero_documento desde el JWT.

interface DetalleMovilidadSelf {
  contacto: unknown;
  tributario: unknown;
  emocional: unknown;
}

interface DetalleMovilidadResult {
  data: DetalleMovilidadSelf | undefined;
  isLoading: boolean;
  refetch: () => void;
}

export function useMiDetalleMovilidad(): DetalleMovilidadResult {
  const contacto = useMiContacto();
  const tributario = useMiTributario();
  const emocional = useMiEmocional();

  const isLoading: boolean =
    contacto.isLoading || tributario.isLoading || emocional.isLoading;
  const settled: boolean =
    contacto.isSuccess || tributario.isSuccess || emocional.isSuccess;

  // La identidad de `data` DEBE ser estable entre renders: la pagina tiene efectos con
  // dependencia [detalle.data] que hacen setState. Un objeto literal nuevo en cada render
  // los dispararia siempre -> setState -> re-render -> bucle infinito ("Maximum update
  // depth exceeded"). Las referencias .data de react-query si son estables, asi que
  // memorizamos sobre ellas y solo cambia cuando los datos cambian de verdad.
  const data: DetalleMovilidadSelf | undefined = useMemo(
    () =>
      settled && !isLoading
        ? {
            contacto: contacto.data ?? null,
            tributario: tributario.data ?? null,
            emocional: emocional.data ?? null,
          }
        : undefined,
    [settled, isLoading, contacto.data, tributario.data, emocional.data],
  );

  // Estable por el mismo motivo: se pasa a manejadores y podria acabar en un array de
  // dependencias. Las funciones refetch de react-query ya son estables, pero hay que
  // extraerlas a consts para poder depender de ellas (y no del objeto de la query, que
  // cambia de identidad en cada render y volveria a romper la estabilidad).
  const refetchContacto = contacto.refetch;
  const refetchTributario = tributario.refetch;
  const refetchEmocional = emocional.refetch;
  const refetch = useCallback((): void => {
    void refetchContacto();
    void refetchTributario();
    void refetchEmocional();
  }, [refetchContacto, refetchTributario, refetchEmocional]);

  return { data, isLoading, refetch };
}

function _miDocumento(): string {
  return useAuthStore.getState().user?.username ?? '';
}

export function useGuardarMiContactoMovilidad() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Record<string, unknown>): Promise<{ numero_documento: string }> => {
      await putMiContacto(payload as unknown as Omit<PerfilContacto, 'numero_documento'>);
      return { numero_documento: _miDocumento() };
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['perfil-self'] });
    },
  });
}

export function useGuardarMiTributarioMovilidad() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Record<string, unknown>): Promise<{ numero_documento: string }> => {
      await putMiTributario(payload);
      return { numero_documento: _miDocumento() };
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['perfil-self'] });
    },
  });
}

export function useGuardarMiEmocionalMovilidad() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: Record<string, unknown>): Promise<{ numero_documento: string }> => {
      await putMiEmocional(payload);
      return { numero_documento: _miDocumento() };
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['perfil-self'] });
    },
  });
}
