import { ChangeDetectionStrategy, Component, effect, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { PageHeaderComponent } from '../../shared/ui/components/page-header.component';
import { AutofocusDirective } from '../../shared/ui/directives/autofocus.directive';
import { extractError } from '../../shared/lib/extractError';
import {
  injectActualizarAdminPrograma,
  injectAdminProgramasList,
} from '../../features/admin-programas/model/queries';
import type { AdminProgramaItem } from '../../features/admin-programas/model/types';

@Component({
  selector: 'app-programas-admin-page',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [PageHeaderComponent, AutofocusDirective],
  template: `
    <div>
      <app-page-header
        title="Administrar Programas"
        subtitle="Solo edición del nombre — los códigos cpid están cableados al dominio (1=Movilidad, 2=Consumo)."
        icon="bi-bookmark-star-fill"
      />
      <div class="mb-3">
        <button type="button" class="btn btn-sm btn-outline-secondary" (click)="volver()">
          <i class="bi bi-arrow-left me-1"></i>Volver
        </button>
      </div>

      @if (success()) {
        <div class="alert alert-success alert-dismissible">
          <i class="bi bi-check-circle me-2"></i>{{ success() }}
          <button type="button" class="btn-close" aria-label="Close" (click)="success.set('')"></button>
        </div>
      }

      <div class="card border-0 shadow-sm">
        <div class="card-body p-0">
          @if (lista.isLoading()) {
            <div class="text-center py-5"><div class="spinner-border" role="status"></div></div>
          } @else if (lista.isError()) {
            <div class="alert alert-danger m-3">Error al cargar los programas</div>
          } @else {
            <div class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th style="width: 100px">cpid</th>
                    <th>Nombre</th>
                    <th class="text-end" style="width: 180px">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  @for (p of lista.data() ?? []; track p.cpid) {
                    <tr>
                      <td><code>{{ p.cpid }}</code></td>
                      <td>
                        @if (editId() === p.cpid) {
                          <form (submit)="handleGuardar($event)" class="d-flex gap-2 align-items-center">
                            <input
                              type="text"
                              class="form-control form-control-sm"
                              maxlength="50"
                              [value]="nombre()"
                              (input)="nombre.set($any($event.target).value)"
                              appAutofocus
                              style="max-width: 300px"
                            />
                            <button type="submit" class="btn btn-sm btn-primary" [disabled]="actualizarMut.isPending()">
                              @if (actualizarMut.isPending()) {
                                <span class="spinner-border spinner-border-sm"></span>
                              } @else {
                                <i class="bi bi-check-lg"></i>
                              }
                            </button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" (click)="handleCancelar()"
                              [disabled]="actualizarMut.isPending()">
                              <i class="bi bi-x-lg"></i>
                            </button>
                          </form>
                        } @else {
                          <span class="fw-semibold">{{ p.cp_nombre }}</span>
                        }
                      </td>
                      <td class="text-end">
                        @if (editId() !== p.cpid) {
                          <button type="button" class="btn btn-sm btn-outline-primary" (click)="handleEditar(p)">
                            <i class="bi bi-pencil-fill me-1"></i>Editar nombre
                          </button>
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

      @if (editId() !== null && error()) {
        <div class="alert alert-danger mt-3">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ error() }}
        </div>
      }
    </div>
  `,
})
export class ProgramasAdminPageComponent {
  private readonly router = inject(Router);
  protected readonly lista = injectAdminProgramasList();
  protected readonly actualizarMut = injectActualizarAdminPrograma();

  protected readonly editId = signal<number | null>(null);
  protected readonly nombre = signal<string>('');
  protected readonly error = signal<string>('');
  protected readonly success = signal<string>('');

  constructor() {
    effect((onCleanup) => {
      if (!this.success()) return;
      const t = setTimeout(() => this.success.set(''), 3500);
      onCleanup(() => clearTimeout(t));
    });
  }

  protected volver(): void {
    void this.router.navigateByUrl('/admin/catalogos');
  }

  protected handleEditar(item: AdminProgramaItem): void {
    this.editId.set(item.cpid);
    this.nombre.set(item.cp_nombre);
    this.error.set('');
  }

  protected handleCancelar(): void {
    this.editId.set(null);
    this.nombre.set('');
    this.error.set('');
  }

  protected async handleGuardar(e: Event): Promise<void> {
    e.preventDefault();
    this.error.set('');
    const editId = this.editId();
    if (editId === null) return;
    const nombre: string = this.nombre().trim();
    if (!nombre) {
      this.error.set('El nombre del programa es obligatorio');
      return;
    }
    try {
      await this.actualizarMut.mutateAsync({ cpid: editId, payload: { cp_nombre: nombre } });
      this.success.set('Programa actualizado correctamente');
      this.editId.set(null);
      this.nombre.set('');
    } catch (err) {
      this.error.set(extractError(err, 'Error al actualizar el programa'));
    }
  }
}
