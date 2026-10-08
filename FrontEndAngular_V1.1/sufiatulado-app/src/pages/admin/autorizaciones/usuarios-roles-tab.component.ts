import { ChangeDetectionStrategy, Component, effect, signal } from '@angular/core';
import { EmptyStateComponent } from '../../../shared/ui/components/empty-state.component';
import { injectRolesAsignables } from '../../../features/admin-asignaciones/model/queries';
import type { UsuarioCuentaItem } from '../../../features/admin-asignaciones/model/types';
import { UsuariosColumnComponent } from './usuarios-column.component';
import { DetalleColumnComponent } from './detalle-column.component';

@Component({
  selector: 'app-usuarios-roles-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [EmptyStateComponent, UsuariosColumnComponent, DetalleColumnComponent],
  template: `
    <div>
      @if (success()) {
        <div class="alert alert-success d-flex align-items-center" role="alert">
          <i class="bi bi-check-circle me-2"></i>
          {{ success() }}
        </div>
      }
      @if (error()) {
        <div class="alert alert-danger d-flex align-items-center" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>
          <span>{{ error() }}</span>
          <button type="button" class="btn-close ms-auto" (click)="error.set('')"></button>
        </div>
      }

      <div class="d-flex flex-column flex-lg-row gap-3 align-items-stretch">
        <!-- Roles -->
        <div class="flex-shrink-0" style="flex-basis: 25%">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white fw-semibold">
              <i class="bi bi-shield-lock-fill me-2"></i>
              Roles
            </div>
            <div class="card-body p-2">
              @if (roles.isLoading()) {
                <div class="text-center py-4"><div class="spinner-border" role="status"></div></div>
              } @else {
                <div class="list-group list-group-flush">
                  @for (rol of roles.data() ?? []; track rol.rid) {
                    @let activo = selectedRid() === rol.rid;
                    <button
                      type="button"
                      class="list-group-item list-group-item-action rounded mb-1 d-flex justify-content-between align-items-center"
                      [class.active]="activo"
                      (click)="handleSelectRol(rol.rid)"
                    >
                      <span class="fw-semibold text-truncate">{{ rol.name }}</span>
                      <span class="badge" [class]="activo ? 'bg-light text-dark' : 'bg-secondary'">#{{ rol.rid }}</span>
                    </button>
                  }
                </div>
              }
            </div>
          </div>
        </div>

        <!-- Usuarios del rol -->
        <div style="flex-basis: 45%; min-width: 0">
          @if (selectedRid() === null) {
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body d-flex align-items-center justify-content-center">
                <app-empty-state
                  icon="bi-arrow-left-circle"
                  title="Selecciona un rol"
                  description="Elige un rol de la izquierda para ver y gestionar sus usuarios."
                />
              </div>
            </div>
          } @else {
            <!-- track por rid: al cambiar de rol se recrea la columna (como key en React) -->
            @for (rid of [selectedRid()!]; track rid) {
              <div class="anim-fade-in h-100">
                <app-usuarios-column
                  [rid]="rid"
                  [selectedUid]="selectedUser()?.uid ?? null"
                  (selectUser)="selectedUser.set($event)"
                  (toast)="success.set($event)"
                  (failed)="error.set($event)"
                />
              </div>
            }
          }
        </div>

        <!-- Detalle del usuario -->
        <div style="flex-basis: 30%; min-width: 0">
          @if (selectedUser(); as usr) {
            @for (uid of [usr.uid]; track uid) {
              <div class="anim-slide-in h-100">
                <app-detalle-column [user]="usr" (toast)="success.set($event)" (failed)="error.set($event)" />
              </div>
            }
          } @else {
            <div class="anim-fade-in h-100">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body d-flex align-items-center justify-content-center">
                  <app-empty-state
                    icon="bi-person-lines-fill"
                    title="Sin usuario seleccionado"
                    description="Selecciona un usuario para ver su detalle y gestionar sus roles"
                  />
                </div>
              </div>
            </div>
          }
        </div>
      </div>
    </div>
  `,
  styles: `
    .anim-fade-in {
      animation: roles-fade-in 0.25s ease both;
    }
    .anim-slide-in {
      animation: roles-slide-in 0.25s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
    @keyframes roles-fade-in {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    @keyframes roles-slide-in {
      from { opacity: 0; transform: translateX(30px); }
      to { opacity: 1; transform: translateX(0); }
    }
  `,
})
export class UsuariosRolesTabComponent {
  protected readonly roles = injectRolesAsignables();
  protected readonly selectedRid = signal<number | null>(null);
  protected readonly selectedUser = signal<UsuarioCuentaItem | null>(null);
  protected readonly success = signal<string>('');
  protected readonly error = signal<string>('');

  constructor() {
    effect((onCleanup) => {
      if (!this.success()) return;
      const t = setTimeout(() => this.success.set(''), 3000);
      onCleanup(() => clearTimeout(t));
    });
  }

  protected handleSelectRol(rid: number): void {
    this.selectedRid.set(rid);
    this.selectedUser.set(null);
  }
}
