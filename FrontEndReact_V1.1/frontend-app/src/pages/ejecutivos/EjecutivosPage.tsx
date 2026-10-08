import { useEffect, useState } from 'react';
import {
  Alert,
  Badge,
  Button,
  Card,
  Form,
  Nav,
  Spinner,
  Table,
} from 'react-bootstrap';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { EstadoSwitch } from '../../shared/ui/components/EstadoSwitch';
import {
  useActualizarEjecutivo,
  useCrearEjecutivo,
  useEjecutivos,
} from '../../features/ejecutivos/model/useEjecutivos';
import type {
  EjecutivoFormPayload,
  EjecutivoListItem,
} from '../../features/ejecutivos/model/types';

type Tab = 'lista' | 'registro';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

const TIPOS_DOCUMENTO: ReadonlyArray<{ value: string; label: string }> = [
  { value: 'CC', label: 'C.C.' },
  { value: 'CE', label: 'C.E.' },
  { value: 'F&I', label: 'F&I' },
  { value: 'GC', label: 'GC' },
  { value: 'PEP', label: 'PEP' },
  { value: 'PPT', label: 'PPT' },
  { value: 'VDA', label: 'VDA' },
];

const PERFILES: ReadonlyArray<{ value: string; label: string }> = [
  { value: '0', label: 'Ejecutivo Consumo' },
  { value: '1', label: 'Ejecutivo Vehiculo' },
  { value: '2', label: 'Ejecutivo Movilidad. Consumo y Servicios' },
];

const PERFIL_BADGE_BG: Record<string, string> = {
  '0': 'info',
  '1': 'primary',
  '2': 'dark',
};

interface FormState {
  tipo_documento: string;
  numero_documento: string;
  nombre_completo: string;
  codigo_ejecutivo: string;
  email: string;
  celular: string;
  perfil: string;
  estado: boolean;
}

const initForm: FormState = {
  tipo_documento: 'CC',
  numero_documento: '',
  nombre_completo: '',
  codigo_ejecutivo: '',
  email: '',
  celular: '',
  perfil: '0',
  estado: true,
};

