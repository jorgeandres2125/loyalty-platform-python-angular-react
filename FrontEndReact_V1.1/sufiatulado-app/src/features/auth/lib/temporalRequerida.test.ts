import { describe, it, expect } from 'vitest';
import { AxiosError, AxiosHeaders } from 'axios';
import { temporalRequeridaDeError } from './temporalRequerida';

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

describe('temporalRequeridaDeError (AP-0046)', () => {
  it('devuelve los datos ante 409 con el code de temporal', () => {
    const err = axiosConRespuesta(409, {
      code: 'password_temporal_change_required',
      username: 'jdoe',
      expira_iso: '2026-07-06T15:00:00',
    });
    expect(temporalRequeridaDeError(err)).toEqual({
      username: 'jdoe',
      expiraIso: '2026-07-06T15:00:00',
    });
  });

  it('devuelve null ante 409 con otro code (gracia AP-0038)', () => {
    const err = axiosConRespuesta(409, { code: 'password_expired_in_grace' });
    expect(temporalRequeridaDeError(err)).toBeNull();
  });

  it('devuelve null ante 403 (temporal vencida)', () => {
    const err = axiosConRespuesta(403, { code: 'password_temporal_expired' });
    expect(temporalRequeridaDeError(err)).toBeNull();
  });

  it('devuelve null ante un error que no es de axios', () => {
    expect(temporalRequeridaDeError(new Error('boom'))).toBeNull();
  });
});
