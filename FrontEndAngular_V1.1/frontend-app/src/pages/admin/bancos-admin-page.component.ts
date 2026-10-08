import { ChangeDetectionStrategy, Component } from '@angular/core';
import {
  CatalogoCrudComponent,
  type AvisoBorrado,
  type CampoCatalogo,
  type ColumnaCatalogo,
} from '../../shared/ui/components/catalogo-crud/catalogo-crud.component';
import { injectCatalogoCrud, type FormValues } from '../../shared/ui/components/catalogo-crud/catalogo-crud';
import {
  injectActualizarAdminBanco,
  injectAdminBancosList,
  injectCrearAdminBanco,
  injectEliminarAdminBanco,
} from '../../features/admin-bancos/model/queries';
import type { AdminBancoFormPayload, AdminBancoListItem } from '../../features/admin-bancos/model/types';

const COLUMNAS: ColumnaCatalogo<AdminBancoListItem>[] = [
  { header: 'Código', width: 100, tipo: 'code', valor: (i) => i.tid },
  { header: 'Nombre', className: 'fw-semibold', tipo: 'text', valor: (i) => i.nombre },
  { header: 'Código bancario', width: 200, tipo: 'codeOpcional', valor: (i) => i.codigo },
];

const CAMPOS: CampoCatalogo[] = [
  { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: Bancolombia' },
  { key: 'codigo', label: 'Código bancario', maxLength: 10, col: 4, placeholder: 'Opcional' },
];

const AVISO: AvisoBorrado = { objeto: 'el banco', nota: 'Si está referenciado en perfiles, la operación será rechazada.' };

@Component({
  selector: 'app-bancos-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoCrudComponent],
  template: `
    <app-catalogo-crud
      [crud]="crud"
      title="Administrar Bancos"
      icon="bi-bank2"
      backTo="/admin/catalogos"
      [columns]="columnas"
      [fields]="campos"
      [deleteWarning]="aviso"
    />
  `,
})
export class BancosAdminPageComponent {
  protected readonly columnas = COLUMNAS;
  protected readonly campos = CAMPOS;
  protected readonly aviso = AVISO;

  private readonly actualizarMut = injectActualizarAdminBanco();

  protected readonly crud = injectCatalogoCrud<AdminBancoListItem, AdminBancoFormPayload>({
    singular: 'Banco',
    idOf: (item) => item.tid,
    initForm: { nombre: '', codigo: '' },
    itemToForm: (i) => ({ nombre: i.nombre, codigo: i.codigo ?? '' }),
    toPayload: (f: FormValues): AdminBancoFormPayload => ({
      nombre: f['nombre'].trim(),
      codigo: f['codigo'].trim() === '' ? null : f['codigo'].trim(),
    }),
    validate: (f) => (f['nombre'].trim() ? null : 'El nombre del banco es obligatorio'),
    list: (q) => injectAdminBancosList(q),
    crear: injectCrearAdminBanco(),
    actualizar: (tid, payload) => this.actualizarMut.mutateAsync({ tid, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminBanco(),
  });
}
