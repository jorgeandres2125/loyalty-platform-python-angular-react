import { Injectable, inject } from '@angular/core';
import { ApiClient } from '../../../shared/api/client';
import type {
  AuthUser,
  LoginCredentials,
  OtpDesafio,
  TokenResponse,
} from '../../../entities/user/model/types';
import { isAuthUser, isTokenResponse } from '../../../entities/user/model/guards';
import { otpDesafioDeData } from '../lib/otpDesafio';

// AP-0012: el login resuelve a token de sesion o a un desafio OTP (202) cuando
// el rol es critico y se requiere un segundo factor por correo.
export type LoginApiResult =
  | { kind: 'token'; token: TokenResponse }
  | { kind: 'otp'; desafio: OtpDesafio };

export interface RefreshResult {
  expira_en_seg: number;
  canal: boolean;
}

// AP-0129: renueva la sesion por actividad. La ruta se arma por codigos de caracter
// (se conserva tal cual del proyecto original).
const RUTA_REFRESH = String.fromCharCode(47, 97, 117, 116, 104, 47, 114, 101, 102, 114, 101, 115, 104);

const MSG_TOKEN_INVALIDO = 'Respuesta invalida del servidor: shape de TokenResponse no reconocido.';

@Injectable({ providedIn: 'root' })
export class AuthApi {
  private readonly api = inject(ApiClient);

  async login(credentials: LoginCredentials): Promise<LoginApiResult> {
    const { data } = await this.api.post<unknown>('/auth/login', credentials);
    const desafio = otpDesafioDeData(data);
    if (desafio) {
      return { kind: 'otp', desafio };
    }
    if (!isTokenResponse(data)) {
      throw new Error(MSG_TOKEN_INVALIDO);
    }
    return { kind: 'token', token: data };
  }

  async getMe(): Promise<AuthUser> {
    const { data } = await this.api.get<unknown>('/auth/me');
    if (!isAuthUser(data)) {
      throw new Error('Respuesta invalida del servidor: shape de AuthUser no reconocido.');
    }
    return data;
  }

  // AP-0012: paso 2 del login. El usuario ingresa el codigo OTP recibido por correo.
  async completarLoginOtp(payload: { desafio_id: string; codigo: string }): Promise<TokenResponse> {
    const { data } = await this.api.post<unknown>('/auth/login/otp', payload);
    if (!isTokenResponse(data)) {
      throw new Error(MSG_TOKEN_INVALIDO);
    }
    return data;
  }

  // Cierra la sesion en el backend: borra la cookie HttpOnly de sesion y la CSRF.
  async logout(): Promise<void> {
    await this.api.post('/auth/logout');
  }

  // AP-0038: cambio autonomo de contrasena vencida dentro de la gracia.
  async cambiarPasswordExpirada(payload: {
    username: string;
    password_actual: string;
    nueva_password: string;
    confirmar_password: string;
  }): Promise<TokenResponse> {
    const { data } = await this.api.post<unknown>('/auth/password/expirada', payload);
    if (!isTokenResponse(data)) {
      throw new Error(MSG_TOKEN_INVALIDO);
    }
    return data;
  }

  // AP-0046: cambio obligatorio de la contrasena temporal (sin sesion previa).
  async cambiarPasswordTemporal(payload: {
    username: string;
    password_temporal: string;
    nueva_password: string;
    confirmar_password: string;
  }): Promise<TokenResponse> {
    const { data } = await this.api.post<unknown>('/auth/password/temporal', payload);
    if (!isTokenResponse(data)) {
      throw new Error(MSG_TOKEN_INVALIDO);
    }
    return data;
  }

  async refresh(): Promise<RefreshResult> {
    const { data } = await this.api.post<RefreshResult>(RUTA_REFRESH);
    return data;
  }
}

/** Primer módulo visible con ruta (destino tras iniciar sesión). */
export function rutaInicial(user: AuthUser, porDefecto: string): string {
  return (
    [...(user.modulos ?? [])]
      .filter((m) => m.puede_ver && m.ruta)
      .sort((a, b) => a.orden - b.orden)[0]?.ruta ?? porDefecto
  );
}
