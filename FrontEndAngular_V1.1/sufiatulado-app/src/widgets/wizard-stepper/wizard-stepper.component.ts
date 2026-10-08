import { ChangeDetectionStrategy, Component, input } from '@angular/core';

export interface PasoWizard {
  label: string;
  icon: string;
}

/** Indicador de pasos de los asistentes de registro (equivalente a `WizardStepper`). */
@Component({
  selector: 'app-wizard-stepper',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="wizard-stepper mb-4">
      @for (paso of steps(); track paso.label; let idx = $index; let ultimo = $last) {
        <div
          class="wizard-stepper__item"
          [class.active]="idx + 1 === step()"
          [class.done]="idx + 1 < step()"
        >
          <div class="wizard-stepper__circle">
            @if (idx + 1 < step()) {
              <i class="bi bi-check-lg"></i>
            } @else {
              <i class="bi" [class]="paso.icon"></i>
            }
          </div>
          <span class="wizard-stepper__label">{{ paso.label }}</span>
          @if (!ultimo) {
            <div class="wizard-stepper__line"></div>
          }
        </div>
      }
    </div>
  `,
})
export class WizardStepperComponent {
  readonly steps = input.required<readonly PasoWizard[]>();
  readonly step = input.required<number>();
}
