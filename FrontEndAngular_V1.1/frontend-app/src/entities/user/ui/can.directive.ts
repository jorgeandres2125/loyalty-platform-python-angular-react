import { Directive, TemplateRef, ViewContainerRef, effect, inject, input } from '@angular/core';
import { Permissions } from '../model/permissions';
import type { AccionModulo } from '../model/types';

/**
 * Renderiza el contenido solo si el usuario tiene la accion sobre el modulo
 * (equivalente al componente `<Can>`).
 * Uso: <button *appCan="'REPORTES'; accion: 'exportar'; else sinPermiso">…</button>
 */
@Directive({ selector: '[appCan]' })
export class CanDirective {
  private readonly permisos = inject(Permissions);
  private readonly tpl = inject(TemplateRef<unknown>);
  private readonly vcr = inject(ViewContainerRef);

  readonly appCan = input.required<string>();
  readonly appCanAccion = input<AccionModulo>('ver');
  readonly appCanElse = input<TemplateRef<unknown> | null>(null);

  constructor() {
    effect(() => {
      const permitido: boolean = this.permisos.can(this.appCan(), this.appCanAccion());
      const fallback = this.appCanElse();
      this.vcr.clear();
      if (permitido) {
        this.vcr.createEmbeddedView(this.tpl);
      } else if (fallback) {
        this.vcr.createEmbeddedView(fallback);
      }
    });
  }
}
