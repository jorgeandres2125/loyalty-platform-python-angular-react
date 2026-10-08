import { type ReactNode, useEffect, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import TomSelect from 'tom-select';
import 'tom-select/dist/css/tom-select.bootstrap5.css';
import { useDropzone } from 'react-dropzone';
import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Collapse,
  Form,
  Nav,
  Row,
  Spinner,
  Table,
} from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../shared/api/client';
import { useMaxUploadBytes } from '../../features/config/model/useUploadLimits';
import { validarTamanoArchivo } from '../../shared/lib/archivos';
import { useToastContext } from '../../shared/ui/hooks/useToastContext';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { EstadoSwitch } from '../../shared/ui/components/EstadoSwitch';
import { ConQuienVivesSelector } from '../../shared/ui/components/ConQuienVivesSelector';
import { TieneHijosSelector } from '../../shared/ui/components/TieneHijosSelector';
import { TieneMascotaSelector } from '../../shared/ui/components/TieneMascotaSelector';
import { HobbiesSelector } from '../../shared/ui/components/HobbiesSelector';
import { PremiosSelector } from '../../shared/ui/components/PremiosSelector';
import { TemasProfundizarSelector } from '../../shared/ui/components/TemasProfundizarSelector';
import { PropositosFamiliaresSelector } from '../../shared/ui/components/PropositosFamiliaresSelector';
import { PropositosFinancierosSelector } from '../../shared/ui/components/PropositosFinancierosSelector';
import { PropositosDiversionSelector } from '../../shared/ui/components/PropositosDiversionSelector';
import { PropositosSaludSelector } from '../../shared/ui/components/PropositosSaludSelector';
import { PropositosCompetenciasSelector } from '../../shared/ui/components/PropositosCompetenciasSelector';
import { MetroTileToggle } from '../../shared/ui/components/MetroTileToggle';
import { ConfirmModal } from '../../shared/ui/components/ConfirmModal';
import {
  useMiDetalleMovilidad,
  useGuardarMiContactoMovilidad,
  useGuardarMiTributarioMovilidad,
  useGuardarMiEmocionalMovilidad,
} from '../../features/perfil-self/model/useMiPerfilMovilidad';
import { useAuthStore } from '../../entities/user/model/authStore';
import {
  useEliminarMiDocumento,
  useMisDocumentos,
} from '../../features/perfil-self/model/usePerfilSelf';
import type { DocumentoSelfItem } from '../../features/perfil-self/model/types';
import {
  fechaCorta, parseBoolOrNull, parseEstado, parseGenero, parseNumOrNull,
  parseTipoDoc, refId, refObj, strDe,
} from '../../shared/lib/parseContacto';

const PROGRAMA_MOVILIDAD_ID = 1;
const NO_COMISION_EPS = 7848;
const NO_COMISION_AFP = 7846;
const NO_COMISION_ARL = 7847;

function countSelections(raw: string): number {
  if (!raw) return 0;
  try {
    const parsed: unknown = JSON.parse(raw);
    if (Array.isArray(parsed)) return parsed.length;
  } catch {
    return raw.split(',').filter(s => s.trim()).length;
  }
  return 0;
}

type PerfilTab = 'contacto' | 'tributario' | 'emocional' | 'documentacion';