export function EjecutivosPage() {
  const [tab, setTab] = useState<Tab>('lista');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchTipoDoc, setSearchTipoDoc] = useState<string>('');
  const [searchDocumento, setSearchDocumento] = useState<string>('');
  const [filtroTipoDoc, setFiltroTipoDoc] = useState<string>('');
  const [filtroDocumento, setFiltroDocumento] = useState<string>('');

  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(initForm);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const lista = useEjecutivos({
    page,
    page_size: pageSize,
    tipo_doc: filtroTipoDoc || undefined,
    documento: filtroDocumento || undefined,
  });
  const crearMut = useCrearEjecutivo();
  const actualizarMut = useActualizarEjecutivo();

  const filtrosActivos: boolean = !!filtroTipoDoc || !!filtroDocumento;
  const totalPages: number = lista.data ? Math.max(1, Math.ceil(lista.data.total / pageSize)) : 1;
  const isEditing: boolean = editId !== null;
  const isSaving: boolean = crearMut.isPending || actualizarMut.isPending;

  useEffect(() => {
    if (tab !== 'registro') {
      setError('');
    }
  }, [tab]);

  useEffect(() => {
    if (!success) return;
    const timeoutId = setTimeout(() => setSuccess(''), 3500);
    return () => clearTimeout(timeoutId);
  }, [success]);

  const handleBuscar = () => {
    setFiltroTipoDoc(searchTipoDoc);
    setFiltroDocumento(searchDocumento.trim());
    setPage(1);
  };

  const handleLimpiar = () => {
    setSearchTipoDoc('');
    setSearchDocumento('');
    setFiltroTipoDoc('');
    setFiltroDocumento('');
    setPage(1);
  };

  const handleNuevo = () => {
    setEditId(null);
    setForm(initForm);
    setError('');
    setSuccess('');
    setTab('registro');
  };

  const handleEditar = (item: EjecutivoListItem) => {
    setEditId(item.id);
    setForm({
      tipo_documento: item.tipo_documento || 'CC',
      numero_documento: item.numero_documento,
      nombre_completo: item.nombre_completo,
      codigo_ejecutivo: item.codigo_ejecutivo,
      email: item.email,
      celular: item.celular,
      perfil: item.perfil || '0',
      estado: item.estado,
    });
    setError('');
    setSuccess('');
    setTab('registro');
  };

  const handleCancelar = () => {
    setEditId(null);
    setForm(initForm);
    setError('');
    setSuccess('');
    setTab('lista');
  };

  const handleGuardar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!form.tipo_documento || !form.numero_documento.trim() || !form.nombre_completo.trim() ||
        !form.codigo_ejecutivo.trim() || !form.email.trim() || !form.perfil) {
      setError('Completa todos los campos obligatorios (marcados con *)');
      return;
    }

    const payload: EjecutivoFormPayload = {
      tipo_documento: form.tipo_documento,
      numero_documento: form.numero_documento.trim(),
      nombre_completo: form.nombre_completo.trim(),
      codigo_ejecutivo: form.codigo_ejecutivo.trim(),
      email: form.email.trim(),
      celular: form.celular.trim(),
      perfil: form.perfil,
      estado: form.estado,
    };

    try {
      if (isEditing && editId !== null) {
        await actualizarMut.mutateAsync({ id: editId, payload });
        setSuccess('Ejecutivo actualizado correctamente');
      } else {
        await crearMut.mutateAsync(payload);
        setSuccess('Ejecutivo creado correctamente');
      }
      setEditId(null);
      setForm(initForm);
      setTab('lista');
    } catch (err) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const msg: string = Array.isArray(detail) ? detail.join('; ') : typeof detail === 'string' ? detail : err instanceof Error ? err.message : 'Error al guardar';
      setError(msg);
    }
  };

  return (
    <div>
      <PageHeader
        title="Ejecutivos"
        subtitle={lista.data ? `${lista.data.total} ejecutivos${filtrosActivos ? ' encontrados' : ''}` : undefined}
        icon="bi-person-workspace"
      />

      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-bottom-0 pb-0">
          <Nav variant="tabs" activeKey={tab} onSelect={(tabKey) => tabKey && setTab(tabKey as Tab)}>
            <Nav.Item>
              <Nav.Link eventKey="lista">
                <i className="bi bi-list-ul me-2" />Lista de Ejecutivos
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="registro">
                <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-person-plus'} me-2`} />
                {isEditing ? 'Editar Ejecutivo' : 'Nuevo Ejecutivo'}
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>
        <Card.Body className={tab === 'lista' ? 'p-0' : 'p-4'}>
          {tab === 'lista' && (
            <ListaEjecutivos
              lista={lista}
              page={page}
              pageSize={pageSize}
              totalPages={totalPages}
              searchTipoDoc={searchTipoDoc}
              searchDocumento={searchDocumento}
              filtrosActivos={filtrosActivos}
              successMessage={success}
              onPageChange={setPage}
              onPageSizeChange={(newSize) => { setPageSize(newSize); setPage(1); }}
              onSearchTipoDocChange={setSearchTipoDoc}
              onSearchDocumentoChange={setSearchDocumento}
              onBuscar={handleBuscar}
              onLimpiar={handleLimpiar}
              onEditar={handleEditar}
              onNuevo={handleNuevo}
              onDismissSuccess={() => setSuccess('')}
            />
          )}
          {tab === 'registro' && (
            <FormularioEjecutivo
              form={form}
              setForm={setForm}
              isEditing={isEditing}
              isSaving={isSaving}
              error={error}
              success={success}
              onSubmit={handleGuardar}
              onCancelar={handleCancelar}
            />
          )}
        </Card.Body>
      </Card>
    </div>
  );
}

interface ListaProps {
  lista: ReturnType<typeof useEjecutivos>;
  page: number;
  pageSize: number;
  totalPages: number;
  searchTipoDoc: string;
  searchDocumento: string;
  filtrosActivos: boolean;
  successMessage: string;
  onPageChange: (p: number) => void;
  onPageSizeChange: (n: number) => void;
  onSearchTipoDocChange: (v: string) => void;
  onSearchDocumentoChange: (v: string) => void;
  onBuscar: () => void;
  onLimpiar: () => void;
  onEditar: (item: EjecutivoListItem) => void;
  onNuevo: () => void;
  onDismissSuccess: () => void;
}

