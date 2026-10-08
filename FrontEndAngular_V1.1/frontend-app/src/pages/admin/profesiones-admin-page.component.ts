import { ChangeDetectionStrategy, Component } from '@angular/core';
import {
  CatalogoCrudComponent,
  type AvisoBorrado,
  type CampoCatalogo,
  type ColumnaCatalogo,
} from '../../shared/ui/components/catalogo-crud/catalogo-crud.component';
import { injectCatalogoCrud, type FormValues } from '../../shared/ui/components/catalogo-crud/catalogo-crud';
import {
  injectActualizarAdminProfesion,
  injectAdminProfesionesList,
  injectCrearAdminProfesion,
  injectEliminarAdminProfesion,
} from '../../features/admin-profesiones/model/queries';
import type { AdminProfesionFormPayload, AdminProfesionListItem } from '../../features/admin-profesiones/model/types';

const COLUMNAS: ColumnaCatalogo<AdminProfesionListItem>[] = [
  { header: 'Código', width: 100, tipo: 'code', valor: (i) => i.tid },
  { header: 'Nombre', className: 'fw-semibold', tipo: 'text', valor: (i) => i.nombre },
];

const CAMPOS: CampoCatalogo[] = [
  { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 12, placeholder: 'Ej: Ingeniero' },
];

const AVISO: AvisoBorrado = { objeto: 'la profesión', nota: 'Si está referenciada en perfiles, la operación será rechazada.' };

@Component({
  selector: 'app-profesiones-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoCrudComponent],
  template: `
    <app-catalogo-crud
      [crud]="crud"
      title="Administrar Profesiones"
      icon="bi-briefcase-fill"
      backTo="/admin/catalogos"
      [columns]="columnas"
      [fields]="campos"
      [deleteWarning]="aviso"
    />
  `,
})
export class ProfesionesAdminPageComponent {
  protected readonly columnas = COLUMNAS;
  protected readonly campos = CAMPOS;
  protected readonly aviso = AVISO;

  private readonly actualizarMut = injectActualizarAdminProfesion();

  protected readonly crud = injectCatalogoCrud<AdminProfesionListItem, AdminProfesionFormPayload>({
    singular: 'Profesión',
    idOf: (item) => item.tid,
    initForm: { nombre: '' },
    itemToForm: (i) => ({ nombre: i.nombre }),
    toPayload: (f: FormValues): AdminProfesionFormPayload => ({ nombre: f['nombre'].trim() }),
    validate: (f) => (f['nombre'].trim() ? null : 'El nombre de la profesión es obligatorio'),
    list: (q) => injectAdminProfesionesList(q),
    crear: injectCrearAdminProfesion(),
    actualizar: (tid, payload) => this.actualizarMut.mutateAsync({ tid, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminProfesion(),
  });
}
