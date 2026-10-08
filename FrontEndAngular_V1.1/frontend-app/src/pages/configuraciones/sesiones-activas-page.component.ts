import { ChangeDetectionStrategy, Component, computed, signal } from '@angular/core';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { LoadingSpinnerComponent } from '../../shared/ui/components/loading-spinner.component';
import { EmptyStateComponent } from '../../shared/ui/components/empty-state.component';
import { ConfirmModalComponent } from '../../shared/ui/components/confirm-modal.component';
import {
  injectCerrarOtrasSesiones,
  injectCerrarSesion,
  injectMisSesiones,
} from '../../features/sesiones/model/sesiones';

function formatoFecha(iso: string): string {
  try {
    return new Date(iso).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' });
  } catch {
    return iso;
  }
}

// AP-0130: pantalla de autoservicio -- el usuario ve e informa sus propias sesiones
// concurrentes y puede cerrar remotamente cualquiera que no reconozca.
@Component({
  selector: 'app-sesiones-activas-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, LoadingSpinnerComponent, EmptyStateComponent, ConfirmModalComponent],
  template: `
    <div class="sesiones-activas-page">
      <app-page-header
        title="Mis sesiones"
        subtitle="Sesiones activas de tu cuenta en distintos equipos o navegadores"
        icon="bi-laptop"
        backTo="/configuraciones"
      >
        @if (hayOtras()) {
          <button actions type="button" class="btn btn-outline-danger btn-sm" (click)="confirmarCerrarOtras.set(true)">
            <i class="bi bi-box-arrow-right me-1"></i>
            Cerrar las demas sesiones
          </button>
        }
      </app-page-header>

      <div class="card shadow-sm" style="border: none">
        <div class="card-body p-0">
          @if (sesiones.isLoading()) {
            <app-loading-spinner [fullPage]="true" />
          } @else if (sesiones.isError()) {
            <div class="alert alert-danger m-3">
              No fue posible cargar tus sesiones activas. Intenta de nuevo.
            </div>
          } @else if ((sesiones.data()?.length ?? 0) > 0) {
            <div class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead>
                  <tr>
                    <th>Dispositivo / Navegador</th>
                    <th>IP</th>
                    <th>Inicio</th>
                    <th>Ultima actividad</th>
                    <th>Tipo</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  @for (sesion of sesiones.data(); track sesion.sid) {
                    <tr>
                      <td>
                        <span class="text-truncate d-inline-block" style="max-width: 320px">
                          {{ sesion.user_agent || 'Desconocido' }}
                        </span>
                        @if (sesion.es_actual) {
                          <span class="badge bg-success ms-2">Este dispositivo</span>
                        }
                      </td>
                      <td class="font-monospace">{{ sesion.ip }}</td>
                      <td>{{ formatoFecha(sesion.inicio) }}</td>
                      <td>{{ formatoFecha(sesion.last_activity) }}</td>
                      <td>{{ sesion.canal ? 'Canal' : 'Otra aplicacion' }}</td>
                      <td class="text-end">
                        @if (!sesion.es_actual) {
                          <button type="button" class="btn btn-outline-secondary btn-sm" (click)="sidAConfirmar.set(sesion.sid)">
                            <i class="bi bi-x-lg me-1"></i>
                            Cerrar
                          </button>
                        }
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          } @else {
            <app-empty-state icon="bi-laptop" title="No hay sesiones activas registradas" />
          }
        </div>
      </div>

      <app-confirm-modal
        [show]="sidAConfirmar() !== null"
        title="Cerrar sesion"
        message="Esa sesion se cerrara de inmediato en el otro equipo o navegador. Deseas continuar?"
        confirmLabel="Cerrar sesion"
        [loading]="cerrarSesion.isPending()"
        (confirm)="confirmarCierre()"
        (hide)="sidAConfirmar.set(null)"
      />

      <app-confirm-modal
        [show]="confirmarCerrarOtras()"
        title="Cerrar las demas sesiones"
        message="Se cerraran todas tus sesiones activas, excepto la de este dispositivo. Deseas continuar?"
        confirmLabel="Cerrar las demas"
        [loading]="cerrarOtras.isPending()"
        (confirm)="confirmarCierreOtras()"
        (hide)="confirmarCerrarOtras.set(false)"
      />
    </div>
  `,
})
export class SesionesActivasPageComponent {
  protected readonly sesiones = injectMisSesiones();
  protected readonly cerrarSesion = injectCerrarSesion();
  protected readonly cerrarOtras = injectCerrarOtrasSesiones();
  protected readonly sidAConfirmar = signal<string | null>(null);
  protected readonly confirmarCerrarOtras = signal<boolean>(false);

  protected readonly hayOtras = computed<boolean>(() => (this.sesiones.data()?.length ?? 0) > 1);

  protected formatoFecha(iso: string): string {
    return formatoFecha(iso);
  }

  protected async confirmarCierre(): Promise<void> {
    const sid = this.sidAConfirmar();
    try {
      if (sid) {
        await this.cerrarSesion.mutateAsync(sid);
      }
      this.sidAConfirmar.set(null);
    } catch {
      // El error queda en el estado de la mutación; el modal permanece abierto.
    }
  }

  protected async confirmarCierreOtras(): Promise<void> {
    try {
      await this.cerrarOtras.mutateAsync();
      this.confirmarCerrarOtras.set(false);
    } catch {
      // El error queda en el estado de la mutación; el modal permanece abierto.
    }
  }
}
