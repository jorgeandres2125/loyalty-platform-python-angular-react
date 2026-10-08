import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'Atención al cliente', label: 'a. Atención al cliente', icon: 'bi-headset' },
  { value: 'Ventas', label: 'b. Ventas', icon: 'bi-cash-stack' },
  { value: 'Crecimiento personal', label: 'c. Crecimiento personal', icon: 'bi-graph-up-arrow' },
];

/** Equivalente a `TemasProfundizarSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-temas-profundizar-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="blue" mode="ci" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class TemasProfundizarSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
