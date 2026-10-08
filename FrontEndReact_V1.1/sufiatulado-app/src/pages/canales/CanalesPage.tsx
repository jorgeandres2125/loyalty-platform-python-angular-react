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
import { TomSelectMultiField } from '../../shared/ui/components/TomSelectMultiField';
import type { TomSelectOption } from '../../shared/ui/components/TomSelectMultiField';
import { EstadoSwitch } from '../../shared/ui/components/EstadoSwitch';
import {
  useActualizarCanal,
  useCanal,
  useCanales,
  useCrearCanal,
} from '../../features/canales/model/useCanales';
import type {
  CanalFormPayload,
  CanalListItem,
} from '../../features/canales/model/types';
import { useOficinasActivas } from '../../features/oficinas/model/useOficinas';
import type { OficinaActivaItem } from '../../features/oficinas/model/types';
import {
  useProgramas,
  useSubprogramas,
} from '../../features/programas/model/useProgramas';
import type {
  ProgramaItem,
  SubprogramaItem,
} from '../../features/programas/model/types';

type Tab = 'lista' | 'registro';

const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

const ESTADO_OPTIONS: ReadonlyArray<{ value: string; label: string }> = [
  { value: '', label: 'Todos' },
  { value: 'true', label: 'Activos' },
  { value: 'false', label: 'Inactivos' },
];

const PROGRAMA_BADGE_BG: Record<number, string> = {
  1: 'primary',
  2: 'success',
};

const CPID_MOVILIDAD: number = 1;

interface FormState {
  nom_canales: string;
  cpid: string;
  cspid: string;
  ind_activo: boolean;
  id_canales: string;
  oficinas_ids: string[];
}

const initForm: FormState = {
  nom_canales: '',
  cpid: '',
  cspid: '',
  ind_activo: true,
  id_canales: '0',
  oficinas_ids: [],
};

