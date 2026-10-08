import { ChangeDetectionStrategy, Component } from '@angular/core';
import {
  CatalogoCrudComponent,
  type AvisoBorrado,
  type CampoCatalogo,
  type ColumnaCatalogo,
} from '../../shared/ui/components/catalogo-crud/catalogo-crud.component';
import { injectCatalogoCrud, type FormValues } from '../../shared/ui/components/catalogo-crud/catalogo-crud';
import {
  injectActualizarAdminDepartamento,
  injectAdminDepartamentosList,
  injectCrearAdminDepartamento,
  injectEliminarAdminDepartamento,
} from '../../features/admin-departamentos/model/queries';
import type { AdminDepartamentoFormPayload, AdminDepartamentoListItem } from '../../features/admin-departamentos/model/types';

const COLUMNAS: ColumnaCatalogo<AdminDepartamentoListItem>[] = [
  { header: 'Código', width: 100, tipo: 'code', valor: (i) => i.did },
  { header: 'Nombre', className: 'fw-semibold', tipo: 'text', valor: (i) => i.departamento },
  { header: 'Padre (pid)', width: 120, tipo: 'codeOpcional', valor: (i) => i.pid },
];

const CAMPOS: CampoCatalogo[] = [
  { key: 'departamento', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: Antioquia' },
  { key: 'pid', label: 'Padre (pid)', maxLength: 10, col: 4, placeholder: 'Opcional' },
];

const AVISO: AvisoBorrado = { objeto: 'el departamento', nota: 'Si tiene ciudades asociadas, la operación será rechazada.' };

@Component({
  selector: 'app-departamentos-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoCrudComponent],
  template: `
    <app-catalogo-crud
      [crud]="crud"
      title="Administrar Departamentos"
      icon="bi-map-fill"
      backTo="/admin/catalogos"
      [columns]="columnas"
      [fields]="campos"
      [deleteWarning]="aviso"
    />
  `,
})
export class DepartamentosAdminPageComponent {
  protected readonly columnas = COLUMNAS;
  protected readonly campos = CAMPOS;
  protected readonly aviso = AVISO;

  private readonly actualizarMut = injectActualizarAdminDepartamento();

  protected readonly crud = injectCatalogoCrud<AdminDepartamentoListItem, AdminDepartamentoFormPayload>({
    singular: 'Departamento',
    idOf: (item) => item.did,
    initForm: { departamento: '', pid: '' },
    itemToForm: (i) => ({ departamento: i.departamento, pid: i.pid !== null ? String(i.pid) : '' }),
    toPayload: (f: FormValues): AdminDepartamentoFormPayload => ({
      departamento: f['departamento'].trim(),
      pid: f['pid'].trim() === '' ? null : Number(f['pid']),
    }),
    validate: (f) => (f['departamento'].trim() ? null : 'El nombre del departamento es obligatorio'),
    list: (q) => injectAdminDepartamentosList(q),
    crear: injectCrearAdminDepartamento(),
    actualizar: (did, payload) => this.actualizarMut.mutateAsync({ did, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminDepartamento(),
  });
}
