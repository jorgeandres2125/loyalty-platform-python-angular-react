import { ChangeDetectionStrategy, Component, effect, signal } from '@angular/core';
import { injectRolesList } from '../../../features/admin-autorizaciones/model/queries';
import { RolPermisosPanelComponent } from './rol-permisos-panel.component';

@Component({
  selector: 'app-permisos-modulos-tab',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RolPermisosPanelComponent],
  template: `
    <div>
      @if (success()) {
        <div class="alert alert-success alert-dismissible">
          <i class="bi bi-check-circle me-2"></i>
          {{ success() }}
          <button type="button" class="btn-close" aria-label="Close" (click)="success.set('')"></button>
        </div>
      }
      @if (error()) {
        <div class="alert alert-danger alert-dismissible">
          <i class="bi bi-exclamation-triangle me-2"></i>
          {{ error() }}
          <button type="button" class="btn-close" aria-label="Close" (click)="error.set('')"></button>
        </div>
      }

      @if (roles.isLoading()) {
        <div class="text-center py-5"><div class="spinner-border" role="status"></div></div>
      } @else {
        <div class="d-flex flex-column gap-2">
          @for (r of roles.data() ?? []; track r.rid) {
            <app-rol-permisos-panel
              [rid]="r.rid"
              [name]="r.name"
              (saved)="success.set($event)"
              (failed)="error.set($event)"
            />
          }
        </div>
      }
    </div>
  `,
})
export class PermisosModulosTabComponent {
  protected readonly roles = injectRolesList();
  protected readonly success = signal<string>('');
  protected readonly error = signal<string>('');

  constructor() {
    effect((onCleanup) => {
      if (!this.success()) return;
      const t = setTimeout(() => this.success.set(''), 3000);
      onCleanup(() => clearTimeout(t));
    });
  }
}
