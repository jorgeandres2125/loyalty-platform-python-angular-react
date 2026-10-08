import { useEffect, useMemo, useState } from 'react';
import { Badge, Button, Card, Form, Spinner } from 'react-bootstrap';
import { motion, AnimatePresence } from 'framer-motion';
import { EmptyState } from '../../../shared/ui/components/EmptyState';
import { ConfirmModal } from '../../../shared/ui/components/ConfirmModal';
import {
  DragDropProvider,
  useDraggable,
  useDroppable,
  type DragEndEvent,
} from '@dnd-kit/react';
import { extractError } from '../../../shared/lib/extractError';
import '../../../styles/components/RolesDnD.scss';
import {
  useAsignarRol,
  useBuscarUsuarios,
  useQuitarRol,
  useRolesAsignables,
  useRolesDeUsuario,
  useUsuariosDeRol,
} from '../../../features/admin-asignaciones/model/useAdminAsignaciones';
import type {
  RolAsignableItem,
  RolDeUsuarioItem,
  UsuarioCuentaItem,
} from '../../../features/admin-asignaciones/model/types';

const PAGE_SIZE = 10 as const;
const CRITICAL_ROLES: ReadonlySet<string> = new Set(['administrator', 'webmaster']);

function isCriticalRole(name: string): boolean {
  return CRITICAL_ROLES.has(name.trim().toLowerCase());
}

interface Toasters {
  onToast: (mensaje: string) => void;
  onError: (mensaje: string) => void;
}

interface RolesColumnProps {
  roles: RolAsignableItem[];
  isLoading: boolean;
  selectedRid: number | null;
  onSelect: (rid: number) => void;
}

function RolesColumn({ roles, isLoading, selectedRid, onSelect }: RolesColumnProps) {
  return (
    <Card className="border-0 shadow-sm h-100">
      <Card.Header className="bg-white fw-semibold">
        <i className="bi bi-shield-lock-fill me-2" />
        Roles
      </Card.Header>
      <Card.Body className="p-2">
        {isLoading ? (
          <div className="text-center py-4">
            <Spinner animation="border" />
          </div>
        ) : (
          <div className="list-group list-group-flush">
            {roles.map((rol) => {
              const activo: boolean = selectedRid === rol.rid;
              return (
                <button
                  type="button"
                  key={rol.rid}
                  className={`list-group-item list-group-item-action rounded mb-1 d-flex justify-content-between align-items-center ${activo ? 'active' : ''}`}
                  onClick={() => onSelect(rol.rid)}
                >
                  <span className="fw-semibold text-truncate">{rol.name}</span>
                  <Badge bg={activo ? 'light' : 'secondary'} text={activo ? 'dark' : undefined}>
                    #{rol.rid}
                  </Badge>
                </button>
              );
            })}
          </div>
        )}
      </Card.Body>
    </Card>
  );
}

interface AsignarResultadosProps {
  resultados: ReturnType<typeof useBuscarUsuarios>;
  pending: boolean;
  excluidos: ReadonlySet<number>;
  onAdd: (usr : UsuarioCuentaItem) => void;
}

function AsignarResultados({ resultados, pending, excluidos, onAdd }: AsignarResultadosProps) {
  if (resultados.isLoading) {
    return (
      <div className="text-center py-2">
        <Spinner animation="border" size="sm" />
      </div>
    );
  }
  const todos: UsuarioCuentaItem[] = resultados.data?.items ?? [];
  const items: UsuarioCuentaItem[] = todos.filter((usr) => !excluidos.has(usr.uid));
  if (items.length === 0) {
    return <div className="text-muted small">Sin coincidencias.</div>;
  }
  return (
    <div className="list-group">
      {items.map((usr) => (
        <div
          key={usr.uid}
          className="list-group-item d-flex justify-content-between align-items-center py-2"
        >
          <span className="small text-truncate">
            <strong>{usr.nombre}</strong>{' '}
            <span className="text-muted">{usr.email}</span>
          </span>
          <Button
            size="sm"
            variant="outline-success"
            disabled={pending}
            onClick={() => onAdd(usr)}
          >
            <i className="bi bi-person-check" />
          </Button>
        </div>
      ))}
    </div>
  );
}

interface AsignarUsuarioBoxProps extends Toasters {
  rid: number;
  onAssigned: (usr : UsuarioCuentaItem) => void;
}

