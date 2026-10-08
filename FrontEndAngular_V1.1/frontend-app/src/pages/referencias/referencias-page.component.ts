import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../shared/api/client';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { LoadingSpinnerComponent } from '../../shared/ui/components/loading-spinner.component';
import { EmptyStateComponent } from '../../shared/ui/components/empty-state.component';
import { QUERY_KEYS } from '../../shared/config/constants';
import type { Canal, Ejecutivo, Oficina } from '../../entities/referencias/model/types';

type Tab = 'canales' | 'oficinas' | 'ejecutivos';

@Component({
  selector: 'app-referencias-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, LoadingSpinnerComponent, EmptyStateComponent],
  template: `
    <div>
      <app-page-header title="Referencias" subtitle="Catálogos del sistema" icon="bi-diagram-3" />

      <div class="card shadow-sm" style="border: none">
        <div class="card-header bg-white border-0 pt-3">
          <ul class="nav nav-tabs" role="tablist">
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'canales'" (click)="tab.set('canales')">
                <i class="bi bi-broadcast me-2"></i>Canales
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'oficinas'" (click)="tab.set('oficinas')">
                <i class="bi bi-building me-2"></i>Oficinas
              </button>
            </li>
            <li class="nav-item">
              <button type="button" class="nav-link" [class.active]="tab() === 'ejecutivos'" (click)="tab.set('ejecutivos')">
                <i class="bi bi-person-badge me-2"></i>Ejecutivos
              </button>
            </li>
          </ul>
        </div>
        <div class="card-body p-0">
          @if (isLoading()) {
            <app-loading-spinner [fullPage]="true" />
          } @else {
            @switch (tab()) {
              @case ('canales') {
                @if (canales.data()?.length) {
                  <table class="table table-hover mb-0">
                    <thead><tr><th>ID</th><th>Nombre</th><th>Código</th></tr></thead>
                    <tbody>
                      @for (canal of canales.data(); track canal.id) {
                        <tr><td>{{ canal.id }}</td><td>{{ canal.nombre }}</td><td>{{ canal.codigo ?? '—' }}</td></tr>
                      }
                    </tbody>
                  </table>
                } @else {
                  <app-empty-state icon="bi-broadcast" title="Sin canales" />
                }
              }
              @case ('oficinas') {
                @if (oficinas.data()?.length) {
                  <table class="table table-hover mb-0">
                    <thead><tr><th>ID</th><th>Nombre</th><th>Canal</th></tr></thead>
                    <tbody>
                      @for (oficina of oficinas.data(); track oficina.id) {
                        <tr><td>{{ oficina.id }}</td><td>{{ oficina.nombre }}</td><td>{{ oficina.canal_id ?? '—' }}</td></tr>
                      }
                    </tbody>
                  </table>
                } @else {
                  <app-empty-state icon="bi-building" title="Sin oficinas" />
                }
              }
              @case ('ejecutivos') {
                @if (ejecutivos.data()?.length) {
                  <table class="table table-hover mb-0">
                    <thead><tr><th>Usuario</th><th>Nombre</th><th>Canal</th><th>Oficina</th></tr></thead>
                    <tbody>
                      @for (ejecutivo of ejecutivos.data(); track ejecutivo.id) {
                        <tr>
                          <td class="font-monospace">{{ ejecutivo.usuario_asesor }}</td>
                          <td>{{ ejecutivo.nombre ?? '—' }}</td>
                          <td>{{ ejecutivo.canal ?? '—' }}</td>
                          <td>{{ ejecutivo.oficina ?? '—' }}</td>
                        </tr>
                      }
                    </tbody>
                  </table>
                } @else {
                  <app-empty-state icon="bi-person-badge" title="Sin ejecutivos" />
                }
              }
            }
          }
        </div>
      </div>
    </div>
  `,
})
export class ReferenciasPageComponent {
  private readonly api = inject(ApiClient);
  protected readonly tab = signal<Tab>('canales');

  protected readonly canales = injectQuery<Canal[]>(() => ({
    queryKey: [QUERY_KEYS.REFERENCIAS_CANALES],
    queryFn: async () => (await this.api.get<Canal[]>('/referencias/canales')).data,
    enabled: this.tab() === 'canales',
  }));

  protected readonly oficinas = injectQuery<Oficina[]>(() => ({
    queryKey: [QUERY_KEYS.REFERENCIAS_OFICINAS],
    queryFn: async () => (await this.api.get<Oficina[]>('/referencias/oficinas')).data,
    enabled: this.tab() === 'oficinas',
  }));

  protected readonly ejecutivos = injectQuery<Ejecutivo[]>(() => ({
    queryKey: [QUERY_KEYS.REFERENCIAS_EJECUTIVOS],
    queryFn: async () => (await this.api.get<Ejecutivo[]>('/referencias/ejecutivos')).data,
    enabled: this.tab() === 'ejecutivos',
  }));

  protected readonly isLoading = computed<boolean>(
    () =>
      (this.tab() === 'canales' && this.canales.isLoading()) ||
      (this.tab() === 'oficinas' && this.oficinas.isLoading()) ||
      (this.tab() === 'ejecutivos' && this.ejecutivos.isLoading()),
  );
}
