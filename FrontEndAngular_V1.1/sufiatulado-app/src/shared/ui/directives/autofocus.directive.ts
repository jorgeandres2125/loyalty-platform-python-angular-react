import { Directive, ElementRef, afterNextRender, inject } from '@angular/core';

/** Enfoca el elemento al montarse (equivalente a la prop `autoFocus` de React). */
@Directive({ selector: '[appAutofocus]' })
export class AutofocusDirective {
  constructor() {
    const el = inject<ElementRef<HTMLElement>>(ElementRef);
    afterNextRender(() => el.nativeElement.focus());
  }
}
