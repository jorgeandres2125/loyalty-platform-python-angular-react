import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'Experiencias', label: 'a. Experiencias', icon: 'bi-stars' },
  { value: 'Deporte', label: 'b. Deporte', icon: 'bi-trophy-fill' },
  { value: 'Tecnología', label: 'c. Tecnología', icon: 'bi-laptop-fill' },
  { value: 'Hogar', label: 'd. Hogar', icon: 'bi-house-heart-fill' },
  { value: 'Viajes', label: 'e. Viajes', icon: 'bi-airplane-fill' },
];

/** Equivalente a `PremiosSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-premios-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="gold" mode="ci" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class PremiosSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
