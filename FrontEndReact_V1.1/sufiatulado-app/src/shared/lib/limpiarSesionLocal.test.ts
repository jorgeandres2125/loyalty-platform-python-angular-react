import { describe, it, expect, beforeEach, vi } from 'vitest';
import type { QueryClient } from '@tanstack/react-query';
import { limpiarSesionLocal, limpiarAlmacenamientoSesion } from './limpiarSesionLocal';
import { useAuthStore } from '../../entities/user/model/authStore';

beforeEach(() => {
  localStorage.clear();
  sessionStorage.clear();
});

describe('limpiarAlmacenamientoSesion', () => {
  it('borra las claves sufi- de localStorage y todo sessionStorage, conservando otras', () => {
    localStorage.setItem('sufi-auth', '{"user":1}');
    localStorage.setItem('tema', 'oscuro');
    sessionStorage.setItem('sufi-pwd-aviso-1', '1');

    limpiarAlmacenamientoSesion();

    expect(localStorage.getItem('sufi-auth')).toBeNull();
    expect(localStorage.getItem('tema')).toBe('oscuro');
    expect(sessionStorage.getItem('sufi-pwd-aviso-1')).toBeNull();
  });
});

describe('limpiarSesionLocal', () => {
  it('limpia el cache de React Query, el store de auth y el almacenamiento', () => {
    const clear = vi.fn();
    const qc = { clear } as unknown as QueryClient;
    useAuthStore.getState().setAuth({
      uid: 1,
      username: 'u',
      email: 'e@sufi.co',
      roles: [],
      tiene_incentivos: false,
      programa: null,
      modulos: [],
    });
    localStorage.setItem('sufi-auth', 'x');

    limpiarSesionLocal(qc);

    expect(clear).toHaveBeenCalledOnce();
    expect(useAuthStore.getState().user).toBeNull();
    expect(localStorage.getItem('sufi-auth')).toBeNull();
  });
});