export function CanalesPage() {
  const [tab, setTab] = useState<Tab>('lista');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchNombre, setSearchNombre] = useState<string>('');
  const [searchEstado, setSearchEstado] = useState<string>('');
  const [filtroNombre, setFiltroNombre] = useState<string>('');
  const [filtroEstado, setFiltroEstado] = useState<string>('');

  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(initForm);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  const indActivoFiltro: boolean | undefined =
    filtroEstado === '' ? undefined : filtroEstado === 'true';

  const lista = useCanales({
    page,
    page_size: pageSize,
    nombre: filtroNombre || undefined,
    ind_activo: indActivoFiltro,
  });
  const programasQ = useProgramas();
  const subprogramasQ = useSubprogramas();
  const oficinasActivasQ = useOficinasActivas();
  const canalEditQ = useCanal(editId);
  const programas: ProgramaItem[] = programasQ.data ?? [];
  const subprogramas: SubprogramaItem[] = subprogramasQ.data ?? [];
  const oficinasActivas: OficinaActivaItem[] = oficinasActivasQ.data ?? [];
  const crearMut = useCrearCanal();
  const actualizarMut = useActualizarCanal();

  // Cuando se está editando y llega el detalle del canal, sincroniza oficinas_ids
  useEffect(() => {
    if (!editId) return;
    const data = canalEditQ.data;
    if (!data || data.cod_canales !== editId) return;
    setForm((prev) => ({
      ...prev,
      oficinas_ids: data.oficinas_ids.map((id) => String(id)),
    }));
  }, [editId, canalEditQ.data]);

  const filtrosActivos: boolean = !!filtroNombre || filtroEstado !== '';
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
    setFiltroNombre(searchNombre.trim());
    setFiltroEstado(searchEstado);
    setPage(1);
  };

  const handleLimpiar = () => {
    setSearchNombre('');
    setSearchEstado('');
    setFiltroNombre('');
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

  const handleEditar = (item: CanalListItem) => {
    setEditId(item.cod_canales);
    setForm({
      nom_canales: item.nom_canales,
      cpid: item.cpid === null ? '' : String(item.cpid),
      cspid: item.cspid === null ? '' : String(item.cspid),
      ind_activo: item.ind_activo,
      id_canales: String(item.id_canales ?? 0),
      oficinas_ids: [],
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

    if (!form.nom_canales.trim()) {
      setError('El nombre del canal es obligatorio');
      return;
    }

    const payload: CanalFormPayload = {
      nom_canales: form.nom_canales.trim(),
      cpid: form.cpid.trim() === '' ? null : parseInt(form.cpid, 10),
      cspid: form.cspid.trim() === '' ? null : parseInt(form.cspid, 10),
      ind_activo: form.ind_activo,
      oficinas_ids: form.oficinas_ids
        .map((strId) => parseInt(strId, 10))
        .filter((num) => Number.isFinite(num)),
    };

    try {
      if (isEditing && editId !== null) {
        await actualizarMut.mutateAsync({ codCanales: editId, payload });
        setSuccess('Canal actualizado correctamente');
      } else {
        await crearMut.mutateAsync(payload);
        setSuccess('Canal creado correctamente');
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
        title="Canales"
        subtitle={lista.data ? `${lista.data.total} canales${filtrosActivos ? ' encontrados' : ''}` : undefined}
        icon="bi-diagram-3"
      />

      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-bottom-0 pb-0">
          <Nav variant="tabs" activeKey={tab} onSelect={(tabKey) => tabKey && setTab(tabKey as Tab)}>
            <Nav.Item>
              <Nav.Link eventKey="lista">
                <i className="bi bi-list-ul me-2" />Lista de Canales
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="registro">
                <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-plus-circle'} me-2`} />
                {isEditing ? 'Editar Canal' : 'Nuevo Canal'}
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>
        <Card.Body className={tab === 'lista' ? 'p-0' : 'p-4'}>
          {tab === 'lista' && (
            <ListaCanales
              lista={lista}
              programas={programas}
              subprogramas={subprogramas}
              page={page}
              pageSize={pageSize}
              totalPages={totalPages}
              searchNombre={searchNombre}
              searchEstado={searchEstado}
              filtrosActivos={filtrosActivos}
              successMessage={success}
              onPageChange={setPage}
              onPageSizeChange={(n) => { setPageSize(n); setPage(1); }}
              onSearchNombreChange={setSearchNombre}
              onSearchEstadoChange={setSearchEstado}
              onBuscar={handleBuscar}
              onLimpiar={handleLimpiar}
              onEditar={handleEditar}
              onNuevo={handleNuevo}
              onDismissSuccess={() => setSuccess('')}
            />
          )}
          {tab === 'registro' && (
            <FormularioCanal
              form={form}
              setForm={setForm}
              programas={programas}
              subprogramas={subprogramas}
              oficinasActivas={oficinasActivas}
              oficinasCargando={oficinasActivasQ.isLoading}
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
  lista: ReturnType<typeof useCanales>;
  programas: ProgramaItem[];
  subprogramas: SubprogramaItem[];
  page: number;
  pageSize: number;
  totalPages: number;
  searchNombre: string;
  searchEstado: string;
  filtrosActivos: boolean;
  successMessage: string;
  onPageChange: (p: number) => void;
  onPageSizeChange: (n: number) => void;
  onSearchNombreChange: (v: string) => void;
  onSearchEstadoChange: (v: string) => void;
  onBuscar: () => void;
  onLimpiar: () => void;
  onEditar: (item: CanalListItem) => void;
  onNuevo: () => void;
  onDismissSuccess: () => void;
}

function ListaCanales({
  lista, programas, subprogramas, page, pageSize, totalPages,
  searchNombre, searchEstado, filtrosActivos, successMessage,
  onPageChange, onPageSizeChange,
  onSearchNombreChange, onSearchEstadoChange,
  onBuscar, onLimpiar, onEditar, onNuevo, onDismissSuccess,
}: ListaProps) {
  const programaPorCpid: Map<number, string> = new Map(
    programas.map((programa) => [programa.cpid, programa.cp_nombre]),
  );
  const subprogramaPorCspid: Map<number, string> = new Map(
    subprogramas.map((subprograma) => [subprograma.cspid, subprograma.cspid_nombre]),
  );

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
          <Form.Group style={{ minWidth: 220 }}>
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
          <Form.Group style={{ minWidth: 140 }}>
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
            <i className="bi bi-plus-lg me-1" />Nuevo Canal
          </Button>
        </div>
      </div>

      {lista.isLoading ? (
        <div className="text-center py-5"><Spinner animation="border" /></div>
      ) : lista.isError ? (
        <Alert variant="danger" className="m-3">Error al cargar canales</Alert>
      ) : !lista.data || lista.data.items.length === 0 ? (
        <div className="text-center py-5 text-muted">
          <i className="bi bi-inbox display-4 d-block mb-2" />
          No se encontraron canales
        </div>
      ) : (
        <>
          <Table hover responsive className="mb-0 align-middle">
            <thead className="table-light">
              <tr>
                <th>Código</th>
                <th>Nombre</th>
                <th>Programa</th>
                <th>Subprograma</th>
                <th>Estado</th>
                <th className="text-end">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {lista.data.items.map((canal) => {
                const nombrePrograma = canal.cpid !== null ? programaPorCpid.get(canal.cpid) : undefined;
                const nombreSubprograma = canal.cspid !== null && canal.cspid > 0
                  ? subprogramaPorCspid.get(canal.cspid)
                  : undefined;
                return (
                  <tr key={canal.cod_canales}>
                    <td><code>{canal.cod_canales}</code></td>
                    <td className="fw-semibold">{canal.nom_canales}</td>
                    <td>
                      {canal.cpid !== null && nombrePrograma ? (
                        <Badge bg={PROGRAMA_BADGE_BG[canal.cpid] ?? 'secondary'}>
                          {nombrePrograma}
                        </Badge>
                      ) : (
                        <span className="text-muted">—</span>
                      )}
                    </td>
                    <td>
                      {canal.cpid === CPID_MOVILIDAD ? (
                        <span className="text-muted fst-italic">Sin subprograma</span>
                      ) : nombreSubprograma ? (
                        <span>{nombreSubprograma}</span>
                      ) : (
                        <span className="text-muted">—</span>
                      )}
                    </td>
                    <td>
                      <Badge bg={canal.ind_activo ? 'success' : 'secondary'}>
                        {canal.ind_activo ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </td>
                    <td className="text-end">
                      <Button size="sm" variant="outline-primary" onClick={() => onEditar(canal)}>
                        <i className="bi bi-pencil-square me-1" />Editar
                      </Button>
                    </td>
                  </tr>
                );
              })}
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

interface FormularioProps {
  form: FormState;
  setForm: React.Dispatch<React.SetStateAction<FormState>>;
  programas: ProgramaItem[];
  subprogramas: SubprogramaItem[];
  oficinasActivas: OficinaActivaItem[];
  oficinasCargando: boolean;
  isEditing: boolean;
  isSaving: boolean;
  error: string;
  success: string;
  onSubmit: (e: React.FormEvent) => void;
  onCancelar: () => void;
}

function FormularioCanal({
  form, setForm, programas, subprogramas, oficinasActivas, oficinasCargando,
  isEditing, isSaving, error, success, onSubmit, onCancelar,
}: FormularioProps) {
  const update = <K extends keyof FormState>(key: K, value: FormState[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleProgramaChange = (value: string) => {
    if (value === '') {
      setForm((prev) => ({ ...prev, cpid: '', cspid: '' }));
      return;
    }
    const cpidNum: number = parseInt(value, 10);
    if (cpidNum === CPID_MOVILIDAD) {
      // Movilidad (Vehículos) no tiene subprograma → cspid = 0
      setForm((prev) => ({ ...prev, cpid: value, cspid: '0' }));
    } else {
      setForm((prev) => ({ ...prev, cpid: value, cspid: '' }));
    }
  };

  const cpidNum: number | null = form.cpid === '' ? null : parseInt(form.cpid, 10);
  const subprogramasFiltrados: SubprogramaItem[] = cpidNum === null
    ? []
    : subprogramas.filter((subprograma) => subprograma.cpid === cpidNum);
  const subprogramaDisabled: boolean = cpidNum === null || cpidNum === CPID_MOVILIDAD;

  const oficinaOpts: TomSelectOption[] = oficinasActivas.map((oficina) => ({
    value: String(oficina.cod_oficinas),
    label: oficina.nom_oficinas,
  }));

  const handleOficinasChange = (values: string[]) => {
    setForm((prev) => ({ ...prev, oficinas_ids: values }));
  };

  return (
    <Form onSubmit={onSubmit}>
      {error && <Alert variant="danger"><i className="bi bi-exclamation-triangle me-2" />{error}</Alert>}
      {success && <Alert variant="success"><i className="bi bi-check-circle me-2" />{success}</Alert>}

      <div className="row g-3">
        <Form.Group className="col-12">
          <Form.Label>Nombre del canal <span className="text-danger">*</span></Form.Label>
          <Form.Control
            type="text"
            value={form.nom_canales}
            onChange={(e) => update('nom_canales', e.target.value)}
            placeholder="Ej. AUTOMONTANA"
            maxLength={120}
            required
          />
        </Form.Group>

        <Form.Group className="col-md-4">
          <Form.Label>Programa</Form.Label>
          <Form.Select
            value={form.cpid}
            onChange={(e) => handleProgramaChange(e.target.value)}
          >
            <option value="">— Sin programa —</option>
            {programas.map((programa) => (
              <option key={programa.cpid} value={programa.cpid}>{programa.cp_nombre}</option>
            ))}
          </Form.Select>
        </Form.Group>

        <Form.Group className="col-md-4">
          <Form.Label>Subprograma</Form.Label>
          <Form.Select
            value={form.cspid}
            onChange={(e) => update('cspid', e.target.value)}
            disabled={subprogramaDisabled}
          >
            {cpidNum === CPID_MOVILIDAD ? (
              <option value="0">Sin subprograma</option>
            ) : (
              <>
                <option value="">— Seleccionar —</option>
                {subprogramasFiltrados.map((subprograma) => (
                  <option key={subprograma.cspid} value={subprograma.cspid}>{subprograma.cspid_nombre}</option>
                ))}
              </>
            )}
          </Form.Select>
          <Form.Text className="text-muted">
            {cpidNum === CPID_MOVILIDAD
              ? 'Movilidad no usa subprograma.'
              : cpidNum === null
                ? 'Selecciona un programa primero.'
                : `${subprogramasFiltrados.length} subprogramas disponibles.`}
          </Form.Text>
        </Form.Group>

        <Form.Group className="col-md-4 d-flex align-items-end">
          <EstadoSwitch
            id="canal-estado"
            checked={form.ind_activo}
            onChange={(v) => update('ind_activo', v)}
          />
        </Form.Group>

        <Form.Group className="col-12">
          <Form.Label>
            Oficinas asociadas
            {oficinasCargando && <Spinner animation="border" size="sm" className="ms-2" />}
          </Form.Label>
          <TomSelectMultiField
            id="canal-oficinas"
            options={oficinaOpts}
            value={form.oficinas_ids}
            onChange={handleOficinasChange}
            placeholder="— Seleccionar una o varias oficinas —"
            disabled={oficinasCargando}
          />
          <Form.Text className="text-muted">
            {form.oficinas_ids.length === 0
              ? 'Un canal puede asociarse a varias oficinas.'
              : `${form.oficinas_ids.length} oficina${form.oficinas_ids.length === 1 ? '' : 's'} seleccionada${form.oficinas_ids.length === 1 ? '' : 's'}.`}
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
