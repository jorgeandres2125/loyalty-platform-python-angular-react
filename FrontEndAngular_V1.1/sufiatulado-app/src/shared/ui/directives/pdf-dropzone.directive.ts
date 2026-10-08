import {
  Directive,
  ElementRef,
  Renderer2,
  afterNextRender,
  inject,
  input,
  output,
  signal,
} from '@angular/core';

function esPdf(file: File): boolean {
  return file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
}

/**
 * Zona para soltar/seleccionar un PDF (sustituye a `useDropzone` de react-dropzone con
 * `accept: application/pdf` y `maxFiles: 1`). Clic, Enter o Espacio abren el selector;
 * arrastrar activa `isDragActive`. Emite `soltado` con los archivos aceptados (vacío si
 * se rechazan: no es PDF o vienen varios).
 *
 *   <div appPdfDropzone #dz="pdfDropzone" [dropzoneDisabled]="…" (soltado)="subir($event)">
 *     {{ dz.isDragActive() ? 'Suelta…' : 'Arrastra…' }}
 *   </div>
 */
@Directive({
  selector: '[appPdfDropzone]',
  exportAs: 'pdfDropzone',
  host: {
    role: 'presentation',
    '[attr.tabindex]': 'dropzoneDisabled() ? -1 : 0',
    '(click)': 'abrir()',
    '(keydown.enter)': 'abrir()',
    '(keydown.space)': '$event.preventDefault(); abrir()',
    '(dragenter)': 'onDragEnter($event)',
    '(dragover)': 'onDragOver($event)',
    '(dragleave)': 'onDragLeave($event)',
    '(drop)': 'onDrop($event)',
  },
})
export class PdfDropzoneDirective {
  readonly dropzoneDisabled = input<boolean>(false);
  readonly soltado = output<File[]>();

  readonly isDragActive = signal<boolean>(false);

  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);
  private readonly renderer = inject(Renderer2);
  private inputEl: HTMLInputElement | null = null;
  private profundidad = 0;

  constructor() {
    afterNextRender(() => {
      const input: HTMLInputElement = this.renderer.createElement('input');
      input.type = 'file';
      input.accept = 'application/pdf,.pdf';
      input.style.display = 'none';
      input.tabIndex = -1;
      // Evita que el clic programático burbujee y vuelva a abrir el selector.
      input.addEventListener('click', (e) => e.stopPropagation());
      input.addEventListener('change', () => {
        const archivos: File[] = Array.from(input.files ?? []);
        input.value = '';
        this.emitir(archivos);
      });
      this.renderer.appendChild(this.host.nativeElement, input);
      this.inputEl = input;
    });
  }

  protected abrir(): void {
    if (this.dropzoneDisabled()) return;
    this.inputEl?.click();
  }

  protected onDragEnter(e: DragEvent): void {
    e.preventDefault();
    if (this.dropzoneDisabled()) return;
    this.profundidad += 1;
    this.isDragActive.set(true);
  }

  protected onDragOver(e: DragEvent): void {
    e.preventDefault();
    if (e.dataTransfer) e.dataTransfer.dropEffect = this.dropzoneDisabled() ? 'none' : 'copy';
  }

  protected onDragLeave(e: DragEvent): void {
    e.preventDefault();
    this.profundidad = Math.max(0, this.profundidad - 1);
    if (this.profundidad === 0) this.isDragActive.set(false);
  }

  protected onDrop(e: DragEvent): void {
    e.preventDefault();
    this.profundidad = 0;
    this.isDragActive.set(false);
    if (this.dropzoneDisabled()) return;
    this.emitir(Array.from(e.dataTransfer?.files ?? []));
  }

  private emitir(archivos: File[]): void {
    // maxFiles: 1 → si llegan varios, se rechazan todos (igual que react-dropzone).
    const aceptados: File[] = archivos.length === 1 && esPdf(archivos[0]) ? archivos : [];
    this.soltado.emit(aceptados);
  }
}
