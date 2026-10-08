import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink],
  template: `
    <div
      class="d-flex flex-column align-items-center justify-content-center text-center"
      style="min-height: 70vh"
    >
      <div style="font-size: 5rem; font-weight: 800; color: #FF0026; line-height: 1">404</div>
      <h4 class="mt-3 fw-bold" style="color: #333241">Página no encontrada</h4>
      <p class="text-muted mb-4">La URL que ingresaste no existe o no tienes permiso de acceso.</p>
      <a routerLink="/dashboard" class="btn btn-primary">
        <i class="bi bi-house me-2"></i>
        Ir al Dashboard
      </a>
    </div>
  `,
})
export class NotFoundPageComponent {}
