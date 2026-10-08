import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'a', label: 'a. Experiencias para pasar tiempo juntos', icon: 'bi-emoji-laughing-fill' },
  { value: 'b', label: 'b. Viajes y vacaciones', icon: 'bi-airplane-fill' },
  { value: 'c', label: 'c. Actividades lúdicas', icon: 'bi-controller' },
];

/** Equivalente a `PropositosFamiliaresSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-propositos-familiares-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="red" mode="keys" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class PropositosFamiliaresSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
