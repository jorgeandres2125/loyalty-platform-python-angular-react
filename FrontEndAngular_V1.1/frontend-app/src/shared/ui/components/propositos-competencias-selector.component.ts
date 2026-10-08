import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'Crecer Conocimiento en ventas', label: 'a. Crecer conocimiento en ventas', icon: 'bi-graph-up-arrow' },
  { value: 'Aprender sobre marketing digital', label: 'b. Marketing digital', icon: 'bi-megaphone-fill' },
  { value: 'Saber sobre servicio al cliente', label: 'c. Servicio al cliente', icon: 'bi-headset' },
  { value: 'Entender al consumidor', label: 'd. Entender al consumidor', icon: 'bi-person-check-fill' },
  { value: 'Mejorar habilidades de negociacion', label: 'e. Habilidades de negociación', icon: 'bi-award-fill' },
  { value: 'Aprender otro idioma', label: 'f. Aprender otro idioma', icon: 'bi-translate' },
];

/** Equivalente a `PropositosCompetenciasSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-propositos-competencias-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="purple" mode="ci" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class PropositosCompetenciasSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
