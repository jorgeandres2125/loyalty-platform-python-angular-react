import { describe, it, expect } from 'vitest';
import { isAuthUser } from '../../../entities/user/model/guards';
import { makeAuthUser } from '../../../test/fixtures';

describe('isAuthUser con password_aviso (AP-0037)', () => {
  it('acepta un usuario sin el campo password_aviso', () => {
    expect(isAuthUser(makeAuthUser())).toBe(true);
  });

  it('acepta password_aviso en null', () => {
    expect(isAuthUser({ ...makeAuthUser(), password_aviso: null })).toBe(true);
  });

  it('acepta un password_aviso bien formado', () => {
    const user = {
      ...makeAuthUser(),
      password_aviso: { dias_restantes: 7, fecha_expiracion: '2026-09-30' },
    };
    expect(isAuthUser(user)).toBe(true);
  });

  it('rechaza un password_aviso mal formado', () => {
    const user = {
      ...makeAuthUser(),
      password_aviso: { dias_restantes: 'siete' },
    };
    expect(isAuthUser(user)).toBe(false);
  });
});
