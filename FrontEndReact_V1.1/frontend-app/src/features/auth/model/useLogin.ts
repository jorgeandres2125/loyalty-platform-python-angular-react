import { graciaExpiradaDeError } from '../lib/graciaExpirada';
import { temporalRequeridaDeError } from '../lib/temporalRequerida';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { loginApi, getMeApi } from './apiAuth';
import { useAuthStore } from '../../../entities/user/model/authStore';
import { useToastContext } from '../../../shared/ui/hooks/useToastContext';
import { QUERY_KEYS } from '../../../shared/config/constants';
import { navigateWithTransition } from '../../../shared/lib/viewTransition';
import type { LoginCredentials, AuthUser, OtpDesafio } from '../../../entities/user/model/types';

// AP-0012: el login resuelve a sesion establecida (ok) o a un desafio OTP.
type LoginResultado =
  | { kind: 'ok'; user: AuthUser }
  | { kind: 'otp'; desafio: OtpDesafio };

export function useLogin() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const setAuth = useAuthStore((s) => s.setAuth);
  const toast = useToastContext();

  return useMutation<LoginResultado, unknown, LoginCredentials>({
    mutationFn: async (credentials: LoginCredentials) => {
      // El backend emite la cookie de sesion HttpOnly aqui; el cliente no
      // necesita (ni debe) guardar el access_token.
      const resultado = await loginApi(credentials);
      if (resultado.kind === 'otp') {
        return { kind: 'otp', desafio: resultado.desafio };
      }
      const user = await getMeApi();
      return { kind: 'ok', user };
    },
    onSuccess: (resultado) => {
      // AP-0012: si el backend exige OTP no hay sesion todavia. Avisamos por
      // toast y el formulario muestra el enlace para ingresar el codigo.
      if (resultado.kind === 'otp') {
        toast.info(resultado.desafio.mensaje, { title: 'Verificacion requerida' });
        return;
      }
      const user = resultado.user;
      setAuth(user);
      queryClient.setQueryData([QUERY_KEYS.ME], user);
      const destino: string =
        [...(user.modulos ?? [])]
          .filter((m) => m.puede_ver && m.ruta)
          .sort((a, b) => a.orden - b.orden)[0]?.ruta ?? '/login';
      navigateWithTransition(() => navigate(destino));
    },
    onError: (error: unknown) => {
      // AP-0038 y AP-0046: contrasena vencida en gracia (409) o temporal (409).
      const temporal = temporalRequeridaDeError(error);
      if (temporal) {
        navigateWithTransition(() =>
          navigate('/cambiar-contrasena-temporal', { state: temporal }),
        );
        return;
      }
      const gracia = graciaExpiradaDeError(error);
      if (gracia) {
        navigateWithTransition(() =>
          navigate('/cambiar-contrasena-vencida', { state: gracia }),
        );
      }
    },
  });
}
