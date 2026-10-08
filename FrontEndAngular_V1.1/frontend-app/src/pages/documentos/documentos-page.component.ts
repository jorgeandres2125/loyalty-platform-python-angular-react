import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../shared/api/client';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { LoadingSpinnerComponent } from '../../shared/ui/components/loading-spinner.component';
import { EmptyStateComponent } from '../../shared/ui/components/empty-state.component';
import { QUERY_KEYS, TIPO_DOCUMENTO } from '../../shared/config/constants';
import { formatDate } from '../../shared/lib/formatters';

interface Documento {
  id: number;
  numero_documento: string;
  tipo: number;
  nombre_archivo: string | null;
  url: string | null;
  created: number;
}

const TIPO_LABELS: Record<number, string> = {
  [TIPO_DOCUMENTO.CEDULA]: 'Cédula',
  [TIPO_DOCUMENTO.RUT]: 'RUT',
  [TIPO_DOCUMENTO.CONTRATO]: 'Contrato',
};

@Component({
  selector: 'app-documentos-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, LoadingSpinnerComponent, EmptyStateComponent],
  template: `
    <div>
      <app-page-header
        title="Documentos"
        subtitle="Gestión de documentos por comisionista"
        icon="bi-file-earmark-text"
      >
        <button actions type="button" class="btn btn-primary btn-sm">
          <i class="bi bi-upload me-2"></i>
          Subir documento
        </button>
      </app-page-header>

      <div class="card shadow-sm" style="border: none">
        <div class="card-header bg-white border-0 pt-4 pb-0 px-4">
          <div class="input-group" style="max-width: 360px">
            <span class="input-group-text bg-light border-end-0">
              <i class="bi bi-search text-muted"></i>
            </span>
            <input
              class="form-control border-start-0"
              placeholder="Buscar por cédula..."
              [value]="busqueda()"
              (input)="busqueda.set($any($event.target).value)"
            />
          </div>
        </div>
        <div class="card-body p-0">
          @if (documentos.isLoading()) {
            <app-loading-spinner [fullPage]="true" />
          } @else if (!documentos.data()?.length) {
            <app-empty-state icon="bi-file-earmark" title="Sin documentos" description="No se encontraron documentos." />
          } @else {
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead>
                  <tr>
                    <th>Documento</th>
                    <th>Tipo</th>
                    <th>Archivo</th>
                    <th>Fecha</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  @for (doc of documentos.data(); track doc.id) {
                    <tr>
                      <td class="font-monospace">{{ doc.numero_documento }}</td>
                      <td>
                        <span class="badge bg-opacity-15 text-body" [class]="'bg-' + colorTipo(doc.tipo)">
                          {{ etiquetaTipo(doc.tipo) }}
                        </span>
                      </td>
                      <td>{{ doc.nombre_archivo ?? '—' }}</td>
                      <td>{{ formatDate(doc.created) }}</td>
                      <td>
                        @if (doc.url) {
                          <a [href]="doc.url" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-primary">
                            <i class="bi bi-download"></i>
                          </a>
                        }
                      </td>
                    </tr>
                  }
                </tbody>
              </table>
            </div>
          }
        </div>
      </div>
    </div>
  `,
})
export class DocumentosPageComponent {
  private readonly api = inject(ApiClient);
  protected readonly busqueda = signal<string>('');

  protected readonly documentos = injectQuery<Documento[]>(() => {
    const busqueda: string = this.busqueda();
    return {
      queryKey: [QUERY_KEYS.DOCUMENTOS, busqueda],
      queryFn: async () => {
        const { data } = await this.api.get<Documento[]>('/documentos', {
          params: busqueda ? { documento: busqueda } : undefined,
        });
        return data;
      },
    };
  });

  protected colorTipo(tipo: number): string {
    if (tipo === TIPO_DOCUMENTO.CONTRATO) return 'primary';
    if (tipo === TIPO_DOCUMENTO.RUT) return 'info';
    return 'secondary';
  }

  protected etiquetaTipo(tipo: number): string {
    return TIPO_LABELS[tipo] ?? `Tipo ${tipo}`;
  }

  protected formatDate(created: number): string {
    return formatDate(String(created));
  }
}
