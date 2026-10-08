import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';
import { extractError } from '../../../shared/lib/extractError';
import {
  injectAsignarRol,
  injectBuscarUsuarios,
  injectUsuariosDeRol,
} from '../../../features/admin-asignaciones/model/queries';
import type { UsuarioCuentaItem } from '../../../features/admin-asignaciones/model/types';

export const PAGE_SIZE = 10 as const;

@Component({
  selector: 'app-usuarios-column',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="card border-0 shadow-sm h-100">
      <div class="card-header bg-white fw-semibold d-flex align-items-center">
        <i class="bi bi-people-fill me-2"></i>
        Usuarios del rol
      </div>
      <div class="d-flex gap-2 p-3 pb-2">
        <input
          class="form-control form-control-sm"
          placeholder="Filtrar por nombre o correo..."
          [value]="busca()"
          (input)="busca.set($any($event.target).value)"
          (keydown.enter)="aplicarBusqueda()"
          maxlength="200"
        />
        <button type="button" class="btn btn-sm btn-primary" (click)="aplicarBusqueda()">
          <i class="bi bi-search"></i>
        </button>
        @if (filtro()) {
          <button type="button" class="btn btn-sm btn-outline-secondary" (click)="limpiar()">
            <i class="bi bi-x-circle"></i>
          </button>
        }
      </div>

      <!-- Lista de usuarios del rol -->
      @if (lista.isLoading()) {
        <div class="text-center py-4"><div class="spinner-border" role="status"></div></div>
      } @else if (lista.isError()) {
        <div class="text-danger small px-3 py-4">Error al cargar los usuarios</div>
      } @else if ((lista.data()?.items ?? []).length === 0) {
        <div class="text-center py-4 text-muted">
          <i class="bi bi-inbox display-6 d-block mb-2"></i>
          Sin usuarios con este rol
        </div>
      } @else {
        <div class="list-group list-group-flush">
          @for (usr of lista.data()!.items; track usr.uid) {
            <button
              type="button"
              class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
              [class.active]="selectedUid() === usr.uid"
              (click)="selectUser.emit(usr)"
            >
              <span class="text-truncate">
                <span class="fw-semibold">{{ usr.nombre }}</span>
                <span class="small text-muted"> {{ usr.email }}</span>
              </span>
              <span class="badge" [class]="usr.activo ? 'bg-success' : 'bg-secondary'">
                {{ usr.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </button>
          }
        </div>
        <div class="d-flex align-items-center justify-content-between px-3 py-2 border-top">
          <div class="text-muted small">
            Pag. <strong>{{ page() }}</strong> de <strong>{{ totalPages() }}</strong> &middot; {{ lista.data()!.total }}
          </div>
          <div class="d-flex gap-2">
            <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() <= 1"
              (click)="page.set(page() - 1)">
              <i class="bi bi-chevron-left"></i>
            </button>
            <button type="button" class="btn btn-sm btn-outline-secondary" [disabled]="page() >= totalPages()"
              (click)="page.set(page() + 1)">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
      }

      <!-- Asignar nuevo usuario -->
      <div class="border-top p-3">
        <div class="fw-semibold small mb-2 text-muted">
          <i class="bi bi-person-plus-fill me-1"></i>
          Asignar nuevo usuario
        </div>
        <div class="d-flex gap-2 mb-2">
          <input
            class="form-control form-control-sm"
            placeholder="Buscar usuario por nombre o correo..."
            [value]="texto()"
            (input)="texto.set($any($event.target).value)"
            (keydown.enter)="filtroAsignar.set(texto().trim())"
            maxlength="200"
          />
          <button type="button" class="btn btn-sm btn-primary" (click)="filtroAsignar.set(texto().trim())">
            <i class="bi bi-search"></i>
          </button>
          @if (texto() || filtroAsignar()) {
            <button type="button" class="btn btn-sm btn-outline-secondary" (click)="texto.set(''); filtroAsignar.set('')">
              <i class="bi bi-x-circle"></i>
            </button>
          }
        </div>
        @if (filtroAsignar().length > 0) {
          @if (resultados.isLoading()) {
            <div class="text-center py-2">
              <span class="spinner-border spinner-border-sm" role="status"></span>
            </div>
          } @else if (candidatos().length === 0) {
            <div class="text-muted small">Sin coincidencias.</div>
          } @else {
            <div class="list-group">
              @for (usr of candidatos(); track usr.uid) {
                <div class="list-group-item d-flex justify-content-between align-items-center py-2">
                  <span class="small text-truncate">
                    <strong>{{ usr.nombre }}</strong>
                    <span class="text-muted"> {{ usr.email }}</span>
                  </span>
                  <button type="button" class="btn btn-sm btn-outline-success" [disabled]="asignar.isPending()"
                    (click)="handleAdd(usr)">
                    <i class="bi bi-person-check"></i>
                  </button>
                </div>
              }
            </div>
          }
        }
      </div>
    </div>
  `,
})
export class UsuariosColumnComponent {
  readonly rid = input.required<number>();
  readonly selectedUid = input<number | null>(null);
  readonly selectUser = output<UsuarioCuentaItem>();
  readonly toast = output<string>();
  readonly failed = output<string>();

  // ── Lista de usuarios del rol ──
  protected readonly page = signal<number>(1);
  protected readonly busca = signal<string>('');
  protected readonly filtro = signal<string>('');
  protected readonly lista = injectUsuariosDeRol(
    () => this.rid(),
    () => ({ page: this.page(), page_size: PAGE_SIZE, texto: this.filtro() || undefined }),
  );
  protected readonly totalPages = computed<number>(() => {
    const data = this.lista.data();
    return data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;
  });

  // ── Asignar nuevo usuario ──
  protected readonly texto = signal<string>('');
  protected readonly filtroAsignar = signal<string>('');
  protected readonly resultados = injectBuscarUsuarios(
    () => ({ page: 1, page_size: PAGE_SIZE, texto: this.filtroAsignar() || undefined }),
    () => this.filtroAsignar().length > 0,
  );
  protected readonly asignar = injectAsignarRol();
  private readonly asignados = signal<ReadonlySet<number>>(new Set<number>());
  protected readonly candidatos = computed<UsuarioCuentaItem[]>(() => {
    const excluidos = this.asignados();
    return (this.resultados.data()?.items ?? []).filter((usr) => !excluidos.has(usr.uid));
  });

  protected aplicarBusqueda(): void {
    this.filtro.set(this.busca().trim());
    this.page.set(1);
  }

  protected limpiar(): void {
    this.busca.set('');
    this.filtro.set('');
    this.page.set(1);
  }

  protected async handleAdd(usr: UsuarioCuentaItem): Promise<void> {
    try {
      await this.asignar.mutateAsync({ uid: usr.uid, rid: this.rid() });
      this.asignados.update((prev) => new Set(prev).add(usr.uid));
      this.toast.emit(`Rol asignado a ${usr.nombre}`);
      this.selectUser.emit(usr);
    } catch (err) {
      this.failed.emit(extractError(err, 'No se pudo asignar el rol'));
    }
  }
}
