import { describe, it, expect } from 'vitest';
import { isAuthUser, isTokenResponse } from './guards';
import { makeAuthUser } from '../../../test/fixtures';

describe('isAuthUser', () => {
  it('acepta un AuthUser bien formado', () => {
    expect(isAuthUser(makeAuthUser())).toBe(true);
  });

  it('rechaza null y valores no-objeto', () => {
    expect(isAuthUser(null)).toBe(false);
    expect(isAuthUser('texto')).toBe(false);
    expect(isAuthUser(42)).toBe(false);
  });

  it('rechaza cuando falta o es de tipo erróneo un campo requerido', () => {
    expect(isAuthUser({ ...makeAuthUser(), uid: '100' })).toBe(false);
    expect(isAuthUser({ ...makeAuthUser(), tiene_incentivos: 'sí' })).toBe(false);
    const sinProperty = makeAuthUser() as Record<string, unknown>;
    delete sinProperty.email;
    expect(isAuthUser(sinProperty)).toBe(false);
  });

  it('rechaza roles que no son todos strings', () => {
    expect(isAuthUser({ ...makeAuthUser(), roles: ['comisionista', 7] })).toBe(false);
  });

  it('acepta programa null pero rechaza programa string', () => {
    expect(isAuthUser(makeAuthUser({ programa: null }))).toBe(true);
    expect(isAuthUser({ ...makeAuthUser(), programa: 'uno' })).toBe(false);
  });

  it('rechaza cuando un módulo está mal formado', () => {
    expect(isAuthUser({ ...makeAuthUser(), modulos: [{ foo: 'bar' }] })).toBe(false);
  });
});

describe('isTokenResponse', () => {
  const tokenOk = {
    access_token: 'abc.def.ghi',
    token_type: 'bearer',
    uid: 1,
    username: 'jdoe',
    email: 'jdoe@sufi.test',
    roles: ['comisionista'],
    modulos: [],
  };

  it('acepta una respuesta de token válida', () => {
    expect(isTokenResponse(tokenOk)).toBe(true);
  });

  it('rechaza access_token vacío', () => {
    expect(isTokenResponse({ ...tokenOk, access_token: '' })).toBe(false);
  });

  it('rechaza cuando roles o modulos no son arrays', () => {
    expect(isTokenResponse({ ...tokenOk, roles: 'comisionista' })).toBe(false);
    expect(isTokenResponse({ ...tokenOk, modulos: null })).toBe(false);
  });

  it('rechaza null', () => {
    expect(isTokenResponse(null)).toBe(false);
  });
});
