import type { QueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../entities/user/model/authStore';

// AP-0132: prefijo de las claves de almacenamiento propias de la app. Al cerrar sesion
// se descartan; las preferencias no sensibles (idioma, tema) usarian otros prefijos y
// se conservan.
const PREFIJO_APP = 'sufi-';

// AP-0132: limpia SOLO el almacenamiento del navegador (localStorage con prefijo de la
// app, sessionStorage completo y Cache API best-effort). Es segura de invocar desde el
// interceptor HTTP (ambito de modulo, sin React), tipicamente antes de un
// window.location.replace, que ademas destruye el estado en memoria (React Query, Zustand).
export function limpiarAlmacenamientoSesion(): void {
  try {
    const claves: string[] = [];
    for (let i = 0; i < window.localStorage.length; i += 1) {
      const clave = window.localStorage.key(i);
      if (clave && clave.startsWith(PREFIJO_APP)) claves.push(clave);
    }
    claves.forEach((clave) => window.localStorage.removeItem(clave));
  } catch {
    // Modo privado o almacenamiento no disponible: no hay nada que limpiar.
  }
  try {
    window.sessionStorage.clear();
  } catch {
    // idem: sessionStorage puede no estar disponible.
  }
  if (typeof caches !== 'undefined') {
    void caches
      .keys()
      .then((llaves) =>
        Promise.all(
          llaves.filter((n) => n.startsWith(PREFIJO_APP)).map((n) => caches.delete(n)),
        ),
      )
      .catch(() => undefined);
  }
}

// AP-0132: descarte COMPLETO de los datos de sesion del lado cliente. Se invoca en el
// cierre manual, en la expiracion automatica y ante un 401. Combina el estado en memoria
// (cache de React Query y store de Zustand) con el almacenamiento del navegador. Idempotente.
export function limpiarSesionLocal(queryClient: QueryClient): void {
  queryClient.clear();
  useAuthStore.getState().logout();
  limpiarAlmacenamientoSesion();
}