function tabFromHash(hash: string): PerfilTab | null {
  const clean: string = (hash || '').replace(/^#/, '').toLowerCase();
  if (clean === 'documentos' || clean === 'documentacion') return 'documentacion';
  if (clean === 'contacto') return 'contacto';
  if (clean === 'tributario') return 'tributario';
  if (clean === 'emocional') return 'emocional';
  return null;
}

const ESTADOS_DOCUMENTO_PERFIL: ReadonlyArray<{ value: string; label: string; bg: string }> = [
  { value: 'pendiente', label: 'Pendiente', bg: 'warning' },
  { value: 'revision', label: 'Revisión', bg: 'info' },
  { value: 'aprobado', label: 'Aprobado', bg: 'success' },
];

function estadoDocBadgeBg(estado: string): string {
  return ESTADOS_DOCUMENTO_PERFIL.find((e) => e.value === estado.toLowerCase())?.bg ?? 'secondary';
}

function estadoDocLabel(estado: string): string {
  return ESTADOS_DOCUMENTO_PERFIL.find((e) => e.value === estado.toLowerCase())?.label ?? estado;
}

function formatFechaDisplayPerfil(value: string | null): string {
  if (!value) return '—';
  const d: Date = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function MisDocumentos() {
  // AP-0055: lectura y eliminacion via /me/documentos (ownership por token, no por
  // parametro de ruta). El estado de moderacion (pendiente/revision/aprobado) es un
  // campo de staff (DOCUMENTOS_MODERAR): el propio comisionista no puede editarlo, por
  // eso este panel es de solo lectura mas eliminar, sin "Editar".
  const docs = useMisDocumentos(true);
  const eliminar = useEliminarMiDocumento();
  const [errorMsg, setErrorMsg] = useState<string>('');
  const [docAEliminar, setDocAEliminar] = useState<DocumentoSelfItem | null>(null);

  const confirmarEliminacion = async () => {
    if (!docAEliminar) return;
    setErrorMsg('');
    try {
      await eliminar.mutateAsync(docAEliminar.did);
      setDocAEliminar(null);
    } catch (err) {
      const msg: string = err instanceof Error ? err.message : 'Error al eliminar';
      setErrorMsg(msg);
      setDocAEliminar(null);
    }
  };

  const cancelarEliminacion = () => {
    if (eliminar.isPending) return;
    setDocAEliminar(null);
  };

  if (docs.isLoading) {
    return (
      <div className="text-center py-3">
        <Spinner animation="border" variant="danger" size="sm" />
      </div>
    );
  }

  if (!docs.data || docs.data.length === 0) {
    return (
      <div className="text-center py-4 text-muted">
        <i className="bi bi-inbox fs-3 d-block mb-2" />
        Aún no tienes documentos cargados.
      </div>
    );
  }

  return (
    <div>
      {errorMsg && (
        <Alert variant="danger" onClose={() => setErrorMsg('')} dismissible className="py-2">
          {errorMsg}
        </Alert>
      )}
      <Table size="sm" hover responsive className="mb-0">
        <thead className="table-light">
          <tr>
            <th>Id</th>
            <th>Tipo de documento</th>
            <th>Documento</th>
            <th>Estado</th>
            <th className="text-center">Versión</th>
            <th>Fecha Alta</th>
            <th className="text-center">Operación</th>
          </tr>
        </thead>
        <tbody>
          {docs.data.map((d: DocumentoSelfItem) => (
            <tr key={d.did}>
              <td className="font-monospace">{d.did}</td>
              <td>{d.tipo_nombre}</td>
              <td className="font-monospace">{d.nombre}</td>
              <td>
                <Badge bg={estadoDocBadgeBg(d.estado)}>{estadoDocLabel(d.estado)}</Badge>
              </td>
              <td className="text-center">{d.version}</td>
              <td>{formatFechaDisplayPerfil(d.fecha)}</td>
              <td className="text-center">
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => setDocAEliminar(d)}
                  disabled={eliminar.isPending}
                >
                  {eliminar.isPending && docAEliminar?.did === d.did ? (
                    <><Spinner animation="border" size="sm" className="me-1" />Eliminando…</>
                  ) : (
                    <><i className="bi bi-trash me-1" />Eliminar</>
                  )}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <ConfirmModal
        show={!!docAEliminar}
        title="Eliminar documento"
        message={
          docAEliminar ? (
            <>
              ¿Seguro que quieres eliminar el documento{' '}
              <strong>{docAEliminar.nombre}</strong> ({docAEliminar.tipo_nombre})?
              <br />
              <span className="text-muted small">Esta acción no se puede deshacer.</span>
            </>
          ) : null
        }
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        loading={eliminar.isPending}
        loadingLabel="Eliminando…"
        onConfirm={confirmarEliminacion}
        onHide={cancelarEliminacion}
      />
    </div>
  );
}

interface FormContacto {
  numero_documento: string;
  tipo_documento: string;
  nombre_completo: string;
  genero: string;
  fecha_nacimiento: string;
  celular: string;
  telefono: string;
  email: string;
  direccion: string;
  departamento: string;
  ciudad: string;
  cod_canales: number | '';
  cod_oficinas: number | '';
  acepto_habeas_data: boolean;
  incentivos: boolean;
  estado: 0 | 1 | null;
  firma_contrato: boolean | null;
  banco: number | null;
  tipo_de_cuenta: string;
  numero_de_cuenta: string;
  numero_de_cuenta_verifica: string;
  requiere_comision: boolean | null;
}

interface FormTributario {
  eps: number | null;
  afp: number | null;
  arl: number | null;
  contratacion_personal: boolean | null;
  regimen_iva: boolean | null;
}

interface FormEmocional {
  con_quien_vives: string;
  estado_civil: string;
  numero_hijos: string;
  info_hijos: string;
  hobbies: string;
  nivel_educativo: string;
  profesion: string;
  temas_a_profundizar: string;
  premios_gustaria_recibir: string;
  propositos_familiares: string;
  propositos_financieros: string;
  propositos_diversion: string;
  propositos_salud: string;
  propositos_competencias: string;
  numero_mascotas: string;
  info_mascotas: string;
  acepto_terminos_y_condiciones: boolean;
}

const initContacto: FormContacto = {
  numero_documento: '', tipo_documento: 'CC', nombre_completo: '', genero: '',
  fecha_nacimiento: '', celular: '', telefono: '', email: '', direccion: '',
  departamento: '', ciudad: '',
  cod_canales: '', cod_oficinas: '',
  acepto_habeas_data: true, incentivos: false, estado: 1, firma_contrato: null,
  banco: null, tipo_de_cuenta: '', numero_de_cuenta: '', numero_de_cuenta_verifica: '',
  requiere_comision: null,
};

const initTributario: FormTributario = {
  eps: null, afp: null, arl: null,
  contratacion_personal: null, regimen_iva: null,
};

const initEmocional: FormEmocional = {
  con_quien_vives: '', estado_civil: '', numero_hijos: '', info_hijos: '', hobbies: '',
  nivel_educativo: '', profesion: '', temas_a_profundizar: '', premios_gustaria_recibir: '',
  propositos_familiares: '', propositos_financieros: '', propositos_diversion: '',
  propositos_salud: '', propositos_competencias: '',
  numero_mascotas: '', info_mascotas: '', acepto_terminos_y_condiciones: true,
};

const _GENERO_NOMBRE: Record<string, string> = {
  '0': 'Femenino', '1': 'Masculino',
  'F': 'Femenino', 'M': 'Masculino',
  'Femenino': 'Femenino', 'Masculino': 'Masculino', 'Otro': 'Otro', 'O': 'Otro',
};

// DocZone para el perfil propio — usa endpoints /me/documentos/* (auth por JWT).
function DocZone({
  tipoLabel, tipoPrefix, tipo, numeroDocumento, existingDoc,
  onUploaded, onDeleted, onUploadingChange, disabled, children,
}: {
  tipoLabel: string;
  tipoPrefix: string;
  tipo: number;
  numeroDocumento: string;
  existingDoc: { did: number; nombre: string; version: number } | null;
  onUploaded: () => void;
  onDeleted: () => void;
  onUploadingChange: (uploading: boolean) => void;
  disabled?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const toast = useToastContext();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  const maxBytes = useMaxUploadBytes();
  const isDisabled = disabled || uploading || !numeroDocumento;

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: isDisabled,
    onDrop: async (accepted) => {
      if (!accepted.length || !numeroDocumento) return;
      setUploading(true);
      onUploadingChange(true);
      setUploadError('');
      const nombre = `${tipoPrefix}${numeroDocumento}.pdf`;
      const form = new FormData();
      // AP-0055: el backend resuelve el numero_documento desde el JWT; no se envia
      // desde el cliente (el dueno solo puede subir sus propios documentos).
      form.append('tipo', String(tipo));
      form.append('file', accepted[0], nombre);
      try {
        validarTamanoArchivo(accepted[0], maxBytes);
        await apiClient.post('/me/documentos/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setOpen(false);
        onUploaded();
        toast.success('Documento cargado correctamente.', { title: 'Carga exitosa' });
      } catch (err) {
        const detalle = detalleError(err, 'Error al subir. Intente de nuevo.');
        setUploadError(detalle);
        toast.error('No se pudo subir el archivo.', { title: 'Error al subir', detail: detalle });
      } finally {
        setUploading(false);
        onUploadingChange(false);
      }
    },
  });

  useEffect(() => {
    if (disabled && open) setOpen(false);
  }, [disabled, open]);

  const confirmarEliminacion = async () => {
    if (!existingDoc) return;
    setDeleting(true);
    setDeleteError('');
    try {
      await apiClient.delete(`/me/documentos/${existingDoc.did}`);
      onDeleted();
      setConfirmDelete(false);
    } catch {
      setDeleteError('No se pudo eliminar el archivo.');
    } finally {
      setDeleting(false);
    }
  };

  const cancelarEliminacion = () => {
    if (deleting) return;
    setConfirmDelete(false);
    setDeleteError('');
  };

  return (
    <>
      <div className="d-flex align-items-center gap-2">
        <div className="flex-grow-1">{children}</div>
        <div className="d-flex gap-1 flex-shrink-0">
          <Button
            variant="outline-primary"
            size="sm"
            onClick={() => setOpen((prev) => !prev)}
            title={`Subir archivo ${tipoLabel}`}
            disabled={isDisabled}
          >
            <i className="bi bi-paperclip" />
          </Button>
          {existingDoc && (
            <Button
              variant="outline-danger"
              size="sm"
              onClick={() => { setConfirmDelete(true); setDeleteError(''); }}
              title={`Eliminar archivo ${tipoLabel}`}
              disabled={deleting}
            >
              <i className="bi bi-trash" />
            </Button>
          )}
        </div>
      </div>
      {existingDoc && !open && (
        <small className="text-success d-block mt-1">
          <i className="bi bi-file-earmark-check me-1" />
          {existingDoc.nombre} <span className="text-muted">(v{existingDoc.version})</span>
        </small>
      )}
      {deleteError && (
        <small className="text-danger d-block mt-1">{deleteError}</small>
      )}
      <ConfirmModal
        show={confirmDelete}
        title={`Eliminar archivo ${tipoLabel}`}
        message={
          existingDoc ? (
            <>
              ¿Seguro que quieres eliminar el archivo <strong>{existingDoc.nombre}</strong> de{' '}
              <strong>{tipoLabel}</strong>?
              <br />
              <span className="text-muted small">Esta acción no se puede deshacer.</span>
            </>
          ) : null
        }
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        loading={deleting}
        loadingLabel="Eliminando…"
        onConfirm={confirmarEliminacion}
        onHide={cancelarEliminacion}
      />
      <Collapse in={open}>
        <div>
          <div className="border rounded p-3 bg-light mt-2">
            <div
              {...getRootProps()}
              className={`rounded p-4 text-center ${isDragActive ? 'border border-primary bg-primary-subtle' : 'border border-secondary'}`}
              style={{ borderStyle: 'dashed', cursor: isDisabled ? 'not-allowed' : 'pointer' }}
            >
              <input {...getInputProps()} />
              {uploading ? (
                <span><Spinner animation="border" size="sm" className="me-2" />Subiendo...</span>
              ) : isDragActive ? (
                <span className="text-primary">Suelta el PDF aquí...</span>
              ) : (
                <span className="text-muted small">
                  <i className="bi bi-upload me-2" />
                  Arrastra un PDF o haz clic para seleccionar
                </span>
              )}
            </div>
            {uploadError && <div className="text-danger small mt-1">{uploadError}</div>}
            <div className="mt-2 text-end">
              <Button variant="outline-secondary" size="sm" onClick={() => setOpen(false)}>
                Cancelar
              </Button>
            </div>
          </div>
        </div>
      </Collapse>
    </>
  );
}

// Fila de subida de certificado (Prepagada, Vivienda, Cédula, etc.) sin colapsable.
function CertificadoRow({
  label, tipo, tipoPrefix, numeroDocumento, existingDoc,
  onUploaded, onDeleted, onUploadingChange,
}: {
  label: string;
  tipo: number;
  tipoPrefix: string;
  numeroDocumento: string;
  existingDoc: { did: number; nombre: string; version: number } | null;
  onUploaded: () => void;
  onDeleted: () => void;
  onUploadingChange: (uploading: boolean) => void;
}) {
  const [uploading, setUploading] = useState(false);
  const [rowError, setRowError] = useState('');
  const toast = useToastContext();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const maxBytes = useMaxUploadBytes();
  const isDisabled = uploading || !numeroDocumento;

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: isDisabled,
    onDrop: async (accepted) => {
      if (!accepted.length || !numeroDocumento) return;
      setUploading(true);
      onUploadingChange(true);
      setRowError('');
      const nombre = `${tipoPrefix}${numeroDocumento}.pdf`;
      const form = new FormData();
      // AP-0055: el backend resuelve el numero_documento desde el JWT; no se envia
      // desde el cliente (el dueno solo puede subir sus propios documentos).
      form.append('tipo', String(tipo));
      form.append('file', accepted[0], nombre);
      try {
        validarTamanoArchivo(accepted[0], maxBytes);
        await apiClient.post('/me/documentos/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        onUploaded();
        toast.success('Documento cargado correctamente.', { title: 'Carga exitosa' });
      } catch (err) {
        const detalle = detalleError(err, 'Error al subir');
        setRowError(detalle);
        toast.error('No se pudo subir el archivo.', { title: 'Error al subir', detail: detalle });
      } finally {
        setUploading(false);
        onUploadingChange(false);
      }
    },
  });

  const confirmarEliminacion = async () => {
    if (!existingDoc) return;
    setDeleting(true);
    setRowError('');
    try {
      await apiClient.delete(`/me/documentos/${existingDoc.did}`);
      onDeleted();
      setConfirmDelete(false);
    } catch {
      setRowError('No se pudo eliminar');
    } finally {
      setDeleting(false);
    }
  };

  const cancelarEliminacion = () => {
    if (deleting) return;
    setConfirmDelete(false);
  };

  return (
    <div className="border rounded mb-2 overflow-hidden bg-white">
      <div className="px-3 py-2 d-flex align-items-center justify-content-between border-bottom" style={{ minHeight: 40 }}>
        <span className="fw-medium">{label}</span>
        <div className="d-flex align-items-center gap-2">
          {existingDoc && (
            <small className="text-success text-truncate">
              <i className="bi bi-check-circle-fill me-1" />
              {existingDoc.nombre} <span className="text-muted">(v{existingDoc.version})</span>
            </small>
          )}
          {rowError && <small className="text-danger">{rowError}</small>}
          {existingDoc && (
            <Button
              variant="outline-danger"
              size="sm"
              onClick={() => { setConfirmDelete(true); setRowError(''); }}
              type="button"
              title="Eliminar archivo"
              disabled={deleting}
            >
              <i className="bi bi-trash" />
            </Button>
          )}
        </div>
      </div>
      <div
        {...getRootProps({
          className: `d-flex align-items-center justify-content-center px-3 py-3 small bg-white${
            isDisabled ? ' text-muted' : isDragActive ? ' text-primary' : ' text-dark'
          }`,
        })}
        style={{
          cursor: isDisabled ? 'not-allowed' : 'pointer',
          border: `1px dashed ${isDragActive ? '#0d6efd' : '#000'}`,
          margin: 8,
          borderRadius: 4,
        }}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <span><Spinner animation="border" size="sm" className="me-2" />Subiendo…</span>
        ) : isDragActive ? (
          <span><i className="bi bi-upload me-2" />Suelta el PDF aquí</span>
        ) : (
          <span>
            <i className="bi bi-upload me-2" />
            {existingDoc ? 'Arrastra un PDF para reemplazar o haz clic para seleccionar' : 'Arrastra un PDF o haz clic para seleccionar'}
          </span>
        )}
      </div>
      <ConfirmModal
        show={confirmDelete}
        title={`Eliminar archivo ${label}`}
        message={
          existingDoc ? (
            <>
              ¿Seguro que quieres eliminar el archivo <strong>{existingDoc.nombre}</strong> de{' '}
              <strong>{label}</strong>?
              <br />
              <span className="text-muted small">Esta acción no se puede deshacer.</span>
            </>
          ) : null
        }
        confirmLabel="Sí, eliminar"
        confirmIcon="bi-trash"
        loading={deleting}
        loadingLabel="Eliminando…"
        onConfirm={confirmarEliminacion}
        onHide={cancelarEliminacion}
      />
    </div>
  );
}

// ── Helpers puros (AP-0036): mapeo del backend, armado de payloads y validación ──
function parseTipoCuenta(v: unknown): string {
  const s = String(v ?? '');
  if (s === '0' || s.toLowerCase().includes('ahor')) return 'Cuenta de ahorros';
  if (s === '1' || s.toLowerCase().includes('corr')) return 'Cuenta corriente';
  return '';
}

function boolToBit(b: boolean | null): 0 | 1 | null {
  if (b === null) return null;
  return b ? 1 : 0;
}

function mapearContactoMovilidad(c: Record<string, unknown>): FormContacto {
  const depObj = refObj(c.departamento);
  const ciuObj = refObj(c.ciudad);
  const cuenta = strDe(c.numero_de_cuenta);
  return {
    numero_documento: strDe(c.numero_documento),
    tipo_documento: parseTipoDoc(c.tipo_documento).replace(/\./g, ''),
    nombre_completo: strDe(c.nombre_completo),
    genero: parseGenero(c.genero, _GENERO_NOMBRE),
    fecha_nacimiento: fechaCorta(c.fecha_nacimiento),
    celular: strDe(c.celular),
    telefono: c.telefono ? String(c.telefono) : '',
    email: c.email ? String(c.email) : '',
    direccion: strDe(c.direccion),
    departamento: depObj ? strDe(depObj.did) : strDe(c.departamento),
    ciudad: ciuObj ? strDe(ciuObj.cid) : strDe(c.ciudad),
    cod_canales: refId(c.cod_canales, 'cod_canales'),
    cod_oficinas: refId(c.cod_oficinas, 'cod_oficinas'),
    acepto_habeas_data: Boolean(c.acepto_habeas_data),
    incentivos: Boolean(c.incentivos),
    estado: parseEstado(c.estado),
    firma_contrato: parseBoolOrNull(c.firma_contrato),
    requiere_comision: parseBoolOrNull(c.requiere_comision),
    banco: parseNumOrNull(c.banco),
    tipo_de_cuenta: parseTipoCuenta(c.tipo_de_cuenta),
    numero_de_cuenta: cuenta,
    numero_de_cuenta_verifica: cuenta,
  };
}

function mapearEmocionalMovilidad(e: Record<string, unknown>): FormEmocional {
  return {
    con_quien_vives: strDe(e.con_quien_vives),
    estado_civil: strDe(e.estado_civil),
    numero_hijos: e.numero_hijos != null ? String(e.numero_hijos) : '',
    info_hijos: strDe(e.info_hijos),
    hobbies: strDe(e.hobbies),
    nivel_educativo: strDe(e.nivel_educativo),
    profesion: strDe(e.profesion),
    temas_a_profundizar: strDe(e.temas_a_profundizar),
    premios_gustaria_recibir: strDe(e.premios_gustaria_recibir),
    propositos_familiares: strDe(e.propositos_familiares),
    propositos_financieros: strDe(e.propositos_financieros),
    propositos_diversion: strDe(e.propositos_diversion),
    propositos_salud: strDe(e.propositos_salud),
    propositos_competencias: strDe(e.propositos_competencias),
    numero_mascotas: e.numero_mascotas != null ? String(e.numero_mascotas) : '',
    info_mascotas: strDe(e.info_mascotas),
    acepto_terminos_y_condiciones: Boolean(e.acepto_terminos_y_condiciones ?? true),
  };
}

function payloadContactoMovilidad(c: FormContacto, numero_documento: string | null) {
  return {
    numero_documento,
    tipo_documento: c.tipo_documento,
    nombre_completo: c.nombre_completo,
    genero: c.genero,
    fecha_nacimiento: c.fecha_nacimiento,
    celular: c.celular,
    telefono: c.telefono || null,
    email: c.email || null,
    direccion: c.direccion,
    departamento: c.departamento,
    ciudad: c.ciudad,
    comisionista_programa_id: PROGRAMA_MOVILIDAD_ID,
    comisionista_subprograma_id: null,
    cod_canales: c.cod_canales !== '' ? Number(c.cod_canales) : null,
    cod_oficinas: c.cod_oficinas !== '' ? Number(c.cod_oficinas) : null,
    acepto_habeas_data: 1 as const,
    incentivos: c.incentivos,
    estado: c.estado as 0 | 1,
    firma_contrato: c.firma_contrato,
    banco: c.banco,
    tipo_de_cuenta: c.tipo_de_cuenta || null,
    numero_de_cuenta: c.numero_de_cuenta || null,
    requiere_comision: c.requiere_comision,
  };
}

function payloadTributarioMovilidad(t: FormTributario, numero_documento: string | null) {
  return {
    numero_documento,
    eps: t.eps,
    afp: t.afp,
    arl: t.arl,
    contratacion_personal: boolToBit(t.contratacion_personal),
    regimen_iva: boolToBit(t.regimen_iva),
  };
}

function payloadEmocionalMovilidad(e: FormEmocional, numero_documento: string | null) {
  return {
    numero_documento,
    con_quien_vives: e.con_quien_vives || null,
    estado_civil: e.estado_civil || null,
    numero_hijos: e.numero_hijos || null,
    info_hijos: e.info_hijos || null,
    hobbies: e.hobbies || null,
    nivel_educativo: e.nivel_educativo || null,
    profesion: e.profesion || null,
    temas_a_profundizar: e.temas_a_profundizar || null,
    premios_gustaria_recibir: e.premios_gustaria_recibir || null,
    propositos_familiares: e.propositos_familiares || null,
    propositos_financieros: e.propositos_financieros || null,
    propositos_diversion: e.propositos_diversion || null,
    propositos_salud: e.propositos_salud || null,
    propositos_competencias: e.propositos_competencias || null,
    numero_mascotas: e.numero_mascotas || null,
    info_mascotas: e.info_mascotas || null,
    comisionista_programa_id: PROGRAMA_MOVILIDAD_ID,
    acepto_terminos_y_condiciones: 1 as const,
  };
}

function validarTributarioMovilidad(c: FormContacto, t: FormTributario): string | null {
  if (c.requiere_comision === null) return 'Debe indicar si el asesor trabaja Con Comisión o Sin Comisión';
  if (c.requiere_comision === true) {
    if (t.eps === null || t.eps === NO_COMISION_EPS) return 'Con Comisión: debe seleccionar una EPS distinta a NO COMISION';
    if (t.afp === null || t.afp === NO_COMISION_AFP) return 'Con Comisión: debe seleccionar un Fondo de Pensiones distinto a NO COMISION';
    if (t.arl === null || t.arl === NO_COMISION_ARL) return 'Con Comisión: debe seleccionar una ARL distinta a NO COMISION';
  }
  if (c.numero_de_cuenta && c.numero_de_cuenta !== c.numero_de_cuenta_verifica) {
    return 'Los números de cuenta no coinciden';
  }
  return null;
}

function documentosTributariosAEliminar(
  t: FormTributario,
  docEps: { did: number } | null | undefined,
  docAfp: { did: number } | null | undefined,
  docArl: { did: number } | null | undefined,
): number[] {
  const ids: number[] = [];
  if (t.eps === NO_COMISION_EPS && docEps) ids.push(docEps.did);
  if (t.afp === NO_COMISION_AFP && docAfp) ids.push(docAfp.did);
  if (t.arl === NO_COMISION_ARL && docArl) ids.push(docArl.did);
  return ids;
}

function detalleError(err: unknown, fallback: string): string {
  const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
  if (Array.isArray(msg)) return msg.join(' | ');
  if (typeof msg === 'string' && msg) return msg;
  if (err instanceof Error && err.message) return err.message;
  return fallback;
}

function BotonGuardar({ pending, disabled }: { pending: boolean; disabled: boolean }) {
  return (
    <Button type="submit" variant="danger" disabled={disabled}>
      {pending ? <Spinner size="sm" className="me-2" /> : <i className="bi bi-check-circle me-2" />}
      Guardar
    </Button>
  );
}

function badgeCount(s: string): number | null {
  return countSelections(s) || null;
}

function docPorTipo<T extends { tipo: number }>(docs: T[] | undefined, tipo: number): T | null {
  return docs?.find((d) => d.tipo === tipo) ?? null;
}

export function PerfilMovilidadPage() {
  const location = useLocation();
  const [tab, setTab] = useState<PerfilTab>(() => tabFromHash(location.hash) ?? 'contacto');

  useEffect(() => {
    const next: PerfilTab | null = tabFromHash(location.hash);
    if (next) setTab(next);
  }, [location.hash]);
  const [contacto, setContacto] = useState<FormContacto>(initContacto);
  const [tributario, setTributario] = useState<FormTributario>(initTributario);
  const [emocional, setEmocional] = useState<FormEmocional>(initEmocional);
  const [error, setError] = useState('');
  const [okMsg, setOkMsg] = useState('');
  const [datosListos, setDatosListos] = useState(false);

  const savedEps = useRef<number | null>(null);
  const savedAfp = useRef<number | null>(null);
  const savedArl = useRef<number | null>(null);

  const miDocumento = useAuthStore((s) => s.user?.username) ?? null;
  const detalle = useMiDetalleMovilidad();
  const guardarContacto = useGuardarMiContactoMovilidad();
  const guardarTributario = useGuardarMiTributarioMovilidad();
  const guardarEmocional = useGuardarMiEmocionalMovilidad();

  const selectedDid = contacto.departamento ? Number(contacto.departamento) : null;

  const { data: departamentos } = useQuery({
    queryKey: ['departamentos'],
    queryFn: () => apiClient.get<{ did: number; departamento: string }[]>('/ubicaciones/departamentos').then(r => r.data),
  });

  const { data: ciudades } = useQuery({
    queryKey: ['ciudades', selectedDid],
    queryFn: () => apiClient.get<{ cid: number; ciudad: string }[]>(`/ubicaciones/ciudades/${selectedDid}`).then(r => r.data),
    enabled: !!selectedDid,
  });

  const { data: canales } = useQuery({
    queryKey: ['canales-movilidad'],
    queryFn: () => apiClient.get<{ cod_canales: number; nom_canales: string; cpid: number }[]>(
      `/referencias/canales?cpid=${PROGRAMA_MOVILIDAD_ID}`,
    ).then(r => r.data),
  });

  const { data: oficinas } = useQuery({
    queryKey: ['oficinas-canal-movilidad', contacto.cod_canales],
    queryFn: () => apiClient.get<{ cod_oficinas: number; nom_oficinas: string | null }[]>(
      `/referencias/oficinas?cod_canales=${contacto.cod_canales}`,
    ).then(r => r.data),
    enabled: contacto.cod_canales !== '',
  });

  const { data: profesiones } = useQuery({
    queryKey: ['profesiones'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/profesiones').then(r => r.data),
  });

  const { data: epsOpciones } = useQuery({
    queryKey: ['eps-catalogo'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/eps').then(r => r.data),
  });

  const { data: afpOpciones } = useQuery({
    queryKey: ['afp-catalogo'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/afp').then(r => r.data),
  });

  const { data: arlOpciones } = useQuery({
    queryKey: ['arl-catalogo'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/arl').then(r => r.data),
  });

  const { data: bancosOpciones } = useQuery({
    queryKey: ['bancos-catalogo'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/bancos').then(r => r.data),
  });

  type DocSelf = { did: number; tipo: number; nombre: string; version: number; estado: string };
  const { data: misDocumentos, refetch: refetchMisDocs } = useQuery({
    queryKey: ['mis-documentos', miDocumento],
    // AP-0055: los PDF propios se leen por /me/documentos (ownership por el JWT). El
    // endpoint /documentos/{doc} es de staff (DOCUMENTOS_MODERAR) y devolvia 403 al
    // comisionista, por lo que la pestana Tributario no mostraba ningun archivo.
    queryFn: () => apiClient.get<DocSelf[]>('/me/documentos').then(r => r.data),
    enabled: !!miDocumento,
  });
  const docEps = docPorTipo(misDocumentos, 7);
  const docAfp = docPorTipo(misDocumentos, 8);
  const docArl = docPorTipo(misDocumentos, 9);
  const docPrepagada = docPorTipo(misDocumentos, 10);
  const docVivienda = docPorTipo(misDocumentos, 11);
  const docPensionVol = docPorTipo(misDocumentos, 12);
  const docAfc = docPorTipo(misDocumentos, 13);
  const docDependientes = docPorTipo(misDocumentos, 14);
  const docCedula = docPorTipo(misDocumentos, 4);
  const docRut = docPorTipo(misDocumentos, 5);
  const [docUploading, setDocUploading] = useState(false);

  // ── TomSelect refs ─────────────────────────────────────────────────────────
  const depSelectRef = useRef<HTMLSelectElement>(null);
  const depTomSelect = useRef<TomSelect | null>(null);
  const ciuSelectRef = useRef<HTMLSelectElement>(null);
  const ciuTomSelect = useRef<TomSelect | null>(null);
  const canalSelectRef = useRef<HTMLSelectElement>(null);
  const canalTomSelect = useRef<TomSelect | null>(null);
  const oficinaSelectRef = useRef<HTMLSelectElement>(null);
  const oficinaTomSelect = useRef<TomSelect | null>(null);
  const profesionSelectRef = useRef<HTMLSelectElement>(null);
  const profesionTomSelect = useRef<TomSelect | null>(null);
  const epsSelectRef = useRef<HTMLSelectElement>(null);
  const epsTs = useRef<TomSelect | null>(null);
  const afpSelectRef = useRef<HTMLSelectElement>(null);
  const afpTs = useRef<TomSelect | null>(null);
  const arlSelectRef = useRef<HTMLSelectElement>(null);
  const arlTs = useRef<TomSelect | null>(null);
  const bancoSelectRef = useRef<HTMLSelectElement>(null);
  const bancoTs = useRef<TomSelect | null>(null);

  // ── Carga de datos del usuario logueado ──────────────────────────────────
  useEffect(() => {
    if (!detalle.data) return;
    const contacto = detalle.data.contacto as Record<string, unknown> | null | undefined;
    if (!contacto) {
      setDatosListos(true);
      return;
    }

    setContacto(mapearContactoMovilidad(contacto));
    setDatosListos(true);
  }, [detalle.data]);

  useEffect(() => {
    const tributario = detalle.data?.tributario as Record<string, unknown> | null | undefined;
    if (!tributario) return;
    setTributario({
      eps: tributario.eps !== null && tributario.eps !== undefined ? Number(tributario.eps) : null,
      afp: tributario.afp !== null && tributario.afp !== undefined ? Number(tributario.afp) : null,
      arl: tributario.arl !== null && tributario.arl !== undefined ? Number(tributario.arl) : null,
      contratacion_personal: tributario.contratacion_personal === null || tributario.contratacion_personal === undefined
        ? null : Boolean(tributario.contratacion_personal),
      regimen_iva: tributario.regimen_iva === null || tributario.regimen_iva === undefined
        ? null : Boolean(tributario.regimen_iva),
    });
  }, [detalle.data]);

  useEffect(() => {
    const emocional = detalle.data?.emocional as Record<string, unknown> | null | undefined;
    if (!emocional) return;
    setEmocional(mapearEmocionalMovilidad(emocional));
  }, [detalle.data]);

  // ── Departamento ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!depSelectRef.current) return;
    depTomSelect.current?.destroy();
    depTomSelect.current = new TomSelect(depSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: (departamentos ?? []).map(dep => ({ value: String(dep.did), text: dep.departamento })),
      items: contacto.departamento ? [contacto.departamento] : [],
      placeholder: 'Seleccione departamento...', maxOptions: null,
      onChange(value: string) {
        setContacto((prev) => prev.departamento === value ? prev : { ...prev, departamento: value, ciudad: '' });
      },
    });
    return () => { depTomSelect.current?.destroy(); depTomSelect.current = null; };
  }, [departamentos, tab, contacto.departamento, datosListos]);

  // ── Ciudad ────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!ciuSelectRef.current) return;
    ciuTomSelect.current?.destroy();
    ciuTomSelect.current = new TomSelect(ciuSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: (ciudades ?? []).map(ciudad => ({ value: String(ciudad.cid), text: ciudad.ciudad })),
      items: contacto.ciudad ? [contacto.ciudad] : [],
      placeholder: contacto.departamento ? 'Seleccione ciudad...' : 'Seleccione un departamento primero',
      maxOptions: null,
      onChange(value: string) {
        setContacto((prev) => prev.ciudad === value ? prev : { ...prev, ciudad: value });
      },
    });
    if (!contacto.departamento) ciuTomSelect.current.lock();
    return () => { ciuTomSelect.current?.destroy(); ciuTomSelect.current = null; };
  }, [ciudades, tab, datosListos]);

  useEffect(() => {
    const ts = ciuTomSelect.current; if (!ts) return;
    if ((ts.getValue() as string) !== (contacto.ciudad || '')) ts.setValue(contacto.ciudad || '', true);
    if (contacto.departamento) ts.unlock(); else ts.lock();
  }, [contacto.ciudad, contacto.departamento]);

  // ── Canal ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!canalSelectRef.current) return;
    const canalOptions = canales ?? [];
    canalTomSelect.current?.destroy();
    canalTomSelect.current = new TomSelect(canalSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: canalOptions.map(canal => ({ value: String(canal.cod_canales), text: canal.nom_canales })),
      items: contacto.cod_canales !== '' ? [String(contacto.cod_canales)] : [],
      placeholder: canalOptions.length === 0 ? 'Sin canales disponibles' : 'Seleccione canal...',
      maxOptions: null,
      onChange(value: string) {
        const numVal = value !== '' ? Number(value) : '';
        setContacto((prev) => prev.cod_canales === numVal ? prev : { ...prev, cod_canales: numVal, cod_oficinas: '' });
      },
    });
    if (canalOptions.length === 0) canalTomSelect.current.lock();
    return () => { canalTomSelect.current?.destroy(); canalTomSelect.current = null; };
  }, [canales, tab, datosListos]);

  useEffect(() => {
    const ts = canalTomSelect.current; if (!ts) return;
    const val = contacto.cod_canales !== '' ? String(contacto.cod_canales) : '';
    if ((ts.getValue() as string) !== val) ts.setValue(val, true);
    const canalOptions = canales ?? [];
    if (canalOptions.length > 0) ts.unlock(); else ts.lock();
  }, [contacto.cod_canales, canales]);

  // ── Oficina ───────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!oficinaSelectRef.current) return;
    const oficinaOptions = (oficinas ?? []).filter(oficina => oficina.nom_oficinas?.trim());
    oficinaTomSelect.current?.destroy();
    oficinaTomSelect.current = new TomSelect(oficinaSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: oficinaOptions.map(oficina => ({ value: String(oficina.cod_oficinas), text: oficina.nom_oficinas! })),
      items: contacto.cod_oficinas !== '' ? [String(contacto.cod_oficinas)] : [],
      placeholder: contacto.cod_canales === '' ? 'Seleccione un canal primero'
        : oficinaOptions.length === 0 ? 'Sin oficinas disponibles' : 'Seleccione oficina...',
      maxOptions: null,
      onChange(value: string) {
        const numVal = value !== '' ? Number(value) : '';
        setContacto((prev) => prev.cod_oficinas === numVal ? prev : { ...prev, cod_oficinas: numVal });
      },
    });
    if (contacto.cod_canales !== '' && oficinaOptions.length > 0) oficinaTomSelect.current.enable();
    else oficinaTomSelect.current.disable();
    return () => { oficinaTomSelect.current?.destroy(); oficinaTomSelect.current = null; };
  }, [oficinas, tab, datosListos]);

  useEffect(() => {
    const ts = oficinaTomSelect.current; if (!ts) return;
    const val = contacto.cod_oficinas !== '' ? String(contacto.cod_oficinas) : '';
    if ((ts.getValue() as string) !== val) ts.setValue(val, true);
    const oficinaOptions = (oficinas ?? []).filter(oficina => oficina.nom_oficinas?.trim());
    if (contacto.cod_canales !== '' && oficinaOptions.length > 0) ts.enable();
    else ts.disable();
  }, [contacto.cod_oficinas, contacto.cod_canales, oficinas]);

  // ── Banco ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!bancoSelectRef.current || !bancosOpciones?.length) return;
    bancoTs.current?.destroy();
    bancoTs.current = new TomSelect(bancoSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: bancosOpciones.map(opcion => ({ value: String(opcion.tid), text: opcion.nombre })),
      items: contacto.banco !== null ? [String(contacto.banco)] : [],
      placeholder: 'Seleccione banco...', maxOptions: null,
      onChange(value: string) {
        const numVal = value !== '' ? Number(value) : null;
        setContacto((prev) => prev.banco === numVal ? prev : { ...prev, banco: numVal });
      },
    });
    return () => { bancoTs.current?.destroy(); bancoTs.current = null; };
  }, [bancosOpciones, tab]);

  useEffect(() => {
    const ts = bancoTs.current; if (!ts) return;
    const wanted = contacto.banco !== null ? String(contacto.banco) : '';
    if ((ts.getValue() as string) !== wanted) ts.setValue(wanted, true);
  }, [contacto.banco]);

  // ── Profesión ─────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!profesionSelectRef.current || !profesiones?.length) return;
    profesionTomSelect.current?.destroy();
    profesionTomSelect.current = new TomSelect(profesionSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: profesiones.map(prof => ({ value: String(prof.tid), text: prof.nombre })),
      items: emocional.profesion ? [emocional.profesion] : [],
      placeholder: 'Seleccione o busque una profesión...',
      maxOptions: null,
      onChange(value: string) {
        setEmocional(prev => prev.profesion === value ? prev : { ...prev, profesion: value });
      },
    });
    return () => { profesionTomSelect.current?.destroy(); profesionTomSelect.current = null; };
  }, [profesiones, tab]);

  useEffect(() => {
    const ts = profesionTomSelect.current;
    if (!ts) return;
    const current = ts.getValue() as string;
    if (current !== (emocional.profesion || '')) ts.setValue(emocional.profesion || '', true);
  }, [emocional.profesion]);

  // ── EPS ───────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!epsSelectRef.current || !epsOpciones?.length) return;
    epsTs.current?.destroy();
    epsTs.current = new TomSelect(epsSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: epsOpciones.map(opcion => ({ value: String(opcion.tid), text: opcion.nombre })),
      items: tributario.eps !== null ? [String(tributario.eps)] : [],
      placeholder: 'Seleccione EPS...', maxOptions: null,
      onChange(value: string) {
        const numVal = value !== '' ? Number(value) : null;
        setTributario((prev) => prev.eps === numVal ? prev : { ...prev, eps: numVal });
      },
    });
    if (contacto.requiere_comision === false) epsTs.current.disable();
    return () => { epsTs.current?.destroy(); epsTs.current = null; };
  }, [epsOpciones, tab]);

  useEffect(() => {
    const ts = epsTs.current; if (!ts) return;
    const wanted = tributario.eps !== null ? String(tributario.eps) : '';
    if ((ts.getValue() as string) !== wanted) ts.setValue(wanted, true);
    if (contacto.requiere_comision === false) ts.disable(); else ts.enable();
  }, [tributario.eps, contacto.requiere_comision]);

  // ── AFP ───────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!afpSelectRef.current || !afpOpciones?.length) return;
    afpTs.current?.destroy();
    afpTs.current = new TomSelect(afpSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: afpOpciones.map(opcion => ({ value: String(opcion.tid), text: opcion.nombre })),
      items: tributario.afp !== null ? [String(tributario.afp)] : [],
      placeholder: 'Seleccione Fondo de pensiones...', maxOptions: null,
      onChange(value: string) {
        const numVal = value !== '' ? Number(value) : null;
        setTributario((prev) => prev.afp === numVal ? prev : { ...prev, afp: numVal });
      },
    });
    if (contacto.requiere_comision === false) afpTs.current.disable();
    return () => { afpTs.current?.destroy(); afpTs.current = null; };
  }, [afpOpciones, tab]);

  useEffect(() => {
    const ts = afpTs.current; if (!ts) return;
    const wanted = tributario.afp !== null ? String(tributario.afp) : '';
    if ((ts.getValue() as string) !== wanted) ts.setValue(wanted, true);
    if (contacto.requiere_comision === false) ts.disable(); else ts.enable();
  }, [tributario.afp, contacto.requiere_comision]);

  // ── ARL ───────────────────────────────────────────────────────────────────
  useEffect(() => {
    if (!arlSelectRef.current || !arlOpciones?.length) return;
    arlTs.current?.destroy();
    arlTs.current = new TomSelect(arlSelectRef.current, {
      valueField: 'value', labelField: 'text', searchField: ['text'],
      options: arlOpciones.map(opcion => ({ value: String(opcion.tid), text: opcion.nombre })),
      items: tributario.arl !== null ? [String(tributario.arl)] : [],
      placeholder: 'Seleccione ARL...', maxOptions: null,
      onChange(value: string) {
        const numVal = value !== '' ? Number(value) : null;
        setTributario((prev) => prev.arl === numVal ? prev : { ...prev, arl: numVal });
      },
    });
    if (contacto.requiere_comision === false) arlTs.current.disable();
    return () => { arlTs.current?.destroy(); arlTs.current = null; };
  }, [arlOpciones, tab]);

  useEffect(() => {
    const ts = arlTs.current; if (!ts) return;
    const wanted = tributario.arl !== null ? String(tributario.arl) : '';
    if ((ts.getValue() as string) !== wanted) ts.setValue(wanted, true);
    if (contacto.requiere_comision === false) ts.disable(); else ts.enable();
  }, [tributario.arl, contacto.requiere_comision]);

  // ── Mantener savedEps/AFP/ARL con el último valor real (no NO_COMISION) ──
  useEffect(() => {
    if (tributario.eps !== null && tributario.eps !== NO_COMISION_EPS) savedEps.current = tributario.eps;
  }, [tributario.eps]);
  useEffect(() => {
    if (tributario.afp !== null && tributario.afp !== NO_COMISION_AFP) savedAfp.current = tributario.afp;
  }, [tributario.afp]);
  useEffect(() => {
    if (tributario.arl !== null && tributario.arl !== NO_COMISION_ARL) savedArl.current = tributario.arl;
  }, [tributario.arl]);

  // ── Sin/Con Comisión — sincroniza eps/afp/arl con NO COMISION ────────────
  useEffect(() => {
    if (contacto.requiere_comision === false) {
      setTributario((prev) => ({ ...prev, eps: NO_COMISION_EPS, afp: NO_COMISION_AFP, arl: NO_COMISION_ARL }));
    } else if (contacto.requiere_comision === true) {
      setTributario((prev) => ({ ...prev, eps: savedEps.current, afp: savedAfp.current, arl: savedArl.current }));
    }
  }, [contacto.requiere_comision]);

  // ── Auto-dismiss de mensajes ──────────────────────────────────────────────
  useEffect(() => {
    if (!okMsg) return;
    const id = setTimeout(() => setOkMsg(''), 10_000);
    return () => clearTimeout(id);
  }, [okMsg]);
  useEffect(() => {
    if (!error) return;
    const id = setTimeout(() => setError(''), 10_000);
    return () => clearTimeout(id);
  }, [error]);

  const setEmo = <K extends keyof FormEmocional>(k: K, v: FormEmocional[K]) =>
    setEmocional(prev => ({ ...prev, [k]: v }));

  // ── Submit handlers ───────────────────────────────────────────────────────
  async function handleGuardarContacto(e: React.FormEvent) {
    e.preventDefault();
    setError(''); setOkMsg('');
    if (!contacto.departamento) { setError('Debe seleccionar un Departamento'); return; }
    if (!contacto.ciudad) { setError('Debe seleccionar una ciudad'); return; }
    if (!contacto.acepto_habeas_data) { setError('Debe aceptar el habeas data'); return; }
    if (contacto.estado === null) { setError('Debe seleccionar el estado del asesor'); return; }
    try {
      const result = await guardarContacto.mutateAsync(
        payloadContactoMovilidad(contacto, contacto.numero_documento || miDocumento),
      );
      setOkMsg('Datos de contacto guardados.');
      if (result?.numero_documento) detalle.refetch();
    } catch (err: unknown) {
      setError(detalleError(err, 'Error en paso 1'));
    }
  }

  async function handleGuardarTributario(e: React.FormEvent) {
    e.preventDefault();
    setError(''); setOkMsg('');
    const mensaje = validarTributarioMovilidad(contacto, tributario);
    if (mensaje) { setError(mensaje); return; }
    const docNum = contacto.numero_documento || miDocumento;
    try {
      // Paso 1: re-guardar contacto para persistir requiere_comision/banco/cuenta antes del tributario
      await guardarContacto.mutateAsync(payloadContactoMovilidad(contacto, docNum));
      await guardarTributario.mutateAsync(payloadTributarioMovilidad(tributario, docNum));
      // Eliminar PDFs cuya entidad quedó en NO COMISION (alineado con AsesorMovilidadPage).
      const idsAEliminar = documentosTributariosAEliminar(tributario, docEps, docAfp, docArl);
      if (idsAEliminar.length > 0) {
        await Promise.all(
          idsAEliminar.map((id) => apiClient.delete(`/me/documentos/${id}`)),
        );
        void refetchMisDocs();
      }
      setOkMsg('Datos tributarios guardados.');
      detalle.refetch();
    } catch (err: unknown) {
      setError(detalleError(err, 'Error en paso 2'));
    }
  }

  async function handleGuardarEmocional(e: React.FormEvent) {
    e.preventDefault();
    setError(''); setOkMsg('');
    if (!emocional.acepto_terminos_y_condiciones) { setError('Debe aceptar los términos y condiciones'); return; }
    try {
      await guardarEmocional.mutateAsync(
        payloadEmocionalMovilidad(emocional, contacto.numero_documento || miDocumento),
      );
      setOkMsg('Perfil emocional guardado.');
      detalle.refetch();
    } catch (err: unknown) {
      setError(detalleError(err, 'Error en paso 3'));
    }
  }

  const isBusy = guardarContacto.isPending || guardarTributario.isPending || guardarEmocional.isPending;
  const cargando = !datosListos || detalle.isLoading;

  return (
    <div>
      <PageHeader
        title="Mi Perfil — Comisionista Movilidad"
        subtitle="Edita tus datos de contacto, tributarios y emocionales"
        icon="bi-person-circle"
      />

      <Card className="shadow-sm" style={{ border: 'none' }}>
        <Card.Header className="bg-white border-0 pt-3">
          <Nav variant="tabs" activeKey={tab} onSelect={(k) => k && setTab(k as PerfilTab)}>
            <Nav.Item>
              <Nav.Link eventKey="contacto">
                <i className="bi bi-person me-2" />Contacto
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="tributario">
                <i className="bi bi-bank me-2" />Tributario
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="emocional">
                <i className="bi bi-heart me-2" />Perfil Emocional
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="documentacion">
                <i className="bi bi-folder2-open me-2" />Documentación
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>

        <Card.Body className="p-4">
          {cargando ? (
            <div className="text-center py-5"><Spinner animation="border" variant="danger" /></div>
          ) : (
            <>
              {error && <Alert variant="danger" onClose={() => setError('')} dismissible>{error}</Alert>}
              {okMsg && <Alert variant="success" onClose={() => setOkMsg('')} dismissible>{okMsg}</Alert>}

              {/* ── Tab: Contacto ── */}
              {tab === 'contacto' && (() => (
                <Form onSubmit={handleGuardarContacto}>
                  <h6 className="mb-3 fw-semibold text-danger">
                    <i className="bi bi-person-lines-fill me-2" />Información de Contacto
                  </h6>
                  <Row className="g-3">
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-person-badge me-1 text-danger" />Tipo Documento</Form.Label>
                        <Form.Select value={contacto.tipo_documento} onChange={e => setContacto((prev) => ({ ...prev,tipo_documento: e.target.value }))}>
                          <option value="CC">CC</option>
                          <option value="CE">CE</option>
                          <option value="F&I">F&amp;I</option>
                          <option value="GC">GC</option>
                          <option value="PEP">PEP</option>
                          <option value="PPT">PPT</option>
                          <option value="VDA">VDA</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-hash me-1 text-danger" />Número Documento</Form.Label>
                        <Form.Control value={contacto.numero_documento} disabled />
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-person me-1 text-danger" />Nombre Completo *</Form.Label>
                        <Form.Control required value={contacto.nombre_completo} onChange={e => setContacto((prev) => ({ ...prev,nombre_completo: e.target.value }))} />
                      </Form.Group>
                    </Col>
                    <Col md={3}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-gender-ambiguous me-1 text-danger" />Género *</Form.Label>
                        <Form.Select required value={contacto.genero} onChange={e => setContacto((prev) => ({ ...prev,genero: e.target.value }))}>
                          <option value="">Seleccione...</option>
                          <option>Masculino</option><option>Femenino</option><option>Otro</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={3}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-calendar-date me-1 text-danger" />Fecha Nacimiento *</Form.Label>
                        <Form.Control required type="date" value={contacto.fecha_nacimiento} onChange={e => setContacto((prev) => ({ ...prev,fecha_nacimiento: e.target.value }))} />
                      </Form.Group>
                    </Col>
                    <Col md={3}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-phone me-1 text-danger" />Celular * (10 dígitos)</Form.Label>
                        <Form.Control required inputMode="numeric" value={contacto.celular} onChange={e => setContacto((prev) => ({ ...prev,celular: e.target.value.replace(/\D/g, '') }))} maxLength={10} />
                      </Form.Group>
                    </Col>
                    <Col md={3}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-telephone me-1 text-danger" />Teléfono</Form.Label>
                        <Form.Control inputMode="numeric" value={contacto.telefono} onChange={e => setContacto((prev) => ({ ...prev,telefono: e.target.value.replace(/\D/g, '') }))} />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-envelope me-1 text-danger" />Correo electrónico</Form.Label>
                        <Form.Control type="email" value={contacto.email} onChange={e => setContacto((prev) => ({ ...prev,email: e.target.value }))} placeholder="ejemplo@correo.com" maxLength={254} />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-geo-alt me-1 text-danger" />Dirección *</Form.Label>
                        <Form.Control required value={contacto.direccion} onChange={e => setContacto((prev) => ({ ...prev,direccion: e.target.value }))} />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-map me-1 text-danger" />Departamento *</Form.Label>
                        <select ref={depSelectRef} className="form-select" />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-pin-map me-1 text-danger" />Ciudad *</Form.Label>
                        <select ref={ciuSelectRef} className="form-select" />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-broadcast me-1 text-danger" />Canal</Form.Label>
                        <select ref={canalSelectRef} className="form-select" />
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-building me-1 text-danger" />Oficina</Form.Label>
                        <select ref={oficinaSelectRef} className="form-select" />
                      </Form.Group>
                    </Col>
                    <Col xs={12} md={6}>
                      <Form.Group>
                        <div>
                          <EstadoSwitch
                            id="perfil-movilidad-estado"
                            checked={contacto.estado === 1}
                            onChange={(checked) => setContacto((prev) => ({ ...prev, estado: checked ? 1 : 0 }))}
                            disabled
                          />
                        </div>
                      </Form.Group>
                    </Col>
                    <Col xs={12}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-file-earmark-check me-1 text-danger" />Firma de Contrato</Form.Label>
                        <div className="d-flex gap-4 flex-wrap">
                          <Form.Check type="radio" id="perfil-mov-firma-si" name="firma_contrato-perfil-mov" label="El contrato fue firmado" checked={contacto.firma_contrato === true} onChange={() => setContacto((prev) => ({ ...prev,firma_contrato: true }))} />
                          <Form.Check type="radio" id="perfil-mov-firma-no" name="firma_contrato-perfil-mov" label="No requiere firma de Contrato" checked={contacto.firma_contrato === false} onChange={() => setContacto((prev) => ({ ...prev,firma_contrato: false }))} />
                        </div>
                      </Form.Group>
                    </Col>
                    <Col xs={12}>
                      <Form.Check type="checkbox" id="perfil-mov-habeas-data" label="Acepto el tratamiento de datos personales (Habeas Data) *" checked={contacto.acepto_habeas_data} onChange={e => setContacto((prev) => ({ ...prev,acepto_habeas_data: e.target.checked }))} />
                    </Col>
                    <Col xs={12}>
                      <Form.Check type="checkbox" id="perfil-mov-incentivos" label="Tiene Incentivos" checked={contacto.incentivos} onChange={e => setContacto((prev) => ({ ...prev,incentivos: e.target.checked }))} disabled />
                    </Col>
                  </Row>
                  <div className="d-flex justify-content-end mt-4">
                    <BotonGuardar pending={guardarContacto.isPending} disabled={isBusy} />
                  </div>
                </Form>
              ))()}

              {/* ── Tab: Tributario ── */}
              {tab === 'tributario' && (() => (
                <Form onSubmit={handleGuardarTributario}>
                  <h6 className="mb-3 fw-semibold text-danger">
                    <i className="bi bi-bank me-2" />Información Tributaria
                  </h6>
                  <Row className="g-3">
                    <Col xs={12}>
                      <div className="border rounded p-3">
                        <p className="mb-3" style={{ fontWeight: 500 }}>
                          1. Para realizar su actividad de comisionista usted tuvo que contratar a más de una persona durante el último año por 6 meses o más?
                        </p>
                        <div className="d-flex gap-4">
                          <Form.Check type="radio" id="perfil-mov-contratacion-no" name="contratacion_personal-perfil-mov" label="No" checked={tributario.contratacion_personal === false} onChange={() => setTributario((prev) => ({ ...prev,contratacion_personal: false }))} />
                          <Form.Check type="radio" id="perfil-mov-contratacion-si" name="contratacion_personal-perfil-mov" label="Sí" checked={tributario.contratacion_personal === true} onChange={() => setTributario((prev) => ({ ...prev,contratacion_personal: true }))} />
                        </div>
                      </div>
                    </Col>
                    <Col xs={12}>
                      <div className="border rounded p-3">
                        <p className="mb-3" style={{ fontWeight: 500 }}>2. ¿A qué régimen de IVA pertenece?</p>
                        <div className="d-flex gap-4">
                          <Form.Check type="radio" id="perfil-mov-regimen-simplificado" name="regimen_iva-perfil-mov" label="No responsable de IVA (Simplificado)" checked={tributario.regimen_iva === false} onChange={() => setTributario((prev) => ({ ...prev,regimen_iva: false }))} />
                          <Form.Check type="radio" id="perfil-mov-regimen-comun" name="regimen_iva-perfil-mov" label="Responsable de IVA (Común)" checked={tributario.regimen_iva === true} onChange={() => setTributario((prev) => ({ ...prev,regimen_iva: true }))} />
                        </div>
                      </div>
                    </Col>

                    {/* ── EPS / AFP / ARL ── */}
                    <Col xs={12}>
                      <div className="border rounded p-3">
                        <p className="mb-3" style={{ fontWeight: 500 }}>
                          3. Autorizo a la compañía CADENA SA, identificada con Nit 890.930.534-0 para que efectúe los descuentos correspondientes a los aportes en seguridad social, en salud, pensión y riesgos laborales y realice los pagos respectivos por cuenta mía a las siguientes entidades:
                        </p>
                        <div className={`rounded p-2 mb-3 ${contacto.requiere_comision === null ? 'bg-warning-subtle border border-warning' : 'bg-light border'}`}>
                          <p className="mb-2 fw-semibold small">
                            <i className="bi bi-toggles me-2" />¿Trabajas con o sin comisión?
                          </p>
                          <div className="d-flex gap-4">
                            <Form.Check type="radio" id="perfil-mov-comision-con" name="requiere_comision-perfil-mov" label="Con Comisión" checked={contacto.requiere_comision === true} onChange={() => setContacto((prev) => ({ ...prev,requiere_comision: true }))} />
                            <Form.Check type="radio" id="perfil-mov-comision-sin" name="requiere_comision-perfil-mov" label="Sin Comisión" checked={contacto.requiere_comision === false} onChange={() => setContacto((prev) => ({ ...prev,requiere_comision: false }))} />
                          </div>
                        </div>

                        <Form.Group className="mb-3">
                          <Form.Label className="fw-semibold">EPS</Form.Label>
                          <DocZone
                            tipoLabel="EPS" tipoPrefix="EPS" tipo={7}
                            numeroDocumento={contacto.numero_documento}
                            existingDoc={docEps}
                            onUploaded={() => { void refetchMisDocs(); }}
                            onDeleted={() => { void refetchMisDocs(); }}
                            onUploadingChange={setDocUploading}
                            disabled={tributario.eps === null || tributario.eps === NO_COMISION_EPS}
                          >
                            <select ref={epsSelectRef} className="form-select" />
                          </DocZone>
                        </Form.Group>
                        <Form.Group className="mb-3">
                          <Form.Label className="fw-semibold">Fondo de pensiones</Form.Label>
                          <DocZone
                            tipoLabel="AFP" tipoPrefix="AFP" tipo={8}
                            numeroDocumento={contacto.numero_documento}
                            existingDoc={docAfp}
                            onUploaded={() => { void refetchMisDocs(); }}
                            onDeleted={() => { void refetchMisDocs(); }}
                            onUploadingChange={setDocUploading}
                            disabled={tributario.afp === null || tributario.afp === NO_COMISION_AFP}
                          >
                            <select ref={afpSelectRef} className="form-select" />
                          </DocZone>
                        </Form.Group>
                        <Form.Group className="mb-0">
                          <Form.Label className="fw-semibold">ARL</Form.Label>
                          <DocZone
                            tipoLabel="ARL" tipoPrefix="ARL" tipo={9}
                            numeroDocumento={contacto.numero_documento}
                            existingDoc={docArl}
                            onUploaded={() => { void refetchMisDocs(); }}
                            onDeleted={() => { void refetchMisDocs(); }}
                            onUploadingChange={setDocUploading}
                            disabled={tributario.arl === null || tributario.arl === NO_COMISION_ARL}
                          >
                            <select ref={arlSelectRef} className="form-select" />
                          </DocZone>
                        </Form.Group>
                      </div>
                    </Col>

                    {/* ── Banco / Cuenta ── */}
                    <Col xs={12}>
                      <div className="border rounded p-3">
                        <p className="mb-3" style={{ fontWeight: 500 }}>4. Información bancaria para pago de comisiones:</p>
                        <Form.Group className="mb-3">
                          <Form.Label className="fw-semibold">Banco</Form.Label>
                          <select ref={bancoSelectRef} className="form-select" />
                        </Form.Group>
                        <Form.Group className="mb-3">
                          <Form.Label className="fw-semibold">Tipo de cuenta</Form.Label>
                          <Form.Select value={contacto.tipo_de_cuenta} onChange={e => setContacto((prev) => ({ ...prev,tipo_de_cuenta: e.target.value }))}>
                            <option value="">Seleccione...</option>
                            <option value="Cuenta de ahorros">Cuenta de ahorros</option>
                            <option value="Cuenta corriente">Cuenta corriente</option>
                          </Form.Select>
                        </Form.Group>
                        <Form.Group className="mb-3">
                          <Form.Label className="fw-semibold">Número de cuenta</Form.Label>
                          <Form.Control value={contacto.numero_de_cuenta} onChange={e => setContacto((prev) => ({ ...prev,numero_de_cuenta: e.target.value.replace(/\D/g, '') }))} placeholder="Número de cuenta" inputMode="numeric" maxLength={30} />
                        </Form.Group>
                        <Form.Group className="mb-0">
                          <Form.Label className="fw-semibold">Verifica número de cuenta</Form.Label>
                          <Form.Control value={contacto.numero_de_cuenta_verifica} onChange={e => setContacto((prev) => ({ ...prev,numero_de_cuenta_verifica: e.target.value.replace(/\D/g, '') }))} placeholder="Repite el número de cuenta" inputMode="numeric" maxLength={30} />
                          {contacto.numero_de_cuenta_verifica !== '' && contacto.numero_de_cuenta !== contacto.numero_de_cuenta_verifica && (
                            <Form.Text className="text-danger">
                              <i className="bi bi-exclamation-circle me-1" />Los números de cuenta no coinciden
                            </Form.Text>
                          )}
                        </Form.Group>
                      </div>
                    </Col>
                    {/* ── Beneficios tributarios (certificados) ── */}
                    <Col xs={12}>
                      <div className="border rounded p-3">
                        <p className="mb-3" style={{ fontWeight: 500 }}>
                          5. Para efectos de obtener los beneficios tributarios me permito adjuntar los siguientes certificados:
                        </p>
                        <Row className="g-3">
                          <Col xs={12} md={6}>
                            <CertificadoRow
                              label="Prepagada" tipo={10} tipoPrefix="PREPAGADA"
                              numeroDocumento={contacto.numero_documento}
                              existingDoc={docPrepagada}
                              onUploaded={() => { void refetchMisDocs(); }}
                              onDeleted={() => { void refetchMisDocs(); }}
                              onUploadingChange={setDocUploading}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <CertificadoRow
                              label="Certificado intereses de vivienda" tipo={11} tipoPrefix="VIVIENDA"
                              numeroDocumento={contacto.numero_documento}
                              existingDoc={docVivienda}
                              onUploaded={() => { void refetchMisDocs(); }}
                              onDeleted={() => { void refetchMisDocs(); }}
                              onUploadingChange={setDocUploading}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <CertificadoRow
                              label="Dependientes" tipo={14} tipoPrefix="DEPENDIENTES"
                              numeroDocumento={contacto.numero_documento}
                              existingDoc={docDependientes}
                              onUploaded={() => { void refetchMisDocs(); }}
                              onDeleted={() => { void refetchMisDocs(); }}
                              onUploadingChange={setDocUploading}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <CertificadoRow
                              label="Pensión voluntaria" tipo={12} tipoPrefix="PENSIONVOL"
                              numeroDocumento={contacto.numero_documento}
                              existingDoc={docPensionVol}
                              onUploaded={() => { void refetchMisDocs(); }}
                              onDeleted={() => { void refetchMisDocs(); }}
                              onUploadingChange={setDocUploading}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <CertificadoRow
                              label="AFC" tipo={13} tipoPrefix="AFC"
                              numeroDocumento={contacto.numero_documento}
                              existingDoc={docAfc}
                              onUploaded={() => { void refetchMisDocs(); }}
                              onDeleted={() => { void refetchMisDocs(); }}
                              onUploadingChange={setDocUploading}
                            />
                          </Col>
                        </Row>
                      </div>
                    </Col>
                    {/* ── Documentos de usuario ── */}
                    <Col xs={12}>
                      <div className="border rounded p-3">
                        <p className="mb-3" style={{ fontWeight: 500 }}>
                          Documentos de usuario:
                        </p>
                        <Row className="g-3">
                          <Col xs={12} md={6}>
                            <CertificadoRow
                              label="Fotocopia cédula de ciudadanía" tipo={4} tipoPrefix="CC"
                              numeroDocumento={contacto.numero_documento}
                              existingDoc={docCedula}
                              onUploaded={() => { void refetchMisDocs(); }}
                              onDeleted={() => { void refetchMisDocs(); }}
                              onUploadingChange={setDocUploading}
                            />
                          </Col>
                          <Col xs={12} md={6}>
                            <CertificadoRow
                              label="RUT" tipo={5} tipoPrefix="RUT"
                              numeroDocumento={contacto.numero_documento}
                              existingDoc={docRut}
                              onUploaded={() => { void refetchMisDocs(); }}
                              onDeleted={() => { void refetchMisDocs(); }}
                              onUploadingChange={setDocUploading}
                            />
                          </Col>
                        </Row>
                      </div>
                    </Col>
                  </Row>
                  <div className="d-flex justify-content-end mt-4">
                    <BotonGuardar pending={guardarTributario.isPending} disabled={isBusy || docUploading} />
                  </div>
                </Form>
              ))()}
              {/* ── Tab: Perfil Emocional ── */}
              {tab === 'emocional' && (() => (
                <Form onSubmit={handleGuardarEmocional}>
                  <h6 className="mb-3 fw-semibold text-danger">
                    <i className="bi bi-emoji-smile me-2" />Perfil Emocional
                  </h6>
                  <Row className="g-3">
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-heart me-1 text-danger" />Estado Civil</Form.Label>
                        <Form.Select value={emocional.estado_civil} onChange={e => setEmo('estado_civil', e.target.value)}>
                          <option value="">Seleccione...</option>
                          <option>Soltero/a</option><option>Casado/a</option><option>Unión libre</option>
                          <option>Divorciado/a</option><option>Viudo/a</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col xs={12}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-person-hearts me-1 text-danger" />¿Tiene hijos?</Form.Label>
                        <TieneHijosSelector numeroHijos={emocional.numero_hijos} infoHijos={emocional.info_hijos} onChange={(numero, info) => setEmocional((prev) => ({ ...prev,numero_hijos: numero, info_hijos: info }))} />
                      </Form.Group>
                    </Col>
                    <Col xs={12}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-patch-heart me-1 text-danger" />¿Tiene mascota?</Form.Label>
                        <TieneMascotaSelector numeroMascotas={emocional.numero_mascotas} infoMascotas={emocional.info_mascotas} onChange={(num, info) => setEmocional((prev) => ({ ...prev,numero_mascotas: num, info_mascotas: info }))} />
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-mortarboard me-1 text-danger" />Nivel Educativo</Form.Label>
                        <Form.Select value={emocional.nivel_educativo} onChange={e => setEmo('nivel_educativo', e.target.value)}>
                          <option value="">Seleccione...</option>
                          <option>Bachiller</option><option>Técnico</option><option>Tecnológico</option>
                          <option>Universitario</option><option>Postgrado</option><option>Doctorado</option>
                        </Form.Select>
                      </Form.Group>
                    </Col>
                    <Col md={4}>
                      <Form.Group>
                        <Form.Label><i className="bi bi-briefcase me-1 text-danger" />Profesión</Form.Label>
                        <select ref={profesionSelectRef} className="form-select" />
                      </Form.Group>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="¿Con quién vives?" icon="bi-people-fill" color="red" size="medium" subtitle="Selecciona una o varias opciones" badge={badgeCount(emocional.con_quien_vives)}>
                        <ConQuienVivesSelector value={emocional.con_quien_vives} onChange={next => setEmo('con_quien_vives', next)} />
                      </MetroTileToggle>
                    </Col>                    
                    <Col xs={12}>
                      <MetroTileToggle title="Premios que te gustaría recibir" icon="bi-trophy-fill" color="gold" size="medium" subtitle="Marca todos los premios de tu interés" badge={badgeCount(emocional.premios_gustaria_recibir)}>
                        <PremiosSelector value={emocional.premios_gustaria_recibir} onChange={next => setEmo('premios_gustaria_recibir', next)} />
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="¿Cuáles son tus Hobbies?" icon="bi-controller" color="teal" size="wide" subtitle="Despliega para elegir hasta 10 hobbies" badge={badgeCount(emocional.hobbies)}>
                        <div className="metro-hobbies-grid">
                          <HobbiesSelector value={emocional.hobbies} onChange={next => setEmo('hobbies', next)} />
                        </div>
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="¿En qué temas te gustaría profundizar o aprender?" icon="bi-book-half" color="blue" size="medium" subtitle="Selecciona los temas de interés" badge={badgeCount(emocional.temas_a_profundizar)}>
                        <TemasProfundizarSelector value={emocional.temas_a_profundizar} onChange={next => setEmo('temas_a_profundizar', next)} />
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="Propósitos con tu Familia" icon="bi-house-heart-fill" color="red" size="medium" subtitle="Marca los propósitos familiares" badge={badgeCount(emocional.propositos_familiares)}>
                        <PropositosFamiliaresSelector value={emocional.propositos_familiares} onChange={next => setEmo('propositos_familiares', next)} />
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="Propósitos Financieros" icon="bi-currency-dollar" color="green" size="medium" subtitle="Selecciona los propósitos financieros" badge={badgeCount(emocional.propositos_financieros)}>
                        <PropositosFinancierosSelector value={emocional.propositos_financieros} onChange={next => setEmo('propositos_financieros', next)} />
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="Propósitos Diversión" icon="bi-joystick" color="yellow" size="wide" subtitle="Despliega para elegir actividades de diversión" badge={badgeCount(emocional.propositos_diversion)}>
                        <div className="metro-twocol-grid">
                          <PropositosDiversionSelector value={emocional.propositos_diversion} onChange={next => setEmo('propositos_diversion', next)} />
                        </div>
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="Propósitos Salud" icon="bi-heart-pulse-fill" color="teal" size="medium" subtitle="Selecciona los propósitos de salud y bienestar" badge={badgeCount(emocional.propositos_salud)}>
                        <PropositosSaludSelector value={emocional.propositos_salud} onChange={next => setEmo('propositos_salud', next)} />
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle title="Propósitos Competencias" icon="bi-award-fill" color="navy" size="wide" subtitle="Despliega para elegir competencias a desarrollar" badge={badgeCount(emocional.propositos_competencias)}>
                        <div className="metro-twocol-grid">
                          <PropositosCompetenciasSelector value={emocional.propositos_competencias} onChange={next => setEmo('propositos_competencias', next)} />
                        </div>
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <Form.Check type="checkbox" id="perfil-mov-terminos" label="Acepto los términos y condiciones *" checked={emocional.acepto_terminos_y_condiciones} onChange={e => setEmo('acepto_terminos_y_condiciones', e.target.checked)} />
                    </Col>
                  </Row>
                  <div className="d-flex justify-content-end mt-4">
                    <BotonGuardar pending={guardarEmocional.isPending} disabled={isBusy} />
                  </div>
                </Form>
              ))()}
              {/* ── Tab: Documentación ── */}
              {tab === 'documentacion' && (() => (
                <div>
                  <h6 className="mb-3 fw-semibold text-danger">
                    <i className="bi bi-folder2-open me-2" />Mis Documentos
                  </h6>
                  <p className="text-muted small mb-3">
                    Aquí puedes consultar y editar el nombre, estado y fecha de los documentos
                    que has cargado. Para subir nuevos archivos utiliza la pestaña Tributario.
                  </p>
                  {miDocumento ? (
                    <MisDocumentos />
                  ) : (
                    <Alert variant="warning" className="mb-0">
                      No se pudo determinar tu número de documento.
                    </Alert>
                  )}
                </div>
              ))()}
            </>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
