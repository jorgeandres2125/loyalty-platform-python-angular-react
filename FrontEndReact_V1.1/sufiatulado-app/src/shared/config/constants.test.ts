import { describe, it, expect } from 'vitest';
import { ROLES, TIPO_DOCUMENTO, PROGRAMA, TOKEN_KEY } from './constants';

// Estas constantes son contratos con el backend (slugs de rol del JWT) y con
// el mainframe (códigos de tipo de documento y programa). Cambiarlas rompe la
// autorización o el import CSV, así que las congelamos en pruebas.
describe('constants — contratos backend/mainframe', () => {
  it('los slugs de rol coinciden con RolUsuario.value del backend', () => {
    expect(ROLES.ADMIN).toBe('administrator');
    expect(ROLES.COMISIONISTA).toBe('comisionista');
    expect(ROLES.COMISIONISTA_CONSUMO).toBe('comisionista_consumo');
    expect(ROLES.DOCUMENTADOR).toBe('documentador');
  });

  it('los códigos de tipo de documento coinciden con el mainframe (4/5/6)', () => {
    expect(TIPO_DOCUMENTO.CEDULA).toBe(4);
    expect(TIPO_DOCUMENTO.RUT).toBe(5);
    expect(TIPO_DOCUMENTO.CONTRATO).toBe(6);
  });

  it('los códigos de programa son 1=Movilidad, 2=Consumo', () => {
    expect(PROGRAMA.MOVILIDAD).toBe(1);
    expect(PROGRAMA.CONSUMO).toBe(2);
  });

  it('la clave de token en localStorage es estable', () => {
    expect(TOKEN_KEY).toBe('sufi_access_token');
  });
});
