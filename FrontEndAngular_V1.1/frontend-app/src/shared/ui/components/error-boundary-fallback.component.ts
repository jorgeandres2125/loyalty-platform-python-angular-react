import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';

@Component({
  selector: 'app-error-boundary-fallback',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="d-flex flex-column align-items-center justify-content-center py-5 px-4 text-center">
      <i class="bi bi-exclamation-triangle-fill text-warning" style="font-size: 3rem"></i>
      <h5 class="mt-3 fw-bold">Ocurrió un error</h5>
      <p class="text-muted small mb-3">{{ error()?.message ?? 'Error inesperado' }}</p>
      @if (resettable()) {
        <button class="btn btn-outline-primary btn-sm" (click)="reset.emit()">
          <i class="bi bi-arrow-clockwise me-1"></i>
          Reintentar
        </button>
      }
    </div>
  `,
})
export class ErrorBoundaryFallbackComponent {
  readonly error = input<Error | undefined>(undefined);
  readonly resettable = input<boolean>(false);
  readonly reset = output<void>();
}
