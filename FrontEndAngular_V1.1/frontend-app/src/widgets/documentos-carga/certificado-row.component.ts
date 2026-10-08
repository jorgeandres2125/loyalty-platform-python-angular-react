import { ChangeDetectionStrategy, Component, computed, inject, input, output, signal } from '@angular/core';
import { ConfirmModalComponent } from '../../shared/ui/components/confirm-modal.component';
import { PdfDropzoneDirective } from '../../shared/ui/directives/pdf-dropzone.directive';
import { ToastService } from '../../shared/ui/toast/toast.service';
import { injectMaxUploadBytes } from '../../features/config/model/uploadLimits';
import { formatBytes } from '../../shared/lib/archivos';
import { detalleErrorDoc, type DocExistente, type DocumentoUploader } from './documento-uploader';

/** Fila de carga de certificado (Prepagada, Vivienda, Cédula, RUT…) sin colapsable. */
@Component({
  selector: 'app-certificado-row',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ConfirmModalComponent, PdfDropzoneDirective],
  template: `
    <div class="border rounded mb-2 overflow-hidden bg-white">
      <div class="px-3 py-2 d-flex align-items-center justify-content-between border-bottom" style="min-height: 40px">
        <span class="fw-medium">{{ label() }}</span>
        <div class="d-flex align-items-center gap-2">
          @if (existingDoc(); as doc) {
            <small class="text-success text-truncate">
              <i class="bi bi-check-circle-fill me-1"></i>
              {{ doc.nombre }} <span class="text-muted">(v{{ doc.version }})</span>
            </small>
          }
          @if (rowError()) {
            <small class="text-danger">{{ rowError() }}</small>
          }
          @if (existingDoc()) {
            <button type="button" class="btn btn-outline-danger btn-sm" (click)="confirmDelete.set(true); rowError.set('')"
              title="Eliminar archivo" [disabled]="deleting()">
              <i class="bi bi-trash"></i>
            </button>
          }
        </div>
      </div>
      <div
        appPdfDropzone
        #dz="pdfDropzone"
        [dropzoneDisabled]="isDisabled()"
        (soltado)="onDrop($event)"
        class="d-flex align-items-center justify-content-center px-3 py-3 small bg-white"
        [class.text-muted]="isDisabled()"
        [class.text-primary]="!isDisabled() && dz.isDragActive()"
        [class.text-dark]="!isDisabled() && !dz.isDragActive()"
        [style.cursor]="isDisabled() ? 'not-allowed' : 'pointer'"
        [style.border]="'1px dashed ' + (dz.isDragActive() ? '#0d6efd' : '#000')"
        style="margin: 8px; border-radius: 4px"
      >
        @if (uploading()) {
          <span><span class="spinner-border spinner-border-sm me-2"></span>Subiendo…</span>
        } @else if (dz.isDragActive()) {
          <span><i class="bi bi-upload me-2"></i>Suelta el PDF aquí</span>
        } @else {
          <span>
            <i class="bi bi-upload me-2"></i>
            {{ existingDoc() ? 'Arrastra un PDF para reemplazar o haz clic para seleccionar' : 'Arrastra un PDF o haz clic para seleccionar' }}
          </span>
        }
      </div>
      <app-confirm-modal
        [show]="confirmDelete()"
        [title]="'Eliminar archivo ' + label()"
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        [loading]="deleting()"
        loadingLabel="Eliminando…"
        (confirm)="confirmarEliminacion()"
        (hide)="cancelarEliminacion()"
      >
        @if (existingDoc(); as doc) {
          ¿Seguro que quieres eliminar el archivo <strong>{{ doc.nombre }}</strong> de
          <strong>{{ label() }}</strong>?
          <br />
          <span class="text-muted small">Esta acción no se puede deshacer.</span>
        }
      </app-confirm-modal>
    </div>
  `,
})
export class CertificadoRowComponent {
  readonly label = input.required<string>();
  readonly tipo = input.required<number>();
  readonly tipoPrefix = input.required<string>();
  readonly numeroDocumento = input.required<string>();
  readonly existingDoc = input<DocExistente | null>(null);
  readonly uploader = input.required<DocumentoUploader>();

  readonly uploaded = output<void>();
  readonly deleted = output<void>();
  readonly uploadingChange = output<boolean>();

  private readonly toast = inject(ToastService);
  private readonly maxBytes = injectMaxUploadBytes();

  protected readonly uploading = signal<boolean>(false);
  protected readonly rowError = signal<string>('');
  protected readonly confirmDelete = signal<boolean>(false);
  protected readonly deleting = signal<boolean>(false);

  protected readonly isDisabled = computed<boolean>(() => this.uploading() || !this.numeroDocumento());

  protected async onDrop(accepted: File[]): Promise<void> {
    const numeroDocumento: string = this.numeroDocumento();
    if (!accepted.length || !numeroDocumento) return;
    const uploader = this.uploader();
    const archivo: File = accepted[0];
    if (uploader.prevalidarTamano && archivo.size > this.maxBytes()) {
      this.rowError.set('El archivo excede el tamano limite permitido.');
      this.toast.error('El archivo excede el tamano limite permitido.', {
        title: 'Error al subir',
        detail: `Tamano maximo permitido: ${formatBytes(this.maxBytes())}.`,
      });
      return;
    }
    this.uploading.set(true);
    this.uploadingChange.emit(true);
    this.rowError.set('');
    const nombre = `${this.tipoPrefix()}${numeroDocumento}.pdf`;
    try {
      await uploader.subir(archivo, nombre, this.tipo(), numeroDocumento);
      this.uploaded.emit();
      if (uploader.toastExito) {
        this.toast.success('Documento cargado correctamente.', { title: 'Carga exitosa' });
      }
    } catch (err) {
      const detalle: string = detalleErrorDoc(err, 'Error al subir');
      this.rowError.set(detalle);
      this.toast.error('No se pudo subir el archivo.', { title: 'Error al subir', detail: detalle });
    } finally {
      this.uploading.set(false);
      this.uploadingChange.emit(false);
    }
  }

  protected async confirmarEliminacion(): Promise<void> {
    const doc = this.existingDoc();
    if (!doc) return;
    this.deleting.set(true);
    this.rowError.set('');
    try {
      await this.uploader().eliminar(doc.did);
      this.deleted.emit();
      this.confirmDelete.set(false);
    } catch {
      this.rowError.set('No se pudo eliminar');
    } finally {
      this.deleting.set(false);
    }
  }

  protected cancelarEliminacion(): void {
    if (this.deleting()) return;
    this.confirmDelete.set(false);
  }
}
