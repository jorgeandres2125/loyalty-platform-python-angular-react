/**
 * Una celda de la matriz rol × módulo: el módulo y los 6 flags de permiso del rol.
 */
export interface AutorizacionModuloItem {
  rid: number;
  module_id: number;
  module_code: string;
  module_nombre: string;
  module_icono: string;
  module_activo: boolean;
  permission_id: number;
  puede_ver: boolean;
  puede_crear: boolean;
  puede_editar: boolean;
  puede_eliminar: boolean;
  puede_exportar: boolean;
  puede_aprobar: boolean;
}
