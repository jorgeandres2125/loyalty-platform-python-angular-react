import { useState } from 'react';
import { Alert, Badge, Button, Card, Table } from 'react-bootstrap';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { LoadingSpinner } from '../../shared/ui/components/LoadingSpinner';
import { EmptyState } from '../../shared/ui/components/EmptyState';
import { ConfirmModal } from '../../shared/ui/components/ConfirmModal';
import {
  useCerrarOtrasSesiones,
  useCerrarSesion,
  useMisSesiones,
} from '../../features/sesiones/model/useSesiones';
import type { SesionActiva } from '../../features/sesiones/model/types';

function formatoFecha(iso: string): string {
  try {
    return new Date(iso).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' });
  } catch {
    return iso;
  }
}

// AP-0130: pantalla de autoservicio -- el usuario ve e informa sus propias sesiones
// concurrentes y puede cerrar remotamente cualquiera que no reconozca.
export function SesionesActivasPage() {
  const { data: sesiones, isLoading, isError } = useMisSesiones();
  const cerrarSesion = useCerrarSesion();
  const cerrarOtras = useCerrarOtrasSesiones();
  const [sidAConfirmar, setSidAConfirmar] = useState<string | null>(null);
  const [confirmarCerrarOtras, setConfirmarCerrarOtras] = useState(false);

  const hayOtras = (sesiones?.length ?? 0) > 1;

  return (
    <div className="sesiones-activas-page">
      <PageHeader
        title="Mis sesiones"
        subtitle="Sesiones activas de tu cuenta en distintos equipos o navegadores"
        icon="bi-laptop"
        backTo="/configuraciones"
        actions={
          hayOtras ? (
            <Button
              variant="outline-danger"
              size="sm"
              onClick={() => setConfirmarCerrarOtras(true)}
            >
              <i className="bi bi-box-arrow-right me-1" />
              Cerrar las demas sesiones
            </Button>
          ) : undefined
        }
      />

      <Card className="shadow-sm" style={{ border: 'none' }}>
        <Card.Body className="p-0">
          {isLoading ? (
            <LoadingSpinner fullPage />
          ) : isError ? (
            <Alert variant="danger" className="m-3">
              No fue posible cargar tus sesiones activas. Intenta de nuevo.
            </Alert>
          ) : sesiones && sesiones.length > 0 ? (
            <Table hover className="mb-0 align-middle">
              <thead>
                <tr>
                  <th>Dispositivo / Navegador</th>
                  <th>IP</th>
                  <th>Inicio</th>
                  <th>Ultima actividad</th>
                  <th>Tipo</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {sesiones.map((sesion: SesionActiva) => (
                  <tr key={sesion.sid}>
                    <td>
                      <span className="text-truncate d-inline-block" style={{ maxWidth: 320 }}>
                        {sesion.user_agent || 'Desconocido'}
                      </span>
                      {sesion.es_actual && (
                        <Badge bg="success" className="ms-2">
                          Este dispositivo
                        </Badge>
                      )}
                    </td>
                    <td className="font-monospace">{sesion.ip}</td>
                    <td>{formatoFecha(sesion.inicio)}</td>
                    <td>{formatoFecha(sesion.last_activity)}</td>
                    <td>{sesion.canal ? 'Canal' : 'Otra aplicacion'}</td>
                    <td className="text-end">
                      {!sesion.es_actual && (
                        <Button
                          variant="outline-secondary"
                          size="sm"
                          onClick={() => setSidAConfirmar(sesion.sid)}
                        >
                          <i className="bi bi-x-lg me-1" />
                          Cerrar
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          ) : (
            <EmptyState icon="bi-laptop" title="No hay sesiones activas registradas" />
          )}
        </Card.Body>
      </Card>

      <ConfirmModal
        show={sidAConfirmar !== null}
        title="Cerrar sesion"
        message="Esa sesion se cerrara de inmediato en el otro equipo o navegador. Deseas continuar?"
        confirmLabel="Cerrar sesion"
        loading={cerrarSesion.isPending}
        onConfirm={async () => {
          if (sidAConfirmar) {
            await cerrarSesion.mutateAsync(sidAConfirmar);
          }
          setSidAConfirmar(null);
        }}
        onHide={() => setSidAConfirmar(null)}
      />

      <ConfirmModal
        show={confirmarCerrarOtras}
        title="Cerrar las demas sesiones"
        message="Se cerraran todas tus sesiones activas, excepto la de este dispositivo. Deseas continuar?"
        confirmLabel="Cerrar las demas"
        loading={cerrarOtras.isPending}
        onConfirm={async () => {
          await cerrarOtras.mutateAsync();
          setConfirmarCerrarOtras(false);
        }}
        onHide={() => setConfirmarCerrarOtras(false)}
      />
    </div>
  );
}