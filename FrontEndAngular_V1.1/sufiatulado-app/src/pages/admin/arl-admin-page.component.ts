import { ChangeDetectionStrategy, Component } from '@angular/core';
import {
  CatalogoCrudComponent,
  type AvisoBorrado,
  type CampoCatalogo,
  type ColumnaCatalogo,
} from '../../shared/ui/components/catalogo-crud/catalogo-crud.component';
import { injectCatalogoCrud, type FormValues } from '../../shared/ui/components/catalogo-crud/catalogo-crud';
import {
  injectActualizarAdminArl,
  injectAdminArlList,
  injectCrearAdminArl,
  injectEliminarAdminArl,
} from '../../features/admin-arl/model/queries';
import type { AdminArlFormPayload, AdminArlListItem } from '../../features/admin-arl/model/types';

const COLUMNAS: ColumnaCatalogo<AdminArlListItem>[] = [
  { header: 'Código', width: 100, tipo: 'code', valor: (i) => i.tid },
  { header: 'Nombre', className: 'fw-semibold', tipo: 'text', valor: (i) => i.nombre },
  { header: 'NIT', width: 200, tipo: 'codeOpcional', valor: (i) => i.nit },
];

const CAMPOS: CampoCatalogo[] = [
  { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: SURA ARL' },
  { key: 'nit', label: 'NIT', maxLength: 30, col: 4, placeholder: 'Opcional' },
];

const AVISO: AvisoBorrado = { objeto: 'la ARL', nota: 'Si está referenciada en perfiles tributarios, la operación será rechazada.' };

@Component({
  selector: 'app-arl-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoCrudComponent],
  template: `
    <app-catalogo-crud
      [crud]="crud"
      title="Administrar ARL"
      icon="bi-shield-fill-plus"
      backTo="/admin/catalogos"
      [columns]="columnas"
      [fields]="campos"
      [deleteWarning]="aviso"
    />
  `,
})
export class ArlAdminPageComponent {
  protected readonly columnas = COLUMNAS;
  protected readonly campos = CAMPOS;
  protected readonly aviso = AVISO;

  private readonly actualizarMut = injectActualizarAdminArl();

  protected readonly crud = injectCatalogoCrud<AdminArlListItem, AdminArlFormPayload>({
    singular: 'ARL',
    idOf: (item) => item.tid,
    initForm: { nombre: '', nit: '' },
    itemToForm: (i) => ({ nombre: i.nombre, nit: i.nit ?? '' }),
    toPayload: (f: FormValues): AdminArlFormPayload => ({
      nombre: f['nombre'].trim(),
      nit: f['nit'].trim() === '' ? null : f['nit'].trim(),
    }),
    validate: (f) => (f['nombre'].trim() ? null : 'El nombre de la ARL es obligatorio'),
    list: (q) => injectAdminArlList(q),
    crear: injectCrearAdminArl(),
    actualizar: (tid, payload) => this.actualizarMut.mutateAsync({ tid, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminArl(),
  });
}
