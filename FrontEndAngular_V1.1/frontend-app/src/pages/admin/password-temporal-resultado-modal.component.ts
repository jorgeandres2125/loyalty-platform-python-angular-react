import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { ModalComponent } from '../../shared/ui/components/modal.component';
import type { PasswordTemporalResultado } from '../../features/admin-usuarios/model/types';

// AP-0047: muestra la clave temporal generada una unica vez (solo viaja en la
// respuesta de emision; el sistema persiste unicamente su hash).
@Component({
  selector: 'app-password-temporal-resultado-modal',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ModalComponent],
  template: `
    <app-modal [show]="resultado() !== null" [centered]="true" (hide)="cerrar.emit()">
      <div class="modal-header">
        <h6 class="modal-title">
          <i class="bi bi-key me-2"></i>
          Contrasena temporal generada
        </h6>
        <button type="button" class="btn-close" aria-label="Close" (click)="cerrar.emit()"></button>
      </div>
      <div class="modal-body">
        <p class="small text-muted mb-3">
          Entregala a <strong>{{ resultado()?.usuario }}</strong> por un canal seguro. Se
          muestra una sola vez, vence en
          {{ resultado()?.ttl_minutos }} minutos y el usuario debera definir su contrasena
          personal al ingresar.
        </p>
        <div class="p-3 bg-light border rounded text-center">
          <code class="fs-5 user-select-all">{{ resultado()?.password_temporal }}</code>
        </div>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary btn-sm" (click)="cerrar.emit()">Cerrar</button>
      </div>
    </app-modal>
  `,
})
export class PasswordTemporalResultadoModalComponent {
  readonly resultado = input<PasswordTemporalResultado | null>(null);
  readonly cerrar = output<void>();
}
