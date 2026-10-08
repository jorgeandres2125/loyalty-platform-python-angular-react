import { useEffect, useState } from 'react';
import {
  Alert,
  Button,
  Card,
  Form,
  Nav,
  Spinner,
  Table,
} from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { ConfirmModal } from '../../shared/ui/components/ConfirmModal';
import {
  useActualizarAdminAfp,
  useAdminAfpList,
  useCrearAdminAfp,
  useEliminarAdminAfp,
} from '../../features/admin-afp/model/useAdminAfp';
import type {
  AdminAfpFormPayload,
  AdminAfpListItem,
} from '../../features/admin-afp/model/types';

type Tab = 'lista' | 'registro';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

interface FormState {
  nombre: string;
  nit: string;
}

const initForm: FormState = { nombre: '', nit: '' };

export function AfpAdminPage() {
  const navigate = useNavigate();

  const [tab, setTab] = useState<Tab>('lista');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchNombre, setSearchNombre] = useState<string>('');
  const [filtroNombre, setFiltroNombre] = useState<string>('');

  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(initForm);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const lista = useAdminAfpList({
    page,
    page_size: pageSize,
    nombre: filtroNombre || undefined,
  });
  const crearMut = useCrearAdminAfp();
  const actualizarMut = useActualizarAdminAfp();
  const eliminarMut = useEliminarAdminAfp();

  const filtrosActivos: boolean = !!filtroNombre;
  const totalPages: number = lista.data ? Math.max(1, Math.ceil(lista.data.total / pageSize)) : 1;
  const isEditing: boolean = editId !== null;
  const isSaving: boolean = crearMut.isPending || actualizarMut.isPending;

  useEffect(() => {
    if (!success) return;
    const timeoutId = setTimeout(() => setSuccess(''), 3500);
    return () => clearTimeout(timeoutId);
  }, [success]);

  useEffect(() => {
    if (tab !== 'registro') setError('');
  }, [tab]);

  const handleBuscar = () => {
    setFiltroNombre(searchNombre.trim());
    setPage(1);
  };

  const handleLimpiar = () => {
    setSearchNombre('');
    setFiltroNombre('');
    setPage(1);
  };

  const handleNuevo = () => {
    setEditId(null);
    setForm(initForm);
    setError('');
    setTab('registro');
  };

  const handleEditar = (item: AdminAfpListItem) => {
    setEditId(item.tid);
    setForm({ nombre: item.nombre, nit: item.nit ?? '' });
    setError('');
    setTab('registro');
  };

  const handleCancelar = () => {
    setEditId(null);
    setForm(initForm);
    setError('');
    setTab('lista');
  };

  const handleGuardar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!form.nombre.trim()) {
      setError('El nombre de la AFP es obligatorio');
      return;
    }

    const payload: AdminAfpFormPayload = {
      nombre: form.nombre.trim(),
      nit: form.nit.trim() === '' ? null : form.nit.trim(),
    };

    try {
      if (isEditing && editId !== null) {
        await actualizarMut.mutateAsync({ tid: editId, payload });
        setSuccess('AFP actualizada correctamente');
      } else {
        await crearMut.mutateAsync(payload);
        setSuccess('AFP creada correctamente');
      }
      setEditId(null);
      setForm(initForm);
      setTab('lista');
    } catch (err) {
      setError(extractError(err, 'Error al guardar la AFP'));
    }
  };

  const handleConfirmDelete = async () => {
    if (confirmDeleteId === null) return;
    try {
      await eliminarMut.mutateAsync(confirmDeleteId);
      setSuccess('AFP eliminada correctamente');
      setConfirmDeleteId(null);
    } catch (err) {
      setError(extractError(err, 'Error al eliminar la AFP'));
      setConfirmDeleteId(null);
    }
  };

  return (
    <div>
      <PageHeader
        title="Administrar AFP"
        subtitle={
          lista.data
            ? `${lista.data.total} AFP${filtrosActivos ? ' encontradas' : ''}`
            : undefined
        }
        icon="bi-piggy-bank-fill"
      />

      <div className="mb-3">
        <Button
          size="sm"
          variant="outline-secondary"
          onClick={() => navigate('/admin/catalogos')}
        >
          <i className="bi bi-arrow-left me-1" />
          Volver
        </Button>
      </div>

      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-bottom-0 pb-0">
          <Nav
            variant="tabs"
            activeKey={tab}
            onSelect={(tabKey) => tabKey && setTab(tabKey as Tab)}
          >
            <Nav.Item>
              <Nav.Link eventKey="lista">
                <i className="bi bi-list-ul me-2" />
                Lista de AFP
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="registro">
                <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-plus-circle'} me-2`} />
                {isEditing ? 'Editar AFP' : 'Nueva AFP'}
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>
        <Card.Body className={tab === 'lista' ? 'p-0' : 'p-4'}>
          {tab === 'lista' && (
            <ListaAfp
              lista={lista}
              page={page}
              pageSize={pageSize}
              totalPages={totalPages}
              searchNombre={searchNombre}
              filtrosActivos={filtrosActivos}
              successMessage={success}
              onPageChange={setPage}
              onPageSizeChange={(n) => {
                setPageSize(n);
                setPage(1);
              }}
              onSearchNombreChange={setSearchNombre}
              onBuscar={handleBuscar}
              onLimpiar={handleLimpiar}
              onEditar={handleEditar}
              onEliminar={(tid) => setConfirmDeleteId(tid)}
              onNuevo={handleNuevo}
              onDismissSuccess={() => setSuccess('')}
            />
          )}
          {tab === 'registro' && (
            <FormularioAfp
              form={form}
              setForm={setForm}
              isEditing={isEditing}
              editId={editId}
              isSaving={isSaving}
              error={error}
              success={success}
              onSubmit={handleGuardar}
              onCancelar={handleCancelar}
            />
          )}
        </Card.Body>
      </Card>

      <ConfirmModal
        show={confirmDeleteId !== null}
        title="Eliminar AFP"
        message={
          <>
            ¿Confirma eliminar la AFP? Esta acción es <strong>permanente</strong>.
            <br />
            <small className="text-muted">
              Si la AFP está referenciada en perfiles tributarios, la operación
              será rechazada.
            </small>
          </>
        }
        confirmLabel="Eliminar"
        confirmIcon="bi-trash-fill"
        confirmVariant="danger"
        loading={eliminarMut.isPending}
        loadingLabel="Eliminando…"
        onConfirm={handleConfirmDelete}
        onHide={() => setConfirmDeleteId(null)}
      />
    </div>
  );
}

