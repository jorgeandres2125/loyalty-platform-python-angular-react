import { NgTemplateOutlet } from '@angular/common';
import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { injectQuery } from '@tanstack/angular-query-experimental';
import { ApiClient } from '../../shared/api/client';
import { AuthStore } from '../../entities/user/model/authStore';
import { injectMiContacto, injectMiDashboard } from '../../features/perfil-self/model/queries';
import type { MiDashboard } from '../../features/perfil-self/model/types';

interface DocInfo {
  subido: boolean;
  estado: string | null;
  version: number;
}

function badgeDocumento(info: DocInfo): string {
  if (info.estado?.toLowerCase() === 'aprobado') return 'success';
  if (info.estado?.toLowerCase() === 'revision') return 'info';
  if (info.subido) return 'warning';
  return 'secondary';
}

function colorPorcentaje(porcentaje: number): 'success' | 'warning' | 'danger' {
  if (porcentaje >= 100) return 'success';
  if (porcentaje >= 50) return 'warning';
  return 'danger';
}

function extraerSubprogramaId(contacto: unknown): number | null {
  const contactoData = contacto as Record<string, unknown> | null | undefined;
  if (!contactoData) return null;
  const subRaw = contactoData['comisionista_subprograma_id'];
  if (typeof subRaw === 'object' && subRaw !== null) {
    const cspid = (subRaw as Record<string, unknown>)['cspid'];
    return typeof cspid === 'number' ? cspid : null;
  }
  return typeof subRaw === 'number' ? subRaw : null;
}

