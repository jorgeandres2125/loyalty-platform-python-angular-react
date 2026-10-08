// AP-0037: aviso de vencimiento de contrasena que el backend expone en la sesion.
// Presente solo cuando el vencimiento cae dentro de la ventana de aviso (7 dias).
export interface PasswordAviso {
  dias_restantes: number;
  fecha_expiracion: string;
}
