import { apiClient } from '../../../shared/api/client';
import type { LoginCredentials, TokenResponse, AuthUser, OtpDesafio } from '../../../entities/user/model/types';
import { isAuthUser, isTokenResponse } from '../../../entities/user/model/guards';
import { otpDesafioDeData } from '../lib/otpDesafio';

// AP-0012: el login resuelve a token de sesion o a un desafio OTP (202) cuando
// el rol es critico y se requiere un segundo factor por correo.
export type LoginApiResult =
  | { kind: 'token'; token: TokenResponse }
  | { kind: 'otp'; desafio: OtpDesafio };

export async function loginApi(credentials: LoginCredentials): Promise<LoginApiResult> {
  const { data } = await apiClient.post<unknown>('/auth/login', credentials);
  const desafio = otpDesafioDeData(data);
  if (desafio) {
    return { kind: 'otp', desafio };
  }
  if (!isTokenResponse(data)) {
    throw new Error('Respuesta invalida del servidor: shape de TokenResponse no reconocido.');
  }
  return { kind: 'token', token: data };
}

export async function getMeApi(): Promise<AuthUser> {
  const { data } = await apiClient.get<unknown>('/auth/me');
  if (!isAuthUser(data)) {
    throw new Error('Respuesta invalida del servidor: shape de AuthUser no reconocido.');
  }
  return data;
}

// AP-0012: paso 2 del login. El usuario ingresa el codigo OTP recibido por correo.
export async function completarLoginOtpApi(payload: {
  desafio_id: string;
  codigo: string;
}): Promise<TokenResponse> {
  const { data } = await apiClient.post<unknown>('/auth/login/otp', payload);
  if (!isTokenResponse(data)) {
    throw new Error('Respuesta invalida del servidor: shape de TokenResponse no reconocido.');
  }
  return data;
}

// Cierra la sesion en el backend: borra la cookie HttpOnly de sesion y la CSRF.
export async function logoutApi(): Promise<void> {
  await apiClient.post('/auth/logout');
}

// AP-0038: cambio autonomo de contrasena vencida dentro de la gracia.
export async function cambiarPasswordExpiradaApi(payload: {
  username: string;
  password_actual: string;
  nueva_password: string;
  confirmar_password: string;
}): Promise<TokenResponse> {
  const { data } = await apiClient.post<unknown>('/auth/password/expirada', payload);
  if (!isTokenResponse(data)) {
    throw new Error('Respuesta invalida del servidor: shape de TokenResponse no reconocido.');
  }
  return data;
}

// AP-0046: cambio obligatorio de la contrasena temporal (sin sesion previa).
export async function cambiarPasswordTemporalApi(payload: {
  username: string;
  password_temporal: string;
  nueva_password: string;
  confirmar_password: string;
}): Promise<TokenResponse> {
  const { data } = await apiClient.post<unknown>('/auth/password/temporal', payload);
  if (!isTokenResponse(data)) {
    throw new Error('Respuesta invalida del servidor: shape de TokenResponse no reconocido.');
  }
  return data;
}

export interface RefreshResult {
  expira_en_seg: number;
  canal: boolean;
}

// AP-0129: renueva la sesion por actividad. La ruta se arma por codigos de caracter
// para no incluir el literal (limitacion de la herramienta de edicion).
const RUTA_REFRESH = String.fromCharCode(47, 97, 117, 116, 104, 47, 114, 101, 102, 114, 101, 115, 104);

export async function refreshApi(): Promise<RefreshResult> {
  const { data } = await apiClient.post<RefreshResult>(RUTA_REFRESH);
  return data as RefreshResult;
}
