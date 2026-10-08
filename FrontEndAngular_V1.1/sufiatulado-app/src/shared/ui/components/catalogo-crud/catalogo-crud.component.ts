import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { Router } from '@angular/router';
import { PageHeaderComponent } from '../page-header.component';
import { ConfirmModalComponent } from '../confirm-modal.component';
import { AutofocusDirective } from '../../directives/autofocus.directive';
import type { CatalogoCrud } from './catalogo-crud';

/**
 * Tipos de celda soportados (equivalentes a los renderers JSX del original):
 * - `code`: `<code>valor</code>`
 * - `text`: texto plano (con `className` opcional)
 * - `codeOpcional`: `<code class="small">valor</code>` o un guion atenuado si es nulo/vacío
 */
export type CeldaTipo = 'code' | 'text' | 'codeOpcional';

export interface ColumnaCatalogo<TItem> {
  header: string;
  width?: number;
  className?: string;
  tipo: CeldaTipo;
  valor: (item: TItem) => string | number | null | undefined;
}

export interface CampoCatalogo {
  key: string;
  label: string;
  required?: boolean;
  maxLength?: number;
  col?: number; // ancho bootstrap (col-md-N); por defecto 6
  placeholder?: string;
}

/** Aviso de borrado: "¿Confirma eliminar {objeto}? … permanente." + nota opcional. */
export interface AvisoBorrado {
  objeto: string;
  nota?: string;
}

/** Textos opcionales de la vista (por defecto se arman con `singular`). */
export interface TextosCatalogo {
  tabLista: string;
  tabNuevo: string;
  tabEditar: string;
  botonNuevo: string;
  errorCarga: string;
  vacio: string;
  editandoTexto: string;
  /** Sustantivo del subtítulo: "{total} {sustantivo}{sufijo}". */
  subtituloSustantivo: string;
  subtituloSufijo: string;
  eliminarTitulo: string;
}

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

