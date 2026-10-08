import { inject } from '@angular/core';
import { QueryClient, injectMutation, injectQuery } from '@tanstack/angular-query-experimental';
import { AdminAsignacionesApi, type ListarParams } from './apiAdminAsignaciones';
import type { RolAsignableItem, RolDeUsuarioItem, UsuariosPaginaResponse } from './types';

const QK_ROLES = 'admin-asignaciones-roles' as const;
const QK_USUARIOS_ROL = 'admin-asignaciones-usuarios-rol' as const;
const QK_BUSCAR = 'admin-asignaciones-buscar' as const;
const QK_ROLES_USUARIO = 'admin-asignaciones-roles-usuario' as const;

export function injectRolesAsignables() {
  const api = inject(AdminAsignacionesApi);
  return injectQuery<RolAsignableItem[]>(() => ({
    queryKey: [QK_ROLES],
    queryFn: () => api.listarRolesAsignables(),
    staleTime: 60_000,
  }));
}

export function injectUsuariosDeRol(rid: () => number | null, params: () => ListarParams) {
  const api = inject(AdminAsignacionesApi);
  return injectQuery<UsuariosPaginaResponse>(() => {
    const r = rid();
    const p = params();
    return {
      queryKey: [QK_USUARIOS_ROL, r, p],
      queryFn: () => api.listarUsuariosDeRol(r as number, p),
      enabled: r !== null,
      staleTime: 15_000,
    };
  });
}

export function injectBuscarUsuarios(params: () => ListarParams, enabled: () => boolean) {
  const api = inject(AdminAsignacionesApi);
  return injectQuery<UsuariosPaginaResponse>(() => {
    const p = params();
    return {
      queryKey: [QK_BUSCAR, p],
      queryFn: () => api.buscarUsuarios(p),
      enabled: enabled(),
      staleTime: 15_000,
    };
  });
}

export function injectRolesDeUsuario(uid: () => number | null) {
  const api = inject(AdminAsignacionesApi);
  return injectQuery<RolDeUsuarioItem[]>(() => {
    const u = uid();
    return {
      queryKey: [QK_ROLES_USUARIO, u],
      queryFn: () => api.obtenerRolesDeUsuario(u as number),
      enabled: u !== null,
      staleTime: 15_000,
    };
  });
}

function invalidarAsignaciones(qc: QueryClient): void {
  void qc.invalidateQueries({ queryKey: [QK_USUARIOS_ROL] });
  void qc.invalidateQueries({ queryKey: [QK_ROLES_USUARIO] });
  void qc.invalidateQueries({ queryKey: [QK_BUSCAR] });
}

export function injectAsignarRol() {
  const api = inject(AdminAsignacionesApi);
  const qc = inject(QueryClient);
  return injectMutation<void, Error, { uid: number; rid: number }>(() => ({
    mutationFn: ({ uid, rid }) => api.asignarRol(uid, rid),
    onSuccess: () => invalidarAsignaciones(qc),
  }));
}

export function injectQuitarRol() {
  const api = inject(AdminAsignacionesApi);
  const qc = inject(QueryClient);
  return injectMutation<void, Error, { uid: number; rid: number }>(() => ({
    mutationFn: ({ uid, rid }) => api.quitarRol(uid, rid),
    onSuccess: () => invalidarAsignaciones(qc),
  }));
}
