import { computed, inject, type Signal } from '@angular/core';
import { QueryClient, injectMutation } from '@tanstack/angular-query-experimental';
import { PerfilSelfApi } from './apiPerfilSelf';
import { injectMiContacto, injectMiEmocional, injectMiTributario } from './queries';
import type { PerfilContacto } from './types';

// Adaptadores self-service que replican la interfaz de los queries de asesor
// (injectDetalleAsesorMovilidad / injectWizardPasoNMovilidad) para que la pagina del
// perfil propio (PerfilMovilidadPage) consuma los endpoints /me/perfil-* del
// propio comisionista, en vez de los endpoints de staff /asesor-movilidad/* que
// exigen el permiso MOVILIDAD_ASESORES_GESTIONAR (un comisionista no lo tiene:
// respondia 403). El backend resuelve el numero_documento desde el JWT.

export interface DetalleMovilidadSelf {
  contacto: unknown;
  tributario: unknown;
  emocional: unknown;
}

export interface DetalleMovilidadResult {
  data: Signal<DetalleMovilidadSelf | undefined>;
  isLoading: Signal<boolean>;
  refetch: () => void;
}

function mismoDetalle(
  a: DetalleMovilidadSelf | undefined,
  b: DetalleMovilidadSelf | undefined,
): boolean {
  if (a === b) return true;
  if (a === undefined || b === undefined) return false;
  return a.contacto === b.contacto && a.tributario === b.tributario && a.emocional === b.emocional;
}

export function injectMiDetalleMovilidad(): DetalleMovilidadResult {
  const contacto = injectMiContacto();
  const tributario = injectMiTributario();
  const emocional = injectMiEmocional();

  const isLoading = computed<boolean>(
    () => contacto.isLoading() || tributario.isLoading() || emocional.isLoading(),
  );
  const settled = computed<boolean>(
    () => contacto.isSuccess() || tributario.isSuccess() || emocional.isSuccess(),
  );

  // `computed` mantiene la identidad estable mientras los datos no cambien (lo que en
  // React exigía useMemo para evitar bucles de efectos).
  const data = computed<DetalleMovilidadSelf | undefined>(
    () =>
      settled() && !isLoading()
        ? {
            contacto: contacto.data() ?? null,
            tributario: tributario.data() ?? null,
            emocional: emocional.data() ?? null,
          }
        : undefined,
    { equal: mismoDetalle },
  );

  const refetch = (): void => {
    void contacto.refetch();
    void tributario.refetch();
    void emocional.refetch();
  };

  return { data, isLoading, refetch };
}

export function injectGuardarMiContactoMovilidad() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  return injectMutation(() => ({
    mutationFn: async (payload: Record<string, unknown>): Promise<{ numero_documento: string }> => {
      await api.putMiContacto(payload as unknown as Omit<PerfilContacto, 'numero_documento'>);
      return { numero_documento: api.miDocumento() };
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['perfil-self'] });
    },
  }));
}

export function injectGuardarMiTributarioMovilidad() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  return injectMutation(() => ({
    mutationFn: async (payload: Record<string, unknown>): Promise<{ numero_documento: string }> => {
      await api.putMiTributario(payload);
      return { numero_documento: api.miDocumento() };
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['perfil-self'] });
    },
  }));
}

export function injectGuardarMiEmocionalMovilidad() {
  const api = inject(PerfilSelfApi);
  const qc = inject(QueryClient);
  return injectMutation(() => ({
    mutationFn: async (payload: Record<string, unknown>): Promise<{ numero_documento: string }> => {
      await api.putMiEmocional(payload);
      return { numero_documento: api.miDocumento() };
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['perfil-self'] });
    },
  }));
}
