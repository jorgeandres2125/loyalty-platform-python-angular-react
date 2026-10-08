import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { Alert, Button, Card, Form, Nav, Spinner, Table } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { PageHeader } from './PageHeader';
import { ConfirmModal } from './ConfirmModal';
import { extractError } from '../../lib/extractError';

/**
 * Scaffold CRUD genérico para los catálogos admin de un solo recurso
 * (lista paginada con filtro por nombre + alta/edición + borrado confirmado).
 *
 * AP-0036: extrae el patrón repetido de las páginas admin a un único componente
 * con la lógica repartida en subcomponentes (CatalogoListaTab / CatalogoRegistroForm),
 * de modo que ninguna función supera complejidad ciclomática 20.
 */

export type FormValues = Record<string, string>;

export interface ColumnaCatalogo<TItem> {
  header: ReactNode;
  width?: number;
  className?: string;
  cell: (item: TItem) => ReactNode;
}

export interface CampoCatalogo {
  key: string;
  label: string;
  required?: boolean;
  maxLength?: number;
  col?: number; // ancho bootstrap (col-md-N); por defecto 6
  placeholder?: string;
}

interface MutacionLike<TArg> {
  mutateAsync: (arg: TArg) => Promise<unknown>;
  isPending: boolean;
}

interface ListaResultado<TItem> {
  data?: { items: TItem[]; total: number };
  isLoading: boolean;
  isError: boolean;
}

export interface CatalogoCrudProps<TItem, TPayload> {
  title: string;
  icon: string;
  singular: string; // p.ej. "ARL", "Banco"
  backTo?: string;
  idOf: (item: TItem) => number;
  columns: ColumnaCatalogo<TItem>[];
  fields: CampoCatalogo[];
  initForm: FormValues;
  itemToForm: (item: TItem) => FormValues;
  toPayload: (form: FormValues) => TPayload;
  validate: (form: FormValues) => string | null;
  deleteWarning?: ReactNode;
  useList: (q: { page: number; page_size: number; nombre?: string }) => ListaResultado<TItem>;
  crearMut: MutacionLike<TPayload>;
  actualizar: (id: number, payload: TPayload) => Promise<unknown>;
  actualizarPending: boolean;
  eliminarMut: MutacionLike<number>;
}

type Tab = 'lista' | 'registro';
const PAGE_SIZE_OPTIONS: ReadonlyArray<number> = [10, 20, 30];