@Component({
  selector: 'app-mi-dashboard-comisionista',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgTemplateOutlet, RouterLink],
  template: `
    <!-- Fila de etapa del perfil -->
    <ng-template #stageRow let-label="label" let-ok="ok">
      @if (ok === null) {
        <li class="d-flex align-items-center justify-content-between py-2 border-bottom">
          <span class="text-muted small">{{ label }}</span>
          <span class="badge bg-light text-dark">N/A</span>
        </li>
      } @else {
        <li class="d-flex align-items-center justify-content-between py-2 border-bottom">
          <span [class]="ok ? 'text-success' : 'text-muted'">
            <i class="bi me-2" [class]="ok ? 'bi-check-circle-fill' : 'bi-circle'"></i>
            {{ label }}
          </span>
          @if (ok) {
            <span class="badge bg-success">Completo</span>
          } @else {
            <a [routerLink]="perfilRoute()" class="btn btn-sm btn-outline-danger">
              Completar <i class="bi bi-arrow-right ms-1"></i>
            </a>
          }
        </li>
      }
    </ng-template>

    <!-- Fila de documento -->
    <ng-template #documentoRow let-label="label" let-info="info">
      <li class="d-flex align-items-center justify-content-between py-2 border-bottom">
        <span [class]="info.subido ? '' : 'text-muted'">
          <i
            class="bi me-2"
            [class]="info.subido ? 'bi-file-earmark-pdf-fill text-danger' : 'bi-file-earmark'"
          ></i>
          {{ label }}
          @if (info.subido && info.version > 1) {
            <span class="badge bg-light text-muted ms-2">v{{ info.version }}</span>
          }
        </span>
        <span class="badge" [class]="'bg-' + badgeDocumento(info)">
          {{ info.subido ? (info.estado ?? 'pendiente') : 'Sin cargar' }}
        </span>
      </li>
    </ng-template>

    @if (dash.isLoading()) {
      <div class="text-center py-5">
        <div class="spinner-border text-danger" role="status"></div>
      </div>
    } @else if (dash.isError() || !dash.data()) {
      <div class="alert alert-danger" role="alert">No se pudo cargar tu dashboard.</div>
    } @else {
      @let d = dash.data()!;
      <div class="container-fluid py-3">
        <!-- Saludo -->
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="row align-items-center">
              <div class="col-md-8">
                <h3 class="fw-bold mb-1">Hola, {{ d.nombre_completo || d.numero_documento }}</h3>
                <div class="text-muted">
                  <span class="badge bg-dark me-2">
                    <i class="bi me-1" [class]="esMovilidad() ? 'bi-car-front-fill' : 'bi-bag-fill'"></i>
                    {{ d.programa?.nombre ?? (esMovilidad() ? 'Movilidad' : 'Consumo y Servicios') }}
                  </span>
                  Documento: <span class="font-monospace">{{ d.numero_documento }}</span>
                </div>
              </div>
              <div class="col-md-4">
                <div class="text-end">
                  <div class="text-muted small fw-semibold mb-1">
                    Tu perfil está {{ porcentaje() }}% completo
                  </div>
                  <div class="progress" style="height: 12px">
                    <div
                      class="progress-bar"
                      [class]="'bg-' + porcentajeColor()"
                      role="progressbar"
                      [style.width.%]="porcentaje()"
                      [attr.aria-valuenow]="porcentaje()"
                      aria-valuemin="0"
                      aria-valuemax="100"
                    >
                      {{ d.perfil.stages_completos }}/{{ d.perfil.stages_total }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <!-- Mi Perfil -->
          <div class="col-md-6" [class]="esMovilidad() ? 'col-lg-4' : 'col-lg-6'">
            <div class="card shadow-sm border-0 h-100">
              <div class="card-header bg-white border-bottom-0 pt-3 pb-0">
                <h6 class="fw-bold mb-0">
                  <i class="bi bi-person-vcard-fill text-danger me-2"></i>Mi Perfil
                </h6>
              </div>
              <div class="card-body">
                <ul class="list-unstyled mb-3">
                  <ng-container
                    [ngTemplateOutlet]="stageRow"
                    [ngTemplateOutletContext]="{ label: 'Datos de contacto', ok: d.perfil.contacto_completo }"
                  />
                  @if (esMovilidad()) {
                    <ng-container
                      [ngTemplateOutlet]="stageRow"
                      [ngTemplateOutletContext]="{ label: 'Datos tributarios', ok: d.perfil.tributario_completo }"
                    />
                  }
                  <ng-container
                    [ngTemplateOutlet]="stageRow"
                    [ngTemplateOutletContext]="{ label: 'Perfil emocional', ok: d.perfil.emocional_completo }"
                  />
                </ul>
                <a [routerLink]="perfilRoute()" class="btn btn-danger btn-sm w-100">
                  <i class="bi bi-pencil-square me-1"></i>Editar mi perfil
                </a>
              </div>
            </div>
          </div>

          <!-- Mis Documentos (solo Movilidad) -->
          @if (esMovilidad() && d.documentos) {
            <div class="col-md-6 col-lg-4">
              <div class="card shadow-sm border-0 h-100">
                <div
                  class="card-header bg-white border-bottom-0 pt-3 pb-0 d-flex justify-content-between align-items-center"
                >
                  <h6 class="fw-bold mb-0">
                    <i class="bi bi-folder2-open text-danger me-2"></i>Mis Documentos
                  </h6>
                  <span class="text-muted small">
                    {{ d.documentos.total_subidos }}/{{ d.documentos.total_esperados }}
                  </span>
                </div>
                <div class="card-body">
                  <ul class="list-unstyled mb-3">
                    <ng-container
                      [ngTemplateOutlet]="documentoRow"
                      [ngTemplateOutletContext]="{ label: 'Cédula', info: d.documentos.items.cedula }"
                    />
                    <ng-container
                      [ngTemplateOutlet]="documentoRow"
                      [ngTemplateOutletContext]="{ label: 'RUT', info: d.documentos.items.rut }"
                    />
                    <ng-container
                      [ngTemplateOutlet]="documentoRow"
                      [ngTemplateOutletContext]="{ label: 'Contrato', info: d.documentos.items.contrato }"
                    />
                  </ul>
                  <a
                    [routerLink]="perfilRoute()"
                    fragment="documentos"
                    class="btn btn-outline-danger btn-sm w-100"
                  >
                    <i class="bi bi-upload me-1"></i>Gestionar mis documentos
                  </a>
                </div>
              </div>
            </div>
          }

          <!-- SAPIN / Incentivos -->
          <div class="col-md-6" [class]="esMovilidad() ? 'col-lg-4' : 'col-lg-6'">
            <div class="card shadow-sm border-0 h-100">
              <div class="card-header bg-white border-bottom-0 pt-3 pb-0">
                <h6 class="fw-bold mb-0">
                  <i class="bi bi-gift-fill text-warning me-2"></i>SAPIN / Incentivos
                </h6>
              </div>
              <div class="card-body">
                <div class="text-center py-2">
                  @if (auth.canAccessSapin() && d.incentivos_habilitados) {
                    <i class="bi bi-check-circle-fill text-success display-5 d-block mb-2"></i>
                    <p class="mb-3 fw-semibold">Tienes acceso a incentivos</p>
                    <a routerLink="/sapin" class="btn btn-warning btn-sm">
                      Ir a SAPIN <i class="bi bi-arrow-right ms-1"></i>
                    </a>
                  } @else {
                    <i class="bi bi-info-circle-fill text-muted display-5 d-block mb-2"></i>
                    <p class="text-muted mb-0">
                      {{
                        d.incentivos_habilitados
                          ? 'SAPIN aún no está habilitado para tu usuario.'
                          : 'Tu perfil no tiene incentivos asignados.'
                      }}
                    </p>
                  }
                </div>
              </div>
            </div>
          </div>

          <!-- Mis datos clave -->
          <div class="col-12">
            <div class="card shadow-sm border-0">
              <div class="card-header bg-white border-bottom-0 pt-3 pb-0">
                <h6 class="fw-bold mb-0">
                  <i class="bi bi-info-square text-danger me-2"></i>Mis datos clave
                </h6>
              </div>
              <div class="card-body">
                <div class="row g-3">
                  <div class="col-md-3">
                    <div class="text-muted small fw-semibold">Celular</div>
                    <div class="font-monospace">{{ d.celular ?? '—' }}</div>
                  </div>
                  <div class="col-md-4">
                    <div class="text-muted small fw-semibold">Email</div>
                    <div>{{ d.email ?? '—' }}</div>
                  </div>
                  <div [class]="esMovilidad() ? 'col-md-3' : 'col-md-2'">
                    <div class="text-muted small fw-semibold">Departamento</div>
                    <div>{{ d.departamento_nombre ?? d.departamento ?? '—' }}</div>
                  </div>
                  <div class="col-md-2">
                    <div class="text-muted small fw-semibold">Ciudad</div>
                    <div>{{ d.ciudad_nombre ?? d.ciudad ?? '—' }}</div>
                  </div>
                  @if (!esMovilidad()) {
                    <div class="col-md-3">
                      <div class="text-muted small fw-semibold">Subprograma</div>
                      <div>{{ subprogramaNombre() ?? '—' }}</div>
                    </div>
                  }
                  @if (d.direccion) {
                    <div class="col-12">
                      <div class="text-muted small fw-semibold">Dirección</div>
                      <div>{{ d.direccion }}</div>
                    </div>
                  }
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    }
  `,
})
export class MiDashboardComisionistaComponent {
  /** /perfil-movilidad o /perfil-consumo */
  readonly perfilRoute = input.required<string>();

