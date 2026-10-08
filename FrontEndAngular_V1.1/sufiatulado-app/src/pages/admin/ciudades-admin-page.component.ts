import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { CatalogoConPadreComponent, type VistaCatalogoPadre } from './catalogo-con-padre/catalogo-con-padre.component';
import { injectCatalogoConPadre, type OpcionPadre } from './catalogo-con-padre/catalogo-con-padre';
import {
  injectActualizarAdminCiudad,
  injectAdminCiudadesList,
  injectCrearAdminCiudad,
  injectEliminarAdminCiudad,
} from '../../features/admin-ciudades/model/queries';
import { injectAdminDepartamentosList } from '../../features/admin-departamentos/model/queries';
import type { AdminCiudadFormPayload, AdminCiudadListItem } from '../../features/admin-ciudades/model/types';

const VISTA: VistaCatalogoPadre = {
  titulo: 'Administrar Ciudades',
  icono: 'bi-geo-alt-fill',
  plural: 'ciudades',
  sufijoEncontrados: ' encontradas',
  tabLista: 'Lista de Ciudades',
  tabNuevo: 'Nueva Ciudad',
  tabEditar: 'Editar Ciudad',
  botonNuevo: 'Nueva Ciudad',
  errorCarga: 'Error al cargar las ciudades',
  vacio: 'No se encontraron ciudades',
  editandoTexto: 'Editando ciudad con código',
  idHeader: 'Código',
  padreHeader: 'Departamento',
  padrePrefijoCodigo: 'did=',
  filtroPadreLabel: 'Departamento',
  filtroPadreMinWidth: 200,
  formPadreLabel: 'Departamento',
  nombreMaxLength: 50,
  nombrePlaceholder: 'Ej: MEDELLIN',
  eliminarTitulo: 'Eliminar Ciudad',
  eliminarObjeto: 'la ciudad',
  eliminarNota: 'Si está referenciada en perfiles de contacto, la operación será rechazada.',
};

@Component({
  selector: 'app-ciudades-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoConPadreComponent],
  template: `<app-catalogo-con-padre [ctl]="ctl" [vista]="vista" />`,
})
export class CiudadesAdminPageComponent {
  protected readonly vista = VISTA;

  private readonly departamentosQ = injectAdminDepartamentosList(() => ({ page: 1, page_size: 100 }));
  private readonly actualizarMut = injectActualizarAdminCiudad();

  protected readonly ctl = injectCatalogoConPadre<AdminCiudadListItem, AdminCiudadFormPayload>({
    textos: {
      errorObligatorio: 'El nombre de la ciudad es obligatorio',
      creado: 'Ciudad creada correctamente',
      actualizado: 'Ciudad actualizada correctamente',
      eliminado: 'Ciudad eliminada correctamente',
      errorGuardar: 'Error al guardar la ciudad',
      errorEliminar: 'Error al eliminar la ciudad',
    },
    normalizar: (c) => ({ id: c.cid, nombre: c.ciudad, padreId: c.did }),
    toPayload: (f) => ({
      ciudad: f.nombre.trim(),
      did: f.padre.trim() === '' ? null : Number(f.padre),
    }),
    list: (q) =>
      injectAdminCiudadesList(() => {
        const query = q();
        return { page: query.page, page_size: query.page_size, nombre: query.nombre, did: query.padre };
      }),
    padres: computed<OpcionPadre[]>(() =>
      (this.departamentosQ.data()?.items ?? []).map((d) => ({ id: d.did, nombre: d.departamento })),
    ),
    crear: injectCrearAdminCiudad(),
    actualizar: (cid, payload) => this.actualizarMut.mutateAsync({ cid, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminCiudad(),
  });
}
