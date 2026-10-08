import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { ConfirmModalComponent } from '../../shared/ui/components/confirm-modal.component';
import { injectEliminarMiDocumento, injectMisDocumentos } from '../../features/perfil-self/model/queries';
import type { DocumentoSelfItem } from '../../features/perfil-self/model/types';
import { estadoBadgeBg, estadoLabel, formatFechaDisplay } from '../asesor-movilidad/documentos-asesor.component';

/**
 * AP-0055: lectura y eliminacion via /me/documentos (ownership por token, no por
 * parametro de ruta). El estado de moderacion (pendiente/revision/aprobado) es un
 * campo de staff (DOCUMENTOS_MODERAR): el propio comisionista no puede editarlo, por
 * eso este panel es de solo lectura mas eliminar, sin "Editar".
 */
@Component({
  selector: 'app-mis-documentos',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ConfirmModalComponent],
  template: `
    @if (docs.isLoading()) {
      <div class="text-center py-3">
        <span class="spinner-border spinner-border-sm text-danger" role="status"></span>
      </div>
    } @else if (!docs.data() || docs.data()!.length === 0) {
      <div class="text-center py-4 text-muted">
        <i class="bi bi-inbox fs-3 d-block mb-2"></i>
        Aún no tienes documentos cargados.
      </div>
    } @else {
      <div>
        @if (errorMsg()) {
          <div class="alert alert-danger alert-dismissible py-2">
            {{ errorMsg() }}
            <button type="button" class="btn-close" aria-label="Close" (click)="errorMsg.set('')"></button>
          </div>
        }
        <div class="table-responsive">
          <table class="table table-sm table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>Id</th>
                <th>Tipo de documento</th>
                <th>Documento</th>
                <th>Estado</th>
                <th class="text-center">Versión</th>
                <th>Fecha Alta</th>
                <th class="text-center">Operación</th>
              </tr>
            </thead>
            <tbody>
              @for (d of docs.data(); track d.did) {
                <tr>
                  <td class="font-monospace">{{ d.did }}</td>
                  <td>{{ d.tipo_nombre }}</td>
                  <td class="font-monospace">{{ d.nombre }}</td>
                  <td><span class="badge" [class]="'bg-' + badgeBg(d.estado)">{{ label(d.estado) }}</span></td>
                  <td class="text-center">{{ d.version }}</td>
                  <td>{{ fecha(d.fecha) }}</td>
                  <td class="text-center">
                    <button type="button" class="btn btn-outline-danger btn-sm" (click)="docAEliminar.set(d)"
                      [disabled]="eliminar.isPending()">
                      @if (eliminar.isPending() && docAEliminar()?.did === d.did) {
                        <span class="spinner-border spinner-border-sm me-1"></span>Eliminando…
                      } @else {
                        <i class="bi bi-trash me-1"></i>Eliminar
                      }
                    </button>
                  </td>
                </tr>
              }
            </tbody>
          </table>
        </div>

        <app-confirm-modal
          [show]="!!docAEliminar()"
          title="Eliminar documento"
          confirmLabel="Sí, eliminar"
          confirmIcon="bi-trash"
          [loading]="eliminar.isPending()"
          loadingLabel="Eliminando…"
          (confirm)="confirmarEliminacion()"
          (hide)="cancelarEliminacion()"
        >
          @if (docAEliminar(); as doc) {
            ¿Seguro que quieres eliminar el documento <strong>{{ doc.nombre }}</strong> ({{ doc.tipo_nombre }})?
            <br />
            <span class="text-muted small">Esta acción no se puede deshacer.</span>
          }
        </app-confirm-modal>
      </div>
    }
  `,
})
export class MisDocumentosComponent {
  protected readonly docs = injectMisDocumentos(() => true);
  protected readonly eliminar = injectEliminarMiDocumento();
  protected readonly errorMsg = signal<string>('');
  protected readonly docAEliminar = signal<DocumentoSelfItem | null>(null);

  protected badgeBg(estado: string): string {
    return estadoBadgeBg(estado);
  }

  protected label(estado: string): string {
    return estadoLabel(estado);
  }

  protected fecha(value: string | null): string {
    return formatFechaDisplay(value);
  }

  protected async confirmarEliminacion(): Promise<void> {
    const doc = this.docAEliminar();
    if (!doc) return;
    this.errorMsg.set('');
    try {
      await this.eliminar.mutateAsync(doc.did);
      this.docAEliminar.set(null);
    } catch (err) {
      this.errorMsg.set(err instanceof Error ? err.message : 'Error al eliminar');
      this.docAEliminar.set(null);
    }
  }

  protected cancelarEliminacion(): void {
    if (this.eliminar.isPending()) return;
    this.docAEliminar.set(null);
  }
}
