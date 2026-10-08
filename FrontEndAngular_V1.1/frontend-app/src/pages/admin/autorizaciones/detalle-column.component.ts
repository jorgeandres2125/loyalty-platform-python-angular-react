import { ChangeDetectionStrategy, Component, computed, input, output, signal } from '@angular/core';
import {
  CdkDrag,
  CdkDropList,
  CdkDropListGroup,
  type CdkDragDrop,
} from '@angular/cdk/drag-drop';
import { ConfirmModalComponent } from '../../../shared/ui/components/confirm-modal.component';
import { extractError } from '../../../shared/lib/extractError';
import {
  injectAsignarRol,
  injectQuitarRol,
  injectRolesDeUsuario,
} from '../../../features/admin-asignaciones/model/queries';
import type {
  RolDeUsuarioItem,
  UsuarioCuentaItem,
} from '../../../features/admin-asignaciones/model/types';

const CRITICAL_ROLES: ReadonlySet<string> = new Set(['administrator', 'webmaster']);

function isCriticalRole(name: string): boolean {
  return CRITICAL_ROLES.has(name.trim().toLowerCase());
}

const ZONE_ASIGNADOS = 'zona-asignados';
const ZONE_DISPONIBLES = 'zona-disponibles';

interface ZonaRoles {
  id: string;
  variante: 'asignados' | 'disponibles';
  titulo: string;
  icono: string;
  vacioTexto: string;
}

const ZONAS: readonly ZonaRoles[] = [
  {
    id: ZONE_ASIGNADOS,
    variante: 'asignados',
    titulo: 'Roles asignados',
    icono: 'bi-person-check-fill',
    vacioTexto: 'Arrastra aqui los roles para asignarlos al usuario',
  },
  {
    id: ZONE_DISPONIBLES,
    variante: 'disponibles',
    titulo: 'Roles disponibles',
    icono: 'bi-collection',
    vacioTexto: 'El usuario ya tiene todos los roles',
  },
];

/**
 * Detalle del usuario + gestión de roles por arrastrar y soltar. El `@dnd-kit` del
 * original se sustituye por Angular CDK Drag & Drop (dos listas conectadas).
 */
@Component({
  selector: 'app-detalle-column',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [CdkDropListGroup, CdkDropList, CdkDrag, ConfirmModalComponent],
  template: `
    @let usr = user();
    <div class="card border-0 shadow-sm h-100">
      <div class="card-header bg-white fw-semibold">
        <i class="bi bi-person-badge me-2"></i>
        Detalle del usuario
      </div>
      <div class="card-body">
        <div class="mb-2">
          <div class="fw-bold fs-6 text-truncate">{{ usr.nombre }}</div>
          <div class="small text-muted text-truncate">{{ usr.email || '—' }}</div>
          <span class="badge mt-1" [class]="usr.activo ? 'bg-success' : 'bg-secondary'">
            {{ usr.activo ? 'Activo' : 'Inactivo' }}
          </span>
          <span class="small text-muted ms-2">UID {{ usr.uid }}</span>
        </div>
        <hr />
        <div class="fw-semibold small mb-1">Gestion de roles</div>
        <p class="text-muted roles-dnd__hint">
          Arrastra un rol entre las listas (o usa los botones) para asignarlo o quitarlo. Revocar un rol critico pide confirmacion.
        </p>
        @if (rolesQuery.isLoading()) {
          <div class="text-center py-3"><div class="spinner-border" role="status"></div></div>
        } @else if (rolesQuery.isError()) {
          <div class="text-danger small">Error al cargar los roles</div>
        } @else {
          <div class="roles-dnd" cdkDropListGroup>
            @for (zona of zonas; track zona.id) {
              @let roles = zona.variante === 'asignados' ? asignados() : disponibles();
              <section
                cdkDropList
                [id]="zona.id"
                [cdkDropListData]="roles"
                cdkDropListSortingDisabled
                (cdkDropListEntered)="zonaSobre.set(zona.id)"
                (cdkDropListExited)="zonaSobre.set(null)"
                (cdkDropListDropped)="onDrop($event)"
                class="roles-dnd__zone"
                [class]="'roles-dnd__zone--' + zona.variante"
                [class.is-over]="zonaSobre() === zona.id"
                [attr.aria-label]="zona.titulo"
              >
                <header class="roles-dnd__zone-head">
                  <i class="bi" [class]="zona.icono" aria-hidden="true"></i>
                  <span class="roles-dnd__zone-title">{{ zona.titulo }}</span>
                  <span class="roles-dnd__count">{{ roles.length }}</span>
                </header>
                @if (roles.length === 0) {
                  <p class="roles-dnd__empty">
                    <i class="bi bi-arrow-down-square me-1" aria-hidden="true"></i>
                    {{ zona.vacioTexto }}
                  </p>
                } @else {
                  <ul class="roles-dnd__list">
                    @for (rol of roles; track rol.rid) {
                      @let critico = esCritico(rol.name);
                      @let haciaAsignados = zona.variante !== 'asignados';
                      <li
                        cdkDrag
                        [cdkDragData]="rol"
                        [cdkDragDisabled]="cargando()"
                        (cdkDragStarted)="arrastrando.set(rol.rid)"
                        (cdkDragEnded)="arrastrando.set(null)"
                        class="roles-dnd__chip"
                        [class.is-dragging]="arrastrando() === rol.rid"
                        [class.is-critico]="critico"
                      >
                        <span class="roles-dnd__grip" aria-hidden="true">
                          <i class="bi bi-grip-vertical"></i>
                        </span>
                        <i
                          class="bi roles-dnd__chip-ico"
                          [class]="critico ? 'bi-shield-lock-fill' : 'bi-person-badge'"
                          aria-hidden="true"
                        ></i>
                        <span class="roles-dnd__chip-name" [title]="rol.name">{{ rol.name }}</span>
                        <span class="roles-dnd__chip-rid">#{{ rol.rid }}</span>
                        <button
                          type="button"
                          class="roles-dnd__chip-btn"
                          [disabled]="cargando()"
                          (mousedown)="$event.stopPropagation()"
                          (touchstart)="$event.stopPropagation()"
                          (click)="mover(rol, haciaAsignados)"
                          [attr.aria-label]="(haciaAsignados ? 'Asignar rol ' : 'Quitar rol ') + rol.name"
                          [title]="(haciaAsignados ? 'Asignar rol ' : 'Quitar rol ') + rol.name"
                        >
                          <i class="bi" [class]="haciaAsignados ? 'bi-plus-lg' : 'bi-dash-lg'"></i>
                        </button>
                      </li>
                    }
                  </ul>
                }
              </section>
            }
          </div>
        }
      </div>
      <app-confirm-modal
        [show]="pendingRol() !== null"
        title="Revocar rol critico"
        [message]="mensajeRevocar()"
        confirmLabel="Revocar"
        confirmIcon="bi-shield-x"
        confirmVariant="danger"
        [loading]="quitar.isPending()"
        loadingLabel="Revocando..."
        (confirm)="confirmar()"
        (hide)="pendingRol.set(null)"
      />
    </div>
  `,
})
export class DetalleColumnComponent {
  readonly user = input.required<UsuarioCuentaItem>();
  readonly toast = output<string>();
  readonly failed = output<string>();

