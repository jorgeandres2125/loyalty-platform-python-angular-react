import { computed, effect, signal, type Signal, type WritableSignal } from '@angular/core';
import { extractError } from '../../../lib/extractError';

/**
 * Lógica del scaffold CRUD genérico para los catálogos admin de un solo recurso
 * (lista paginada con filtro por nombre + alta/edición + borrado confirmado).
 * Equivalente al estado interno de `CatalogoCrudPage` del proyecto React: aquí vive
 * en signals creados en el contexto de inyección de la página, y el componente
 * `<app-catalogo-crud>` solo lo pinta.
 */

export type FormValues = Record<string, string>;

export interface ListaCatalogoQuery {
  page: number;
  page_size: number;
  nombre?: string;
}

/** Forma mínima del resultado de una query de TanStack (signals). */
export interface ListaResultado<TItem> {
  data: () => { items: TItem[]; total: number } | undefined;
  isLoading: () => boolean;
  isError: () => boolean;
}

/** Forma mínima de una mutación de TanStack (signals + mutateAsync). */
export interface MutacionLike<TArg> {
  mutateAsync: (arg: TArg) => Promise<unknown>;
  isPending: () => boolean;
}

export interface CatalogoCrudConfig<TItem, TPayload> {
  singular: string; // p.ej. "ARL", "Banco"
  idOf: (item: TItem) => number;
  initForm: FormValues;
  itemToForm: (item: TItem) => FormValues;
  toPayload: (form: FormValues) => TPayload;
  validate: (form: FormValues) => string | null;
  /** Crea la query de listado (se invoca una vez, en contexto de inyección). */
  list: (query: () => ListaCatalogoQuery) => ListaResultado<TItem>;
  crear: MutacionLike<TPayload>;
  actualizar: (id: number, payload: TPayload) => Promise<unknown>;
  actualizarPending: () => boolean;
  eliminar: MutacionLike<number>;
  /** Mensajes opcionales (por defecto se arman con `singular`). */
  mensajes?: Partial<MensajesCatalogo>;
}

export interface MensajesCatalogo {
  creado: string;
  actualizado: string;
  eliminado: string;
  errorGuardar: string;
  errorEliminar: string;
}

export type CatalogoTab = 'lista' | 'registro';

export interface CatalogoCrud<TItem> {
  singular: string;
  idOf: (item: TItem) => number;
  lista: ListaResultado<TItem>;
  eliminarPending: () => boolean;
  tab: WritableSignal<CatalogoTab>;
  page: WritableSignal<number>;
  pageSize: Signal<number>;
  searchNombre: WritableSignal<string>;
  filtroNombre: Signal<string>;
  editId: Signal<number | null>;
  form: WritableSignal<FormValues>;
  error: Signal<string>;
  success: WritableSignal<string>;
  confirmDeleteId: WritableSignal<number | null>;
  filtrosActivos: Signal<boolean>;
  totalPages: Signal<number>;
  isEditing: Signal<boolean>;
  isSaving: Signal<boolean>;
  setPageSize: (n: number) => void;
  buscar: () => void;
  limpiar: () => void;
  nuevo: () => void;
  editar: (item: TItem) => void;
  cancelar: () => void;
  guardar: () => Promise<void>;
  confirmarEliminar: () => Promise<void>;
}

export function injectCatalogoCrud<TItem, TPayload>(
  config: CatalogoCrudConfig<TItem, TPayload>,
): CatalogoCrud<TItem> {
  const tab = signal<CatalogoTab>('lista');
  const page = signal<number>(1);
  const pageSize = signal<number>(10);
  const searchNombre = signal<string>('');
  const filtroNombre = signal<string>('');
  const editId = signal<number | null>(null);
  const form = signal<FormValues>(config.initForm);
  const error = signal<string>('');
  const success = signal<string>('');
  const confirmDeleteId = signal<number | null>(null);
  const mensajes: MensajesCatalogo = {
    creado: `${config.singular} creado correctamente`,
    actualizado: `${config.singular} actualizado correctamente`,
    eliminado: `${config.singular} eliminado correctamente`,
    errorGuardar: `Error al guardar (${config.singular})`,
    errorEliminar: `Error al eliminar (${config.singular})`,
    ...config.mensajes,
  };

  const lista = config.list(() => ({
    page: page(),
    page_size: pageSize(),
    nombre: filtroNombre() || undefined,
  }));

  const filtrosActivos = computed<boolean>(() => !!filtroNombre());
  const totalPages = computed<number>(() => {
    const data = lista.data();
    return data ? Math.max(1, Math.ceil(data.total / pageSize())) : 1;
  });
  const isEditing = computed<boolean>(() => editId() !== null);
  const isSaving = computed<boolean>(() => config.crear.isPending() || config.actualizarPending());

  effect((onCleanup) => {
    if (!success()) return;
    const t = setTimeout(() => success.set(''), 3500);
    onCleanup(() => clearTimeout(t));
  });

  effect(() => {
    if (tab() !== 'registro') error.set('');
  });

  const cancelar = (): void => {
    editId.set(null);
    form.set(config.initForm);
    error.set('');
    tab.set('lista');
  };

  return {
    singular: config.singular,
    idOf: config.idOf,
    lista,
    eliminarPending: config.eliminar.isPending,
    tab,
    page,
    pageSize,
    searchNombre,
    filtroNombre,
    editId,
    form,
    error,
    success,
    confirmDeleteId,
    filtrosActivos,
    totalPages,
    isEditing,
    isSaving,
    setPageSize: (n: number) => {
      pageSize.set(n);
      page.set(1);
    },
    buscar: () => {
      filtroNombre.set(searchNombre().trim());
      page.set(1);
    },
    limpiar: () => {
      searchNombre.set('');
      filtroNombre.set('');
      page.set(1);
    },
    nuevo: () => {
      editId.set(null);
      form.set(config.initForm);
      error.set('');
      tab.set('registro');
    },
    editar: (item: TItem) => {
      editId.set(config.idOf(item));
      form.set(config.itemToForm(item));
      error.set('');
      tab.set('registro');
    },
    cancelar,
    guardar: async () => {
      error.set('');
      const valores: FormValues = form();
      const mensaje: string | null = config.validate(valores);
      if (mensaje) {
        error.set(mensaje);
        return;
      }
      const payload: TPayload = config.toPayload(valores);
      const editando: boolean = isEditing();
      const id: number | null = editId();
      try {
        if (editando && id !== null) {
          await config.actualizar(id, payload);
        } else {
          await config.crear.mutateAsync(payload);
        }
        cancelar();
        success.set(editando ? mensajes.actualizado : mensajes.creado);
      } catch (err) {
        error.set(extractError(err, mensajes.errorGuardar));
      }
    },
    confirmarEliminar: async () => {
      const id: number | null = confirmDeleteId();
      if (id === null) return;
      try {
        await config.eliminar.mutateAsync(id);
        success.set(mensajes.eliminado);
      } catch (err) {
        error.set(extractError(err, mensajes.errorEliminar));
      } finally {
        confirmDeleteId.set(null);
      }
    },
  };
}
