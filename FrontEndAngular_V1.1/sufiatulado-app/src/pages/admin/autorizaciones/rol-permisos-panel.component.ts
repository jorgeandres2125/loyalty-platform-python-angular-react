import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  input,
  output,
  signal,
  untracked,
} from '@angular/core';
import { EstadoSwitchComponent } from '../../../shared/ui/components/estado-switch.component';
import {
  MetroTileToggleComponent,
  type MetroTileColor,
} from '../../../shared/ui/components/metro-tile-toggle.component';
import { extractError } from '../../../shared/lib/extractError';
import {
  injectActualizarModuloActivo,
  injectActualizarPermisos,
  injectMatrizPorRol,
} from '../../../features/admin-autorizaciones/model/queries';
import type {
  AutorizacionFlagsPayload,
  AutorizacionModuloItem,
} from '../../../features/admin-autorizaciones/model/types';

export const FLAGS: { key: keyof AutorizacionFlagsPayload; label: string }[] = [
  { key: 'puede_ver', label: 'Ver' },
  { key: 'puede_crear', label: 'Crear' },
  { key: 'puede_editar', label: 'Editar' },
  { key: 'puede_eliminar', label: 'Eliminar' },
  { key: 'puede_exportar', label: 'Exportar' },
  { key: 'puede_aprobar', label: 'Aprobar' },
];

// -- Rol -> icono y color Metro ----------------------------------------------
const ROL_META_MAP: Record<number, { icon: string; color: MetroTileColor }> = {
  1: { icon: 'bi-person-slash', color: 'gray' },
  2: { icon: 'bi-person-check-fill', color: 'navy' },
  3: { icon: 'bi-shield-fill', color: 'dark-navy' },
  4: { icon: 'bi-person-badge-fill', color: 'teal' },
  5: { icon: 'bi-globe', color: 'blue' },
  7: { icon: 'bi-truck', color: 'gold' },
  8: { icon: 'bi-graph-up-arrow', color: 'green' },
  12: { icon: 'bi-headset', color: 'yellow' },
  13: { icon: 'bi-file-earmark-text-fill', color: 'gray' },
  14: { icon: 'bi-bag-fill', color: 'red' },
  15: { icon: 'bi-bag-check-fill', color: 'cyan' },
  16: { icon: 'bi-briefcase-fill', color: 'amber' },
  18: { icon: 'bi-telephone-fill', color: 'purple' },
  19: { icon: 'bi-briefcase-fill', color: 'orange' },
};

function getRolMeta(rid: number): { icon: string; color: MetroTileColor } {
  return ROL_META_MAP[rid] ?? { icon: 'bi-person-fill', color: 'gray' };
}

// -- Helpers de permisos -----------------------------------------------------

interface DraftEntry {
  flags: AutorizacionFlagsPayload;
  activo: boolean;
}

function toPayload(item: AutorizacionModuloItem): AutorizacionFlagsPayload {
  return {
    puede_ver: item.puede_ver,
    puede_crear: item.puede_crear,
    puede_editar: item.puede_editar,
    puede_eliminar: item.puede_eliminar,
    puede_exportar: item.puede_exportar,
    puede_aprobar: item.puede_aprobar,
  };
}

function buildDraft(data: AutorizacionModuloItem[]): Record<number, DraftEntry> {
  const out: Record<number, DraftEntry> = {};
  for (const item of data) {
    out[item.module_id] = { flags: toPayload(item), activo: item.module_activo };
  }
  return out;
}

function flagsDiffer(a: AutorizacionFlagsPayload, b: AutorizacionFlagsPayload): boolean {
  return FLAGS.some((f) => a[f.key] !== b[f.key]);
}

function entryDirty(a: DraftEntry, b: DraftEntry): boolean {
  return a.activo !== b.activo || flagsDiffer(a.flags, b.flags);
}

@Component({
  selector: 'app-rol-permisos-panel',
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [MetroTileToggleComponent, EstadoSwitchComponent],
  template: `
    <app-metro-tile-toggle
      [title]="name()"
      [icon]="meta().icon"
      [color]="meta().color"
      size="wide"
      [subtitle]="subtitle()"
      [badge]="badge()"
      closeLabel="Cerrar permisos"
      saveLabel="Guardar permisos"
      [hasSave]="true"
      (save)="handleSave()"
      [saving]="saving()"
      [saveDisabled]="!isDirty()"
    >
      @if (matriz.isLoading()) {
        <div class="text-center py-4"><div class="spinner-border" role="status"></div></div>
      } @else if (matriz.isError()) {
        <div class="alert alert-danger mb-0">Error al cargar la matriz de permisos</div>
      } @else {
        <div class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="table-light">
              <tr>
                <th>Modulo</th>
                <th class="text-center">Activo</th>
                @for (f of flags; track f.key) {
                  <th class="text-center">{{ f.label }}</th>
                }
              </tr>
            </thead>
            <tbody>
              @for (item of matriz.data() ?? []; track item.module_id) {
                @if (draft()[item.module_id]; as entry) {
                  @let dirty = esDirty(item.module_id);
                  <tr [style.background]="dirty ? 'rgba(255, 193, 0, 0.10)' : null">
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <i class="bi text-secondary" [class]="item.module_icono" style="font-size: 1.1rem"></i>
                        <div>
                          <div class="fw-semibold d-flex align-items-center gap-2" style="font-size: 0.9rem">
                            {{ item.module_nombre }}
                            @if (dirty) {
                              <span class="badge bg-warning text-dark" style="font-size: 0.6rem">sin guardar</span>
                            }
                          </div>
                          <code class="text-muted" style="font-size: 0.72rem">{{ item.module_code }}</code>
                        </div>
                      </div>
                    </td>
                    <td class="text-center align-middle">
                      <app-estado-switch
                        [id]="'mod-activo-' + item.module_id"
                        [checked]="entry.activo"
                        (checkedChange)="handleActivoChange(item.module_id, $event)"
                        [compact]="true"
                        [disabled]="saving()"
                        labelActivo="Activo"
                        labelInactivo="Inactivo"
                      />
                    </td>
                    @for (f of flags; track f.key) {
                      <td class="text-center align-middle">
                        <app-estado-switch
                          [id]="'perm-' + item.module_id + '-' + f.key"
                          [checked]="entry.flags[f.key]"
                          (checkedChange)="toggleFlag(item.module_id, f.key)"
                          [compact]="true"
                          [disabled]="saving()"
                        />
                      </td>
                    }
                  </tr>
                }
              }
            </tbody>
          </table>
        </div>
      }
    </app-metro-tile-toggle>
  `,
})
export class RolPermisosPanelComponent {
  readonly rid = input.required<number>();
  readonly name = input.required<string>();
  readonly saved = output<string>();
  readonly failed = output<string>();

