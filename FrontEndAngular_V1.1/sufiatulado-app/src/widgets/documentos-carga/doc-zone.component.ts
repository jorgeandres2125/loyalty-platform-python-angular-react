import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  inject,
  input,
  output,
  signal,
} from '@angular/core';
import { ConfirmModalComponent } from '../../shared/ui/components/confirm-modal.component';
import { PdfDropzoneDirective } from '../../shared/ui/directives/pdf-dropzone.directive';
import { ToastService } from '../../shared/ui/toast/toast.service';
import { injectMaxUploadBytes } from '../../features/config/model/uploadLimits';
import { formatBytes } from '../../shared/lib/archivos';
import { detalleErrorDoc, type DocExistente, type DocumentoUploader } from './documento-uploader';

/**
 * Campo con adjunto PDF desplegable (EPS / AFP / ARL). El control (select) se proyecta
 * como contenido; a la derecha van los botones de adjuntar y eliminar.
 */
@Component({
  selector: 'app-doc-zone',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ConfirmModalComponent, PdfDropzoneDirective],
  template: `
    <div class="d-flex align-items-center gap-2">
      <div class="flex-grow-1"><ng-content /></div>
      <div class="d-flex gap-1 flex-shrink-0">
        <button type="button" class="btn btn-outline-primary btn-sm" (click)="open.set(!open())"
          [title]="'Subir archivo ' + tipoLabel()" [disabled]="isDisabled()">
          <i class="bi bi-paperclip"></i>
        </button>
        @if (existingDoc()) {
          <button type="button" class="btn btn-outline-danger btn-sm" (click)="confirmDelete.set(true); deleteError.set('')"
            [title]="'Eliminar archivo ' + tipoLabel()" [disabled]="deleting()">
            <i class="bi bi-trash"></i>
          </button>
        }
      </div>
    </div>
    @if (existingDoc() && !open()) {
      <small class="text-success d-block mt-1">
        <i class="bi bi-file-earmark-check me-1"></i>
        {{ existingDoc()!.nombre }} <span class="text-muted">(v{{ existingDoc()!.version }})</span>
      </small>
    }
    @if (deleteError()) {
      <small class="text-danger d-block mt-1">{{ deleteError() }}</small>
    }
    <app-confirm-modal
      [show]="confirmDelete()"
      [title]="'Eliminar archivo ' + tipoLabel()"
      confirmLabel="Sí, eliminar"
      confirmIcon="bi-trash"
      [loading]="deleting()"
      loadingLabel="Eliminando…"
      (confirm)="confirmarEliminacion()"
      (hide)="cancelarEliminacion()"
    >
      @if (existingDoc(); as doc) {
        ¿Seguro que quieres eliminar el archivo <strong>{{ doc.nombre }}</strong> de
        <strong>{{ tipoLabel() }}</strong>?
        <br />
        <span class="text-muted small">Esta acción no se puede deshacer.</span>
      }
    </app-confirm-modal>
    @if (open()) {
      <div class="doc-zone__collapse">
        <div class="border rounded p-3 bg-light mt-2">
          <div
            appPdfDropzone
            #dz="pdfDropzone"
            [dropzoneDisabled]="isDisabled()"
            (soltado)="onDrop($event)"
            class="rounded p-4 text-center"
            [class]="dz.isDragActive() ? 'border border-primary bg-primary-subtle' : 'border border-secondary'"
            style="border-style: dashed"
            [style.cursor]="isDisabled() ? 'not-allowed' : 'pointer'"
          >
            @if (uploading()) {
              <span><span class="spinner-border spinner-border-sm me-2"></span>Subiendo...</span>
            } @else if (dz.isDragActive()) {
              <span class="text-primary">Suelta el PDF aquí...</span>
            } @else {
              <span class="text-muted small">
                <i class="bi bi-upload me-2"></i>
                Arrastra un PDF o haz clic para seleccionar
              </span>
            }
          </div>
          @if (uploadError()) {
            <div class="text-danger small mt-1">{{ uploadError() }}</div>
          }
          <div class="mt-2 text-end">
            <button type="button" class="btn btn-outline-secondary btn-sm" (click)="open.set(false)">Cancelar</button>
          </div>
        </div>
      </div>
    }
  `,
  styles: `
    .doc-zone__collapse {
      animation: doc-zone-collapse 0.35s ease;
      overflow: hidden;
    }
    @keyframes doc-zone-collapse {
      from { opacity: 0; max-height: 0; }
      to { opacity: 1; max-height: 400px; }
    }
  `,
})
export class DocZoneComponent {
  readonly tipoLabel = input.required<string>();
  readonly tipoPrefix = input.required<string>();
  readonly tipo = input.required<number>();
  readonly numeroDocumento = input.required<string>();
  readonly existingDoc = input<DocExistente | null>(null);
  readonly disabled = input<boolean>(false);
  readonly uploader = input.required<DocumentoUploader>();

  readonly uploaded = output<void>();
  readonly deleted = output<void>();
  readonly uploadingChange = output<boolean>();

  private readonly toast = inject(ToastService);
  private readonly maxBytes = injectMaxUploadBytes();

  protected readonly open = signal<boolean>(false);
  protected readonly uploading = signal<boolean>(false);
  protected readonly uploadError = signal<string>('');
  protected readonly confirmDelete = signal<boolean>(false);
  protected readonly deleting = signal<boolean>(false);
  protected readonly deleteError = signal<string>('');

  protected readonly isDisabled = computed<boolean>(
    () => this.disabled() || this.uploading() || !this.numeroDocumento(),
  );

  constructor() {
    effect(() => {
      if (this.disabled() && this.open()) this.open.set(false);
    });
  }

  protected async onDrop(accepted: File[]): Promise<void> {
    const numeroDocumento: string = this.numeroDocumento();
    if (!accepted.length || !numeroDocumento) return;
    const uploader = this.uploader();
    const archivo: File = accepted[0];
    if (uploader.prevalidarTamano && archivo.size > this.maxBytes()) {
      this.uploadError.set('El archivo excede el tamano limite permitido.');
      this.toast.error('El archivo excede el tamano limite permitido.', {
        title: 'Error al subir',
        detail: `Tamano maximo permitido: ${formatBytes(this.maxBytes())}.`,
      });
      return;
    }
    this.uploading.set(true);
    this.uploadingChange.emit(true);
    this.uploadError.set('');
    const nombre = `${this.tipoPrefix()}${numeroDocumento}.pdf`;
    try {
      await uploader.subir(archivo, nombre, this.tipo(), numeroDocumento);
      this.open.set(false);
      this.uploaded.emit();
      if (uploader.toastExito) {
        this.toast.success('Documento cargado correctamente.', { title: 'Carga exitosa' });
      }
    } catch (err) {
      const detalle: string = detalleErrorDoc(err, 'Error al subir. Intente de nuevo.');
      this.uploadError.set(detalle);
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
    this.deleteError.set('');
    try {
      await this.uploader().eliminar(doc.did);
      this.deleted.emit();
      this.confirmDelete.set(false);
    } catch {
      this.deleteError.set('No se pudo eliminar el archivo.');
    } finally {
      this.deleting.set(false);
    }
  }

  protected cancelarEliminacion(): void {
    if (this.deleting()) return;
    this.confirmDelete.set(false);
    this.deleteError.set('');
  }
}
