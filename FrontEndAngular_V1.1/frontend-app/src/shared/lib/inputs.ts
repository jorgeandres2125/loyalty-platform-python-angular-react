/**
 * Lee el valor de un `<input>`/`<textarea>`/`<select>` desde su evento y, si se pasa
 * `transform` (solo dígitos, mayúsculas, recorte…), reescribe el valor transformado
 * en el elemento. Reproduce el comportamiento de los inputs controlados de React,
 * donde el valor mostrado siempre es el del estado aunque el signal no cambie.
 */
export function leerInput(e: Event, transform?: (valor: string) => string): string {
  const el = e.target as HTMLInputElement;
  const valor: string = transform ? transform(el.value) : el.value;
  if (el.value !== valor) el.value = valor;
  return valor;
}

export const soloDigitos = (v: string): string => v.replace(/\D/g, '');
export const mayusculas = (v: string): string => v.toUpperCase();
