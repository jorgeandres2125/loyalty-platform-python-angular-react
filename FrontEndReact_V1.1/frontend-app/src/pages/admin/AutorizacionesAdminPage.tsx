import { useState } from 'react';
import { Tab, Tabs } from 'react-bootstrap';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { PermisosModulosTab } from './autorizaciones/PermisosModulosTab';
import { UsuariosRolesTab } from './autorizaciones/UsuariosRolesTab';

export function AutorizacionesAdminPage() {
  const [tab, setTab] = useState<string>('permisos');

  return (
    <div>
      <PageHeader
        title="Autorizaciones de usuarios"
        subtitle="Parametriza los permisos de cada rol sobre los módulos y la asignación de roles a los usuarios."
        icon="bi-shield-lock-fill"
        backTo="/admin/dashboard"
      />

      <Tabs
        activeKey={tab}
        onSelect={(k) => setTab(k ?? 'permisos')}
        className="mb-3"
        mountOnEnter
      >
        <Tab eventKey="permisos" title="Permisos sobre módulos">
          <PermisosModulosTab />
        </Tab>
        <Tab eventKey="usuarios-roles" title="Usuarios & Roles">
          <UsuariosRolesTab />
        </Tab>
      </Tabs>
    </div>
  );
}