interface ListaProps {
  lista: ReturnType<typeof useAdminAfpList>;
  page: number;
  pageSize: number;
  totalPages: number;
  searchNombre: string;
  filtrosActivos: boolean;
  successMessage: string;
  onPageChange: (p: number) => void;
  onPageSizeChange: (n: number) => void;
  onSearchNombreChange: (v: string) => void;
  onBuscar: () => void;
  onLimpiar: () => void;
  onEditar: (item: AdminAfpListItem) => void;
  onEliminar: (tid: number) => void;
  onNuevo: () => void;
  onDismissSuccess: () => void;
}

function ListaAfp({
  lista,
  page,
  pageSize,
  totalPages,
  searchNombre,
  filtrosActivos,
  successMessage,
  onPageChange,
  onPageSizeChange,
  onSearchNombreChange,
  onBuscar,
  onLimpiar,
  onEditar,
  onEliminar,
  onNuevo,
  onDismissSuccess,
}: ListaProps) {
  return (
    <>
      {successMessage && (
        <div className="px-3 pt-3">
          <Alert variant="success" dismissible onClose={onDismissSuccess} className="mb-0">
            <i className="bi bi-check-circle me-2" />
            {successMessage}
          </Alert>
        </div>
      )}

      <div className="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
        <div className="d-flex align-items-end gap-2 flex-wrap">
          <Form.Group style={{ minWidth: 260 }}>
            <Form.Label className="small mb-1">Nombre</Form.Label>
            <Form.Control
              size="sm"
              type="text"
              placeholder="Filtrar por nombre..."
              value={searchNombre}
              onChange={(e) => onSearchNombreChange(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') onBuscar();
              }}
              maxLength={200}
            />
          </Form.Group>
          <Button size="sm" variant="primary" onClick={onBuscar}>
            <i className="bi bi-search me-1" />
            Buscar
          </Button>
          {filtrosActivos && (
            <Button size="sm" variant="outline-secondary" onClick={onLimpiar}>
              <i className="bi bi-x-circle me-1" />
              Limpiar
            </Button>
          )}
        </div>
        <div className="d-flex align-items-end gap-2">
          <Form.Group style={{ minWidth: 80 }}>
            <Form.Label className="small mb-1">Mostrar</Form.Label>
            <Form.Select
              size="sm"
              value={pageSize}
              onChange={(e) => onPageSizeChange(Number(e.target.value))}
            >
              {PAGE_SIZE_OPTIONS.map((size) => (
                <option key={size} value={size}>
                  {size}
                </option>
              ))}
            </Form.Select>
          </Form.Group>
          <Button size="sm" variant="success" onClick={onNuevo}>
            <i className="bi bi-plus-lg me-1" />
            Nueva AFP
          </Button>
        </div>
      </div>

      {lista.isLoading ? (
        <div className="text-center py-5">
          <Spinner animation="border" />
        </div>
      ) : lista.isError ? (
        <Alert variant="danger" className="m-3">
          Error al cargar las AFP
        </Alert>
      ) : !lista.data || lista.data.items.length === 0 ? (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-inbox display-4 d-block mb-2" />
          No se encontraron AFP
        </div>
      ) : (
        <>
          <Table hover responsive className="mb-0 align-middle">
            <thead className="table-light">
              <tr>
                <th style={{ width: 100 }}>Código</th>
                <th>Nombre</th>
                <th style={{ width: 200 }}>NIT</th>
                <th className="text-end" style={{ width: 180 }}>
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody>
              {lista.data.items.map((afp) => (
                <tr key={afp.tid}>
                  <td>
                    <code>{afp.tid}</code>
                  </td>
                  <td className="fw-semibold">{afp.nombre}</td>
                  <td>
                    {afp.nit ? (
                      <code className="small">{afp.nit}</code>
                    ) : (
                      <span className="text-muted small">—</span>
                    )}
                  </td>
                  <td className="text-end">
                    <Button
                      size="sm"
                      variant="outline-primary"
                      className="me-1"
                      onClick={() => onEditar(afp)}
                    >
                      <i className="bi bi-pencil-fill" />
                    </Button>
                    <Button
                      size="sm"
                      variant="outline-danger"
                      onClick={() => onEliminar(afp.tid)}
                    >
                      <i className="bi bi-trash-fill" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>

          <div className="d-flex align-items-center justify-content-between px-3 py-3 border-top">
            <div className="text-muted small">
              Página <strong>{page}</strong> de <strong>{totalPages}</strong>
              {' — '}
              {lista.data.total} resultados
            </div>
            <div className="d-flex gap-2">
              <Button
                size="sm"
                variant="outline-secondary"
                disabled={page <= 1}
                onClick={() => onPageChange(page - 1)}
              >
                <i className="bi bi-chevron-left me-1" />
                Anterior
              </Button>
              <Button
                size="sm"
                variant="outline-secondary"
                disabled={page >= totalPages}
                onClick={() => onPageChange(page + 1)}
              >
                Siguiente
                <i className="bi bi-chevron-right ms-1" />
              </Button>
            </div>
          </div>
        </>
      )}
    </>
  );
}

interface FormularioProps {
  form: FormState;
  setForm: (updater: FormState | ((prev: FormState) => FormState)) => void;
  isEditing: boolean;
  editId: number | null;
  isSaving: boolean;
  error: string;
  success: string;
  onSubmit: (e: React.FormEvent) => void;
  onCancelar: () => void;
}

function FormularioAfp({
  form,
  setForm,
  isEditing,
  editId,
  isSaving,
  error,
  success,
  onSubmit,
  onCancelar,
}: FormularioProps) {
  return (
    <Form onSubmit={onSubmit} noValidate>
      {success && (
        <Alert variant="success" className="mb-3">
          <i className="bi bi-check-circle me-2" />
          {success}
        </Alert>
      )}
      {error && (
        <Alert variant="danger" className="mb-3">
          <i className="bi bi-exclamation-triangle me-2" />
          {error}
        </Alert>
      )}

      {isEditing && editId !== null && (
        <div className="mb-3 text-muted small">
          Editando AFP con código <code>{editId}</code>
        </div>
      )}

      <div className="row g-3">
        <div className="col-md-8">
          <Form.Group>
            <Form.Label>
              Nombre <span className="text-danger">*</span>
            </Form.Label>
            <Form.Control
              type="text"
              maxLength={200}
              value={form.nombre}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, nombre: e.target.value }))
              }
              required
              autoFocus
              placeholder="Ej: PORVENIR PENSIONES"
            />
          </Form.Group>
        </div>
        <div className="col-md-4">
          <Form.Group>
            <Form.Label>NIT</Form.Label>
            <Form.Control
              type="text"
              maxLength={30}
              value={form.nit}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, nit: e.target.value }))
              }
              placeholder="Opcional"
            />
          </Form.Group>
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2 mt-4">
        <Button
          type="button"
          variant="outline-secondary"
          onClick={onCancelar}
          disabled={isSaving}
        >
          <i className="bi bi-x-circle me-1" />
          Cancelar
        </Button>
        <Button type="submit" variant="primary" disabled={isSaving}>
          {isSaving ? (
            <>
              <Spinner size="sm" className="me-1" />
              Guardando…
            </>
          ) : (
            <>
              <i className="bi bi-check-circle me-1" />
              {isEditing ? 'Actualizar' : 'Crear'}
            </>
          )}
        </Button>
      </div>
    </Form>
  );
}

function extractError(err: unknown, fallback: string): string {
  const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data
    ?.detail;
  if (Array.isArray(detail)) return detail.join('; ');
  if (typeof detail === 'string') return detail;
  if (err instanceof Error) return err.message;
  return fallback;
}
