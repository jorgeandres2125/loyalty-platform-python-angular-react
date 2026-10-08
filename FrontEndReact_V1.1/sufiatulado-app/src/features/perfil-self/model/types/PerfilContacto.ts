export interface PerfilContacto {
  numero_documento: string;
  tipo_documento: string;
  nombre_completo: string;
  genero: string;
  fecha_nacimiento: string;
  celular: string;
  telefono: string | null;
  email: string | null;
  direccion: string;
  departamento: string;
  ciudad: string;
  // Nombres pre-resueltos por el backend (JOIN con departamentos / ciudades).
  departamento_nombre?: string | null;
  ciudad_nombre?: string | null;
  comisionista_programa_id: number;
  comisionista_subprograma_id: number | null;
  cod_canales: number | null;
  cod_oficinas: number | null;
  usuario_responsable: number | null;
  concesionario: string | null;
  tipo_de_cuenta: string | null;
  banco: number | null;
  numero_de_cuenta: string | null;
  requiere_comision: boolean | null;
  acepto_habeas_data: 1;
  incentivos: boolean;
  estado: 0 | 1;
  firma_contrato: boolean | null;
}
