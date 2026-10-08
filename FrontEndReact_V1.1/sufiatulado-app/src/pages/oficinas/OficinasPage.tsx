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
import { TomSelectField } from '../../shared/ui/components/TomSelectField';
import type { TomSelectOption } from '../../shared/ui/components/TomSelectField';
import { TomSelectMultiField } from '../../shared/ui/components/TomSelectMultiField';
import { EstadoSwitch } from '../../shared/ui/components/EstadoSwitch';
import {
  useActualizarOficina,
  useCrearOficina,
  useOficina,
  useOficinas,
} from '../../features/oficinas/model/useOficinas';
import type {
  OficinaFormPayload,
  OficinaListItem,
} from '../../features/oficinas/model/types';
import { useCanalesActivas } from '../../features/canales/model/useCanales';
import type { CanalActivaItem } from '../../features/canales/model/types';
import {
  useCiudades,
  useDepartamentos,
} from '../../features/ubicaciones/model/useUbicaciones';

type Tab = 'lista' | 'registro';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

const ESTADO_OPTIONS: ReadonlyArray<{ value: string; label: string }> = [
  { value: '', label: 'Todos' },
  { value: 'true', label: 'Activos' },
  { value: 'false', label: 'Inactivos' },
];

interface FormState {
  cod_oficinas: string;
  id_oficinas: string;
  nom_oficinas: string;
  marca: string;
  regional: string;
  did: string;    // departamentos.did — solo para filtrar ciudades
  cpid: string;   // ciudades.cid — se persiste en oficinas.cpid
  ind_activo: boolean;
  canales_ids: string[];
}

const initForm: FormState = {
  cod_oficinas: '',
  id_oficinas: '',
  nom_oficinas: '',
  marca: '',
  regional: '',
  did: '',
  cpid: '',
  ind_activo: true,
  canales_ids: [],
};

function hayFiltros(nombre: string, marca: string, regional: string, estado: string): boolean {
  return !!nombre || !!marca || !!regional || estado !== '';
}

function estadoFiltro(estado: string): boolean | undefined {
  if (estado === '') return undefined;
  return estado === 'true';
}

function subtituloOficinas(total: number | undefined, filtros: boolean): string | undefined {
  if (total === undefined) return undefined;
  return `${total} oficinas${filtros ? ' encontradas' : ''}`;
}

