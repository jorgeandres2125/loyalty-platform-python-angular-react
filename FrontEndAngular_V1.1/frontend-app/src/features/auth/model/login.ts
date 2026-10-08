import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { QueryClient, injectMutation } from '@tanstack/angular-query-experimental';
import { graciaExpiradaDeError } from '../lib/graciaExpirada';
import { temporalRequeridaDeError } from '../lib/temporalRequerida';
import { AuthApi, rutaInicial } from './apiAuth';
import { AuthStore } from '../../../entities/user/model/authStore';
import { ToastService } from '../../../shared/ui/toast/toast.service';
import { QUERY_KEYS } from '../../../shared/config/constants';
import { navigateWithTransition } from '../../../shared/lib/viewTransition';
import type { AuthUser, LoginCredentials, OtpDesafio } from '../../../entities/user/model/types';

// AP-0012: el login resuelve a sesion establecida (ok) o a un desafio OTP.
export type LoginResultado = { kind: 'ok'; user: AuthUser } | { kind: 'otp'; desafio: OtpDesafio };

/** Mutación de login (equivalente al hook `useLogin`). */
export function injectLogin() {
  const router = inject(Router);
  const queryClient = inject(QueryClient);
  const auth = inject(AuthStore);
  const authApi = inject(AuthApi);
  const toast = inject(ToastService);

  return injectMutation<LoginResultado, unknown, LoginCredentials>(() => ({
    mutationFn: async (credentials: LoginCredentials): Promise<LoginResultado> => {
      // El backend emite la cookie de sesion HttpOnly aqui; el cliente no
      // necesita (ni debe) guardar el access_token.
      const resultado = await authApi.login(credentials);
      if (resultado.kind === 'otp') {
        return { kind: 'otp', desafio: resultado.desafio };
      }
      const user = await authApi.getMe();
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
      auth.setAuth(user);
      queryClient.setQueryData([QUERY_KEYS.ME], user);
      const destino: string = rutaInicial(user, '/login');
      navigateWithTransition(() => void router.navigateByUrl(destino));
    },
    onError: (error: unknown) => {
      // AP-0038 y AP-0046: contrasena vencida en gracia (409) o temporal (409).
      const temporal = temporalRequeridaDeError(error);
      if (temporal) {
        navigateWithTransition(
          () => void router.navigate(['/cambiar-contrasena-temporal'], { state: temporal }),
        );
        return;
      }
      const gracia = graciaExpiradaDeError(error);
      if (gracia) {
        navigateWithTransition(
          () => void router.navigate(['/cambiar-contrasena-vencida'], { state: gracia }),
        );
      }
    },
  }));
}
