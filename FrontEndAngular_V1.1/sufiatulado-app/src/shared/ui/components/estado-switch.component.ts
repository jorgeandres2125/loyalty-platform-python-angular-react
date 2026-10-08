import { ChangeDetectionStrategy, Component, input, model } from '@angular/core';

/** Interruptor de estado Activo/Inactivo. Soporta `[(checked)]`. */
@Component({
  selector: 'app-estado-switch',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (compact()) {
      <div
        class="form-check form-switch mb-0"
        [class]="className()"
        [title]="checked() ? labelActivo() : labelInactivo()"
        style="transform: scale(1.3); transform-origin: center center"
      >
        <input
          class="form-check-input"
          type="checkbox"
          role="switch"
          [id]="id()"
          [checked]="checked()"
          [disabled]="disabled()"
          (change)="cambiar($any($event.target).checked)"
        />
      </div>
    } @else {
      <div
        class="d-inline-flex align-items-center gap-3 px-4 py-3 rounded-3 border"
        [class]="className()"
        [style.background]="checked() ? 'rgba(25, 135, 84, 0.07)' : 'rgba(108, 117, 125, 0.07)'"
        [style.border-color]="checked() ? 'rgba(25, 135, 84, 0.25)' : 'rgba(108, 117, 125, 0.2)'"
        [style.cursor]="disabled() ? 'not-allowed' : 'pointer'"
        style="transition: background 0.2s ease; min-width: 190px"
        (click)="onContenedorClick()"
        role="group"
        aria-label="Estado"
      >
        <div
          class="form-check form-switch mb-0"
          style="flex-shrink: 0; transform: scale(1.35); transform-origin: left center"
        >
          <input
            class="form-check-input"
            type="checkbox"
            role="switch"
            [id]="id()"
            [checked]="checked()"
            [disabled]="disabled()"
            (click)="$event.stopPropagation()"
            (change)="cambiar($any($event.target).checked)"
          />
        </div>
        <div class="d-flex flex-column" style="line-height: 1.3">
          <small
            class="text-muted"
            style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600"
          >
            Estado
          </small>
          <span
            class="fw-semibold"
            [style.color]="checked() ? '#198754' : '#6c757d'"
            style="font-size: 1rem; transition: color 0.2s ease"
          >
            @if (checked()) {
              <i class="bi bi-check-circle-fill me-1" style="font-size: 0.85rem"></i>{{ labelActivo() }}
            } @else {
              <i class="bi bi-dash-circle me-1" style="font-size: 0.85rem"></i>{{ labelInactivo() }}
            }
          </span>
        </div>
      </div>
    }
  `,
})
export class EstadoSwitchComponent {
  readonly id = input.required<string>();
  readonly checked = model.required<boolean>();
  readonly labelActivo = input<string>('Activo');
  readonly labelInactivo = input<string>('Inactivo');
  readonly compact = input<boolean>(false);
  readonly disabled = input<boolean>(false);
  readonly className = input<string>('');

  protected onContenedorClick(): void {
    if (!this.disabled()) this.cambiar(!this.checked());
  }

  protected cambiar(valor: boolean): void {
    this.checked.set(valor);
  }
}
