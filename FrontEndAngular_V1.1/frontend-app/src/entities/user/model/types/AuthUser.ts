import type { ModuloPermiso } from './ModuloPermiso';
import type { PasswordAviso } from './PasswordAviso';

export interface AuthUser {
  uid: number;
  username: string;
  email: string;
  roles: string[];
  tiene_incentivos: boolean;
  programa: number | null;
  modulos: ModuloPermiso[];
  // AP-0037: aviso de vencimiento de contrasena; presente solo dentro de la ventana.
  password_aviso?: PasswordAviso | null;
  // AP-0132: instante absoluto de expiracion de la sesion (ISO 8601, no secreto); el
  // cliente lo usa para anticipar el cierre y descartar los datos locales.
  session_expires_at?: string | null;
}