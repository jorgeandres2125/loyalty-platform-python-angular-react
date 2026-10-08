import { describe, it, expect } from 'vitest';
import { mensajeExpiracionPassword } from './mensajeExpiracion';

describe('mensajeExpiracionPassword (AP-0037)', () => {
  it('a 7 dias usa plural y el numero exacto', () => {
    expect(mensajeExpiracionPassword(7)).toBe(
      'Tu contraseña vencerá en 7 días. Te recomendamos actualizarla.',
    );
  });

  it('a 3 dias usa plural', () => {
    expect(mensajeExpiracionPassword(3)).toBe(
      'Tu contraseña vencerá en 3 días. Te recomendamos actualizarla.',
    );
  });

  it('a 2 dias usa plural', () => {
    expect(mensajeExpiracionPassword(2)).toBe(
      'Tu contraseña vencerá en 2 días. Te recomendamos actualizarla.',
    );
  });

  it('a 1 dia usa manana en lugar del numero', () => {
    expect(mensajeExpiracionPassword(1)).toBe(
      'Tu contraseña vencerá mañana. Te recomendamos actualizarla.',
    );
  });
});
