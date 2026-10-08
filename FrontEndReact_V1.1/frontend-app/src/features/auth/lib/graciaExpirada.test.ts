import { describe, it, expect } from 'vitest';
import { AxiosError, AxiosHeaders } from 'axios';
import { graciaExpiradaDeError } from './graciaExpirada';

function axiosConRespuesta(status: number, data: unknown): AxiosError {
  const err = new AxiosError('fallo');
  err.response = {
    status,
    data,
    statusText: '',
    headers: {},
    config: { headers: new AxiosHeaders() },
  };
  return err;
}

describe('graciaExpiradaDeError (AP-0038)', () => {
  it('devuelve los datos ante 409 con el code de gracia', () => {
    const err = axiosConRespuesta(409, {
      code: 'password_expired_in_grace',
      username: 'jdoe',
      dias_restantes_gracia: 3,
    });
    expect(graciaExpiradaDeError(err)).toEqual({
      username: 'jdoe',
      diasRestantesGracia: 3,
    });
  });

  it('devuelve null ante 409 con otro code', () => {
    const err = axiosConRespuesta(409, { code: 'password_still_valid' });
    expect(graciaExpiradaDeError(err)).toBeNull();
  });

  it('devuelve null ante 403 (fuera de gracia)', () => {
    const err = axiosConRespuesta(403, { code: 'password_expired_grace_over' });
    expect(graciaExpiradaDeError(err)).toBeNull();
  });

  it('devuelve null ante un error que no es de axios', () => {
    expect(graciaExpiradaDeError(new Error('boom'))).toBeNull();
  });
});
