import { CatalogoCrudPage } from '../../shared/ui/components/CatalogoCrudPage';
import type { FormValues } from '../../shared/ui/components/CatalogoCrudPage';
import {
  useActualizarAdminArl,
  useAdminArlList,
  useCrearAdminArl,
  useEliminarAdminArl,
} from '../../features/admin-arl/model/useAdminArl';
import type {
  AdminArlFormPayload,
  AdminArlListItem,
} from '../../features/admin-arl/model/types';

export function ArlAdminPage() {
  const actualizarMut = useActualizarAdminArl();
  return (
    <CatalogoCrudPage<AdminArlListItem, AdminArlFormPayload>
      title="Administrar ARL"
      icon="bi-shield-fill-plus"
      singular="ARL"
      backTo="/admin/catalogos"
      idOf={(item) => item.tid}
      columns={[
        { header: 'Código', width: 100, cell: (i) => <code>{i.tid}</code> },
        { header: 'Nombre', className: 'fw-semibold', cell: (i) => i.nombre },
        {
          header: 'NIT', width: 200,
          cell: (i) => (i.nit ? <code className="small">{i.nit}</code> : <span className="text-muted small">—</span>),
        },
      ]}
      fields={[
        { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: SURA ARL' },
        { key: 'nit', label: 'NIT', maxLength: 30, col: 4, placeholder: 'Opcional' },
      ]}
      initForm={{ nombre: '', nit: '' }}
      itemToForm={(i) => ({ nombre: i.nombre, nit: i.nit ?? '' })}
      toPayload={(f: FormValues): AdminArlFormPayload => ({
        nombre: f.nombre.trim(),
        nit: f.nit.trim() === '' ? null : f.nit.trim(),
      })}
      validate={(f) => (f.nombre.trim() ? null : 'El nombre de la ARL es obligatorio')}
      deleteWarning={
        <>¿Confirma eliminar la ARL? Esta acción es <strong>permanente</strong>.<br />
          <small className="text-muted">Si está referenciada en perfiles tributarios, la operación será rechazada.</small></>
      }
      useList={useAdminArlList}
      crearMut={useCrearAdminArl()}
      actualizar={(tid, payload) => actualizarMut.mutateAsync({ tid, payload })}
      actualizarPending={actualizarMut.isPending}
      eliminarMut={useEliminarAdminArl()}
    />
  );
}
