import { ChangeDetectionStrategy, Component, inject, input } from '@angular/core';
import { Router } from '@angular/router';
import { PageHeaderComponent } from '../../../shared/ui/components/page-header.component';
import { ConfirmModalComponent } from '../../../shared/ui/components/confirm-modal.component';
import { AutofocusDirective } from '../../../shared/ui/directives/autofocus.directive';
import type { CatalogoConPadre } from './catalogo-con-padre';

/** Textos de presentación (títulos, etiquetas, mensajes) de la vista. */
export interface VistaCatalogoPadre {
  titulo: string;
  icono: string;
  /** p.ej. "ciudades" / "sub-programas" */
  plural: string;
  /** p.ej. " encontradas" / " encontrados" */
  sufijoEncontrados: string;
  tabLista: string;
  tabNuevo: string;
  tabEditar: string;
  botonNuevo: string;
  errorCarga: string;
  vacio: string;
  editandoTexto: string;
  idHeader: string;
  padreHeader: string;
  padrePrefijoCodigo: string;
  filtroPadreLabel: string;
  filtroPadreMinWidth: number;
  formPadreLabel: string;
  nombreMaxLength: number;
  nombrePlaceholder: string;
  eliminarTitulo: string;
  eliminarObjeto: string;
  eliminarNota: string;
}

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

