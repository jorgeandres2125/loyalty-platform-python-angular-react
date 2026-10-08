import { useEffect, useState } from 'react';
import { Alert, Spinner, Table } from 'react-bootstrap';
import { EstadoSwitch } from '../../../shared/ui/components/EstadoSwitch';
import { extractError } from '../../../shared/lib/extractError';
import {
  MetroTileToggle,
  type MetroTileColor,
} from '../../../shared/ui/components/MetroTileToggle';
import {
  useActualizarModuloActivo,
  useActualizarPermisos,
  useMatrizPorRol,
  useRolesList,
} from '../../../features/admin-autorizaciones/model/useAdminAutorizaciones';
import type {
  AutorizacionFlagsPayload,
  AutorizacionModuloItem,
} from '../../../features/admin-autorizaciones/model/types';

const FLAGS: { key: keyof AutorizacionFlagsPayload; label: string }[] = [
  { key: 'puede_ver', label: 'Ver' },
  { key: 'puede_crear', label: 'Crear' },
  { key: 'puede_editar', label: 'Editar' },
  { key: 'puede_eliminar', label: 'Eliminar' },
  { key: 'puede_exportar', label: 'Exportar' },
  { key: 'puede_aprobar', label: 'Aprobar' },
];

// -- Rol -> icono y color Metro ----------------------------------------------
const ROL_META_MAP: Record<number, { icon: string; color: MetroTileColor }> = {
  1:  { icon: 'bi-person-slash',            color: 'gray'      },
  2:  { icon: 'bi-person-check-fill',       color: 'navy'      },
  3:  { icon: 'bi-shield-fill',             color: 'dark-navy' },
  4:  { icon: 'bi-person-badge-fill',       color: 'teal'      },
  5:  { icon: 'bi-globe',                   color: 'blue'      },
  7:  { icon: 'bi-truck',                   color: 'gold'      },
  8:  { icon: 'bi-graph-up-arrow',          color: 'green'     },
  12: { icon: 'bi-headset',                 color: 'yellow'    },
  13: { icon: 'bi-file-earmark-text-fill',  color: 'gray'      },
  14: { icon: 'bi-bag-fill',                color: 'red'       },
  15: { icon: 'bi-bag-check-fill',          color: 'cyan'      },
  16: { icon: 'bi-briefcase-fill',          color: 'amber'     },
  18: { icon: 'bi-telephone-fill',          color: 'purple'    },
  19: { icon: 'bi-briefcase-fill',          color: 'orange'    },
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

// -- PermisoModuloRow --------------------------------------------------------

interface RowProps {
  item: AutorizacionModuloItem;
  flags: AutorizacionFlagsPayload;
  activo: boolean;
  dirty: boolean;
  disabled: boolean;
  onFlagsChange: (flags: AutorizacionFlagsPayload) => void;
  onActivoChange: (activo: boolean) => void;
}

function PermisoModuloRow({
  item,
  flags,
  activo,
  dirty,
  disabled,
  onFlagsChange,
  onActivoChange,
}: RowProps) {
  const toggleFlag = (key: keyof AutorizacionFlagsPayload) => {
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
    onFlagsChange(next);
  };

  return (
    <tr style={{ background: dirty ? 'rgba(255, 193, 0, 0.10)' : undefined }}>
      <td>
        <div className="d-flex align-items-center gap-2">
          <i className={`bi ${item.module_icono} text-secondary`} style={{ fontSize: '1.1rem' }} />
          <div>
            <div className="fw-semibold d-flex align-items-center gap-2" style={{ fontSize: '0.9rem' }}>
              {item.module_nombre}
              {dirty && (
                <span className="badge bg-warning text-dark" style={{ fontSize: '0.6rem' }}>
                  sin guardar
                </span>
              )}
            </div>
            <code className="text-muted" style={{ fontSize: '0.72rem' }}>{item.module_code}</code>
          </div>
        </div>
      </td>
      <td className="text-center align-middle">
        <EstadoSwitch
          id={`mod-activo-${item.module_id}`}
          checked={activo}
          onChange={onActivoChange}
          compact
          disabled={disabled}
          labelActivo="Activo"
          labelInactivo="Inactivo"
        />
      </td>
      {FLAGS.map((f) => (
        <td key={f.key} className="text-center align-middle">
          <EstadoSwitch
            id={`perm-${item.module_id}-${f.key}`}
            checked={flags[f.key]}
            onChange={() => toggleFlag(f.key)}
            compact
            disabled={disabled}
          />
        </td>
      ))}
    </tr>
  );
}

// -- RolPermisosPanel --------------------------------------------------------

interface RolPanelProps {
  rid: number;
  name: string;
  onSaved: (mensaje: string) => void;
  onError: (mensaje: string) => void;
}

function RolPermisosPanel({ rid, name, onSaved, onError }: RolPanelProps) {
  const { icon, color } = getRolMeta(rid);
  const matriz = useMatrizPorRol(rid);
  const mutPermisos = useActualizarPermisos();
  const mutActivo = useActualizarModuloActivo();

  const [draft, setDraft] = useState<Record<number, DraftEntry>>({});
  const [original, setOriginal] = useState<Record<number, DraftEntry>>({});
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
    if (!matriz.data) return;
    setDraft(buildDraft(matriz.data));
    setOriginal(buildDraft(matriz.data));
  }, [matriz.data]);

  const handleFlagsChange = (moduleId: number, flags: AutorizacionFlagsPayload) => {
    setDraft((prev) => ({ ...prev, [moduleId]: { ...prev[moduleId], flags } }));
  };

  const handleActivoChange = (moduleId: number, activo: boolean) => {
    setDraft((prev) => ({ ...prev, [moduleId]: { ...prev[moduleId], activo } }));
  };

  const dirtyIds: number[] = Object.keys(draft)
    .map(Number)
    .filter((id) => {
      const d = draft[id];
      const o = original[id];
      return d !== undefined && o !== undefined && entryDirty(d, o);
    });
  const isDirty: boolean = dirtyIds.length > 0;

  const handleSave = async () => {
    if (!isDirty || saving) return;
    setSaving(true);
    try {
      for (const id of dirtyIds) {
        const entry = draft[id];
        const orig = original[id];
        if (entry === undefined || orig === undefined) continue;
        if (flagsDiffer(entry.flags, orig.flags)) {
          await mutPermisos.mutateAsync({ rid, moduleId: id, payload: entry.flags });
        }
        if (entry.activo !== orig.activo) {
          await mutActivo.mutateAsync({ moduleId: id, activo: entry.activo });
        }
      }
      const total: number = dirtyIds.length;
      onSaved(`Permisos de "${name}" guardados (${total} ${total === 1 ? 'modulo' : 'modulos'})`);
      setOriginal(draft);
    } catch (err) {
      onError(extractError(err, 'Error al guardar los permisos'));
    } finally {
      setSaving(false);
    }
  };

  const activeCount: number = (matriz.data ?? []).filter(
    (m) => draft[m.module_id]?.flags.puede_ver,
  ).length;
  const totalCount: number = (matriz.data ?? []).length;
  const subtitle: string = matriz.data
    ? `${activeCount} de ${totalCount} modulos con acceso${isDirty ? ` - ${dirtyIds.length} sin guardar` : ''}`
    : 'Cargando permisos...';
  const badge: number | null = matriz.data ? (activeCount || null) : null;

  return (
    <MetroTileToggle
      title={name}
      icon={icon}
      color={color}
      size="wide"
      subtitle={subtitle}
      badge={badge}
      closeLabel="Cerrar permisos"
      saveLabel="Guardar permisos"
      onSave={handleSave}
      saving={saving}
      saveDisabled={!isDirty}
    >
      {matriz.isLoading ? (
        <div className="text-center py-4">
          <Spinner animation="border" />
        </div>
      ) : matriz.isError ? (
        <Alert variant="danger" className="mb-0">
          Error al cargar la matriz de permisos
        </Alert>
      ) : (
        <Table hover responsive className="mb-0 align-middle">
          <thead className="table-light">
            <tr>
              <th>Modulo</th>
              <th className="text-center">Activo</th>
              {FLAGS.map((f) => (
                <th key={f.key} className="text-center">
                  {f.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(matriz.data ?? []).map((item) => {
              const entry = draft[item.module_id];
              if (entry === undefined) return null;
              const orig = original[item.module_id];
              return (
                <PermisoModuloRow
                  key={item.module_id}
                  item={item}
                  flags={entry.flags}
                  activo={entry.activo}
                  dirty={orig !== undefined && entryDirty(entry, orig)}
                  disabled={saving}
                  onFlagsChange={(flags) => handleFlagsChange(item.module_id, flags)}
                  onActivoChange={(activo) => handleActivoChange(item.module_id, activo)}
                />
              );
            })}
          </tbody>
        </Table>
      )}
    </MetroTileToggle>
  );
}

// -- PermisosModulosTab ------------------------------------------------------

export function PermisosModulosTab() {
  const roles = useRolesList();
  const [success, setSuccess] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!success) return;
    const t = setTimeout(() => setSuccess(''), 3000);
    return () => clearTimeout(t);
  }, [success]);

  return (
    <div>
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          <i className="bi bi-check-circle me-2" />
          {success}
        </Alert>
      )}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          <i className="bi bi-exclamation-triangle me-2" />
          {error}
        </Alert>
      )}

      {roles.isLoading ? (
        <div className="text-center py-5">
          <Spinner animation="border" />
        </div>
      ) : (
        <div className="d-flex flex-column gap-2">
          {(roles.data ?? []).map((r) => (
            <RolPermisosPanel
              key={r.rid}
              rid={r.rid}
              name={r.name}
              onSaved={setSuccess}
              onError={setError}
            />
          ))}
        </div>
      )}
    </div>
  );
}