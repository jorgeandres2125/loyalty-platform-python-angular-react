import { Suspense, useCallback, useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Outlet } from 'react-router-dom';
import { Topbar } from './Topbar';
import { LoadingSpinner } from '../../shared/ui/components/LoadingSpinner';
import { IdleWarningModal } from '../../shared/ui/IdleWarningModal';
import { getMeApi, logoutApi, refreshApi } from '../../features/auth/model/apiAuth';
import { useAuthStore } from '../../entities/user/model/authStore';
import { usePasswordExpiryToast } from '../../features/password-expiry/model/usePasswordExpiryToast';
import { useIdleTimeout } from '../../shared/lib/useIdleTimeout';
import { IDLE_WARNING_MS, limiteInactividadMs } from '../../shared/lib/idlePolicy';
import { limpiarSesionLocal } from '../../shared/lib/limpiarSesionLocal';

export function AppLayout() {
  const setAuth = useAuthStore((s) => s.setAuth);
  const queryClient = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const [avisoVisible, setAvisoVisible] = useState(false);
  const [segundosRestantes, setSegundosRestantes] = useState(60);

  useEffect(() => {
    getMeApi()
      .then((u) => setAuth(u))
      .catch(() => undefined);
  }, [setAuth]);

  usePasswordExpiryToast();

  const roles = user?.roles ?? [];
  const idleMs = limiteInactividadMs(roles);

  const cerrarSesion = useCallback(() => {
    setAvisoVisible(false);
    // AP-0132: al cerrar por inactividad se descartan tambien los datos locales.
    logoutApi()
      .catch(() => undefined)
      .finally(() => limpiarSesionLocal(queryClient));
  }, [queryClient]);

  const continuarSesion = useCallback(() => {
    setAvisoVisible(false);
    refreshApi().catch(() => cerrarSesion());
  }, [cerrarSesion]);

  useEffect(() => {
    if (!avisoVisible) return;
    setSegundosRestantes(60);
    const id = setInterval(() => {
      setSegundosRestantes((s) => (s > 0 ? s - 1 : 0));
    }, 1000);
    return () => clearInterval(id);
  }, [avisoVisible]);

  // AP-0132: expiracion proactiva. El backend expone session_expires_at (no secreto) en
  // auth/me; al alcanzarlo se descartan los datos locales sin leer el token (HttpOnly).
  const sessionExpiresAt = user?.session_expires_at ?? null;
  useEffect(() => {
    if (!sessionExpiresAt) return;
    const restanteMs = new Date(sessionExpiresAt).getTime() - Date.now();
    if (restanteMs <= 0) {
      limpiarSesionLocal(queryClient);
      return;
    }
    const id = setTimeout(() => limpiarSesionLocal(queryClient), restanteMs);
    return () => clearTimeout(id);
  }, [sessionExpiresAt, queryClient]);

  useIdleTimeout({
    idleMs,
    warningMs: IDLE_WARNING_MS,
    active: user !== null,
    onWarning: () => setAvisoVisible(true),
    onTimeout: cerrarSesion,
    onActivity: () => {
      refreshApi().catch(() => undefined);
    },
  });

  return (
    <div className="app-shell">
      <Topbar />
      <main className="app-main">
        <Suspense fallback={<LoadingSpinner fullPage />}>
          <Outlet />
        </Suspense>
      </main>
      <IdleWarningModal
        show={avisoVisible}
        segundosRestantes={segundosRestantes}
        onContinuar={continuarSesion}
        onCerrar={cerrarSesion}
      />
    </div>
  );
}