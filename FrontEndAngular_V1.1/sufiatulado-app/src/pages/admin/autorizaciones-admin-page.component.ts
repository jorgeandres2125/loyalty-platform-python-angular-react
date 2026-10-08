import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { PermisosModulosTabComponent } from './autorizaciones/permisos-modulos-tab.component';
import { UsuariosRolesTabComponent } from './autorizaciones/usuarios-roles-tab.component';

type TabAutorizaciones = 'permisos' | 'usuarios-roles';

@Component({
  selector: 'app-autorizaciones-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, PermisosModulosTabComponent, UsuariosRolesTabComponent],
  template: `
    <div>
      <app-page-header
        title="Autorizaciones de usuarios"
        subtitle="Parametriza los permisos de cada rol sobre los módulos y la asignación de roles a los usuarios."
        icon="bi-shield-lock-fill"
        backTo="/admin/dashboard"
      />

      <ul class="nav nav-tabs mb-3" role="tablist">
        <li class="nav-item" role="presentation">
          <button type="button" role="tab" class="nav-link" [class.active]="tab() === 'permisos'"
            [attr.aria-selected]="tab() === 'permisos'" (click)="seleccionar('permisos')">
            Permisos sobre módulos
          </button>
        </li>
        <li class="nav-item" role="presentation">
          <button type="button" role="tab" class="nav-link" [class.active]="tab() === 'usuarios-roles'"
            [attr.aria-selected]="tab() === 'usuarios-roles'" (click)="seleccionar('usuarios-roles')">
            Usuarios &amp; Roles
          </button>
        </li>
      </ul>

      <!-- mountOnEnter: cada pestaña se monta la primera vez que se visita y se conserva -->
      <div class="tab-content">
        @if (montadas().has('permisos')) {
          <div class="tab-pane fade" [class.show]="tab() === 'permisos'" [class.active]="tab() === 'permisos'" role="tabpanel">
            <app-permisos-modulos-tab />
          </div>
        }
        @if (montadas().has('usuarios-roles')) {
          <div class="tab-pane fade" [class.show]="tab() === 'usuarios-roles'" [class.active]="tab() === 'usuarios-roles'" role="tabpanel">
            <app-usuarios-roles-tab />
          </div>
        }
      </div>
    </div>
  `,
})
export class AutorizacionesAdminPageComponent {
  protected readonly tab = signal<TabAutorizaciones>('permisos');
  protected readonly montadas = signal<ReadonlySet<TabAutorizaciones>>(new Set(['permisos']));

  protected seleccionar(tab: TabAutorizaciones): void {
    this.tab.set(tab);
    this.montadas.update((prev) => new Set([...prev, tab]));
  }
}