@Component({
  selector: 'app-catalogo-crud',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, ConfirmModalComponent, AutofocusDirective],
  template: `
    @let c = crud();
    <div>
      <app-page-header [title]="title()" [subtitle]="subtitulo()" [icon]="icon()" />

      @if (backTo()) {
        <div class="mb-3">
          <button type="button" class="btn btn-sm btn-outline-secondary" (click)="volver()">
            <i class="bi bi-arrow-left me-1"></i>Volver
          </button>
        </div>
      }

      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-bottom-0 pb-0">
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="c.tab() === 'lista'" (click)="c.tab.set('lista')">
                <i class="bi bi-list-ul me-2"></i>{{ t().tabLista }}
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="c.tab() === 'registro'" (click)="c.tab.set('registro')">
                <i class="bi me-2" [class]="c.isEditing() ? 'bi-pencil-square' : 'bi-plus-circle'"></i>
                {{ c.isEditing() ? t().tabEditar : t().tabNuevo }}
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body" [class]="c.tab() === 'lista' ? 'p-0' : 'p-4'">
          @if (c.tab() === 'lista') {
            <!-- ── Lista ── -->
            @if (c.success()) {
              <div class="px-3 pt-3">
                <div class="alert alert-success alert-dismissible mb-0">
                  <i class="bi bi-check-circle me-2"></i>{{ c.success() }}
                  <button type="button" class="btn-close" aria-label="Close" (click)="c.success.set('')"></button>
                </div>
              </div>
            }
            <div class="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
              <div class="d-flex align-items-end gap-2 flex-wrap">
                <div style="min-width: 260px">
                  <label class="form-label small mb-1">Nombre</label>
                  <input
                    class="form-control form-control-sm"
                    type="text"
                    placeholder="Filtrar por nombre..."
                    [value]="c.searchNombre()"
                    (input)="c.searchNombre.set($any($event.target).value)"
                    (keydown.enter)="c.buscar()"
                    maxlength="200"
                  />
                </div>
                <button type="button" class="btn btn-sm btn-primary" (click)="c.buscar()">
                  <i class="bi bi-search me-1"></i>Buscar
                </button>
                @if (c.filtrosActivos()) {
                  <button type="button" class="btn btn-sm btn-outline-secondary" (click)="c.limpiar()">
                    <i class="bi bi-x-circle me-1"></i>Limpiar
                  </button>
                }
              </div>
              <div class="d-flex align-items-end gap-2">
                <div style="min-width: 80px">
                  <label class="form-label small mb-1">Mostrar</label>
                  <select class="form-select form-select-sm" (change)="c.setPageSize(+$any($event.target).value)">
                    @for (n of pageSizeOptions; track n) {
                      <option [value]="n" [selected]="n === c.pageSize()">{{ n }}</option>
                    }
                  </select>
                </div>
                <button type="button" class="btn btn-sm btn-success" (click)="c.nuevo()">
                  <i class="bi bi-plus-lg me-1"></i>{{ t().botonNuevo }}
                </button>
              </div>
            </div>

            @if (c.lista.isLoading()) {
              <div class="text-center py-5"><div class="spinner-border" role="status"></div></div>
            } @else if (c.lista.isError()) {
              <div class="alert alert-danger m-3">{{ t().errorCarga }}</div>
            } @else if (!c.lista.data() || c.lista.data()!.items.length === 0) {
              <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox display-4 d-block mb-2"></i>{{ t().vacio }}
              </div>
            } @else {
              <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      @for (col of columns(); track $index) {
                        <th [class]="col.className ?? ''" [style.width.px]="col.width ?? null">{{ col.header }}</th>
                      }
                      <th class="text-end" style="width: 180px">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (item of c.lista.data()!.items; track idDe(item)) {
                      <tr>
                        @for (col of columns(); track $index) {
                          <td [class]="col.className ?? ''">
                            @switch (col.tipo) {
                              @case ('code') {
                                <code>{{ col.valor(item) }}</code>
                              }
                              @case ('codeOpcional') {
                                @if (tieneValor(col.valor(item))) {
                                  <code class="small">{{ col.valor(item) }}</code>
                                } @else {
                                  <span class="text-muted small">—</span>
                                }
                              }
                              @default {
                                {{ col.valor(item) }}
                              }
                            }
                          </td>
                        }
                        <td class="text-end">
                          <button type="button" class="btn btn-sm btn-outline-primary me-1" (click)="c.editar(item)">
                            <i class="bi bi-pencil-fill"></i>
                          </button>
                          <button type="button" class="btn btn-sm btn-outline-danger" (click)="c.confirmDeleteId.set(c.idOf(item))">
                            <i class="bi bi-trash-fill"></i>
                          </button>
                        </td>
                      </tr>
                    }
                  </tbody>
                </table>
              </div>
              <div class="d-flex align-items-center justify-content-between px-3 py-3 border-top">
                <div class="text-muted small">
                  Página <strong>{{ c.page() }}</strong> de <strong>{{ c.totalPages() }}</strong> —
                  {{ c.lista.data()!.total }} resultados
                </div>
                <div class="d-flex gap-2">
                  <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="c.page() <= 1"
                    (click)="c.page.set(c.page() - 1)">
                    <i class="bi bi-chevron-left me-1"></i>Anterior
                  </button>
                  <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="c.page() >= c.totalPages()"
                    (click)="c.page.set(c.page() + 1)">
                    Siguiente<i class="bi bi-chevron-right ms-1"></i>
                  </button>
                </div>
              </div>
            }
          } @else {
            <!-- ── Registro ── -->
            <form (submit)="$event.preventDefault(); c.guardar()" novalidate>
              @if (c.success()) {
                <div class="alert alert-success mb-3"><i class="bi bi-check-circle me-2"></i>{{ c.success() }}</div>
              }
              @if (c.error()) {
                <div class="alert alert-danger mb-3"><i class="bi bi-exclamation-triangle me-2"></i>{{ c.error() }}</div>
              }
              @if (c.isEditing() && c.editId() !== null) {
                <div class="mb-3 text-muted small">
                  {{ t().editandoTexto }} <code>{{ c.editId() }}</code>
                </div>
              }
              <div class="row g-3">
                @for (f of fields(); track f.key; let idx = $index) {
                  <div [class]="'col-md-' + (f.col ?? 6)">
                    <label class="form-label" [attr.for]="'cat-' + f.key">
                      {{ f.label }}
                      @if (f.required) {
                        <span class="text-danger">*</span>
                      }
                    </label>
                    @if (idx === 0) {
                      <input
                        [id]="'cat-' + f.key"
                        class="form-control"
                        type="text"
                        [attr.maxlength]="f.maxLength ?? 200"
                        [value]="c.form()[f.key]"
                        (input)="setCampo(f.key, $any($event.target).value)"
                        [required]="f.required ?? false"
                        [attr.placeholder]="f.placeholder ?? null"
                        appAutofocus
                      />
                    } @else {
                      <input
                        [id]="'cat-' + f.key"
                        class="form-control"
                        type="text"
                        [attr.maxlength]="f.maxLength ?? 200"
                        [value]="c.form()[f.key]"
                        (input)="setCampo(f.key, $any($event.target).value)"
                        [required]="f.required ?? false"
                        [attr.placeholder]="f.placeholder ?? null"
                      />
                    }
                  </div>
                }
              </div>
              <div class="d-flex justify-content-end gap-2 mt-4">
                <button type="button" class="btn btn-outline-secondary" (click)="c.cancelar()" [disabled]="c.isSaving()">
                  <i class="bi bi-x-circle me-1"></i>Cancelar
                </button>
                <button type="submit" class="btn btn-primary" [disabled]="c.isSaving()">
                  @if (c.isSaving()) {
                    <span class="spinner-border spinner-border-sm me-1"></span>Guardando…
                  } @else {
                    <i class="bi bi-check-circle me-1"></i>{{ c.isEditing() ? 'Actualizar' : 'Crear' }}
                  }
                </button>
              </div>
            </form>
          }
        </div>
      </div>

      <app-confirm-modal
        [show]="c.confirmDeleteId() !== null"
        [title]="t().eliminarTitulo"
        confirmLabel="Eliminar"
        confirmIcon="bi-trash-fill"
        confirmVariant="danger"
        [loading]="c.eliminarPending()"
        loadingLabel="Eliminando…"
        (confirm)="c.confirmarEliminar()"
        (hide)="c.confirmDeleteId.set(null)"
      >
        @if (deleteWarning(); as aviso) {
          ¿Confirma eliminar {{ aviso.objeto }}? Esta acción es <strong>permanente</strong>.
          @if (aviso.nota) {
            <br />
            <small class="text-muted">{{ aviso.nota }}</small>
          }
        } @else {
          ¿Confirma eliminar el registro? Esta acción es <strong>permanente</strong>.
        }
      </app-confirm-modal>
    </div>
  `,
})
export class CatalogoCrudComponent {
  private readonly router = inject(Router);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  readonly crud = input.required<CatalogoCrud<any>>();
  readonly title = input.required<string>();
  readonly icon = input.required<string>();
  readonly backTo = input<string | undefined>(undefined);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  readonly columns = input.required<ColumnaCatalogo<any>[]>();
  readonly fields = input.required<CampoCatalogo[]>();
  readonly deleteWarning = input<AvisoBorrado | undefined>(undefined);
  readonly textos = input<Partial<TextosCatalogo>>({});

  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;

