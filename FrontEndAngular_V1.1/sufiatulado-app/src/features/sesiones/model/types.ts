export interface SesionActiva {
  sid: string;
  ip: string;
  user_agent: string;
  canal: boolean;
  inicio: string;
  last_activity: string;
  es_actual: boolean;
}