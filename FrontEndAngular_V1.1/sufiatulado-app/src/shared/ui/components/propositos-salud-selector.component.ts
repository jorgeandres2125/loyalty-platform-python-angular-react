import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'Hacer deporte', label: 'a. Hacer deporte', icon: 'bi-bicycle' },
  { value: 'Atencion Medica Complementaria', label: 'b. Atención Médica Complementaria', icon: 'bi-heart-pulse-fill' },
  { value: 'Belleza y Estetica', label: 'c. Belleza y Estética', icon: 'bi-stars' },
  { value: 'Alimentacion Basica y Saludable', label: 'd. Alimentación Saludable', icon: 'bi-apple' },
  { value: 'Yoga y Meditacion', label: 'e. Yoga y Meditación', icon: 'bi-peace-fill' },
];

/** Equivalente a `PropositosSaludSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-propositos-salud-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="teal" mode="ci" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class PropositosSaludSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
