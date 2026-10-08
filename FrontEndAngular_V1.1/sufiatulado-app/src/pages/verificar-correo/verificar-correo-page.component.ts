import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { BrandLogoComponent } from '../../shared/ui/components/brand-logo.component';
import { VerificacionEmailFormComponent } from '../../features/verificacion-email/ui/verificacion-email-form.component';

@Component({
  selector: 'app-verificar-correo-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, BrandLogoComponent, VerificacionEmailFormComponent],
  template: `
    <div
      class="d-flex flex-column align-items-center justify-content-center min-vh-100 px-3"
      style="background: #F4F5FA"
    >
      <div style="width: 100%; max-width: 440px">
        <div class="text-center mb-3">
          <app-brand-logo [height]="32" />
        </div>
        <div class="bg-white rounded-4 shadow-sm p-4 p-md-5">
          <app-verificacion-email-form />
        </div>
        <div class="text-center mt-3">
          <a routerLink="/login" class="text-decoration-none text-muted" style="font-size: 0.85rem">
            <i class="bi bi-arrow-left me-1"></i>
            Volver al inicio de sesión
          </a>
        </div>
      </div>
    </div>
  `,
})
export class VerificarCorreoPageComponent {}
