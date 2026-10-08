import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { ModalComponent } from './components/modal.component';

@Component({
  selector: 'app-idle-warning-modal',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ModalComponent],
  template: `
    <app-modal [show]="show()" backdrop="static" [centered]="true" (hide)="cerrar.emit()">
      <div class="modal-header">
        <div class="modal-title h4">Tu sesion esta por expirar</div>
      </div>
      <div class="modal-body">
        Por seguridad (AP-0129), tu sesion se cerrara por inactividad en
        <strong>{{ segundosRestantes() }}</strong> segundos. Deseas continuar conectado?
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-outline-secondary" (click)="cerrar.emit()">
          Cerrar sesion
        </button>
        <button type="button" class="btn btn-primary" (click)="continuar.emit()">
          Continuar conectado
        </button>
      </div>
    </app-modal>
  `,
})
export class IdleWarningModalComponent {
  readonly show = input<boolean>(false);
  readonly segundosRestantes = input<number>(60);
  readonly continuar = output<void>();
  readonly cerrar = output<void>();
}
