import { ChangeDetectionStrategy, Component } from '@angular/core';
import {
  CatalogoCrudComponent,
  type AvisoBorrado,
  type CampoCatalogo,
  type ColumnaCatalogo,
  type TextosCatalogo,
} from '../../shared/ui/components/catalogo-crud/catalogo-crud.component';
import { injectCatalogoCrud, type FormValues } from '../../shared/ui/components/catalogo-crud/catalogo-crud';
import {
  injectActualizarAdminAfp,
  injectAdminAfpList,
  injectCrearAdminAfp,
  injectEliminarAdminAfp,
} from '../../features/admin-afp/model/queries';
import type { AdminAfpFormPayload, AdminAfpListItem } from '../../features/admin-afp/model/types';

const COLUMNAS: ColumnaCatalogo<AdminAfpListItem>[] = [
  { header: 'Código', width: 100, tipo: 'code', valor: (i) => i.tid },
  { header: 'Nombre', className: 'fw-semibold', tipo: 'text', valor: (i) => i.nombre },
  { header: 'NIT', width: 200, tipo: 'codeOpcional', valor: (i) => i.nit },
];

const CAMPOS: CampoCatalogo[] = [
  { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: PORVENIR PENSIONES' },
  { key: 'nit', label: 'NIT', maxLength: 30, col: 4, placeholder: 'Opcional' },
];

const AVISO: AvisoBorrado = {
  objeto: 'la AFP',
  nota: 'Si la AFP está referenciada en perfiles tributarios, la operación será rechazada.',
};

const TEXTOS: Partial<TextosCatalogo> = {
  tabLista: 'Lista de AFP',
  tabNuevo: 'Nueva AFP',
  tabEditar: 'Editar AFP',
  botonNuevo: 'Nueva AFP',
  errorCarga: 'Error al cargar las AFP',
  vacio: 'No se encontraron AFP',
  editandoTexto: 'Editando AFP con código',
  subtituloSustantivo: 'AFP',
  subtituloSufijo: ' encontradas',
  eliminarTitulo: 'Eliminar AFP',
};

@Component({
  selector: 'app-afp-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CatalogoCrudComponent],
  template: `
    <app-catalogo-crud
      [crud]="crud"
      title="Administrar AFP"
      icon="bi-piggy-bank-fill"
      backTo="/admin/catalogos"
      [columns]="columnas"
      [fields]="campos"
      [deleteWarning]="aviso"
      [textos]="textos"
    />
  `,
})
export class AfpAdminPageComponent {
  protected readonly columnas = COLUMNAS;
  protected readonly campos = CAMPOS;
  protected readonly aviso = AVISO;
  protected readonly textos = TEXTOS;

  private readonly actualizarMut = injectActualizarAdminAfp();

  protected readonly crud = injectCatalogoCrud<AdminAfpListItem, AdminAfpFormPayload>({
    singular: 'AFP',
    idOf: (item) => item.tid,
    initForm: { nombre: '', nit: '' },
    itemToForm: (i) => ({ nombre: i.nombre, nit: i.nit ?? '' }),
    toPayload: (f: FormValues): AdminAfpFormPayload => ({
      nombre: f['nombre'].trim(),
      nit: f['nit'].trim() === '' ? null : f['nit'].trim(),
    }),
    validate: (f) => (f['nombre'].trim() ? null : 'El nombre de la AFP es obligatorio'),
    list: (q) => injectAdminAfpList(q),
    crear: injectCrearAdminAfp(),
    actualizar: (tid, payload) => this.actualizarMut.mutateAsync({ tid, payload }),
    actualizarPending: this.actualizarMut.isPending,
    eliminar: injectEliminarAdminAfp(),
    mensajes: {
      creado: 'AFP creada correctamente',
      actualizado: 'AFP actualizada correctamente',
      eliminado: 'AFP eliminada correctamente',
      errorGuardar: 'Error al guardar la AFP',
      errorEliminar: 'Error al eliminar la AFP',
    },
  });
}
