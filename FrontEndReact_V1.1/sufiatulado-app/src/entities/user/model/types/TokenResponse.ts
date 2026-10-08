import type { ModuloPermiso } from './ModuloPermiso';

export interface TokenResponse {
  access_token: string;
  token_type: string;
  uid: number;
  username: string;
  email: string;
  roles: string[];
  modulos: ModuloPermiso[];
}
