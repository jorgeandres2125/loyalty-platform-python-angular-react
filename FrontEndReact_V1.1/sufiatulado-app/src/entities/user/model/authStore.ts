import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ROLES } from '../../../shared/config/constants';
import type { AccionModulo, AuthUser, ModuloPermiso } from './types';

// Medida A (plan de remediación): el JWT vive SOLO en una cookie HttpOnly emitida
// por el backend; el cliente nunca lo almacena ni lo lee (mitiga XSS, AP-0093/0099).
// La sesión se considera activa por la presencia de `user`; el backend es la fuente
// de verdad y un 401 fuerza el regreso a /login (ver shared/api/client.ts).
interface AuthState {
  user: AuthUser | null;
  sapinToken: string | null;

  setAuth: (user: AuthUser) => void;
  setSapinToken: (token: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
  hasRole: (role: string) => boolean;
  puedeAcceder: (moduleCode: string, accion?: AccionModulo) => boolean;
  modulosVisibles: () => ModuloPermiso[];
  canAccessSapin: () => boolean;
}

const FLAG_POR_ACCION: Record<AccionModulo, keyof ModuloPermiso> = {
  ver: 'puede_ver',
  crear: 'puede_crear',
  editar: 'puede_editar',
  eliminar: 'puede_eliminar',
  exportar: 'puede_exportar',
  aprobar: 'puede_aprobar',
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      sapinToken: null,

      setAuth: (user: AuthUser) => {
        set({ user });
      },

      setSapinToken: (sapinToken: string) => set({ sapinToken }),

      logout: () => {
        // El borrado de la cookie de sesión lo hace el backend (POST /auth/logout).
        // clearStorage() elimina por completo la clave 'sufi-auth' de localStorage
        // (set solo actualiza el valor a null, la clave persiste; clearStorage la elimina).
        set({ user: null, sapinToken: null });
        useAuthStore.persist.clearStorage();
      },

      isAuthenticated: () => get().user !== null,

      hasRole: (role: string) => {
        const { user } = get();
        return user?.roles.includes(role) ?? false;
      },

      puedeAcceder: (moduleCode: string, accion: AccionModulo = 'ver') => {
        const { user } = get();
        if (!user) return false;
        if (user.roles.includes(ROLES.ADMIN)) return true;
        const modulo = user.modulos?.find((mod) => mod.module_code === moduleCode);
        if (!modulo) return false;
        return Boolean(modulo[FLAG_POR_ACCION[accion]]);
      },

      modulosVisibles: () => {
        const { user } = get();
        if (!user) return [];
        return [...user.modulos]
          .filter((modulo) => modulo.puede_ver)
          .sort((a, b) => a.orden - b.orden);
      },

      canAccessSapin: () => {
        const { user } = get();
        if (!user) return false;
        const sapinRoles = [ROLES.COMISIONISTA, ROLES.COMISIONISTA_CONSUMO];
        return (
          sapinRoles.some((role) => user.roles.includes(role)) &&
          user.tiene_incentivos
        );
      },
    }),
    {
      name: 'sufi-auth',
      // Solo se persiste `user` (nombre/roles/módulos), que NO es el secreto de sesión.
      // El token de sesión nunca se guarda en el cliente (vive en la cookie HttpOnly).
      partialize: (state) => ({
        user: state.user,
      }),
    },
  ),
);