function AsignarUsuarioBox({ rid, onAssigned, onToast, onError }: AsignarUsuarioBoxProps) {
  const [texto, setTexto] = useState<string>('');
  const [filtro, setFiltro] = useState<string>('');
  const resultados = useBuscarUsuarios(
    { page: 1, page_size: PAGE_SIZE, texto: filtro || undefined },
    filtro.length > 0,
  );
  const asignar = useAsignarRol();
  const [asignados, setAsignados] = useState<Set<number>>(new Set<number>());

  const handleAdd = async (usr : UsuarioCuentaItem) => {
    try {
      await asignar.mutateAsync({ uid: usr.uid, rid });
      setAsignados((prev) => new Set(prev).add(usr.uid));
      onToast(`Rol asignado a ${usr.nombre}`);
      onAssigned(usr);
    } catch (err) {
      onError(extractError(err, 'No se pudo asignar el rol'));
    }
  };

  return (
    <div className="border-top p-3">
      <div className="fw-semibold small mb-2 text-muted">
        <i className="bi bi-person-plus-fill me-1" />
        Asignar nuevo usuario
      </div>
      <div className="d-flex gap-2 mb-2">
        <Form.Control
          size="sm"
          placeholder="Buscar usuario por nombre o correo..."
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') setFiltro(texto.trim());
          }}
          maxLength={200}
        />
        <Button size="sm" variant="primary" onClick={() => setFiltro(texto.trim())}>
          <i className="bi bi-search" />
        </Button>
        {(texto || filtro) && (
          <Button
            size="sm"
            variant="outline-secondary"
            onClick={() => {
              setTexto('');
              setFiltro('');
            }}
          >
            <i className="bi bi-x-circle" />
          </Button>
        )}
      </div>
      {filtro.length > 0 && (
        <AsignarResultados resultados={resultados} pending={asignar.isPending} excluidos={asignados} onAdd={handleAdd} />
      )}
    </div>
  );
}

interface UsuariosListaProps {
  lista: ReturnType<typeof useUsuariosDeRol>;
  selectedUid: number | null;
  onSelectUser: (usr : UsuarioCuentaItem) => void;
}

function UsuariosLista({ lista, selectedUid, onSelectUser }: UsuariosListaProps) {
  if (lista.isLoading) {
    return (
      <div className="text-center py-4">
        <Spinner animation="border" />
      </div>
    );
  }
  if (lista.isError) {
    return <div className="text-danger small px-3 py-4">Error al cargar los usuarios</div>;
  }
  const items: UsuarioCuentaItem[] = lista.data?.items ?? [];
  if (items.length === 0) {
    return (
      <div className="text-center py-4 text-muted">
        <i className="bi bi-inbox display-6 d-block mb-2" />
        Sin usuarios con este rol
      </div>
    );
  }
  return (
    <div className="list-group list-group-flush">
      {items.map((usr) => (
        <button
          type="button"
          key={usr.uid}
          className={`list-group-item list-group-item-action d-flex justify-content-between align-items-center ${selectedUid === usr.uid ? 'active' : ''}`}
          onClick={() => onSelectUser(usr)}
        >
          <span className="text-truncate">
            <span className="fw-semibold">{usr.nombre}</span>{' '}
            <span className="small text-muted">{usr.email}</span>
          </span>
          <Badge bg={usr.activo ? 'success' : 'secondary'}>
            {usr.activo ? 'Activo' : 'Inactivo'}
          </Badge>
        </button>
      ))}
    </div>
  );
}

interface PaginacionProps {
  page: number;
  totalPages: number;
  total: number;
  onPrev: () => void;
  onNext: () => void;
}

function Paginacion({ page, totalPages, total, onPrev, onNext }: PaginacionProps) {
  return (
    <div className="d-flex align-items-center justify-content-between px-3 py-2 border-top">
      <div className="text-muted small">
        Pag. <strong>{page}</strong> de <strong>{totalPages}</strong> &middot; {total}
      </div>
      <div className="d-flex gap-2">
        <Button size="sm" variant="outline-secondary" disabled={page <= 1} onClick={onPrev}>
          <i className="bi bi-chevron-left" />
        </Button>
        <Button size="sm" variant="outline-secondary" disabled={page >= totalPages} onClick={onNext}>
          <i className="bi bi-chevron-right" />
        </Button>
      </div>
    </div>
  );
}

interface UsuariosColumnProps extends Toasters {
  rid: number;
  selectedUid: number | null;
  onSelectUser: (usr : UsuarioCuentaItem) => void;
}

