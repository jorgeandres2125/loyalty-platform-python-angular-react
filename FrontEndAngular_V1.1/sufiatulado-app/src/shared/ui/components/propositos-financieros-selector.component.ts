import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'Remodelar mi casa, ElectroHogar, Cocina, Muebles', label: 'a. Remodelar casa / ElectroHogar', icon: 'bi-house-fill' },
  { value: 'Tener Tecnologia de Punta', label: 'b. Tecnología de punta', icon: 'bi-cpu-fill' },
  { value: 'Tv, Celular, Tablet y Accesorios', label: 'c. TV, Celular, Tablet', icon: 'bi-tv-fill' },
  { value: 'Montar o mejorar mi negocio', label: 'd. Montar o mejorar mi negocio', icon: 'bi-shop' },
  { value: 'Tener medio de transporte propio', label: 'e. Medio de transporte propio', icon: 'bi-car-front-fill' },
];

/** Equivalente a `PropositosFinancierosSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-propositos-financieros-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="green" mode="ci" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class PropositosFinancierosSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
