import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'solo', label: 'A. Solo', icon: 'bi-person-fill' },
  { value: 'con mi pareja', label: 'B. Con mi pareja', icon: 'bi-suit-heart-fill' },
  { value: 'con mis hijos', label: 'C. Con mis hijos', icon: 'bi-people-fill' },
  { value: 'con mis papás', label: 'D. Con mis papás', icon: 'bi-house-heart-fill' },
  { value: 'con mis amigos', label: 'E. Con mis amigos', icon: 'bi-emoji-smile-fill' },
];

/** Equivalente a `ConQuienVivesSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-con-quien-vives-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="red" mode="lower" colClass="col-12 col-md" [(value)]="value" />`,
})
export class ConQuienVivesSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
