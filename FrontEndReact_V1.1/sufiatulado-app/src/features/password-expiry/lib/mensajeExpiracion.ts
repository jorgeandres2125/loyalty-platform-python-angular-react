// AP-0037: arma el texto del aviso de vencimiento de contrasena a partir de los
// dias restantes. Ajusta singular, plural y el caso especial de manana (1 dia).
// El backend solo envia el aviso dentro de la ventana (por defecto 1 a 7 dias).
export function mensajeExpiracionPassword(diasRestantes: number): string {
  if (diasRestantes <= 1) {
    return 'Tu contraseña vencerá mañana. Te recomendamos actualizarla.';
  }
  return `Tu contraseña vencerá en ${diasRestantes} días. Te recomendamos actualizarla.`;
}