@Component({
  selector: 'app-catalogo-con-padre',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, ConfirmModalComponent, AutofocusDirective],
  template: `
    @let c = ctl();
    @let v = vista();
    <div>
      <app-page-header
        [title]="v.titulo"
        [subtitle]="c.total() !== undefined ? c.total() + ' ' + v.plural + (c.filtrosActivos() ? v.sufijoEncontrados : '') : undefined"
        [icon]="v.icono"
      />
      <div class="mb-3">
        <button type="button" class="btn btn-sm btn-outline-secondary" (click)="volver()">
          <i class="bi bi-arrow-left me-1"></i>Volver
        </button>
      </div>

      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-bottom-0 pb-0">
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="c.tab() === 'lista'" (click)="c.tab.set('lista')">
                <i class="bi bi-list-ul me-2"></i>{{ v.tabLista }}
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="c.tab() === 'registro'" (click)="c.tab.set('registro')">
                <i class="bi me-2" [class]="c.isEditing() ? 'bi-pencil-square' : 'bi-plus-circle'"></i>
                {{ c.isEditing() ? v.tabEditar : v.tabNuevo }}
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body" [class]="c.tab() === 'lista' ? 'p-0' : 'p-4'">
          @if (c.tab() === 'lista') {
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
                <div style="min-width: 200px">
                  <label class="form-label small mb-1">Nombre</label>
                  <input
                    class="form-control form-control-sm"
                    type="text"
                    placeholder="Filtrar por nombre..."
                    [value]="c.searchNombre()"
                    (input)="c.searchNombre.set($any($event.target).value)"
                    (keydown.enter)="c.aplicarFiltros()"
                    [attr.maxlength]="v.nombreMaxLength"
                  />
                </div>
                <div [style.min-width.px]="v.filtroPadreMinWidth">
                  <label class="form-label small mb-1">{{ v.filtroPadreLabel }}</label>
                  <select class="form-select form-select-sm" (change)="c.searchPadre.set($any($event.target).value)">
                    <option value="" [selected]="c.searchPadre() === ''">Todos</option>
                    @for (p of c.padres(); track p.id) {
                      <option [value]="p.id" [selected]="'' + p.id === c.searchPadre()">{{ p.nombre }}</option>
                    }
                  </select>
                </div>
                <button type="button" class="btn btn-sm btn-primary" (click)="c.aplicarFiltros()">
                  <i class="bi bi-search me-1"></i>Buscar
                </button>
                @if (c.filtrosActivos()) {
                  <button type="button" class="btn btn-sm btn-outline-secondary" (click)="c.limpiarFiltros()">
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
                  <i class="bi bi-plus-lg me-1"></i>{{ v.botonNuevo }}
                </button>
              </div>
            </div>

            @if (c.isLoading()) {
              <div class="text-center py-5"><div class="spinner-border" role="status"></div></div>
            } @else if (c.isError()) {
              <div class="alert alert-danger m-3">{{ v.errorCarga }}</div>
            } @else if (!c.filas() || c.filas()!.length === 0) {
              <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox display-4 d-block mb-2"></i>{{ v.vacio }}
              </div>
            } @else {
              <div class="table-responsive">
                <table class="table table-hover mb-0 align-middle">
                  <thead class="table-light">
                    <tr>
                      <th style="width: 100px">{{ v.idHeader }}</th>
                      <th>Nombre</th>
                      <th style="width: 220px">{{ v.padreHeader }}</th>
                      <th class="text-end" style="width: 180px">Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    @for (item of c.filas(); track item.id) {
                      <tr>
                        <td><code>{{ item.id }}</code></td>
                        <td class="fw-semibold">{{ item.nombre }}</td>
                        <td>
                          @if (item.padreId !== null && c.padrePorId().get(item.padreId) !== undefined) {
                            {{ c.padrePorId().get(item.padreId) }}
                          } @else if (item.padreId !== null) {
                            <code class="small">{{ v.padrePrefijoCodigo }}{{ item.padreId }}</code>
                          } @else {
                            <span class="text-muted small">—</span>
                          }
                        </td>
                        <td class="text-end">
                          <button type="button" class="btn btn-sm btn-outline-primary me-1" (click)="c.editar(item)">
                            <i class="bi bi-pencil-fill"></i>
                          </button>
                          <button type="button" class="btn btn-sm btn-outline-danger" (click)="c.confirmDeleteId.set(item.id)">
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
                  {{ c.total() }} resultados
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
            <form (submit)="$event.preventDefault(); c.guardar()" novalidate>
              @if (c.success()) {
                <div class="alert alert-success mb-3"><i class="bi bi-check-circle me-2"></i>{{ c.success() }}</div>
              }
              @if (c.error()) {
                <div class="alert alert-danger mb-3"><i class="bi bi-exclamation-triangle me-2"></i>{{ c.error() }}</div>
              }
              @if (c.isEditing() && c.editId() !== null) {
                <div class="mb-3 text-muted small">{{ v.editandoTexto }} <code>{{ c.editId() }}</code></div>
              }
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label" for="cp-nombre">Nombre <span class="text-danger">*</span></label>
                  <input
                    id="cp-nombre"
                    class="form-control"
                    type="text"
                    [attr.maxlength]="v.nombreMaxLength"
                    [value]="c.form().nombre"
                    (input)="setNombre($any($event.target).value)"
                    required
                    appAutofocus
                    [placeholder]="v.nombrePlaceholder"
                  />
                </div>
                <div class="col-md-6">
                  <label class="form-label" for="cp-padre">{{ v.formPadreLabel }}</label>
                  <select id="cp-padre" class="form-select" (change)="setPadre($any($event.target).value)">
                    <option value="" [selected]="c.form().padre === ''">Sin asignar</option>
                    @for (p of c.padres(); track p.id) {
                      <option [value]="p.id" [selected]="'' + p.id === c.form().padre">{{ p.nombre }}</option>
                    }
                  </select>
                </div>
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
        [title]="v.eliminarTitulo"
        confirmLabel="Eliminar"
        confirmIcon="bi-trash-fill"
        confirmVariant="danger"
        [loading]="c.eliminarPending()"
        loadingLabel="Eliminando…"
        (confirm)="c.confirmarEliminar()"
        (hide)="c.confirmDeleteId.set(null)"
      >
        ¿Confirma eliminar {{ v.eliminarObjeto }}? Esta acción es <strong>permanente</strong>.<br />
        <small class="text-muted">{{ v.eliminarNota }}</small>
      </app-confirm-modal>
    </div>
  `,
})
export class CatalogoConPadreComponent {
  private readonly router = inject(Router);
  readonly ctl = input.required<CatalogoConPadre>();
  readonly vista = input.required<VistaCatalogoPadre>();

  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;

  protected volver(): void {
    void this.router.navigateByUrl('/admin/catalogos');
  }

  protected setNombre(nombre: string): void {
    this.ctl().form.update((p) => ({ ...p, nombre }));
  }

  protected setPadre(padre: string): void {
    this.ctl().form.update((p) => ({ ...p, padre }));
  }
}
