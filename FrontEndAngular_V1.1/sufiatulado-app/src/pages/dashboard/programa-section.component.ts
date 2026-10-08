import { NgTemplateOutlet } from '@angular/common';
import { ChangeDetectionStrategy, Component, input } from '@angular/core';

export interface ProgramaStats {
  total: number;
  activos: number;
  incompletos: number;
  con_incentivos: number;
  nuevos_mes: number;
}

@Component({
  selector: 'app-programa-section',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgTemplateOutlet],
  template: `
    <ng-template #statCard let-icon="icon" let-label="label" let-value="value" let-color="color">
      <div class="stat-card">
        <div class="stat-card__icon" [style.--s-color]="color" [style.--s-bg]="color + '18'">
          <i class="bi" [class]="icon"></i>
        </div>
        <div>
          <div class="stat-card__value">{{ value }}</div>
          <div class="stat-card__label">{{ label }}</div>
        </div>
      </div>
    </ng-template>

    <div class="mb-4">
      <div class="d-flex align-items-center gap-2 mb-3">
        <div
          class="rounded-2 d-flex align-items-center justify-content-center flex-shrink-0"
          style="width: 32px; height: 32px"
          [style.background]="accent()"
        >
          <i class="bi text-white" [class]="icon()" style="font-size: 0.9rem"></i>
        </div>
        <h6 class="mb-0 fw-semibold">{{ label() }}</h6>
      </div>
      <div class="row g-3 row-cols-2 row-cols-sm-3 row-cols-lg-5">
        @for (c of tarjetas(); track c.label) {
          <div class="col">
            <ng-container
              [ngTemplateOutlet]="statCard"
              [ngTemplateOutletContext]="{ icon: c.icon, label: c.label, value: c.value, color: c.color }"
            />
          </div>
        }
      </div>
    </div>
  `,
})
export class ProgramaSectionComponent {
  readonly label = input.required<string>();
  readonly icon = input.required<string>();
  readonly accent = input.required<string>();
  readonly stats = input.required<ProgramaStats>();

  protected tarjetas(): { icon: string; label: string; value: string; color: string }[] {
    const s: ProgramaStats = this.stats();
    const fmt = (n: number): string => n.toLocaleString('es-CO');
    return [
      { icon: 'bi-people-fill', label: 'Total registrados', value: fmt(s.total), color: '#6B7280' },
      { icon: 'bi-person-check-fill', label: 'Activos', value: fmt(s.activos), color: '#10B981' },
      { icon: 'bi-hourglass-split', label: 'Incompletos', value: fmt(s.incompletos), color: '#F59E0B' },
      { icon: 'bi-stars', label: 'Con incentivos', value: fmt(s.con_incentivos), color: '#EAB308' },
      { icon: 'bi-person-plus-fill', label: 'Nuevos este mes', value: fmt(s.nuevos_mes), color: '#3B82F6' },
    ];
  }
}
