import { computed, effect, signal, type Signal, type WritableSignal } from '@angular/core';
import { extractError } from '../../../shared/lib/extractError';
import type { ListaResultado, MutacionLike } from '../../../shared/ui/components/catalogo-crud/catalogo-crud';

/**
 * Estado y acciones de un catálogo admin cuyos registros cuelgan de un "padre"
 * (Ciudades → Departamento, Sub-programas → Programa). Replica la lógica de
 * CiudadesAdminPage / SubprogramasAdminPage del proyecto React.
 */

export interface OpcionPadre {
  id: number;
  nombre: string;
}

export interface ItemConPadre {
  id: number;
  nombre: string;
  padreId: number | null;
}

export interface ListaConPadreQuery {
  page: number;
  page_size: number;
  nombre?: string;
  padre?: number;
}

export interface FormConPadre {
  nombre: string;
  padre: string;
}

export interface TextosCatalogoPadre {
  errorObligatorio: string;
  creado: string;
  actualizado: string;
  eliminado: string;
  errorGuardar: string;
  errorEliminar: string;
}

export interface CatalogoConPadreConfig<TItem, TPayload> {
  textos: TextosCatalogoPadre;
  /** Normaliza el ítem del backend a {id, nombre, padreId}. */
  normalizar: (item: TItem) => ItemConPadre;
  toPayload: (form: FormConPadre) => TPayload;
  list: (query: () => ListaConPadreQuery) => ListaResultado<TItem>;
  padres: Signal<OpcionPadre[]>;
  crear: MutacionLike<TPayload>;
  actualizar: (id: number, payload: TPayload) => Promise<unknown>;
  actualizarPending: () => boolean;
  eliminar: MutacionLike<number>;
}

const FORM_INICIAL: FormConPadre = { nombre: '', padre: '' };

export interface CatalogoConPadre {
  filas: Signal<ItemConPadre[] | undefined>;
  total: Signal<number | undefined>;
  isLoading: () => boolean;
  isError: () => boolean;
  padres: Signal<OpcionPadre[]>;
  padrePorId: Signal<Map<number, string>>;
  eliminarPending: () => boolean;
  tab: WritableSignal<'lista' | 'registro'>;
  page: WritableSignal<number>;
  pageSize: Signal<number>;
  searchNombre: WritableSignal<string>;
  searchPadre: WritableSignal<string>;
  editId: Signal<number | null>;
  form: WritableSignal<FormConPadre>;
  error: Signal<string>;
  success: WritableSignal<string>;
  confirmDeleteId: WritableSignal<number | null>;
  filtrosActivos: Signal<boolean>;
  totalPages: Signal<number>;
  isEditing: Signal<boolean>;
  isSaving: Signal<boolean>;
  setPageSize: (n: number) => void;
  aplicarFiltros: () => void;
  limpiarFiltros: () => void;
  nuevo: () => void;
  editar: (item: ItemConPadre) => void;
  cancelar: () => void;
  guardar: () => Promise<void>;
  confirmarEliminar: () => Promise<void>;
}

export function injectCatalogoConPadre<TItem, TPayload>(
  config: CatalogoConPadreConfig<TItem, TPayload>,
): CatalogoConPadre {
  const tab = signal<'lista' | 'registro'>('lista');
  const page = signal<number>(1);
  const pageSize = signal<number>(10);
  const searchNombre = signal<string>('');
  const searchPadre = signal<string>('');
  const filtroNombre = signal<string>('');
  const filtroPadre = signal<string>('');
  const editId = signal<number | null>(null);
  const form = signal<FormConPadre>(FORM_INICIAL);
  const error = signal<string>('');
  const success = signal<string>('');
  const confirmDeleteId = signal<number | null>(null);

  const lista = config.list(() => ({
    page: page(),
    page_size: pageSize(),
    nombre: filtroNombre() || undefined,
    padre: filtroPadre() ? Number(filtroPadre()) : undefined,
  }));

  const filas = computed<ItemConPadre[] | undefined>(() => lista.data()?.items.map(config.normalizar));
  const total = computed<number | undefined>(() => lista.data()?.total);
  const filtrosActivos = computed<boolean>(() => !!filtroNombre() || !!filtroPadre());
  const totalPages = computed<number>(() => {
    const t = total();
    return t !== undefined ? Math.max(1, Math.ceil(t / pageSize())) : 1;
  });
  const isEditing = computed<boolean>(() => editId() !== null);
  const isSaving = computed<boolean>(() => config.crear.isPending() || config.actualizarPending());
  const padrePorId = computed<Map<number, string>>(() => {
    const m = new Map<number, string>();
    config.padres().forEach((p) => m.set(p.id, p.nombre));
    return m;
  });

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
    form.set(FORM_INICIAL);
    error.set('');
    tab.set('lista');
  };

  return {
    filas,
    total,
    isLoading: lista.isLoading,
    isError: lista.isError,
    padres: config.padres,
    padrePorId,
    eliminarPending: config.eliminar.isPending,
    tab,
    page,
    pageSize,
    searchNombre,
    searchPadre,
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
    aplicarFiltros: () => {
      filtroNombre.set(searchNombre().trim());
      filtroPadre.set(searchPadre());
      page.set(1);
    },
    limpiarFiltros: () => {
      searchNombre.set('');
      searchPadre.set('');
      filtroNombre.set('');
      filtroPadre.set('');
      page.set(1);
    },
    nuevo: () => {
      editId.set(null);
      form.set(FORM_INICIAL);
      error.set('');
      tab.set('registro');
    },
    editar: (item: ItemConPadre) => {
      editId.set(item.id);
      form.set({ nombre: item.nombre, padre: item.padreId !== null ? String(item.padreId) : '' });
      error.set('');
      tab.set('registro');
    },
    cancelar,
    guardar: async () => {
      error.set('');
      const valores: FormConPadre = form();
      if (!valores.nombre.trim()) {
        error.set(config.textos.errorObligatorio);
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
        success.set(editando ? config.textos.actualizado : config.textos.creado);
      } catch (err) {
        error.set(extractError(err, config.textos.errorGuardar));
      }
    },
    confirmarEliminar: async () => {
      const id: number | null = confirmDeleteId();
      if (id === null) return;
      try {
        await config.eliminar.mutateAsync(id);
        success.set(config.textos.eliminado);
      } catch (err) {
        error.set(extractError(err, config.textos.errorEliminar));
      } finally {
        confirmDeleteId.set(null);
      }
    },
  };
}