export function CatalogoCrudPage<TItem, TPayload>(props: CatalogoCrudProps<TItem, TPayload>) {
  const navigate = useNavigate();
  const [tab, setTab] = useState<Tab>('lista');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(10);
  const [searchNombre, setSearchNombre] = useState<string>('');
  const [filtroNombre, setFiltroNombre] = useState<string>('');
  const [editId, setEditId] = useState<number | null>(null);
  const [form, setForm] = useState<FormValues>(props.initForm);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null);

  const lista = props.useList({ page, page_size: pageSize, nombre: filtroNombre || undefined });

  const filtrosActivos: boolean = !!filtroNombre;
  const totalPages: number = lista.data ? Math.max(1, Math.ceil(lista.data.total / pageSize)) : 1;
  const isEditing: boolean = editId !== null;
  const isSaving: boolean = props.crearMut.isPending || props.actualizarPending;

  useEffect(() => {
    if (!success) return;
    const t = setTimeout(() => setSuccess(''), 3500);
    return () => clearTimeout(t);
  }, [success]);

  useEffect(() => { if (tab !== 'registro') setError(''); }, [tab]);

  const handleEditar = (item: TItem) => {
    setEditId(props.idOf(item));
    setForm(props.itemToForm(item));
    setError('');
    setTab('registro');
  };

  const handleNuevo = () => {
    setEditId(null);
    setForm(props.initForm);
    setError('');
    setTab('registro');
  };

  const handleCancelar = () => {
    setEditId(null);
    setForm(props.initForm);
    setError('');
    setTab('lista');
  };

  const handleGuardar = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    const mensaje: string | null = props.validate(form);
    if (mensaje) { setError(mensaje); return; }
    const payload: TPayload = props.toPayload(form);
    try {
      if (isEditing && editId !== null) {
        await props.actualizar(editId, payload);
      } else {
        await props.crearMut.mutateAsync(payload);
      }
      handleCancelar();
      setSuccess(isEditing ? `${props.singular} actualizado correctamente` : `${props.singular} creado correctamente`);
    } catch (err) {
      setError(extractError(err, `Error al guardar (${props.singular})`));
    }
  };

  const handleConfirmDelete = async () => {
    if (confirmDeleteId === null) return;
    try {
      await props.eliminarMut.mutateAsync(confirmDeleteId);
      setSuccess(`${props.singular} eliminado correctamente`);
    } catch (err) {
      setError(extractError(err, `Error al eliminar (${props.singular})`));
    } finally {
      setConfirmDeleteId(null);
    }
  };

  return (
    <div>
      <PageHeader
        title={props.title}
        subtitle={lista.data ? `${lista.data.total} registro(s)${filtrosActivos ? ' encontrados' : ''}` : undefined}
        icon={props.icon}
      />

      {props.backTo && (
        <div className="mb-3">
          <Button size="sm" variant="outline-secondary" onClick={() => navigate(props.backTo as string)}>
            <i className="bi bi-arrow-left me-1" />Volver
          </Button>
        </div>
      )}

      <Card className="border-0 shadow-sm">
        <Card.Header className="bg-white border-bottom-0 pb-0">
          <Nav variant="tabs" activeKey={tab} onSelect={(k) => k && setTab(k as Tab)}>
            <Nav.Item><Nav.Link eventKey="lista"><i className="bi bi-list-ul me-2" />Lista</Nav.Link></Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="registro">
                <i className={`bi ${isEditing ? 'bi-pencil-square' : 'bi-plus-circle'} me-2`} />
                {isEditing ? `Editar ${props.singular}` : `Nuevo ${props.singular}`}
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>
        <Card.Body className={tab === 'lista' ? 'p-0' : 'p-4'}>
          {tab === 'lista' && (
            <CatalogoListaTab
              lista={lista}
              columns={props.columns}
              idOf={props.idOf}
              singular={props.singular}
              success={success}
              onCloseSuccess={() => setSuccess('')}
              searchNombre={searchNombre}
              setSearchNombre={setSearchNombre}
              filtrosActivos={filtrosActivos}
              onBuscar={() => { setFiltroNombre(searchNombre.trim()); setPage(1); }}
              onLimpiar={() => { setSearchNombre(''); setFiltroNombre(''); setPage(1); }}
              pageSize={pageSize}
              setPageSize={(n) => { setPageSize(n); setPage(1); }}
              page={page}
              totalPages={totalPages}
              setPage={setPage}
              onNuevo={handleNuevo}
              onEditar={handleEditar}
              onEliminar={setConfirmDeleteId}
            />
          )}
          {tab === 'registro' && (
            <CatalogoRegistroForm
              fields={props.fields}
              form={form}
              setForm={setForm}
              isEditing={isEditing}
              editId={editId}
              isSaving={isSaving}
              singular={props.singular}
              success={success}
              error={error}
              onSubmit={handleGuardar}
              onCancelar={handleCancelar}
            />
          )}
        </Card.Body>
      </Card>

      <ConfirmModal
        show={confirmDeleteId !== null}
        title={`Eliminar ${props.singular}`}
        message={props.deleteWarning ?? <>¿Confirma eliminar el registro? Esta acción es <strong>permanente</strong>.</>}
        confirmLabel="Eliminar"
        confirmIcon="bi-trash-fill"
        confirmVariant="danger"
        loading={props.eliminarMut.isPending}
        loadingLabel="Eliminando…"
        onConfirm={handleConfirmDelete}
        onHide={() => setConfirmDeleteId(null)}
      />
    </div>
  );
}

interface ListaTabProps<TItem> {
  lista: ListaResultado<TItem>;
  columns: ColumnaCatalogo<TItem>[];
  idOf: (item: TItem) => number;
  singular: string;
  success: string;
  onCloseSuccess: () => void;
  searchNombre: string;
  setSearchNombre: (v: string) => void;
  filtrosActivos: boolean;
  onBuscar: () => void;
  onLimpiar: () => void;
  pageSize: number;
  setPageSize: (n: number) => void;
  page: number;
  totalPages: number;
  setPage: (n: number) => void;
  onNuevo: () => void;
  onEditar: (item: TItem) => void;
  onEliminar: (id: number) => void;
}

