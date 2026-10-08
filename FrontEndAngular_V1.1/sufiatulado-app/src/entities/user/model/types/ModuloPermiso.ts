export interface ModuloPermiso {
  module_id: number;
  module_code: string;
  nombre: string;
  ruta: string | null;
  icono: string | null;
  orden: number;
  puede_ver: boolean;
  puede_crear: boolean;
  puede_editar: boolean;
  puede_eliminar: boolean;
  puede_exportar: boolean;
  puede_aprobar: boolean;
}