function ListaEjecutivos({
  lista, page, pageSize, totalPages,
  searchTipoDoc, searchDocumento, filtrosActivos, successMessage,
  onPageChange, onPageSizeChange,
  onSearchTipoDocChange, onSearchDocumentoChange,
  onBuscar, onLimpiar, onEditar, onNuevo, onDismissSuccess,
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
        <small className="text-muted">
          {lista.data ? `${lista.data.total} ejecutivo${lista.data.total === 1 ? '' : 's'}${filtrosActivos ? ' encontrados' : ''}` : ''}
        </small>
        <div className="d-flex align-items-center gap-2">
          <Form.Select
            size="sm"
            style={{ width: 'auto' }}
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
          >
            {PAGE_SIZE_OPTIONS.map((size) => (
              <option key={size} value={size}>Ver {size} por página</option>
            ))}
          </Form.Select>
          <Button variant="danger" size="sm" onClick={onNuevo}>
            <i className="bi bi-person-plus me-1" />Nuevo Ejecutivo
          </Button>
        </div>
      </div>

      <div className="px-3 pb-3">
        <div className="d-flex align-items-end gap-2 flex-wrap p-3 rounded" style={{ background: '#f8f9fa', border: '1px solid #dee2e6' }}>
          <Form.Group style={{ minWidth: 160 }}>
            <Form.Label className="small mb-1 fw-semibold">Tipo de Documento</Form.Label>
            <Form.Select
              size="sm"
              value={searchTipoDoc}
              onChange={(e) => onSearchTipoDocChange(e.target.value)}
            >
              <option value="">Todos</option>
              {TIPOS_DOCUMENTO.map((tipoDoc) => (
                <option key={tipoDoc.value} value={tipoDoc.value}>{tipoDoc.label}</option>
              ))}
            </Form.Select>
          </Form.Group>
          <Form.Group style={{ minWidth: 180 }}>
            <Form.Label className="small mb-1 fw-semibold">Documento</Form.Label>
            <Form.Control
              size="sm"
              placeholder="Ej: 12345678"
              value={searchDocumento}
              onChange={(e) => onSearchDocumentoChange(e.target.value.replace(/\D/g, ''))}
              maxLength={20}
            />
          </Form.Group>
          <Button
            variant="danger"
            size="sm"
            disabled={!searchTipoDoc && !searchDocumento}
            onClick={onBuscar}
          >
            <i className="bi bi-search me-1" />Buscar
          </Button>
          <Button variant="outline-secondary" size="sm" onClick={onLimpiar}>
            <i className="bi bi-x-circle me-1" />Limpiar
          </Button>
        </div>
      </div>

      {lista.isLoading ? (
        <div className="text-center py-5"><Spinner animation="border" variant="danger" /></div>
      ) : lista.isError ? (
        <Alert variant="danger" className="mx-3">
          <i className="bi bi-exclamation-triangle me-2" />
          Error al cargar los ejecutivos.
        </Alert>
      ) : !lista.data || lista.data.items.length === 0 ? (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-inbox fs-1 d-block mb-2" />
          Sin ejecutivos registrados
        </div>
      ) : (
        <Table hover responsive className="mb-0">
          <thead className="table-light">
            <tr>
              <th>Tipo Doc.</th>
              <th>Número Documento</th>
              <th>Nombre y Apellidos</th>
              <th>Código Ejecutivo</th>
              <th>Correo Electrónico</th>
              <th>Celular</th>
              <th className="text-center">Estado</th>
              <th>Perfil</th>
              <th className="text-center">Operación</th>
            </tr>
          </thead>
          <tbody>
            {lista.data.items.map((item) => (
              <tr key={item.id}>
                <td>{item.tipo_documento || '—'}</td>
                <td className="font-monospace">{item.numero_documento}</td>
                <td>{item.nombre_completo || '—'}</td>
                <td className="font-monospace">{item.codigo_ejecutivo || '—'}</td>
                <td>{item.email || '—'}</td>
                <td className="font-monospace">{item.celular || '—'}</td>
                <td className="text-center">
                  <Badge bg={item.estado ? 'success' : 'secondary'}>
                    {item.estado ? 'Activo' : 'Inactivo'}
                  </Badge>
                </td>
                <td>
                  <Badge bg={PERFIL_BADGE_BG[item.perfil] ?? 'secondary'}>
                    {item.perfil_nombre || '—'}
                  </Badge>
                </td>
                <td className="text-center">
                  <Button variant="outline-primary" size="sm" onClick={() => onEditar(item)}>
                    <i className="bi bi-pencil me-1" />Editar
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {lista.data && totalPages > 1 && (
        <div className="d-flex justify-content-center align-items-center gap-2 py-3">
          <Button variant="outline-secondary" size="sm" disabled={page === 1} onClick={() => onPageChange(1)}>
            <i className="bi bi-chevron-double-left" />
          </Button>
          <Button variant="outline-secondary" size="sm" disabled={page === 1} onClick={() => onPageChange(page - 1)}>
            <i className="bi bi-chevron-left" />
          </Button>
          <span className="small">Página {page} de {totalPages}</span>
          <Button variant="outline-secondary" size="sm" disabled={page === totalPages} onClick={() => onPageChange(page + 1)}>
            <i className="bi bi-chevron-right" />
          </Button>
          <Button variant="outline-secondary" size="sm" disabled={page === totalPages} onClick={() => onPageChange(totalPages)}>
            <i className="bi bi-chevron-double-right" />
          </Button>
        </div>
      )}
    </>
  );
}

interface FormularioProps {
  form: FormState;
  setForm: (f: FormState) => void;
  isEditing: boolean;
  isSaving: boolean;
  error: string;
  success: string;
  onSubmit: (e: React.FormEvent) => void;
  onCancelar: () => void;
}

function FormularioEjecutivo({
  form, setForm, isEditing, isSaving, error, success, onSubmit, onCancelar,
}: FormularioProps) {
  return (
    <Form onSubmit={onSubmit}>
      <h6 className="fw-semibold mb-3">
        <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-person-plus'} me-2 text-danger`} />
        {isEditing ? 'Editar Ejecutivo' : 'Nuevo Ejecutivo'}
      </h6>

      {error && (
        <Alert variant="danger" dismissible onClose={() => { /* reset by parent */ }}>
          <i className="bi bi-exclamation-circle me-2" />
          {error}
        </Alert>
      )}
      {success && (
        <Alert variant="success">
          <i className="bi bi-check-circle me-2" />
          {success}
        </Alert>
      )}

      <div className="row g-3">
        <div className="col-md-4">
          <Form.Label className="small fw-semibold mb-1">
            Tipo de Documento <span className="text-danger">*</span>
          </Form.Label>
          <Form.Select
            value={form.tipo_documento}
            onChange={(e) => setForm({ ...form, tipo_documento: e.target.value })}
            required
          >
            {TIPOS_DOCUMENTO.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </Form.Select>
        </div>

        <div className="col-md-4">
          <Form.Label className="small fw-semibold mb-1">
            Número de Documento <span className="text-danger">*</span>
          </Form.Label>
          <Form.Control
            value={form.numero_documento}
            onChange={(e) => setForm({ ...form, numero_documento: e.target.value.replace(/\D/g, '') })}
            placeholder="Ej: 1037585639"
            maxLength={40}
            required
            disabled={isEditing}
            className="font-monospace"
          />
        </div>

        <div className="col-md-4">
          <Form.Label className="small fw-semibold mb-1">
            Código Ejecutivo <span className="text-danger">*</span>
          </Form.Label>
          <Form.Control
            value={form.codigo_ejecutivo}
            onChange={(e) => setForm({ ...form, codigo_ejecutivo: e.target.value })}
            placeholder="Ej: 12345"
            maxLength={200}
            required
            className="font-monospace"
          />
        </div>

        <div className="col-md-6">
          <Form.Label className="small fw-semibold mb-1">
            Nombre y Apellidos <span className="text-danger">*</span>
          </Form.Label>
          <Form.Control
            value={form.nombre_completo}
            onChange={(e) => setForm({ ...form, nombre_completo: e.target.value.toUpperCase() })}
            placeholder="Nombre completo"
            maxLength={200}
            required
          />
        </div>

        <div className="col-md-6">
          <Form.Label className="small fw-semibold mb-1">
            Correo Electrónico <span className="text-danger">*</span>
          </Form.Label>
          <Form.Control
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            placeholder="ejecutivo@sufi.com"
            maxLength={254}
            required
          />
        </div>

        <div className="col-md-4">
          <Form.Label className="small fw-semibold mb-1">Celular</Form.Label>
          <Form.Control
            value={form.celular}
            onChange={(e) => setForm({ ...form, celular: e.target.value.replace(/\D/g, '') })}
            placeholder="3001234567"
            maxLength={36}
            className="font-monospace"
          />
        </div>

        <div className="col-md-4">
          <Form.Label className="small fw-semibold mb-1">
            Perfil <span className="text-danger">*</span>
          </Form.Label>
          <Form.Select
            value={form.perfil}
            onChange={(e) => setForm({ ...form, perfil: e.target.value })}
            required
          >
            {PERFILES.map((perfil) => (
              <option key={perfil.value} value={perfil.value}>{perfil.label}</option>
            ))}
          </Form.Select>
        </div>

        <div className="col-md-4 d-flex align-items-end">
          <div>
            <EstadoSwitch
              id="ejecutivo-estado"
              checked={form.estado}
              onChange={(v) => setForm({ ...form, estado: v })}
            />
          </div>
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2 mt-4">
        <Button variant="outline-secondary" onClick={onCancelar} disabled={isSaving}>
          <i className="bi bi-x-circle me-1" />Cancelar
        </Button>
        <Button variant="danger" type="submit" disabled={isSaving}>
          {isSaving ? (
            <><Spinner animation="border" size="sm" className="me-1" />Guardando…</>
          ) : (
            <><i className="bi bi-check-circle me-1" />{isEditing ? 'Actualizar' : 'Crear'} Ejecutivo</>
          )}
        </Button>
      </div>
    </Form>
  );
}
