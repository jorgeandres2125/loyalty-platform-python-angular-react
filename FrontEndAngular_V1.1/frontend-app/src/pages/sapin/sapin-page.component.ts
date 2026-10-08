import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { DomSanitizer, type SafeResourceUrl } from '@angular/platform-browser';
import { injectSapinToken } from '../../features/sapin/model/sapinToken';
import { AuthStore } from '../../entities/user/model/authStore';
import { LoadingSpinnerComponent } from '../../shared/ui/components/loading-spinner.component';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';

@Component({
  selector: 'app-sapin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [LoadingSpinnerComponent, PageHeaderComponent],
  template: `
    @if (!auth.canAccessSapin()) {
      <div>
        <app-page-header title="Incentivos SAPIN" icon="bi-stars" />
        <div class="text-center py-5">
          <i class="bi bi-lock-fill text-muted" style="font-size: 3rem"></i>
          <h5 class="mt-3 text-muted">Acceso restringido</h5>
          <p class="text-muted small">No tienes acceso a los incentivos SAPIN.</p>
        </div>
      </div>
    } @else {
      <div>
        <app-page-header
          title="Incentivos SAPIN"
          subtitle="Plataforma de incentivos y recompensas"
          icon="bi-stars"
        />

        @if (token.isLoading()) {
          <app-loading-spinner [fullPage]="true" text="Cargando plataforma SAPIN..." />
        }

        @if (token.error()) {
          <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle me-2"></i>
            No se pudo cargar la plataforma SAPIN. Intenta de nuevo.
          </div>
        }

        @if (token.data(); as data) {
          <div class="bg-white rounded-3 shadow-sm overflow-hidden" style="min-height: 75vh">
            <div class="p-3 border-bottom d-flex align-items-center justify-content-between">
              <div class="d-flex align-items-center gap-2">
                <i class="bi bi-stars text-warning"></i>
                <span class="fw-semibold small">Portal de Incentivos SAPIN</span>
              </div>
              <a
                [href]="data.sapin_url"
                target="_blank"
                rel="noopener noreferrer"
                class="btn btn-sm btn-outline-primary"
              >
                <i class="bi bi-box-arrow-up-right me-1"></i>
                Abrir en nueva ventana
              </a>
            </div>
            <iframe
              [src]="iframeSrc()"
              title="Portal SAPIN"
              width="100%"
              style="height: calc(75vh - 56px); border: none"
              sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
            ></iframe>
          </div>
        }
      </div>
    }
  `,
})
export class SapinPageComponent {
  protected readonly auth = inject(AuthStore);
  private readonly sanitizer = inject(DomSanitizer);
  protected readonly token = injectSapinToken();

  // La URL del portal la entrega el backend (fuente confiable), por eso se marca segura.
  protected readonly iframeSrc = computed<SafeResourceUrl | null>(() => {
    const data = this.token.data();
    if (!data) return null;
    return this.sanitizer.bypassSecurityTrustResourceUrl(`${data.sapin_url}?token=${data.token}`);
  });
}
