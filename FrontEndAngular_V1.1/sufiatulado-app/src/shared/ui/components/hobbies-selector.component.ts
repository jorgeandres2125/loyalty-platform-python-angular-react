import { ChangeDetectionStrategy, Component, model } from '@angular/core';
import { PillMultiSelectorComponent, type PillOption } from './pill-multi-selector.component';

const OPTIONS: readonly PillOption[] = [
  { value: 'leer', label: 'a. Leer', icon: 'bi-book-fill' },
  { value: 'escuchar musica', label: 'b. Escuchar música', icon: 'bi-music-note-beamed' },
  { value: 'escribir', label: 'c. Escribir', icon: 'bi-pencil-fill' },
  { value: 'hacer deporte', label: 'd. Hacer deporte', icon: 'bi-bicycle' },
  { value: 'navegar en internet', label: 'e. Navegar en internet', icon: 'bi-laptop-fill' },
  { value: 'cocinar', label: 'f. Cocinar', icon: 'bi-egg-fried' },
  { value: 'ver television', label: 'g. Ver televisión', icon: 'bi-tv-fill' },
  { value: 'ir al cine', label: 'h. Ir al cine', icon: 'bi-film' },
  { value: 'salir con amigos', label: 'i. Salir con amigos', icon: 'bi-people-fill' },
  { value: 'estar con la familia', label: 'j. Estar con la familia', icon: 'bi-house-heart-fill' },
];

/** Equivalente a `HobbiesSelector`. Valor serializado como JSON; soporta `[(value)]`. */
@Component({
  selector: 'app-hobbies-selector',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PillMultiSelectorComponent],
  template: `<app-pill-multi-selector [options]="options" color="teal" mode="lower" colClass="col-12 col-sm-6 col-md" [(value)]="value" />`,
})
export class HobbiesSelectorComponent {
  protected readonly options = OPTIONS;
  readonly value = model<string>('');
}