  protected readonly t = computed<TextosCatalogo>(() => {
    const singular: string = this.crud().singular;
    return {
      tabLista: 'Lista',
      tabNuevo: `Nuevo ${singular}`,
      tabEditar: `Editar ${singular}`,
      botonNuevo: `Nuevo ${singular}`,
      errorCarga: 'Error al cargar los datos',
      vacio: 'No se encontraron registros',
      editandoTexto: 'Editando registro con código',
      subtituloSustantivo: 'registro(s)',
      subtituloSufijo: ' encontrados',
      eliminarTitulo: `Eliminar ${singular}`,
      ...this.textos(),
    };
  });

  protected readonly subtitulo = computed<string | undefined>(() => {
    const c = this.crud();
    const data = c.lista.data();
    const t = this.t();
    return data
      ? `${data.total} ${t.subtituloSustantivo}${c.filtrosActivos() ? t.subtituloSufijo : ''}`
      : undefined;
  });

  protected volver(): void {
    const destino = this.backTo();
    if (destino) void this.router.navigateByUrl(destino);
  }

  protected setCampo(key: string, value: string): void {
    this.crud().form.update((prev) => ({ ...prev, [key]: value }));
  }

  protected idDe(item: unknown): number {
    return this.crud().idOf(item);
  }

  protected tieneValor(v: string | number | null | undefined): boolean {
    return v !== null && v !== undefined && v !== '';
  }
}