  protected readonly zonas = ZONAS;
  protected readonly rolesQuery = injectRolesDeUsuario(() => this.user().uid);
  private readonly asignar = injectAsignarRol();
  protected readonly quitar = injectQuitarRol();
  protected readonly pendingRol = signal<RolDeUsuarioItem | null>(null);
  protected readonly zonaSobre = signal<string | null>(null);
  protected readonly arrastrando = signal<number | null>(null);

  private readonly allRoles = computed<RolDeUsuarioItem[]>(() => this.rolesQuery.data() ?? []);
  protected readonly asignados = computed<RolDeUsuarioItem[]>(() => this.allRoles().filter((r) => r.asignado));
  protected readonly disponibles = computed<RolDeUsuarioItem[]>(() =>
    this.allRoles().filter((r) => !r.asignado),
  );
  protected readonly cargando = computed<boolean>(() => this.asignar.isPending() || this.quitar.isPending());
  protected readonly mensajeRevocar = computed<string>(() => {
    const rol = this.pendingRol();
    return rol
      ? `El rol "${rol.name}" otorga privilegios elevados. Confirmas retirarlo de ${this.user().nombre}?`
      : '';
  });

  protected esCritico(name: string): boolean {
    return isCriticalRole(name);
  }

  private async aplicarAsignar(rol: RolDeUsuarioItem): Promise<void> {
    try {
      await this.asignar.mutateAsync({ uid: this.user().uid, rid: rol.rid });
      this.toast.emit(`Rol "${rol.name}" asignado`);
    } catch (err) {
      this.failed.emit(extractError(err, 'No se pudo asignar el rol'));
    }
  }

  private async aplicarQuitar(rol: RolDeUsuarioItem): Promise<void> {
    try {
      await this.quitar.mutateAsync({ uid: this.user().uid, rid: rol.rid });
      this.toast.emit(`Rol "${rol.name}" retirado`);
    } catch (err) {
      this.failed.emit(extractError(err, 'No se pudo quitar el rol'));
    }
  }

  protected mover(rol: RolDeUsuarioItem, haciaAsignados: boolean): void {
    if (haciaAsignados && !rol.asignado) {
      void this.aplicarAsignar(rol);
    } else if (!haciaAsignados && rol.asignado) {
      if (isCriticalRole(rol.name)) this.pendingRol.set(rol);
      else void this.aplicarQuitar(rol);
    }
  }

  protected onDrop(event: CdkDragDrop<RolDeUsuarioItem[]>): void {
    this.zonaSobre.set(null);
    // Solo cuenta el movimiento entre listas; soltar en la misma zona no hace nada.
    if (event.previousContainer === event.container) return;
    const info = event.item.data as RolDeUsuarioItem;
    const rol: RolDeUsuarioItem | undefined = this.allRoles().find((r) => r.rid === info.rid);
    if (rol) this.mover(rol, event.container.id === ZONE_ASIGNADOS);
  }

  protected async confirmar(): Promise<void> {
    const rol = this.pendingRol();
    if (!rol) return;
    await this.aplicarQuitar(rol);
    this.pendingRol.set(null);
  }
}