function UsuariosColumn({ rid, selectedUid, onSelectUser, onToast, onError }: UsuariosColumnProps) {
  const [page, setPage] = useState<number>(1);
  const [busca, setBusca] = useState<string>('');
  const [filtro, setFiltro] = useState<string>('');
  const lista = useUsuariosDeRol(rid, { page, page_size: PAGE_SIZE, texto: filtro || undefined });

  const totalPages: number = lista.data
    ? Math.max(1, Math.ceil(lista.data.total / PAGE_SIZE))
    : 1;

  const aplicarBusqueda = () => {
    setFiltro(busca.trim());
    setPage(1);
  };

  const limpiar = () => {
    setBusca('');
    setFiltro('');
    setPage(1);
  };

  const hayItems: boolean = !!lista.data && lista.data.items.length > 0;

  return (
    <Card className="border-0 shadow-sm h-100">
      <Card.Header className="bg-white fw-semibold d-flex align-items-center">
        <i className="bi bi-people-fill me-2" />
        Usuarios del rol
      </Card.Header>
      <div className="d-flex gap-2 p-3 pb-2">
        <Form.Control
          size="sm"
          placeholder="Filtrar por nombre o correo..."
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') aplicarBusqueda();
          }}
          maxLength={200}
        />
        <Button size="sm" variant="primary" onClick={aplicarBusqueda}>
          <i className="bi bi-search" />
        </Button>
        {filtro && (
          <Button size="sm" variant="outline-secondary" onClick={limpiar}>
            <i className="bi bi-x-circle" />
          </Button>
        )}
      </div>
      <UsuariosLista lista={lista} selectedUid={selectedUid} onSelectUser={onSelectUser} />
      {hayItems && lista.data && (
        <Paginacion
          page={page}
          totalPages={totalPages}
          total={lista.data.total}
          onPrev={() => setPage(page - 1)}
          onNext={() => setPage(page + 1)}
        />
      )}
      <AsignarUsuarioBox rid={rid} onAssigned={onSelectUser} onToast={onToast} onError={onError} />
    </Card>
  );
}

const ZONE_ASIGNADOS = 'zona-asignados';
const ZONE_DISPONIBLES = 'zona-disponibles';

interface DetalleColumnProps extends Toasters {
  user: UsuarioCuentaItem;
}

