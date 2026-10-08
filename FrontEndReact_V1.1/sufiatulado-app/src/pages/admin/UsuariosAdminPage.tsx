import { useEffect, useState } from 'react';
import { Alert, Badge, Button, Card, Form, Spinner, Table } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { ConfirmModal } from '../../shared/ui/components/ConfirmModal';
import { PasswordTemporalResultadoModal } from './PasswordTemporalResultadoModal';
import { extractError } from '../../shared/lib/extractError';
import {
  useAdminUsuariosList,
  useCambiarEstadoUsuario,
  useEmitirPasswordTemporal,
} from '../../features/admin-usuarios/model/useAdminUsuarios';
import type {
  PasswordTemporalResultado,
  UsuarioListItem,
} from '../../features/admin-usuarios/model/types';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

type FiltroEstado = 'todos' | 'activos' | 'inactivos';

const ESTADO_QUERY: Record<FiltroEstado, boolean | undefined> = {
  todos: undefined,
  activos: true,
  inactivos: false,
};

export function UsuariosAdminPage() {
  const navigate = useNavigate();

  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchTexto, setSearchTexto] = useState<string>('');
  const [filtroTexto, setFiltroTexto] = useState<string>('');
  const [filtroEstado, setFiltroEstado] = useState<FiltroEstado>('todos');

  const [objetivo, setObjetivo] = useState<UsuarioListItem | null>(null);
  const [temporalObjetivo, setTemporalObjetivo] = useState<UsuarioListItem | null>(null);
  const [temporalResultado, setTemporalResultado] =
    useState<PasswordTemporalResultado | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const lista = useAdminUsuariosList({
    page,
    page_size: pageSize,
    texto: filtroTexto || undefined,
    activo: ESTADO_QUERY[filtroEstado],
  });
  const cambiarEstadoMut = useCambiarEstadoUsuario();
  const emitirTemporalMut = useEmitirPasswordTemporal();

  const filtrosActivos: boolean = !!filtroTexto || filtroEstado !== 'todos';
  const totalPages: number = lista.data ? Math.max(1, Math.ceil(lista.data.total / pageSize)) : 1;
  const vaDeshabilitar: boolean = objetivo !== null && objetivo.activo;

  useEffect(() => {
    if (!success) return;
    const timeoutId = setTimeout(() => setSuccess(''), 3500);
    return () => clearTimeout(timeoutId);
  }, [success]);

  const handleBuscar = () => { setFiltroTexto(searchTexto.trim()); setPage(1); };

  const handleLimpiar = () => {
    setSearchTexto('');
    setFiltroTexto('');
    setFiltroEstado('todos');
    setPage(1);
  };

  const handleConfirm = async () => {
    if (objetivo === null) return;
    setError('');
    try {
      const resultado = await cambiarEstadoMut.mutateAsync({
        uid: objetivo.uid,
        payload: { activo: !objetivo.activo },
      });
      setSuccess(
        resultado.activo
          ? `Cuenta de ${resultado.nombre} habilitada`
          : `Cuenta de ${resultado.nombre} deshabilitada`,
      );
    } catch (err) {
      setError(extractError(err, 'No se pudo cambiar el estado de la cuenta'));
    } finally {
      setObjetivo(null);
    }
  };

  const handleEmitirTemporal = async () => {
    if (temporalObjetivo === null) return;
    setError('');
    try {
      const resultado = await emitirTemporalMut.mutateAsync({ uid: temporalObjetivo.uid });
      setTemporalResultado(resultado);
    } catch (err) {
      setError(extractError(err, 'No se pudo generar la contrasena temporal'));
    } finally {
      setTemporalObjetivo(null);
    }
  };

  const renderFila = (u: UsuarioListItem) => (
    <tr key={u.uid}>
      <td><code>{u.uid}</code></td>
      <td className="fw-semibold">{u.nombre}</td>
      <td className="small">{u.email || <span className="text-muted">—</span>}</td>
      <td>
        {u.roles.length > 0 ? (
          <span className="d-flex flex-wrap gap-1">
            {u.roles.map((rol) => (
              <Badge key={rol} bg="light" text="dark" className="border">{rol}</Badge>
            ))}
          </span>
        ) : (
          <span className="text-muted small">—</span>
        )}
      </td>
      <td>
        <Badge bg={u.activo ? 'success' : 'secondary'}>{u.activo ? 'Activo' : 'Inactivo'}</Badge>
      </td>
      <td className="text-end">
        <Button
          size="sm"
          variant="outline-primary"
          className="me-2"
          title="Generar contrasena temporal (AP-0047)"
          onClick={() => setTemporalObjetivo(u)}
        >
          <i className="bi bi-key me-1" />Temporal
        </Button>
        {u.activo ? (
          <Button size="sm" variant="outline-danger" onClick={() => setObjetivo(u)}>
            <i className="bi bi-person-fill-slash me-1" />Deshabilitar
          </Button>
        ) : (
          <Button size="sm" variant="outline-success" onClick={() => setObjetivo(u)}>
            <i className="bi bi-person-fill-check me-1" />Habilitar
          </Button>
        )}
      </td>
    </tr>
  );

  const renderTabla = () => {
    if (lista.isLoading) return <div className="text-center py-5"><Spinner animation="border" /></div>;
    if (lista.isError) return <Alert variant="danger" className="m-3">Error al cargar las cuentas</Alert>;
    if (!lista.data || lista.data.items.length === 0) {
      return (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-inbox display-4 d-block mb-2" />No se encontraron cuentas
        </div>
      );
    }
    return (
      <>
        <Table hover responsive className="mb-0 align-middle">
          <thead className="table-light">
            <tr>
              <th style={{ width: 90 }}>UID</th>
              <th>Usuario</th>
              <th>Correo</th>
              <th>Roles</th>
              <th style={{ width: 110 }}>Estado</th>
              <th className="text-end" style={{ width: 280 }}>Acciones</th>
            </tr>
          </thead>
          <tbody>{lista.data.items.map(renderFila)}</tbody>
        </Table>
        <div className="d-flex align-items-center justify-content-between px-3 py-3 border-top">
          <div className="text-muted small">
            Página <strong>{page}</strong> de <strong>{totalPages}</strong>{' — '}{lista.data.total} resultados
          </div>
          <div className="d-flex gap-2">
            <Button size="sm" variant="outline-secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
              <i className="bi bi-chevron-left me-1" />Anterior
            </Button>
            <Button size="sm" variant="outline-secondary" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
              Siguiente<i className="bi bi-chevron-right ms-1" />
            </Button>
          </div>
        </div>
      </>
    );
  };

  const mensajeTemporal = temporalObjetivo ? (
    <>
      Se generara una contrasena temporal para <strong>{temporalObjetivo.nombre}</strong>.
      <br />
      <small className="text-muted">
        Reemplaza cualquier temporal vigente, tiene vigencia limitada y el usuario
        debera definir su contrasena personal en el primer ingreso.
      </small>
    </>
  ) : (
    ''
  );

  const mensajeConfirm = objetivo ? (
    <>
      ¿Confirma {vaDeshabilitar ? 'deshabilitar' : 'habilitar'} la cuenta de <strong>{objetivo.nombre}</strong>?
      {vaDeshabilitar && (
        <><br /><small className="text-muted">El usuario no podrá iniciar sesión hasta que sea habilitado de nuevo.</small></>
      )}
    </>
  ) : '';

  return (
    <div>
      <PageHeader
        title="Gestión de Cuentas"
        subtitle={lista.data ? `${lista.data.total} cuenta${lista.data.total === 1 ? '' : 's'}${filtrosActivos ? ' encontradas' : ''}` : undefined}
        icon="bi-person-fill-gear"
      />

      <div className="mb-3">
        <Button size="sm" variant="outline-secondary" onClick={() => navigate('/admin/dashboard')}>
          <i className="bi bi-arrow-left me-1" />Volver
        </Button>
      </div>

      <Card className="border-0 shadow-sm">
        <Card.Body className="p-0">
          {success && (
            <div className="px-3 pt-3">
              <Alert variant="success" dismissible onClose={() => setSuccess('')} className="mb-0">
                <i className="bi bi-check-circle me-2" />{success}
              </Alert>
            </div>
          )}
          {error && (
            <div className="px-3 pt-3">
              <Alert variant="danger" dismissible onClose={() => setError('')} className="mb-0">
                <i className="bi bi-exclamation-triangle me-2" />{error}
              </Alert>
            </div>
          )}

          <div className="d-flex align-items-end justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
            <div className="d-flex align-items-end gap-2 flex-wrap">
              <Form.Group style={{ minWidth: 260 }}>
                <Form.Label className="small mb-1">Usuario o correo</Form.Label>
                <Form.Control
                  size="sm" type="text" placeholder="Filtrar por nombre o email..."
                  value={searchTexto}
                  onChange={(e) => setSearchTexto(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleBuscar(); }}
                  maxLength={200}
                />
              </Form.Group>
              <Form.Group style={{ minWidth: 140 }}>
                <Form.Label className="small mb-1">Estado</Form.Label>
                <Form.Select
                  size="sm" value={filtroEstado}
                  onChange={(e) => { setFiltroEstado(e.target.value as FiltroEstado); setPage(1); }}
                >
                  <option value="todos">Todos</option>
                  <option value="activos">Activos</option>
                  <option value="inactivos">Inactivos</option>
                </Form.Select>
              </Form.Group>
              <Button size="sm" variant="primary" onClick={handleBuscar}>
                <i className="bi bi-search me-1" />Buscar
              </Button>
              {filtrosActivos && (
                <Button size="sm" variant="outline-secondary" onClick={handleLimpiar}>
                  <i className="bi bi-x-circle me-1" />Limpiar
                </Button>
              )}
            </div>
            <Form.Group style={{ minWidth: 80 }}>
              <Form.Label className="small mb-1">Mostrar</Form.Label>
              <Form.Select size="sm" value={pageSize} onChange={(e) => { setPageSize(Number(e.target.value)); setPage(1); }}>
                {PAGE_SIZE_OPTIONS.map((size) => <option key={size} value={size}>{size}</option>)}
              </Form.Select>
            </Form.Group>
          </div>

          {renderTabla()}
        </Card.Body>
      </Card>

      <ConfirmModal
        show={objetivo !== null}
        title={vaDeshabilitar ? 'Deshabilitar cuenta' : 'Habilitar cuenta'}
        message={mensajeConfirm}
        confirmLabel={vaDeshabilitar ? 'Deshabilitar' : 'Habilitar'}
        confirmIcon={vaDeshabilitar ? 'bi-person-fill-slash' : 'bi-person-fill-check'}
        confirmVariant={vaDeshabilitar ? 'danger' : 'success'}
        loading={cambiarEstadoMut.isPending}
        loadingLabel="Guardando…"
        onConfirm={handleConfirm}
        onHide={() => setObjetivo(null)}
      />

      <ConfirmModal
        show={temporalObjetivo !== null}
        title="Generar contrasena temporal"
        message={mensajeTemporal}
        confirmLabel="Generar"
        confirmIcon="bi-key"
        confirmVariant="primary"
        loading={emitirTemporalMut.isPending}
        loadingLabel="Generando…"
        onConfirm={handleEmitirTemporal}
        onHide={() => setTemporalObjetivo(null)}
      />

      <PasswordTemporalResultadoModal
        resultado={temporalResultado}
        onCerrar={() => setTemporalResultado(null)}
      />
    </div>
  );
}
