import { CatalogoCrudPage } from '../../shared/ui/components/CatalogoCrudPage';
import type { FormValues } from '../../shared/ui/components/CatalogoCrudPage';
import {
  useActualizarAdminDepartamento,
  useAdminDepartamentosList,
  useCrearAdminDepartamento,
  useEliminarAdminDepartamento,
} from '../../features/admin-departamentos/model/useAdminDepartamentos';
import type {
  AdminDepartamentoFormPayload,
  AdminDepartamentoListItem,
} from '../../features/admin-departamentos/model/types';

export function DepartamentosAdminPage() {
  const actualizarMut = useActualizarAdminDepartamento();
  return (
    <CatalogoCrudPage<AdminDepartamentoListItem, AdminDepartamentoFormPayload>
      title="Administrar Departamentos"
      icon="bi-map-fill"
      singular="Departamento"
      backTo="/admin/catalogos"
      idOf={(i) => i.did}
      columns={[
        { header: 'Código', width: 100, cell: (i) => <code>{i.did}</code> },
        { header: 'Nombre', className: 'fw-semibold', cell: (i) => i.departamento },
        {
          header: 'Padre (pid)', width: 120,
          cell: (i) => (i.pid !== null ? <code className="small">{i.pid}</code> : <span className="text-muted small">—</span>),
        },
      ]}
      fields={[
        { key: 'departamento', label: 'Nombre', required: true, maxLength: 200, col: 8, placeholder: 'Ej: Antioquia' },
        { key: 'pid', label: 'Padre (pid)', maxLength: 10, col: 4, placeholder: 'Opcional' },
      ]}
      initForm={{ departamento: '', pid: '' }}
      itemToForm={(i) => ({ departamento: i.departamento, pid: i.pid !== null ? String(i.pid) : '' })}
      toPayload={(f: FormValues): AdminDepartamentoFormPayload => ({
        departamento: f.departamento.trim(),
        pid: f.pid.trim() === '' ? null : Number(f.pid),
      })}
      validate={(f) => (f.departamento.trim() ? null : 'El nombre del departamento es obligatorio')}
      deleteWarning={
        <>¿Confirma eliminar el departamento? Esta acción es <strong>permanente</strong>.<br />
          <small className="text-muted">Si tiene ciudades asociadas, la operación será rechazada.</small></>
      }
      useList={useAdminDepartamentosList}
      crearMut={useCrearAdminDepartamento()}
      actualizar={(did, payload) => actualizarMut.mutateAsync({ did, payload })}
      actualizarPending={actualizarMut.isPending}
      eliminarMut={useEliminarAdminDepartamento()}
    />
  );
}