function DetalleColumn({ user, onToast, onError }: DetalleColumnProps) {
  const rolesQuery = useRolesDeUsuario(user.uid);
  const asignar = useAsignarRol();
  const quitar = useQuitarRol();
  const [pendingRol, setPendingRol] = useState<RolDeUsuarioItem | null>(null);

  const allRoles: RolDeUsuarioItem[] = useMemo(() => rolesQuery.data ?? [], [rolesQuery.data]);
  const asignados: RolDeUsuarioItem[] = useMemo(
    () => allRoles.filter((r) => r.asignado),
    [allRoles],
  );
  const disponibles: RolDeUsuarioItem[] = useMemo(
    () => allRoles.filter((r) => !r.asignado),
    [allRoles],
  );

  const aplicarAsignar = async (rol: RolDeUsuarioItem) => {
    try {
      await asignar.mutateAsync({ uid: user.uid, rid: rol.rid });
      onToast(`Rol "${rol.name}" asignado`);
    } catch (err) {
      onError(extractError(err, 'No se pudo asignar el rol'));
    }
  };

  const aplicarQuitar = async (rol: RolDeUsuarioItem) => {
    try {
      await quitar.mutateAsync({ uid: user.uid, rid: rol.rid });
      onToast(`Rol "${rol.name}" retirado`);
    } catch (err) {
      onError(extractError(err, 'No se pudo quitar el rol'));
    }
  };

  const mover = (rol: RolDeUsuarioItem, haciaAsignados: boolean) => {
    if (haciaAsignados && !rol.asignado) {
      void aplicarAsignar(rol);
    } else if (!haciaAsignados && rol.asignado) {
      if (isCriticalRole(rol.name)) setPendingRol(rol);
      else void aplicarQuitar(rol);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const source = event.operation.source;
    const target = event.operation.target;
    if (event.canceled || !source || !target) return;
    const info = source.data as { rid: number };
    const rol: RolDeUsuarioItem | undefined = allRoles.find((r) => r.rid === info.rid);
    if (rol) mover(rol, String(target.id) === ZONE_ASIGNADOS);
  };

  const confirmar = async () => {
    if (!pendingRol) return;
    await aplicarQuitar(pendingRol);
    setPendingRol(null);
  };

  const cargando: boolean = asignar.isPending || quitar.isPending;

  return (
    <Card className="border-0 shadow-sm h-100">
      <Card.Header className="bg-white fw-semibold">
        <i className="bi bi-person-badge me-2" />
        Detalle del usuario
      </Card.Header>
      <Card.Body>
        <div className="mb-2">
          <div className="fw-bold fs-6 text-truncate">{user.nombre}</div>
          <div className="small text-muted text-truncate">{user.email || '—'}</div>
          <Badge bg={user.activo ? 'success' : 'secondary'} className="mt-1">
            {user.activo ? 'Activo' : 'Inactivo'}
          </Badge>
          <span className="small text-muted ms-2">UID {user.uid}</span>
        </div>
        <hr />
        <div className="fw-semibold small mb-1">Gestion de roles</div>
        <p className="text-muted roles-dnd__hint">
          Arrastra un rol entre las listas (o usa los botones) para asignarlo o quitarlo. Revocar un rol critico pide confirmacion.
        </p>
        {rolesQuery.isLoading ? (
          <div className="text-center py-3">
            <Spinner animation="border" />
          </div>
        ) : rolesQuery.isError ? (
          <div className="text-danger small">Error al cargar los roles</div>
        ) : (
          <RolesDragDrop
            asignados={asignados}
            disponibles={disponibles}
            disabled={cargando}
            onMover={mover}
            onDragEnd={handleDragEnd}
          />
        )}
      </Card.Body>
      <ConfirmModal
        show={pendingRol !== null}
        title="Revocar rol critico"
        message={
          pendingRol
            ? `El rol "${pendingRol.name}" otorga privilegios elevados. Confirmas retirarlo de ${user.nombre}?`
            : ''
        }
        confirmLabel="Revocar"
        confirmIcon="bi-shield-x"
        confirmVariant="danger"
        loading={quitar.isPending}
        loadingLabel="Revocando..."
        onConfirm={confirmar}
        onHide={() => setPendingRol(null)}
      />
    </Card>
  );
}

interface RolChipProps {
  rol: RolDeUsuarioItem;
  zona: string;
  haciaAsignados: boolean;
  disabled: boolean;
  onMover: (rol: RolDeUsuarioItem, haciaAsignados: boolean) => void;
}

function RolChip({ rol, zona, haciaAsignados, disabled, onMover }: RolChipProps) {
  const { ref, isDragging } = useDraggable({
    id: `rol-${rol.rid}`,
    data: { rid: rol.rid, zona },
    disabled,
  });
  const critico: boolean = isCriticalRole(rol.name);
  const accionIcon: string = haciaAsignados ? 'bi-plus-lg' : 'bi-dash-lg';
  const accionLabel: string = haciaAsignados
    ? `Asignar rol ${rol.name}`
    : `Quitar rol ${rol.name}`;
  return (
    <li
      ref={ref}
      className={`roles-dnd__chip ${isDragging ? 'is-dragging' : ''} ${critico ? 'is-critico' : ''}`}
    >
      <span className="roles-dnd__grip" aria-hidden="true">
        <i className="bi bi-grip-vertical" />
      </span>
      <i
        className={`bi ${critico ? 'bi-shield-lock-fill' : 'bi-person-badge'} roles-dnd__chip-ico`}
        aria-hidden="true"
      />
      <span className="roles-dnd__chip-name" title={rol.name}>
        {rol.name}
      </span>
      <span className="roles-dnd__chip-rid">#{rol.rid}</span>
      <button
        type="button"
        className="roles-dnd__chip-btn"
        disabled={disabled}
        onPointerDown={(e) => e.stopPropagation()}
        onClick={() => onMover(rol, haciaAsignados)}
        aria-label={accionLabel}
        title={accionLabel}
      >
        <i className={`bi ${accionIcon}`} />
      </button>
    </li>
  );
}

interface RolDropZoneProps {
  id: string;
  variante: 'asignados' | 'disponibles';
  titulo: string;
  icono: string;
  vacioTexto: string;
  roles: RolDeUsuarioItem[];
  disabled: boolean;
  onMover: (rol: RolDeUsuarioItem, haciaAsignados: boolean) => void;
}

function RolDropZone({ id, variante, titulo, icono, vacioTexto, roles, disabled, onMover }: RolDropZoneProps) {
  const { ref, isDropTarget } = useDroppable({ id, data: { zona: id } });
  const esAsignados: boolean = variante === 'asignados';
  return (
    <section
      ref={ref}
      className={`roles-dnd__zone roles-dnd__zone--${variante} ${isDropTarget ? 'is-over' : ''}`}
      aria-label={titulo}
    >
      <header className="roles-dnd__zone-head">
        <i className={`bi ${icono}`} aria-hidden="true" />
        <span className="roles-dnd__zone-title">{titulo}</span>
        <span className="roles-dnd__count">{roles.length}</span>
      </header>
      {roles.length === 0 ? (
        <p className="roles-dnd__empty">
          <i className="bi bi-arrow-down-square me-1" aria-hidden="true" />
          {vacioTexto}
        </p>
      ) : (
        <ul className="roles-dnd__list">
          {roles.map((rol) => (
            <RolChip
              key={rol.rid}
              rol={rol}
              zona={id}
              haciaAsignados={!esAsignados}
              disabled={disabled}
              onMover={onMover}
            />
          ))}
        </ul>
      )}
    </section>
  );
}

interface RolesDragDropProps {
  asignados: RolDeUsuarioItem[];
  disponibles: RolDeUsuarioItem[];
  disabled: boolean;
  onMover: (rol: RolDeUsuarioItem, haciaAsignados: boolean) => void;
  onDragEnd: (event: DragEndEvent) => void;
}

function RolesDragDrop({ asignados, disponibles, disabled, onMover, onDragEnd }: RolesDragDropProps) {
  return (
    <DragDropProvider onDragEnd={onDragEnd}>
      <div className="roles-dnd">
        <RolDropZone
          id={ZONE_ASIGNADOS}
          variante="asignados"
          titulo="Roles asignados"
          icono="bi-person-check-fill"
          vacioTexto="Arrastra aqui los roles para asignarlos al usuario"
          roles={asignados}
          disabled={disabled}
          onMover={onMover}
        />
        <RolDropZone
          id={ZONE_DISPONIBLES}
          variante="disponibles"
          titulo="Roles disponibles"
          icono="bi-collection"
          vacioTexto="El usuario ya tiene todos los roles"
          roles={disponibles}
          disabled={disabled}
          onMover={onMover}
        />
      </div>
    </DragDropProvider>
  );
}

export function UsuariosRolesTab() {
  const roles = useRolesAsignables();
  const [selectedRid, setSelectedRid] = useState<number | null>(null);
  const [selectedUser, setSelectedUser] = useState<UsuarioCuentaItem | null>(null);
  const [success, setSuccess] = useState<string>('');
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (!success) return;
    const t = setTimeout(() => setSuccess(''), 3000);
    return () => clearTimeout(t);
  }, [success]);

  const handleSelectRol = (rid: number) => {
    setSelectedRid(rid);
    setSelectedUser(null);
  };

  return (
    <div>
      {success && (
        <div className="alert alert-success d-flex align-items-center" role="alert">
          <i className="bi bi-check-circle me-2" />
          {success}
        </div>
      )}
      {error && (
        <div className="alert alert-danger d-flex align-items-center" role="alert">
          <i className="bi bi-exclamation-triangle me-2" />
          <span>{error}</span>
          <button type="button" className="btn-close ms-auto" onClick={() => setError('')} />
        </div>
      )}

      <div className="d-flex flex-column flex-lg-row gap-3 align-items-stretch">
        <div className="flex-shrink-0" style={{ flexBasis: '25%' }}>
          <RolesColumn
            roles={roles.data ?? []}
            isLoading={roles.isLoading}
            selectedRid={selectedRid}
            onSelect={handleSelectRol}
          />
        </div>

        <div style={{ flexBasis: '45%', minWidth: 0 }}>
          {selectedRid === null ? (
            <Card className="border-0 shadow-sm h-100">
              <Card.Body className="d-flex align-items-center justify-content-center">
                <EmptyState
                  icon="bi-arrow-left-circle"
                  title="Selecciona un rol"
                  description="Elige un rol de la izquierda para ver y gestionar sus usuarios."
                />
              </Card.Body>
            </Card>
          ) : (
            <AnimatePresence mode="wait">
              <motion.div
                key={selectedRid}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25 }}
              >
                <UsuariosColumn
                  key={selectedRid}
                  rid={selectedRid}
                  selectedUid={selectedUser?.uid ?? null}
                  onSelectUser={setSelectedUser}
                  onToast={setSuccess}
                  onError={setError}
                />
              </motion.div>
            </AnimatePresence>
          )}
        </div>

        <div style={{ flexBasis: '30%', minWidth: 0 }}>
          <AnimatePresence mode="wait">
            {selectedUser ? (
              <motion.div
                key={selectedUser.uid}
                initial={{ x : 30, opacity: 0 }}
                animate={{ x : 0, opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              >
                <DetalleColumn
                  key={selectedUser.uid}
                  user={selectedUser}
                  onToast={setSuccess}
                  onError={setError}
                />
              </motion.div>
            ) : (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <Card className="border-0 shadow-sm h-100">
                  <Card.Body className="d-flex align-items-center justify-content-center">
                    <EmptyState
                      icon="bi-person-lines-fill"
                      title="Sin usuario seleccionado"
                      description="Selecciona un usuario para ver su detalle y gestionar sus roles"
                    />
                  </Card.Body>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}