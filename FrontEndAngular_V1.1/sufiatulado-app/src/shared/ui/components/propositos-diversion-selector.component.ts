import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'Cine', label: 'a. Cine', icon: 'bi-film' },
  { value: 'Cocina', label: 'b. Cocina', icon: 'bi-egg-fried' },
  { value: 'Maquillaje', label: 'c. Maquillaje', icon: 'bi-stars' },
  { value: 'Asados', label: 'd. Asados', icon: 'bi-fire' },
  { value: 'Lectura', label: 'e. Lectura', icon: 'bi-book-fill' },
  { value: 'Video Juegos', label: 'f. Video Juegos', icon: 'bi-controller' },
  { value: 'Entretenimiento en el Hogar/Suscripcion TV', label: 'g. Entret. Hogar / Suscripción TV', icon: 'bi-tv-fill' },
];

/** Equivalente a `PropositosDiversionSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-propositos-diversion-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="orange" mode="ci" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class PropositosDiversionSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
