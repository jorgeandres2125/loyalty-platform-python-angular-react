import { CatalogoCrudPage } from '../../shared/ui/components/CatalogoCrudPage';
import type { FormValues } from '../../shared/ui/components/CatalogoCrudPage';
import {
  useActualizarAdminBanco,
  useAdminBancosList,
  useCrearAdminBanco,
  useEliminarAdminBanco,
} from '../../features/admin-bancos/model/useAdminBancos';
import type {
  AdminBancoFormPayload,
  AdminBancoListItem,
} from '../../features/admin-bancos/model/types';

export function BancosAdminPage() {
  const actualizarMut = useActualizarAdminBanco();
  return (
    <CatalogoCrudPage<AdminBancoListItem, AdminBancoFormPayload>
      title="Administrar Bancos"
      icon="bi-bank2"
      singular="Banco"
      backTo="/admin/catalogos"
      idOf={(i) => i.tid}
      columns={[
        { header: 'Código', width: 100, cell: (i) => <code>{i.tid}</code> },
        { header: 'Nombre', className: 'fw-semibold', cell: (i) => i.nombre },
        {
          header: 'Código bancario', width: 200,
          cell: (i) => (i.codigo ? <code className="small">{i.codigo}</code> : <span className="text-muted small">—</span>),
        },
      ]}
      fields={[
        { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: Bancolombia' },
        { key: 'codigo', label: 'Código bancario', maxLength: 10, col: 4, placeholder: 'Opcional' },
      ]}
      initForm={{ nombre: '', codigo: '' }}
      itemToForm={(i) => ({ nombre: i.nombre, codigo: i.codigo ?? '' })}
      toPayload={(f: FormValues): AdminBancoFormPayload => ({
        nombre: f.nombre.trim(),
        codigo: f.codigo.trim() === '' ? null : f.codigo.trim(),
      })}
      validate={(f) => (f.nombre.trim() ? null : 'El nombre del banco es obligatorio')}
      deleteWarning={
        <>¿Confirma eliminar el banco? Esta acción es <strong>permanente</strong>.<br />
          <small className="text-muted">Si está referenciado en perfiles, la operación será rechazada.</small></>
      }
      useList={useAdminBancosList}
      crearMut={useCrearAdminBanco()}
      actualizar={(tid, payload) => actualizarMut.mutateAsync({ tid, payload })}
      actualizarPending={actualizarMut.isPending}
      eliminarMut={useEliminarAdminBanco()}
    />
  );
}
