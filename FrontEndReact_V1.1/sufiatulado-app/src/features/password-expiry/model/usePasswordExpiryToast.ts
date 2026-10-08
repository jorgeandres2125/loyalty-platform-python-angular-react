import { useEffect } from 'react';
import { useAuthStore } from '../../../entities/user/model/authStore';
import { useToastContext } from '../../../shared/ui/hooks/useToastContext';
import { mensajeExpiracionPassword } from '../lib/mensajeExpiracion';

const PREFIJO_GUARDIA = 'sufi-pwd-aviso';

// AP-0037: aviso de vencimiento una sola vez por sesion (guardia en sessionStorage).
export function usePasswordExpiryToast(): void {
  const user = useAuthStore((s) => s.user);
  const { warning } = useToastContext();

  useEffect(() => {
    const aviso = user?.password_aviso;
    if (!user || !aviso) return;
    const clave = `${PREFIJO_GUARDIA}:${user.uid}`;
    if (sessionStorage.getItem(clave)) return;
    sessionStorage.setItem(clave, '1');
    warning(mensajeExpiracionPassword(aviso.dias_restantes));
  }, [user, warning]);
}