export function OficinasPage() {
  const [tab, setTab] = useState<Tab>('lista');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchNombre, setSearchNombre] = useState<string>('');
  const [searchMarca, setSearchMarca] = useState<string>('');
  const [searchRegional, setSearchRegional] = useState<string>('');
  const [searchEstado, setSearchEstado] = useState<string>('');
  const [filtroNombre, setFiltroNombre] = useState<string>('');
  const [filtroMarca, setFiltroMarca] = useState<string>('');
  const [filtroRegional, setFiltroRegional] = useState<string>('');
  const [filtroEstado, setFiltroEstado] = useState<string>('');

  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(initForm);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const indActivoFiltro: boolean | undefined = estadoFiltro(filtroEstado);

  const lista = useOficinas({
    page,
    page_size: pageSize,
    nombre: filtroNombre || undefined,
    marca: filtroMarca || undefined,
    regional: filtroRegional || undefined,
    ind_activo: indActivoFiltro,
  });

  const departamentosQ = useDepartamentos();
  const didNum: number | null = form.did ? parseInt(form.did, 10) : null;
  const ciudadesQ = useCiudades(didNum);
  const canalesActivasQ = useCanalesActivas();
  const oficinaEditQ = useOficina(editId);
  const departamentos = departamentosQ.data ?? [];
  const ciudades = ciudadesQ.data ?? [];
  const canalesActivas: CanalActivaItem[] = canalesActivasQ.data ?? [];

  const crearMut = useCrearOficina();
  const actualizarMut = useActualizarOficina();

  // Cuando se está editando y llega el detalle de la oficina, sincroniza canales_ids
  useEffect(() => {
    if (!editId) return;
    const data = oficinaEditQ.data;
    if (!data || data.cod_oficinas !== editId) return;
    setForm((prev) => ({
      ...prev,
      canales_ids: data.canales_ids.map((id) => String(id)),
    }));
  }, [editId, oficinaEditQ.data]);

  const filtrosActivos: boolean = hayFiltros(filtroNombre, filtroMarca, filtroRegional, filtroEstado);
  const totalPages: number = lista.data ? Math.max(1, Math.ceil(lista.data.total / pageSize)) : 1;
  const subtitle: string | undefined = subtituloOficinas(lista.data?.total, filtrosActivos);
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
    setFiltroNombre(searchNombre.trim());
    setFiltroMarca(searchMarca.trim());
    setFiltroRegional(searchRegional.trim());
    setFiltroEstado(searchEstado);
    setPage(1);
  };

  const handleLimpiar = () => {
    setSearchNombre('');
    setSearchMarca('');
    setSearchRegional('');
    setSearchEstado('');
    setFiltroNombre('');
    setFiltroMarca('');
    setFiltroRegional('');
    setFiltroEstado('');
    setPage(1);
  };

  const handleNuevo = () => {
    setEditId(null);
    setForm(initForm);
    setError('');
    setSuccess('');
    setTab('registro');
  };

  const handleEditar = (item: OficinaListItem) => {
    setEditId(item.cod_oficinas);
    setForm({
      cod_oficinas: String(item.cod_oficinas),
      id_oficinas: item.id_oficinas === null ? '' : String(item.id_oficinas),
      nom_oficinas: item.nom_oficinas,
      marca: item.marca,
      regional: item.regional,
      did: item.did !== null ? String(item.did) : '',
      cpid: item.cpid !== null ? String(item.cpid) : '',
      ind_activo: item.ind_activo,
      canales_ids: [],
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

    if (!form.nom_oficinas.trim()) {
      setError('El nombre de la oficina es obligatorio');
      return;
    }
    if (!form.cpid) {
      setError('La ciudad es obligatoria');
      return;
    }

    const payload: OficinaFormPayload = {
      nom_oficinas: form.nom_oficinas.trim(),
      marca: form.marca.trim(),
      regional: form.regional.trim(),
      cpid: parseInt(form.cpid, 10),
      ind_activo: form.ind_activo,
      canales_ids: form.canales_ids
        .map((strId) => parseInt(strId, 10))
        .filter((num) => Number.isFinite(num)),
    };

    try {
      if (isEditing && editId !== null) {
        await actualizarMut.mutateAsync({ codOficinas: editId, payload });
        setSuccess('Oficina actualizada correctamente');
      } else {
        await crearMut.mutateAsync(payload);
        setSuccess('Oficina creada correctamente');
      }
      setEditId(null);
      setForm(initForm);
      setTab('lista');
    } catch (err) {
      const detail = (err as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail;
      const msg: string = Array.isArray(detail)
        ? detail.join('; ')
        : typeof detail === 'string'
          ? detail
          : err instanceof Error
            ? err.message
            : 'Error al guardar';
      setError(msg);
    }
  };

  return (
    <div>
      <PageHeader
        title="Oficinas"
        subtitle={subtitle}
        icon="bi-building"
      />

      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-bottom-0 pb-0">
          <Nav variant="tabs" activeKey={tab} onSelect={(tabKey) => tabKey && setTab(tabKey as Tab)}>
            <Nav.Item>
              <Nav.Link eventKey="lista">
                <i className="bi bi-list-ul me-2" />Lista de Oficinas
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="registro">
                <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-plus-circle'} me-2`} />
                {isEditing ? 'Editar Oficina' : 'Nueva Oficina'}
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>
        <Card.Body className={tab === 'lista' ? 'p-0' : 'p-4'}>
          {tab === 'lista' && (
            <ListaOficinas
              lista={lista}
              page={page}
              pageSize={pageSize}
              totalPages={totalPages}
              searchNombre={searchNombre}
              searchMarca={searchMarca}
              searchRegional={searchRegional}
              searchEstado={searchEstado}
              filtrosActivos={filtrosActivos}
              successMessage={success}
              onPageChange={setPage}
              onPageSizeChange={(newSize) => { setPageSize(newSize); setPage(1); }}
              onSearchNombreChange={setSearchNombre}
              onSearchMarcaChange={setSearchMarca}
              onSearchRegionalChange={setSearchRegional}
              onSearchEstadoChange={setSearchEstado}
              onBuscar={handleBuscar}
              onLimpiar={handleLimpiar}
              onEditar={handleEditar}
              onNuevo={handleNuevo}
              onDismissSuccess={() => setSuccess('')}
            />
          )}
          {tab === 'registro' && (
            <FormularioOficina
              form={form}
              setForm={setForm}
              departamentos={departamentos}
              ciudades={ciudades}
              ciudadesCargando={ciudadesQ.isFetching}
              canalesActivas={canalesActivas}
              canalesCargando={canalesActivasQ.isLoading}
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

// ─── Lista ────────────────────────────────────────────────────────────────────

interface ListaProps {
  lista: ReturnType<typeof useOficinas>;
  page: number;
  pageSize: number;
  totalPages: number;
  searchNombre: string;
  searchMarca: string;
  searchRegional: string;
  searchEstado: string;
  filtrosActivos: boolean;
  successMessage: string;
  onPageChange: (p: number) => void;
  onPageSizeChange: (n: number) => void;
  onSearchNombreChange: (v: string) => void;
  onSearchMarcaChange: (v: string) => void;
  onSearchRegionalChange: (v: string) => void;
  onSearchEstadoChange: (v: string) => void;
  onBuscar: () => void;
  onLimpiar: () => void;
  onEditar: (item: OficinaListItem) => void;
  onNuevo: () => void;
  onDismissSuccess: () => void;
}

function ListaOficinas({
  lista, page, pageSize, totalPages,
  searchNombre, searchMarca, searchRegional, searchEstado, filtrosActivos, successMessage,
  onPageChange, onPageSizeChange,
  onSearchNombreChange, onSearchMarcaChange, onSearchRegionalChange, onSearchEstadoChange,
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
      <div className="d-flex align-items-end justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
        <div className="d-flex align-items-end gap-2 flex-wrap">
          <Form.Group style={{ minWidth: 180 }}>
            <Form.Label className="small mb-1">Nombre</Form.Label>
            <Form.Control
              size="sm"
              type="text"
              placeholder="Filtrar por nombre..."
              value={searchNombre}
              onChange={(e) => onSearchNombreChange(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') onBuscar(); }}
              maxLength={120}
            />
          </Form.Group>
          <Form.Group style={{ minWidth: 130 }}>
            <Form.Label className="small mb-1">Marca</Form.Label>
            <Form.Control
              size="sm"
              type="text"
              placeholder="Marca..."
              value={searchMarca}
              onChange={(e) => onSearchMarcaChange(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') onBuscar(); }}
              maxLength={45}
            />
          </Form.Group>
          <Form.Group style={{ minWidth: 130 }}>
            <Form.Label className="small mb-1">Regional</Form.Label>
            <Form.Control
              size="sm"
              type="text"
              placeholder="Regional..."
              value={searchRegional}
              onChange={(e) => onSearchRegionalChange(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') onBuscar(); }}
              maxLength={45}
            />
          </Form.Group>
          <Form.Group style={{ minWidth: 130 }}>
            <Form.Label className="small mb-1">Estado</Form.Label>
            <Form.Select size="sm" value={searchEstado} onChange={(e) => onSearchEstadoChange(e.target.value)}>
              {ESTADO_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </Form.Select>
          </Form.Group>
          <Button size="sm" variant="primary" onClick={onBuscar}>
            <i className="bi bi-search me-1" />Buscar
          </Button>
          {filtrosActivos && (
            <Button size="sm" variant="outline-secondary" onClick={onLimpiar}>
              <i className="bi bi-x-circle me-1" />Limpiar
            </Button>
          )}
        </div>
        <div className="d-flex align-items-end gap-2">
          <Form.Group style={{ minWidth: 80 }}>
            <Form.Label className="small mb-1">Mostrar</Form.Label>
            <Form.Select size="sm" value={pageSize} onChange={(e) => onPageSizeChange(Number(e.target.value))}>
              {PAGE_SIZE_OPTIONS.map((size) => <option key={size} value={size}>{size}</option>)}
            </Form.Select>
          </Form.Group>
          <Button size="sm" variant="success" onClick={onNuevo}>
            <i className="bi bi-plus-lg me-1" />Nueva Oficina
          </Button>
        </div>
      </div>

      {lista.isLoading ? (
        <div className="text-center py-5"><Spinner animation="border" /></div>
      ) : lista.isError ? (
        <Alert variant="danger" className="m-3">Error al cargar oficinas</Alert>
      ) : !lista.data || lista.data.items.length === 0 ? (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-inbox display-4 d-block mb-2" />
          No se encontraron oficinas
        </div>
      ) : (
        <>
          <Table hover responsive className="mb-0 align-middle">
            <thead className="table-light">
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Marca</th>
                <th>Regional</th>
                <th>Ciudad</th>
                <th>Departamento</th>
                <th>Estado</th>
                <th className="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {lista.data.items.map((oficina) => (
                <tr key={oficina.cod_oficinas}>
                  <td><code>{oficina.cod_oficinas}</code></td>
                  <td className="fw-semibold">{oficina.nom_oficinas}</td>
                  <td>{oficina.marca || <span className="text-muted">—</span>}</td>
                  <td>{oficina.regional || <span className="text-muted">—</span>}</td>
                  <td>{oficina.ciudad_nombre || <span className="text-muted">—</span>}</td>
                  <td>{oficina.departamento_nombre || <span className="text-muted">—</span>}</td>
                  <td>
                    <Badge bg={oficina.ind_activo ? 'success' : 'secondary'}>
                      {oficina.ind_activo ? 'Activa' : 'Inactiva'}
                    </Badge>
                  </td>
                  <td className="text-end">
                    <Button size="sm" variant="outline-primary" onClick={() => onEditar(oficina)}>
                      <i className="bi bi-pencil-square me-1" />Editar
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
          <div className="d-flex align-items-center justify-content-between px-3 py-2 border-top">
            <small className="text-muted">
              Página {page} de {totalPages} · {lista.data.total} registros
            </small>
            <div className="d-flex gap-1">
              <Button size="sm" variant="outline-secondary" disabled={page <= 1} onClick={() => onPageChange(1)}>
                <i className="bi bi-chevron-double-left" />
              </Button>
              <Button size="sm" variant="outline-secondary" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
                <i className="bi bi-chevron-left" />
              </Button>
              <Button size="sm" variant="outline-secondary" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
                <i className="bi bi-chevron-right" />
              </Button>
              <Button size="sm" variant="outline-secondary" disabled={page >= totalPages} onClick={() => onPageChange(totalPages)}>
                <i className="bi bi-chevron-double-right" />
              </Button>
            </div>
          </div>
        </>
      )}
    </>
  );
}

// ─── Formulario ───────────────────────────────────────────────────────────────

interface FormularioProps {
  form: FormState;
  setForm: React.Dispatch<React.SetStateAction<FormState>>;
  departamentos: { did: number; departamento: string }[];
  ciudades: { cid: number; ciudad: string }[];
  ciudadesCargando: boolean;
  canalesActivas: CanalActivaItem[];
  canalesCargando: boolean;
  isEditing: boolean;
  isSaving: boolean;
  error: string;
  success: string;
  onSubmit: (e: React.FormEvent) => void;
  onCancelar: () => void;
}

function FormularioOficina({
  form, setForm, departamentos, ciudades, ciudadesCargando,
  canalesActivas, canalesCargando,
  isEditing, isSaving, error, success, onSubmit, onCancelar,
}: FormularioProps) {
  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleDepartamentoChange = (value: string) => {
    setForm((prev) => ({ ...prev, did: value, cpid: '' }));
  };

  const handleCanalesChange = (values: string[]) => {
    setForm((prev) => ({ ...prev, canales_ids: values }));
  };

  const depOpts: TomSelectOption[] = departamentos.map((dep) => ({
    value: String(dep.did),
    label: dep.departamento,
  }));

  const ciudadOpts: TomSelectOption[] = ciudades.map((ciudad) => ({
    value: String(ciudad.cid),
    label: ciudad.ciudad,
  }));

  const canalOpts: TomSelectOption[] = canalesActivas.map((canal) => ({
    value: String(canal.cod_canales),
    label: canal.nom_canales,
  }));

  return (
    <Form onSubmit={onSubmit}>
      {error && <Alert variant="danger"><i className="bi bi-exclamation-triangle me-2" />{error}</Alert>}
      {success && <Alert variant="success"><i className="bi bi-check-circle me-2" />{success}</Alert>}

      <div className="row g-3">
        {/* Identificadores del sistema — solo visibles en edición */}
        {isEditing && (
          <>
            <Form.Group className="col-md-4">
              <Form.Label className="text-muted small">Código de oficina</Form.Label>
              <Form.Control
                type="text"
                value={form.cod_oficinas}
                readOnly
                plaintext
                className="fw-semibold"
              />
            </Form.Group>
            <div className="col-md-8" />
          </>
        )}

        {/* Nombre + Marca + Regional */}
        <Form.Group className="col-md-4">
          <Form.Label>Nombre de la oficina <span className="text-danger">*</span></Form.Label>
          <Form.Control
            type="text"
            value={form.nom_oficinas}
            onChange={(e) => update('nom_oficinas', e.target.value)}
            placeholder="Ej. AUTOMONTANA - BOGOTA"
            maxLength={120}
            required
          />
        </Form.Group>

        <Form.Group className="col-md-4">
          <Form.Label>Marca</Form.Label>
          <Form.Control
            type="text"
            value={form.marca}
            onChange={(e) => update('marca', e.target.value)}
            placeholder="Ej. RENAULT, MAZDA, KIA..."
            maxLength={45}
          />
        </Form.Group>

        <Form.Group className="col-md-4">
          <Form.Label>Regional</Form.Label>
          <Form.Control
            type="text"
            value={form.regional}
            onChange={(e) => update('regional', e.target.value)}
            placeholder="Ej. BOGOTA, SUR, CARIBE..."
            maxLength={45}
          />
        </Form.Group>

        {/* Departamento */}
        <Form.Group className="col-md-4">
          <Form.Label>Departamento <span className="text-danger">*</span></Form.Label>
          <TomSelectField
            id="oficina-departamento"
            options={depOpts}
            value={form.did}
            onChange={handleDepartamentoChange}
            placeholder="— Seleccionar departamento —"
            required
          />
        </Form.Group>

        {/* Ciudad */}
        <Form.Group className="col-md-4">
          <Form.Label>
            Ciudad <span className="text-danger">*</span>
            {ciudadesCargando && <Spinner animation="border" size="sm" className="ms-2" />}
          </Form.Label>
          <TomSelectField
            key={`ciudad-${form.did}`}
            id="oficina-ciudad"
            options={ciudadOpts}
            value={form.cpid}
            onChange={(v) => update('cpid', v)}
            placeholder={form.did ? '— Seleccionar ciudad —' : '— Selecciona primero un departamento —'}
            disabled={!form.did || ciudadesCargando}
            required
          />
          {!form.did && (
            <Form.Text className="text-muted">Selecciona un departamento para ver las ciudades.</Form.Text>
          )}
        </Form.Group>

        {/* Estado */}
        <Form.Group className="col-md-4 d-flex align-items-end">
          <EstadoSwitch
            id="oficina-estado"
            checked={form.ind_activo}
            onChange={(v) => update('ind_activo', v)}
            labelActivo="Activa"
            labelInactivo="Inactiva"
          />
        </Form.Group>

        <Form.Group className="col-12">
          <Form.Label>
            Canales asociados
            {canalesCargando && <Spinner animation="border" size="sm" className="ms-2" />}
          </Form.Label>
          <TomSelectMultiField
            id="oficina-canales"
            options={canalOpts}
            value={form.canales_ids}
            onChange={handleCanalesChange}
            placeholder="— Seleccionar uno o varios canales —"
            disabled={canalesCargando}
          />
          <Form.Text className="text-muted">
            {form.canales_ids.length === 0
              ? 'Una oficina puede asociarse a varios canales.'
              : `${form.canales_ids.length} canal${form.canales_ids.length === 1 ? '' : 'es'} seleccionado${form.canales_ids.length === 1 ? '' : 's'}.`}
          </Form.Text>
        </Form.Group>
      </div>

      <div className="d-flex gap-2 mt-4 pt-3 border-top">
        <Button type="submit" variant="primary" disabled={isSaving}>
          {isSaving ? (
            <><Spinner as="span" animation="border" size="sm" className="me-2" />Guardando...</>
          ) : (
            <><i className="bi bi-check-lg me-1" />{isEditing ? 'Actualizar' : 'Crear'}</>
          )}
        </Button>
        <Button type="button" variant="outline-secondary" onClick={onCancelar} disabled={isSaving}>
          <i className="bi bi-x-lg me-1" />Cancelar
        </Button>
      </div>
    </Form>
  );
}
