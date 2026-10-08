export interface MiDashboard {
  numero_documento: string;
  nombre_completo: string;
  celular: string | null;
  email: string | null;
  direccion: string | null;
  departamento: string | null;
  ciudad: string | null;
  departamento_nombre: string | null;
  ciudad_nombre: string | null;
  programa: { cpid: number; nombre: string } | null;
  incentivos_habilitados: boolean;
  rol_principal: 'comisionista' | 'comisionista consumo' | 'otro';
  perfil: {
    contacto_completo: boolean;
    tributario_completo: boolean | null;
    emocional_completo: boolean;
    stages_completos: number;
    stages_total: number;
    porcentaje_completado: number;
  };
  documentos: {
    items: Record<
      'cedula' | 'rut' | 'contrato',
      { subido: boolean; estado: string | null; version: number }
    >;
    total_subidos: number;
    total_esperados: number;
    total_aprobados: number;
  } | null;
}
