// AP-0047: resultado de la emision de una contrasena temporal (clave visible una sola vez).
export interface PasswordTemporalResultado {
  uid: number;
  usuario: string;
  password_temporal: string;
  expira_iso: string;
  ttl_minutos: number;
}
