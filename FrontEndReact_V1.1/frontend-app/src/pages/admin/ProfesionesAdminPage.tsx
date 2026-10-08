import { CatalogoCrudPage } from '../../shared/ui/components/CatalogoCrudPage';
import type { FormValues } from '../../shared/ui/components/CatalogoCrudPage';
import {
  useActualizarAdminProfesion,
  useAdminProfesionesList,
  useCrearAdminProfesion,
  useEliminarAdminProfesion,
} from '../../features/admin-profesiones/model/useAdminProfesiones';
import type {
  AdminProfesionFormPayload,
  AdminProfesionListItem,
} from '../../features/admin-profesiones/model/types';

export function ProfesionesAdminPage() {
  const actualizarMut = useActualizarAdminProfesion();
  return (
    <CatalogoCrudPage<AdminProfesionListItem, AdminProfesionFormPayload>
      title="Administrar Profesiones"
      icon="bi-briefcase-fill"
      singular="Profesión"
      backTo="/admin/catalogos"
      idOf={(i) => i.tid}
      columns={[
        { header: 'Código', width: 100, cell: (i) => <code>{i.tid}</code> },
        { header: 'Nombre', className: 'fw-semibold', cell: (i) => i.nombre },
      ]}
      fields={[
        { key: 'nombre', label: 'Nombre', required: true, maxLength: 200, col: 12, placeholder: 'Ej: Ingeniero' },
      ]}
      initForm={{ nombre: '' }}
      itemToForm={(i) => ({ nombre: i.nombre })}
      toPayload={(f: FormValues): AdminProfesionFormPayload => ({ nombre: f.nombre.trim() })}
      validate={(f) => (f.nombre.trim() ? null : 'El nombre de la profesión es obligatorio')}
      deleteWarning={
        <>¿Confirma eliminar la profesión? Esta acción es <strong>permanente</strong>.<br />
          <small className="text-muted">Si está referenciada en perfiles, la operación será rechazada.</small></>
      }
      useList={useAdminProfesionesList}
      crearMut={useCrearAdminProfesion()}
      actualizar={(tid, payload) => actualizarMut.mutateAsync({ tid, payload })}
      actualizarPending={actualizarMut.isPending}
      eliminarMut={useEliminarAdminProfesion()}
    />
  );
}
