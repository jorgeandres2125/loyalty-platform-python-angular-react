import { ChangeDetectionStrategy, Component, computed } from '@angular/core';
import { CatalogoConPadreComponent, type VistaCatalogoPadre } from './catalogo-con-padre/catalogo-con-padre.component';
import { injectCatalogoConPadre, type OpcionPadre } from './catalogo-con-padre/catalogo-con-padre';
import {
  injectActualizarAdminSubprograma,
  injectAdminSubprogramasList,
  injectCrearAdminSubprograma,
  injectEliminarAdminSubprograma,
} from '../../features/admin-subprogramas/model/queries';
import { injectAdminProgramasList } from '../../features/admin-programas/model/queries';
import type {
  AdminSubprogramaFormPayload,
  AdminSubprogramaListItem,
} from '../../features/admin-subprogramas/model/types';

const VISTA: VistaCatalogoPadre = {
  titulo: 'Administrar Sub-programas',
  icono: 'bi-bookmarks-fill',
  plural: 'sub-programas',
  sufijoEncontrados: ' encontrados',
  tabLista: 'Lista de Sub-programas',
  tabNuevo: 'Nuevo Sub-programa',
  tabEditar: 'Editar Sub-programa',
  botonNuevo: 'Nuevo Sub-programa',
  errorCarga: 'Error al cargar los sub-programas',
  vacio: 'No se encontraron sub-programas',
  editandoTexto: 'Editando sub-programa con código',
  idHeader: 'cspid',
  padreHeader: 'Programa',
  padrePrefijoCodigo: 'cpid=',
  filtroPadreLabel: 'Programa',
  filtroPadreMinWidth: 180,
  formPadreLabel: 'Programa padre',
  nombreMaxLength: 45,
  nombrePlaceholder: 'Ej: Sub-programa Vehiculo Nuevo',
  eliminarTitulo: 'Eliminar Sub-programa',
  eliminarObjeto: 'el sub-programa',
  eliminarNota: 'Si está referenciado por canales, la operación será rechazada.',
};

@Component({
  selector: 'app-subprogramas-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoConPadreComponent],
  template: `<app-catalogo-con-padre [ctl]="ctl" [vista]="vista" />`,
})
export class SubprogramasAdminPageComponent {
  protected readonly vista = VISTA;

  private readonly programasQ = injectAdminProgramasList();
  private readonly actualizarMut = injectActualizarAdminSubprograma();

  protected readonly ctl = injectCatalogoConPadre<AdminSubprogramaListItem, AdminSubprogramaFormPayload>({
    textos: {
      errorObligatorio: 'El nombre del sub-programa es obligatorio',
      creado: 'Sub-programa creado correctamente',
      actualizado: 'Sub-programa actualizado correctamente',
      eliminado: 'Sub-programa eliminado correctamente',
      errorGuardar: 'Error al guardar el sub-programa',
      errorEliminar: 'Error al eliminar el sub-programa',
    },
    normalizar: (sp) => ({ id: sp.cspid, nombre: sp.cspid_nombre, padreId: sp.cpid }),
    toPayload: (f) => ({
      cspid_nombre: f.nombre.trim(),
      cpid: f.padre.trim() === '' ? null : Number(f.padre),
    }),
    list: (q) =>
      injectAdminSubprogramasList(() => {
        const query = q();
        return { page: query.page, page_size: query.page_size, nombre: query.nombre, cpid: query.padre };
      }),
    padres: computed<OpcionPadre[]>(() =>
      (this.programasQ.data() ?? []).map((p) => ({ id: p.cpid, nombre: p.cp_nombre })),
    ),
    crear: injectCrearAdminSubprograma(),
    actualizar: (cspid, payload) => this.actualizarMut.mutateAsync({ cspid, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminSubprograma(),
  });
}