  protected readonly auth = inject(AuthStore);
  private readonly api = inject(ApiClient);
  protected readonly dash = injectMiDashboard();
  private readonly miContacto = injectMiContacto();

  protected readonly esMovilidad = computed<boolean>(
    () => this.dash.data()?.rol_principal === 'comisionista',
  );

  private readonly subprogramasConsumo = injectQuery(() => ({
    queryKey: ['asesor-consumo-subprogramas', 2],
    queryFn: () =>
      this.api
        .get<{ cspid: number; cspid_nombre: string; cpid: number }[]>('/asesor-consumo/subprogramas/2')
        .then((r) => r.data),
    enabled: !this.esMovilidad(),
    staleTime: Infinity,
  }));

  protected readonly porcentaje = computed<number>(
    () => (this.dash.data() as MiDashboard | undefined)?.perfil.porcentaje_completado ?? 0,
  );
  protected readonly porcentajeColor = computed(() => colorPorcentaje(this.porcentaje()));

  protected readonly subprogramaNombre = computed<string | null>(() => {
    const subprogramaId: number | null = extraerSubprogramaId(this.miContacto.data());
    if (subprogramaId === null) return null;
    return this.subprogramasConsumo.data()?.find((sub) => sub.cspid === subprogramaId)?.cspid_nombre ?? null;
  });

  protected badgeDocumento(info: DocInfo): string {
    return badgeDocumento(info);
  }
}
