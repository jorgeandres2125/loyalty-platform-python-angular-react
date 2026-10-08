import { CatalogoCrudPage } from '../../shared/ui/components/CatalogoCrudPage';
import type { FormValues } from '../../shared/ui/components/CatalogoCrudPage';
import {
  useActualizarAdminEps,
  useAdminEpsList,
  useCrearAdminEps,
  useEliminarAdminEps,
} from '../../features/admin-eps/model/useAdminEps';
import type {
  AdminEpsFormPayload,
  AdminEpsListItem,
} from '../../features/admin-eps/model/types';

export function EpsAdminPage() {
  const actualizarMut = useActualizarAdminEps();
  return (
    <CatalogoCrudPage<AdminEpsListItem, AdminEpsFormPayload>
      title="Administrar EPS"
      icon="bi-heart-pulse-fill"
      singular="EPS"
      backTo="/admin/catalogos"
      idOf={(i) => i.tid}
      columns={[
        { header: 'Código', width: 100, cell: (i) => <code>{i.tid}</code> },
        { header: 'Nombre', className: 'fw-semibold', cell: (i) => i.nombre },
        {
          header: 'NIT', width: 200,
          cell: (i) => (i.nit ? <code className="small">{i.nit}</code> : <span className="text-muted small">—</span>),
        },
      ]}
      fields={[
        { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: SURA EPS' },
        { key: 'nit', label: 'NIT', maxLength: 30, col: 4, placeholder: 'Opcional' },
      ]}
      initForm={{ nombre: '', nit: '' }}
      itemToForm={(i) => ({ nombre: i.nombre, nit: i.nit ?? '' })}
      toPayload={(f: FormValues): AdminEpsFormPayload => ({
        nombre: f.nombre.trim(),
        nit: f.nit.trim() === '' ? null : f.nit.trim(),
      })}
      validate={(f) => (f.nombre.trim() ? null : 'El nombre de la EPS es obligatorio')}
      deleteWarning={
        <>¿Confirma eliminar la EPS? Esta acción es <strong>permanente</strong>.<br />
          <small className="text-muted">Si está referenciada en perfiles tributarios, la operación será rechazada.</small></>
      }
      useList={useAdminEpsList}
      crearMut={useCrearAdminEps()}
      actualizar={(tid, payload) => actualizarMut.mutateAsync({ tid, payload })}
      actualizarPending={actualizarMut.isPending}
      eliminarMut={useEliminarAdminEps()}
    />
  );
}
