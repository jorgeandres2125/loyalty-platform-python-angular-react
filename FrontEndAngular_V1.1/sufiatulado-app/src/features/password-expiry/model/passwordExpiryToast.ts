import { effect, inject, untracked } from '@angular/core';
import { AuthStore } from '../../../entities/user/model/authStore';
import { ToastService } from '../../../shared/ui/toast/toast.service';
import { mensajeExpiracionPassword } from '../lib/mensajeExpiracion';

const PREFIJO_GUARDIA = 'sufi-pwd-aviso';

/**
 * AP-0037: aviso de vencimiento una sola vez por sesion (guardia en sessionStorage).
 * Equivalente al hook `usePasswordExpiryToast`; llamar en un contexto de inyección.
 */
export function passwordExpiryToast(): void {
  const auth = inject(AuthStore);
  const toast = inject(ToastService);

  effect(() => {
    const user = auth.user();
    const aviso = user?.password_aviso;
    if (!user || !aviso) return;
    const clave = `${PREFIJO_GUARDIA}:${user.uid}`;
    if (sessionStorage.getItem(clave)) return;
    sessionStorage.setItem(clave, '1');
    untracked(() => toast.warning(mensajeExpiracionPassword(aviso.dias_restantes)));
  });
}
