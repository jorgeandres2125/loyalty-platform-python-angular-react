import { ChangeDetectionStrategy, Component } from '@angular/core';
import {
  CatalogoCrudComponent,
  type AvisoBorrado,
  type CampoCatalogo,
  type ColumnaCatalogo,
} from '../../shared/ui/components/catalogo-crud/catalogo-crud.component';
import { injectCatalogoCrud, type FormValues } from '../../shared/ui/components/catalogo-crud/catalogo-crud';
import {
  injectActualizarAdminEps,
  injectAdminEpsList,
  injectCrearAdminEps,
  injectEliminarAdminEps,
} from '../../features/admin-eps/model/queries';
import type { AdminEpsFormPayload, AdminEpsListItem } from '../../features/admin-eps/model/types';

const COLUMNAS: ColumnaCatalogo<AdminEpsListItem>[] = [
  { header: 'Código', width: 100, tipo: 'code', valor: (i) => i.tid },
  { header: 'Nombre', className: 'fw-semibold', tipo: 'text', valor: (i) => i.nombre },
  { header: 'NIT', width: 200, tipo: 'codeOpcional', valor: (i) => i.nit },
];

const CAMPOS: CampoCatalogo[] = [
  { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: SURA EPS' },
  { key: 'nit', label: 'NIT', maxLength: 30, col: 4, placeholder: 'Opcional' },
];

const AVISO: AvisoBorrado = { objeto: 'la EPS', nota: 'Si está referenciada en perfiles tributarios, la operación será rechazada.' };

@Component({
  selector: 'app-eps-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoCrudComponent],
  template: `
    <app-catalogo-crud
      [crud]="crud"
      title="Administrar EPS"
      icon="bi-heart-pulse-fill"
      backTo="/admin/catalogos"
      [columns]="columnas"
      [fields]="campos"
      [deleteWarning]="aviso"
    />
  `,
})
export class EpsAdminPageComponent {
  protected readonly columnas = COLUMNAS;
  protected readonly campos = CAMPOS;
  protected readonly aviso = AVISO;

  private readonly actualizarMut = injectActualizarAdminEps();

  protected readonly crud = injectCatalogoCrud<AdminEpsListItem, AdminEpsFormPayload>({
    singular: 'EPS',
    idOf: (item) => item.tid,
    initForm: { nombre: '', nit: '' },
    itemToForm: (i) => ({ nombre: i.nombre, nit: i.nit ?? '' }),
    toPayload: (f: FormValues): AdminEpsFormPayload => ({
      nombre: f['nombre'].trim(),
      nit: f['nit'].trim() === '' ? null : f['nit'].trim(),
    }),
    validate: (f) => (f['nombre'].trim() ? null : 'El nombre de la EPS es obligatorio'),
    list: (q) => injectAdminEpsList(q),
    crear: injectCrearAdminEps(),
    actualizar: (tid, payload) => this.actualizarMut.mutateAsync({ tid, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminEps(),
  });
}