  protected readonly flags = FLAGS;
  protected readonly meta = computed(() => getRolMeta(this.rid()));

  protected readonly matriz = injectMatrizPorRol(() => this.rid());
  private readonly mutPermisos = injectActualizarPermisos();
  private readonly mutActivo = injectActualizarModuloActivo();

  protected readonly draft = signal<Record<number, DraftEntry>>({});
  private readonly original = signal<Record<number, DraftEntry>>({});
  protected readonly saving = signal<boolean>(false);

  private readonly dirtyIds = computed<number[]>(() => {
    const draft = this.draft();
    const original = this.original();
    return Object.keys(draft)
      .map(Number)
      .filter((id) => {
        const d = draft[id];
        const o = original[id];
        return d !== undefined && o !== undefined && entryDirty(d, o);
      });
  });
  protected readonly isDirty = computed<boolean>(() => this.dirtyIds().length > 0);

  private readonly activeCount = computed<number>(() => {
    const draft = this.draft();
    return (this.matriz.data() ?? []).filter((m) => draft[m.module_id]?.flags.puede_ver).length;
  });

  protected readonly subtitle = computed<string>(() => {
    const data = this.matriz.data();
    if (!data) return 'Cargando permisos...';
    const sinGuardar: string = this.isDirty() ? ` - ${this.dirtyIds().length} sin guardar` : '';
    return `${this.activeCount()} de ${data.length} modulos con acceso${sinGuardar}`;
  });

  protected readonly badge = computed<number | null>(() =>
    this.matriz.data() ? this.activeCount() || null : null,
  );

  constructor() {
    effect(() => {
      const data = this.matriz.data();
      if (!data) return;
      untracked(() => {
        this.draft.set(buildDraft(data));
        this.original.set(buildDraft(data));
      });
    });
  }

  protected esDirty(moduleId: number): boolean {
    const d = this.draft()[moduleId];
    const o = this.original()[moduleId];
    return d !== undefined && o !== undefined && entryDirty(d, o);
  }

  protected toggleFlag(moduleId: number, key: keyof AutorizacionFlagsPayload): void {
    const entry = this.draft()[moduleId];
    if (!entry) return;
    const flags = entry.flags;
    const next: AutorizacionFlagsPayload = { ...flags, [key]: !flags[key] };
    if (key === 'puede_ver' && !next.puede_ver) {
      next.puede_crear = false;
      next.puede_editar = false;
      next.puede_eliminar = false;
      next.puede_exportar = false;
      next.puede_aprobar = false;
    } else if (key !== 'puede_ver' && next[key]) {
      next.puede_ver = true;
    }
    this.draft.update((prev) => ({ ...prev, [moduleId]: { ...prev[moduleId], flags: next } }));
  }

  protected handleActivoChange(moduleId: number, activo: boolean): void {
    this.draft.update((prev) => ({ ...prev, [moduleId]: { ...prev[moduleId], activo } }));
  }

  protected async handleSave(): Promise<void> {
    if (!this.isDirty() || this.saving()) return;
    this.saving.set(true);
    const ids: number[] = this.dirtyIds();
    const draft = this.draft();
    const original = this.original();
    try {
      for (const id of ids) {
        const entry = draft[id];
        const orig = original[id];
        if (entry === undefined || orig === undefined) continue;
        if (flagsDiffer(entry.flags, orig.flags)) {
          await this.mutPermisos.mutateAsync({ rid: this.rid(), moduleId: id, payload: entry.flags });
        }
        if (entry.activo !== orig.activo) {
          await this.mutActivo.mutateAsync({ moduleId: id, activo: entry.activo });
        }
      }
      const total: number = ids.length;
      this.saved.emit(
        `Permisos de "${this.name()}" guardados (${total} ${total === 1 ? 'modulo' : 'modulos'})`,
      );
      this.original.set(draft);
    } catch (err) {
      this.failed.emit(extractError(err, 'Error al guardar los permisos'));
    } finally {
      this.saving.set(false);
    }
  }
}
