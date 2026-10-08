import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';

interface SettingItem {
  icon: string;
  color: string;
  title: string;
  subtitle: string;
  to: string;
  disabled?: boolean;
}

const ITEMS: SettingItem[] = [
  {
    icon: 'bi-lock-fill',
    color: '#FF0026',
    title: 'Cambiar Contraseña',
    subtitle: 'Actualiza tus credenciales de acceso',
    to: '/configuraciones/cambio_contrasena',
  },
  {
    icon: 'bi-laptop',
    color: '#0D6EFD',
    title: 'Mis Sesiones',
    subtitle: 'Consulta y cierra tus sesiones activas',
    to: '/configuraciones/sesiones',
  },
];

@Component({
  selector: 'app-configuraciones-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent],
  template: `
    <div class="configuraciones-page">
      <app-page-header title="Cuenta" icon="bi-person-fill-gear" backTo="/admin/dashboard" />

      <div class="configuraciones-page__list">
        @for (item of items; track item.to) {
          <button
            class="configuraciones-page__item"
            (click)="ir(item.to)"
            [disabled]="item.disabled ?? false"
          >
            <span class="configuraciones-page__item-icon" [style.background]="item.color">
              <i class="bi" [class]="item.icon"></i>
            </span>
            <span class="configuraciones-page__item-body">
              <span class="configuraciones-page__item-title">{{ item.title }}</span>
              <span class="configuraciones-page__item-subtitle">{{ item.subtitle }}</span>
            </span>
            <i class="bi bi-chevron-right configuraciones-page__item-arrow"></i>
          </button>
        }
      </div>
    </div>
  `,
})
export class ConfiguracionesPageComponent {
  private readonly router = inject(Router);
  protected readonly items = ITEMS;

  protected ir(to: string): void {
    void this.router.navigateByUrl(to);
  }
}