function CatalogoListaTab<TItem>(p: ListaTabProps<TItem>) {
  const vacio: boolean = !p.lista.data || p.lista.data.items.length === 0;
  return (
    <>
      {p.success && (
        <div className="px-3 pt-3">
          <Alert variant="success" dismissible onClose={p.onCloseSuccess} className="mb-0">
            <i className="bi bi-check-circle me-2" />{p.success}
          </Alert>
        </div>
      )}
      <div className="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
        <div className="d-flex align-items-end gap-2 flex-wrap">
          <Form.Group style={{ minWidth: 260 }}>
            <Form.Label className="small mb-1">Nombre</Form.Label>
            <Form.Control
              size="sm" type="text" placeholder="Filtrar por nombre..."
              value={p.searchNombre}
              onChange={(e) => p.setSearchNombre(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') p.onBuscar(); }}
              maxLength={200}
            />
          </Form.Group>
          <Button size="sm" variant="primary" onClick={p.onBuscar}><i className="bi bi-search me-1" />Buscar</Button>
          {p.filtrosActivos && (
            <Button size="sm" variant="outline-secondary" onClick={p.onLimpiar}>
              <i className="bi bi-x-circle me-1" />Limpiar
            </Button>
          )}
        </div>
        <div className="d-flex align-items-end gap-2">
          <Form.Group style={{ minWidth: 80 }}>
            <Form.Label className="small mb-1">Mostrar</Form.Label>
            <Form.Select size="sm" value={p.pageSize} onChange={(e) => p.setPageSize(Number(e.target.value))}>
              {PAGE_SIZE_OPTIONS.map((n) => <option key={n} value={n}>{n}</option>)}
            </Form.Select>
          </Form.Group>
          <Button size="sm" variant="success" onClick={p.onNuevo}><i className="bi bi-plus-lg me-1" />Nuevo {p.singular}</Button>
        </div>
      </div>
      <CatalogoTabla {...p} vacio={vacio} />
    </>
  );
}

function CatalogoTabla<TItem>(p: ListaTabProps<TItem> & { vacio: boolean }) {
  if (p.lista.isLoading) return <div className="text-center py-5"><Spinner animation="border" /></div>;
  if (p.lista.isError) return <Alert variant="danger" className="m-3">Error al cargar los datos</Alert>;
  if (p.vacio || !p.lista.data) {
    return (
      <div className="text-center py-5 text-muted">
        <i className="bi bi-inbox display-4 d-block mb-2" />No se encontraron registros
      </div>
    );
  }
  return (
    <>
      <Table hover responsive className="mb-0 align-middle">
        <thead className="table-light">
          <tr>
            {p.columns.map((c, i) => (
              <th key={i} className={c.className} style={c.width ? { width: c.width } : undefined}>{c.header}</th>
            ))}
            <th className="text-end" style={{ width: 180 }}>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {p.lista.data.items.map((item) => (
            <tr key={p.idOf(item)}>
              {p.columns.map((c, i) => <td key={i} className={c.className}>{c.cell(item)}</td>)}
              <td className="text-end">
                <Button size="sm" variant="outline-primary" className="me-1" onClick={() => p.onEditar(item)}>
                  <i className="bi bi-pencil-fill" />
                </Button>
                <Button size="sm" variant="outline-danger" onClick={() => p.onEliminar(p.idOf(item))}>
                  <i className="bi bi-trash-fill" />
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
      <div className="d-flex align-items-center justify-content-between px-3 py-3 border-top">
        <div className="text-muted small">
          Página <strong>{p.page}</strong> de <strong>{p.totalPages}</strong> — {p.lista.data.total} resultados
        </div>
        <div className="d-flex gap-2">
          <Button size="sm" variant="outline-secondary" disabled={p.page <= 1} onClick={() => p.setPage(p.page - 1)}>
            <i className="bi bi-chevron-left me-1" />Anterior
          </Button>
          <Button size="sm" variant="outline-secondary" disabled={p.page >= p.totalPages} onClick={() => p.setPage(p.page + 1)}>
            Siguiente<i className="bi bi-chevron-right ms-1" />
          </Button>
        </div>
      </div>
    </>
  );
}

interface RegistroFormProps {
  fields: CampoCatalogo[];
  form: FormValues;
  setForm: React.Dispatch<React.SetStateAction<FormValues>>;
  isEditing: boolean;
  editId: number | null;
  isSaving: boolean;
  singular: string;
  success: string;
  error: string;
  onSubmit: (e: React.FormEvent) => void;
  onCancelar: () => void;
}

function CatalogoRegistroForm(p: RegistroFormProps) {
  return (
    <Form onSubmit={p.onSubmit} noValidate>
      {p.success && (<Alert variant="success" className="mb-3"><i className="bi bi-check-circle me-2" />{p.success}</Alert>)}
      {p.error && (<Alert variant="danger" className="mb-3"><i className="bi bi-exclamation-triangle me-2" />{p.error}</Alert>)}
      {p.isEditing && p.editId !== null && (
        <div className="mb-3 text-muted small">Editando registro con código <code>{p.editId}</code></div>
      )}
      <div className="row g-3">
        {p.fields.map((f, idx) => (
          <div className={`col-md-${f.col ?? 6}`} key={f.key}>
            <Form.Group>
              <Form.Label>{f.label} {f.required && <span className="text-danger">*</span>}</Form.Label>
              <Form.Control
                type="text"
                maxLength={f.maxLength ?? 200}
                value={p.form[f.key] ?? ''}
                onChange={(e) => p.setForm((prev) => ({ ...prev, [f.key]: e.target.value }))}
                required={f.required}
                autoFocus={idx === 0}
                placeholder={f.placeholder}
              />
            </Form.Group>
          </div>
        ))}
      </div>
      <div className="d-flex justify-content-end gap-2 mt-4">
        <Button type="button" variant="outline-secondary" onClick={p.onCancelar} disabled={p.isSaving}>
          <i className="bi bi-x-circle me-1" />Cancelar
        </Button>
        <Button type="submit" variant="primary" disabled={p.isSaving}>
          {p.isSaving
            ? (<><Spinner size="sm" className="me-1" />Guardando…</>)
            : (<><i className="bi bi-check-circle me-1" />{p.isEditing ? 'Actualizar' : 'Crear'}</>)}
        </Button>
      </div>
    </Form>
  );
}
