import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ToastStackComponent } from '../shared/ui/toast/toast-stack.component';

/** Raíz de la SPA (equivalente a `App` + `ToastProvider` del proyecto React). */
@Component({
  selector: 'app-root',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterOutlet, ToastStackComponent],
  template: `
    <router-outlet />
    <app-toast-stack position="top-end" />
  `,
})
export class App {}
