import { ChangeDetectionStrategy, Component, computed, effect, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { ConfirmModalComponent } from '../../shared/ui/components/confirm-modal.component';
import { PasswordTemporalResultadoModalComponent } from './password-temporal-resultado-modal.component';
import { extractError } from '../../shared/lib/extractError';
import {
  injectAdminUsuariosList,
  injectCambiarEstadoUsuario,
  injectEmitirPasswordTemporal,
} from '../../features/admin-usuarios/model/queries';
import type {
  PasswordTemporalResultado,
  UsuarioListItem,
} from '../../features/admin-usuarios/model/types';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

type FiltroEstado = 'todos' | 'activos' | 'inactivos';

const ESTADO_QUERY: Record<FiltroEstado, boolean | undefined> = {
  todos: undefined,
  activos: true,
  inactivos: false,
};

@Component({
  selector: 'app-usuarios-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, ConfirmModalComponent, PasswordTemporalResultadoModalComponent],
  template: `
    <div>
      <app-page-header title="Gestión de Cuentas" [subtitle]="subtitulo()" icon="bi-person-fill-gear" />

      <div class="mb-3">
        <button type="button" class="btn btn-sm btn-outline-secondary" (click)="volver()">
          <i class="bi bi-arrow-left me-1"></i>Volver
        </button>
      </div>

      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          @if (success()) {
            <div class="px-3 pt-3">
              <div class="alert alert-success alert-dismissible mb-0">
                <i class="bi bi-check-circle me-2"></i>{{ success() }}
                <button type="button" class="btn-close" aria-label="Close" (click)="success.set('')"></button>
              </div>
            </div>
          }
          @if (error()) {
            <div class="px-3 pt-3">
              <div class="alert alert-danger alert-dismissible mb-0">
                <i class="bi bi-exclamation-triangle me-2"></i>{{ error() }}
                <button type="button" class="btn-close" aria-label="Close" (click)="error.set('')"></button>
              </div>
            </div>
          }

          <div class="d-flex align-items-end justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
            <div class="d-flex align-items-end gap-2 flex-wrap">
              <div style="min-width: 260px">
                <label class="form-label small mb-1">Usuario o correo</label>
                <input
                  class="form-control form-control-sm"
                  type="text"
                  placeholder="Filtrar por nombre o email..."
                  [value]="searchTexto()"
                  (input)="searchTexto.set($any($event.target).value)"
                  (keydown.enter)="handleBuscar()"
                  maxlength="200"
                />
              </div>
              <div style="min-width: 140px">
                <label class="form-label small mb-1">Estado</label>
                <select class="form-select form-select-sm" (change)="setFiltroEstado($any($event.target).value)">
                  <option value="todos" [selected]="filtroEstado() === 'todos'">Todos</option>
                  <option value="activos" [selected]="filtroEstado() === 'activos'">Activos</option>
                  <option value="inactivos" [selected]="filtroEstado() === 'inactivos'">Inactivos</option>
                </select>
              </div>
              <button type="button" class="btn btn-sm btn-primary" (click)="handleBuscar()">
                <i class="bi bi-search me-1"></i>Buscar
              </button>
              @if (filtrosActivos()) {
                <button type="button" class="btn btn-sm btn-outline-secondary" (click)="handleLimpiar()">
                  <i class="bi bi-x-circle me-1"></i>Limpiar
                </button>
              }
            </div>
            <div style="min-width: 80px">
              <label class="form-label small mb-1">Mostrar</label>
              <select class="form-select form-select-sm" (change)="setPageSize(+$any($event.target).value)">
                @for (size of pageSizeOptions; track size) {
                  <option [value]="size" [selected]="size === pageSize()">{{ size }}</option>
                }
              </select>
            </div>
          </div>

          @if (lista.isLoading()) {
            <div class="text-center py-5"><div class="spinner-border" role="status"></div></div>
          } @else if (lista.isError()) {
            <div class="alert alert-danger m-3">Error al cargar las cuentas</div>
          } @else if (!lista.data() || lista.data()!.items.length === 0) {
            <div class="text-center py-5 text-muted">
              <i class="bi bi-inbox display-4 d-block mb-2"></i>No se encontraron cuentas
            </div>
          } @else {
            <div class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th style="width: 90px">UID</th>
                    <th>Usuario</th>
                    <th>Correo</th>
                    <th>Roles</th>
                    <th style="width: 110px">Estado</th>
                    <th class="text-end" style="width: 280px">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  @for (u of lista.data()!.items; track u.uid) {
                    <tr>
                      <td><code>{{ u.uid }}</code></td>
                      <td class="fw-semibold">{{ u.nombre }}</td>
                      <td class="small">
                        @if (u.email) {
                          {{ u.email }}
                        } @else {
                          <span class="text-muted">—</span>
                        }
                      </td>
                      <td>
                        @if (u.roles.length > 0) {
                          <span class="d-flex flex-wrap gap-1">
                            @for (rol of u.roles; track rol) {
                              <span class="badge bg-light text-dark border">{{ rol }}</span>
                            }
                          </span>
                        } @else {
                          <span class="text-muted small">—</span>
                        }
                      </td>
                      <td>
                        <span class="badge" [class]="u.activo ? 'bg-success' : 'bg-secondary'">
                          {{ u.activo ? 'Activo' : 'Inactivo' }}
                        </span>
                      </td>
                      <td class="text-end">
                        <button
                          type="button"
                          class="btn btn-sm btn-outline-primary me-2"
                          title="Generar contrasena temporal (AP-0047)"
                          (click)="temporalObjetivo.set(u)"
                        >
                          <i class="bi bi-key me-1"></i>Temporal
                        </button>
                        @if (u.activo) {
                          <button type="button" class="btn btn-sm btn-outline-danger" (click)="objetivo.set(u)">
                            <i class="bi bi-person-fill-slash me-1"></i>Deshabilitar
                          </button>
                        } @else {
                          <button type="button" class="btn btn-sm btn-outline-success" (click)="objetivo.set(u)">
                            <i class="bi bi-person-fill-check me-1"></i>Habilitar
                          </button>
                        }
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
            <div class="d-flex align-items-center justify-content-between px-3 py-3 border-top">
              <div class="text-muted small">
                Página <strong>{{ page() }}</strong> de <strong>{{ totalPages() }}</strong> —
                {{ lista.data()!.total }} resultados
              </div>
              <div class="d-flex gap-2">
                <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() <= 1"
                  (click)="page.set(page() - 1)">
                  <i class="bi bi-chevron-left me-1"></i>Anterior
                </button>
                <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() >= totalPages()"
                  (click)="page.set(page() + 1)">
                  Siguiente<i class="bi bi-chevron-right ms-1"></i>
                </button>
              </div>
            </div>
          }
        </div>
      </div>

      <app-confirm-modal
        [show]="objetivo() !== null"
        [title]="vaDeshabilitar() ? 'Deshabilitar cuenta' : 'Habilitar cuenta'"
        [confirmLabel]="vaDeshabilitar() ? 'Deshabilitar' : 'Habilitar'"
        [confirmIcon]="vaDeshabilitar() ? 'bi-person-fill-slash' : 'bi-person-fill-check'"
        [confirmVariant]="vaDeshabilitar() ? 'danger' : 'success'"
        [loading]="cambiarEstadoMut.isPending()"
        loadingLabel="Guardando…"
        (confirm)="handleConfirm()"
        (hide)="objetivo.set(null)"
      >
        @if (objetivo(); as o) {
          ¿Confirma {{ vaDeshabilitar() ? 'deshabilitar' : 'habilitar' }} la cuenta de <strong>{{ o.nombre }}</strong>?
          @if (vaDeshabilitar()) {
            <br /><small class="text-muted">El usuario no podrá iniciar sesión hasta que sea habilitado de nuevo.</small>
          }
        }
      </app-confirm-modal>

      <app-confirm-modal
        [show]="temporalObjetivo() !== null"
        title="Generar contrasena temporal"
        confirmLabel="Generar"
        confirmIcon="bi-key"
        confirmVariant="primary"
        [loading]="emitirTemporalMut.isPending()"
        loadingLabel="Generando…"
        (confirm)="handleEmitirTemporal()"
        (hide)="temporalObjetivo.set(null)"
      >
        @if (temporalObjetivo(); as t) {
          Se generara una contrasena temporal para <strong>{{ t.nombre }}</strong>.
          <br />
          <small class="text-muted">
            Reemplaza cualquier temporal vigente, tiene vigencia limitada y el usuario
            debera definir su contrasena personal en el primer ingreso.
          </small>
        }
      </app-confirm-modal>

      <app-password-temporal-resultado-modal
        [resultado]="temporalResultado()"
        (cerrar)="temporalResultado.set(null)"
      />
    </div>
  `,
})
export class UsuariosAdminPageComponent {
  private readonly router = inject(Router);

  protected readonly pageSizeOptions = PAGE_SIZE_OPTIONS;

  protected readonly page = signal<number>(1);
  protected readonly pageSize = signal<number>(10);
  protected readonly searchTexto = signal<string>('');
  protected readonly filtroTexto = signal<string>('');
  protected readonly filtroEstado = signal<FiltroEstado>('todos');

  protected readonly objetivo = signal<UsuarioListItem | null>(null);
  protected readonly temporalObjetivo = signal<UsuarioListItem | null>(null);
  protected readonly temporalResultado = signal<PasswordTemporalResultado | null>(null);
  protected readonly error = signal<string>('');
  protected readonly success = signal<string>('');

  protected readonly lista = injectAdminUsuariosList(() => ({
    page: this.page(),
    page_size: this.pageSize(),
    texto: this.filtroTexto() || undefined,
    activo: ESTADO_QUERY[this.filtroEstado()],
  }));
  protected readonly cambiarEstadoMut = injectCambiarEstadoUsuario();
  protected readonly emitirTemporalMut = injectEmitirPasswordTemporal();

  protected readonly filtrosActivos = computed<boolean>(
    () => !!this.filtroTexto() || this.filtroEstado() !== 'todos',
  );
  protected readonly totalPages = computed<number>(() => {
    const data = this.lista.data();
    return data ? Math.max(1, Math.ceil(data.total / this.pageSize())) : 1;
  });
  protected readonly vaDeshabilitar = computed<boolean>(() => {
    const o = this.objetivo();
    return o !== null && o.activo;
  });
  protected readonly subtitulo = computed<string | undefined>(() => {
    const data = this.lista.data();
    if (!data) return undefined;
    return `${data.total} cuenta${data.total === 1 ? '' : 's'}${this.filtrosActivos() ? ' encontradas' : ''}`;
  });

  constructor() {
    effect((onCleanup) => {
      if (!this.success()) return;
      const timeoutId = setTimeout(() => this.success.set(''), 3500);
      onCleanup(() => clearTimeout(timeoutId));
    });
  }

  protected volver(): void {
    void this.router.navigateByUrl('/admin/dashboard');
  }

  protected setFiltroEstado(valor: string): void {
    this.filtroEstado.set(valor as FiltroEstado);
    this.page.set(1);
  }

  protected setPageSize(n: number): void {
    this.pageSize.set(n);
    this.page.set(1);
  }

  protected handleBuscar(): void {
    this.filtroTexto.set(this.searchTexto().trim());
    this.page.set(1);
  }

  protected handleLimpiar(): void {
    this.searchTexto.set('');
    this.filtroTexto.set('');
    this.filtroEstado.set('todos');
    this.page.set(1);
  }

  protected async handleConfirm(): Promise<void> {
    const objetivo = this.objetivo();
    if (objetivo === null) return;
    this.error.set('');
    try {
      const resultado = await this.cambiarEstadoMut.mutateAsync({
        uid: objetivo.uid,
        payload: { activo: !objetivo.activo },
      });
      this.success.set(
        resultado.activo
          ? `Cuenta de ${resultado.nombre} habilitada`
          : `Cuenta de ${resultado.nombre} deshabilitada`,
      );
    } catch (err) {
      this.error.set(extractError(err, 'No se pudo cambiar el estado de la cuenta'));
    } finally {
      this.objetivo.set(null);
    }
  }

  protected async handleEmitirTemporal(): Promise<void> {
    const objetivo = this.temporalObjetivo();
    if (objetivo === null) return;
    this.error.set('');
    try {
      const resultado = await this.emitirTemporalMut.mutateAsync({ uid: objetivo.uid });
      this.temporalResultado.set(resultado);
    } catch (err) {
      this.error.set(extractError(err, 'No se pudo generar la contrasena temporal'));
    } finally {
      this.temporalObjetivo.set(null);
    }
  }
}
