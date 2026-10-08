import { type ReactNode, useEffect, useRef, useState } from 'react';
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
  useAsesorMovilidadList,
  useDetalleAsesorMovilidad,
  useFinalizarMovilidad,
  useWizardPaso1Movilidad,
  useWizardPaso2Movilidad,
  useWizardPaso3Movilidad,
} from '../../features/asesor-movilidad/model/useAsesorMovilidad';
import {
  verificarAsesorMovilidadApi,
} from '../../features/asesor-movilidad/model/apiAsesorMovilidad';
import { useCambiarEstadoComisionista } from '../../features/admin-usuarios/model/useAdminUsuarios';
import { DocumentosTab } from './DocumentosTab';
import { useToastContext } from '../../shared/ui/hooks/useToastContext';
import { useMaxUploadBytes } from '../../features/config/model/useUploadLimits';
import { formatBytes } from '../../shared/lib/archivos';
import {
  parseBoolOrNull, parseGenero, parseNumOrNull, parseTipoDoc, refObj, strDe,
} from '../../shared/lib/parseContacto';

const PROGRAMA_MOVILIDAD_ID = 1 as const;

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
const NO_COMISION_EPS = 7848;
const NO_COMISION_AFP = 7846;
const NO_COMISION_ARL = 7847;

type Tab = 'lista' | 'registro' | 'documentos';
type WizardStep = 1 | 2 | 3 | 4;

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
  acepto_habeas_data: false, incentivos: false, estado: 1, firma_contrato: null,
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
  numero_mascotas: '', info_mascotas: '', acepto_terminos_y_condiciones: false,
};

function DocZone({
  tipoLabel, tipoPrefix, tipo, numeroDocumento, existingDoc, onUploaded, onDeleted, onUploadingChange, disabled, children,
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
  const maxBytes = useMaxUploadBytes();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');

  const isDisabled = disabled || uploading || !numeroDocumento;

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: isDisabled,
    onDrop: async (accepted) => {
      if (!accepted.length || !numeroDocumento) return;
      if (accepted[0].size > maxBytes) {
        setUploadError('El archivo excede el tamano limite permitido.');
        toast.error('El archivo excede el tamano limite permitido.', {
          title: 'Error al subir',
          detail: `Tamano maximo permitido: ${formatBytes(maxBytes)}.`,
        });
        return;
      }
      setUploading(true);
      onUploadingChange(true);
      setUploadError('');
      const nombre = `${tipoPrefix}${numeroDocumento}.pdf`;
      const form = new FormData();
      form.append('numero_documento', numeroDocumento);
      form.append('tipo', String(tipo));
      form.append('file', accepted[0], nombre);
      try {
        await apiClient.post('/documentos/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        setOpen(false);
        onUploaded();
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
      await apiClient.delete(`/documentos/${existingDoc.did}`);
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
  const maxBytes = useMaxUploadBytes();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const isDisabled = uploading || !numeroDocumento;

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    disabled: isDisabled,
    onDrop: async (accepted) => {
      if (!accepted.length || !numeroDocumento) return;
      if (accepted[0].size > maxBytes) {
        setRowError('El archivo excede el tamano limite permitido.');
        toast.error('El archivo excede el tamano limite permitido.', {
          title: 'Error al subir',
          detail: `Tamano maximo permitido: ${formatBytes(maxBytes)}.`,
        });
        return;
      }
      setUploading(true);
      onUploadingChange(true);
      setRowError('');
      const nombre = `${tipoPrefix}${numeroDocumento}.pdf`;
      const form = new FormData();
      form.append('numero_documento', numeroDocumento);
      form.append('tipo', String(tipo));
      form.append('file', accepted[0], nombre);
      try {
        await apiClient.post('/documentos/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        onUploaded();
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
      await apiClient.delete(`/documentos/${existingDoc.did}`);
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

function WizardStepper({ step }: { step: WizardStep }) {
  const steps: { label: string; icon: string }[] = [
    { label: 'Contacto',        icon: 'bi-person'       },
    { label: 'Tributario',      icon: 'bi-bank'         },
    { label: 'Perfil Emocional', icon: 'bi-heart'       },
    { label: 'Confirmación',    icon: 'bi-check-circle' },
  ];
  return (
    <div className="wizard-stepper mb-4">
      {steps.map(({ label, icon }, idx) => {
        const num = (idx + 1) as WizardStep;
        const isActive = num === step;
        const isDone = num < step;
        return (
          <div key={label} className={`wizard-stepper__item${isActive ? ' active' : ''}${isDone ? ' done' : ''}`}>
            <div className="wizard-stepper__circle">
              {isDone ? <i className="bi bi-check-lg" /> : <i className={`bi ${icon}`} />}
            </div>
            <span className="wizard-stepper__label">{label}</span>
            {idx < steps.length - 1 && <div className="wizard-stepper__line" />}
          </div>
        );
      })}
    </div>
  );
}

// ── Helpers puros (AP-0036) ──────────────────────────────────────────────────
const GENERO_MOV: Record<string, string> = {
  '0': 'Femenino', '1': 'Masculino',
  'F': 'Femenino', 'M': 'Masculino',
  'Femenino': 'Femenino', 'Masculino': 'Masculino', 'Otro': 'Otro', 'O': 'Otro',
};

function badgeCount(s: string): number | null {
  return countSelections(s) || null;
}

function detalleError(err: unknown, fallback: string): string {
  const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
  return Array.isArray(msg) ? msg.join(' | ') : (msg ?? fallback);
}

function algunoPendiente(...flags: boolean[]): boolean {
  return flags.some(Boolean);
}

function docPorTipo<T extends { tipo: number }>(docs: T[] | undefined, tipo: number): T | null {
  return docs?.find((d) => d.tipo === tipo) ?? null;
}

function boolToBit(b: boolean | null): 0 | 1 | null {
  if (b === null) return null;
  return b ? 1 : 0;
}

function dash(v: string): string {
  return v || '—';
}

function nombreEn<T>(items: T[] | undefined, match: (x: T) => boolean, get: (x: T) => string | null): string {
  const found = items?.find(match);
  return (found ? get(found) : null) ?? '—';
}

function etiquetaTipoDocMov(t: string): string {
  if (t === 'CC') return 'C.C.';
  if (t === 'CE') return 'C.E.';
  return t || '—';
}

function etiquetaEstadoMov(e: 0 | 1 | null): string {
  if (e === 1) return 'Activo';
  if (e === 0) return 'Inactivo';
  return '—';
}

function etiquetaFirmaMov(f: boolean | null): string {
  if (f === true) return 'Sí';
  if (f === false) return 'No';
  return '—';
}

function construirResumenMov(
  contacto: FormContacto,
  documentoRegistrado: string,
  departamentos: { did: number; departamento: string }[] | undefined,
  ciudades: { cid: number; ciudad: string }[] | undefined,
  canales: { cod_canales: number; nom_canales: string }[] | undefined,
  oficinas: { cod_oficinas: number; nom_oficinas: string | null }[] | undefined,
): [string, string][] {
  return [
    ['Tipo Documento', etiquetaTipoDocMov(contacto.tipo_documento)],
    ['Número Documento', documentoRegistrado || contacto.numero_documento],
    ['Nombre Completo', contacto.nombre_completo],
    ['Género', dash(contacto.genero)],
    ['Fecha de Nacimiento', dash(contacto.fecha_nacimiento)],
    ['Celular', contacto.celular],
    ['Teléfono', dash(contacto.telefono)],
    ['Correo Electrónico', dash(contacto.email)],
    ['Dirección', dash(contacto.direccion)],
    ['Departamento', nombreEn(departamentos, (d) => String(d.did) === contacto.departamento, (d) => d.departamento)],
    ['Ciudad', nombreEn(ciudades, (c) => String(c.cid) === contacto.ciudad, (c) => c.ciudad)],
    ['Programa', 'Movilidad (Vehículos)'],
    ['Canal', nombreEn(canales, (c) => String(c.cod_canales) === String(contacto.cod_canales), (c) => c.nom_canales)],
    ['Oficina', nombreEn(oficinas, (o) => String(o.cod_oficinas) === String(contacto.cod_oficinas), (o) => o.nom_oficinas)],
    ['Estado', etiquetaEstadoMov(contacto.estado)],
    ['Firma Contrato', etiquetaFirmaMov(contacto.firma_contrato)],
    ['Incentivos', contacto.incentivos ? 'Sí' : 'No'],
    ['Habeas Data', contacto.acepto_habeas_data ? 'Aceptado' : 'No aceptado'],
  ];
}

function estadoMov(v: unknown): 0 | 1 | null {
  if (v === undefined || v === null) return null;
  return Number(v) === 1 ? 1 : 0;
}

function parseTipoCuentaMov(v: unknown): string {
  const s = String(v ?? '');
  if (s === '0' || s.toLowerCase().includes('ahor')) return 'Cuenta de ahorros';
  if (s === '1' || s.toLowerCase().includes('corr')) return 'Cuenta corriente';
  return '';
}

function mapearContactoAsesorMov(c: Record<string, unknown>, documentoEditar: string | null): FormContacto {
  const depObj = refObj(c.departamento);
  const ciuObj = refObj(c.ciudad);
  const cuenta = strDe(c.numero_de_cuenta);
  return {
    numero_documento: String(c.numero_documento ?? documentoEditar),
    tipo_documento: parseTipoDoc(c.tipo_documento),
    nombre_completo: strDe(c.nombre_completo),
    genero: parseGenero(c.genero, GENERO_MOV),
    fecha_nacimiento: c.fecha_nacimiento ? String(c.fecha_nacimiento) : '',
    celular: strDe(c.celular),
    telefono: strDe(c.telefono),
    email: c.email ? String(c.email) : '',
    direccion: strDe(c.direccion),
    departamento: depObj ? strDe(depObj.did) : strDe(c.departamento),
    ciudad: ciuObj ? strDe(ciuObj.cid) : strDe(c.ciudad),
    cod_canales: (c.cod_canales as number) || '',
    cod_oficinas: (c.cod_oficinas as number) || '',
    acepto_habeas_data: Boolean(c.acepto_habeas_data),
    incentivos: Boolean(c.incentivos),
    estado: estadoMov(c.estado),
    firma_contrato: parseBoolOrNull(c.firma_contrato),
    requiere_comision: parseBoolOrNull(c.requiere_comision),
    banco: parseNumOrNull(c.banco),
    tipo_de_cuenta: parseTipoCuentaMov(c.tipo_de_cuenta),
    numero_de_cuenta: cuenta,
    numero_de_cuenta_verifica: cuenta,
  };
}

function mapearTributarioAsesorMov(t: Record<string, unknown>): FormTributario {
  return {
    eps: parseNumOrNull(t.eps),
    afp: parseNumOrNull(t.afp),
    arl: parseNumOrNull(t.arl),
    contratacion_personal: parseBoolOrNull(t.contratacion_personal),
    regimen_iva: parseBoolOrNull(t.regimen_iva),
  };
}

function mapearEmocionalAsesorMov(e: Record<string, unknown>): FormEmocional {
  return {
    con_quien_vives: strDe(e.con_quien_vives),
    estado_civil: strDe(e.estado_civil),
    numero_hijos: strDe(e.numero_hijos),
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
    numero_mascotas: strDe(e.numero_mascotas),
    info_mascotas: strDe(e.info_mascotas),
    acepto_terminos_y_condiciones: Boolean(e.acepto_terminos_y_condiciones),
  };
}

function payloadContactoAsesorMov(c: FormContacto, numero_documento: string) {
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

function payloadTributarioAsesorMov(t: FormTributario, numero_documento: string) {
  return {
    numero_documento,
    eps: t.eps,
    afp: t.afp,
    arl: t.arl,
    contratacion_personal: boolToBit(t.contratacion_personal),
    regimen_iva: boolToBit(t.regimen_iva),
  };
}

function payloadEmocionalAsesorMov(e: FormEmocional, numero_documento: string) {
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

function validarTributarioMov(c: FormContacto, t: FormTributario): string | null {
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

export function AsesorMovilidadPage() {
  const [tab, setTab] = useState<Tab>('lista');
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [searchTipoDoc, setSearchTipoDoc] = useState('');
  const [searchDocumento, setSearchDocumento] = useState('');
  const [filtrosActivos, setFiltrosActivos] = useState(false);
  const [filtrosQuery, setFiltrosQuery] = useState<{ tipo_doc?: string; documento?: string } | undefined>(undefined);
  const [documentoEditar, setDocumentoEditar] = useState<string | null>(null);
  const [editTrigger, setEditTrigger] = useState(0);
  const [formReady, setFormReady] = useState(false);
  const [step, setStep] = useState<WizardStep>(1);
  const [contacto, setContacto] = useState<FormContacto>(initContacto);
  const [tributario, setTributario] = useState<FormTributario>(initTributario);
  const tributarioRef = useRef<FormTributario>(initTributario);
  tributarioRef.current = tributario;
  const [emocional, setEmocional] = useState<FormEmocional>(initEmocional);
  const selectedDid = contacto.departamento ? Number(contacto.departamento) : null;
  const [error, setError] = useState('');
  const [exitoso, setExitoso] = useState(false);
  // AP-0001: deshabilitar la cuenta de acceso del comisionista (distinto del estado de registro).
  const [cuentaObjetivo, setCuentaObjetivo] = useState<{ doc: string; nombre: string } | null>(null);
  const [cuentaMsg, setCuentaMsg] = useState('');
  const cambiarCuentaMut = useCambiarEstadoComisionista();
  const [documentoRegistrado, setDocumentoRegistrado] = useState('');
  const profesionSelectRef = useRef<HTMLSelectElement>(null);
  const tomSelectInstance = useRef<TomSelect | null>(null);
  const depSelectRef = useRef<HTMLSelectElement>(null);
  const depTomSelect = useRef<TomSelect | null>(null);
  const ciuSelectRef = useRef<HTMLSelectElement>(null);
  const ciuTomSelect = useRef<TomSelect | null>(null);
  const canalSelectRef = useRef<HTMLSelectElement>(null);
  const canalTomSelect = useRef<TomSelect | null>(null);
  const editLoadedTrigger = useRef<number>(-1);
  const oficinaSelectRef = useRef<HTMLSelectElement>(null);
  const oficinaTomSelect = useRef<TomSelect | null>(null);
  const epsSelectRef = useRef<HTMLSelectElement>(null);
  const epsTs = useRef<TomSelect | null>(null);
  const afpSelectRef = useRef<HTMLSelectElement>(null);
  const afpTs = useRef<TomSelect | null>(null);
  const arlSelectRef = useRef<HTMLSelectElement>(null);
  const savedEps = useRef<number | null>(null);
  const savedAfp = useRef<number | null>(null);
  const savedArl = useRef<number | null>(null);
  const bancoSelectRef = useRef<HTMLSelectElement>(null);
  const bancoTs = useRef<TomSelect | null>(null);
  const arlTs = useRef<TomSelect | null>(null);
  const lista = useAsesorMovilidadList(page, size, filtrosQuery);
  const detalle = useDetalleAsesorMovilidad(documentoEditar);
  const paso1Mut = useWizardPaso1Movilidad();
  const paso2Mut = useWizardPaso2Movilidad();
  const paso3Mut = useWizardPaso3Movilidad();
  const toast = useToastContext();
  const finalizarMut = useFinalizarMovilidad();

  const { data: departamentos } = useQuery({
    queryKey: ['departamentos'],
    queryFn: () => apiClient.get<{ did: number; departamento: string }[]>('/ubicaciones/departamentos').then(r => r.data),
  });

  const { data: ciudades } = useQuery({
    queryKey: ['ciudades', selectedDid],
    queryFn: () => apiClient.get<{ cid: number; ciudad: string }[]>(`/ubicaciones/ciudades/${selectedDid}`).then(r => r.data),
    enabled: !!selectedDid,
  });

  const { data: profesiones } = useQuery({
    queryKey: ['profesiones'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/profesiones').then(r => r.data),
  });

  const { data: canales } = useQuery({
    queryKey: ['canales-movilidad'],
    queryFn: () => apiClient.get<{ cod_canales: number; nom_canales: string; cpid: number }[]>(
      `/referencias/canales?cpid=${PROGRAMA_MOVILIDAD_ID}`
    ).then(r => r.data),
  });

  const { data: oficinas } = useQuery({
    queryKey: ['oficinas-canal-movilidad', contacto.cod_canales],
    queryFn: () => apiClient.get<{ cod_oficinas: number; nom_oficinas: string | null }[]>(
      `/referencias/oficinas?cod_canales=${contacto.cod_canales}`
    ).then(r => r.data),
    enabled: contacto.cod_canales !== '',
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

  type DocExistente = { did: number; tipo: number; nombre: string; version: number; estado: string };
  const { data: docsExistentes, refetch: refetchDocs } = useQuery({
    queryKey: ['docs-asesor-movilidad', contacto.numero_documento],
    queryFn: () =>
      apiClient
        .get<DocExistente[]>(`/documentos/${contacto.numero_documento}`)
        .then(r => r.data),
    enabled: !!contacto.numero_documento && step === 2,
  });
  const docEps = docPorTipo(docsExistentes, 7);
  const docAfp = docPorTipo(docsExistentes, 8);
  const docArl = docPorTipo(docsExistentes, 9);
  const docPrepagada = docPorTipo(docsExistentes, 10);
  const docVivienda = docPorTipo(docsExistentes, 11);
  const docPensionVol = docPorTipo(docsExistentes, 12);
  const docAfc = docPorTipo(docsExistentes, 13);
  const docDependientes = docPorTipo(docsExistentes, 14);
  const docCedula = docPorTipo(docsExistentes, 4);
  const docRut = docPorTipo(docsExistentes, 5);

  useEffect(() => {
    if (!detalle.data || !documentoEditar || editLoadedTrigger.current === editTrigger) return;
    const contactoRaw = detalle.data.contacto as Record<string, unknown> | null;
    const tributarioRaw = detalle.data.tributario as Record<string, unknown> | null;
    const emocionalRaw = detalle.data.emocional as Record<string, unknown> | null;
    if (contactoRaw) {
      setContacto(mapearContactoAsesorMov(contactoRaw, documentoEditar));
      setFormReady(true);
      editLoadedTrigger.current = editTrigger;
    }
    if (tributarioRaw) setTributario(mapearTributarioAsesorMov(tributarioRaw));
    if (emocionalRaw) setEmocional(mapearEmocionalAsesorMov(emocionalRaw));
  }, [detalle.data, documentoEditar, editTrigger]);

  // Inicializa TomSelect cuando llegan los datos de profesiones
  useEffect(() => {
    if (!profesionSelectRef.current || !profesiones?.length) return;
    tomSelectInstance.current?.destroy();
    tomSelectInstance.current = new TomSelect(profesionSelectRef.current, {
      valueField: 'value',
      labelField: 'text',
      searchField: ['text'],
      options: profesiones.map(prof => ({ value: String(prof.tid), text: prof.nombre })),
      items: emocional.profesion ? [emocional.profesion] : [],
      placeholder: 'Seleccione o busque una profesión...',
      maxOptions: null,
      onChange(value: string) {
        setEmocional(prev => ({ ...prev, profesion: value }));
        if (!value) {
          setTimeout(() => {
            const ts = tomSelectInstance.current;
            if (!ts) return;
            ts.setTextboxValue('');
            ts.refreshOptions(false);
            ts.open();
          }, 0);
        }
      },
      render: {
        no_results: () => '<div class="no-results px-3 py-2 text-muted small">Sin resultados</div>',
      },
    });
    return () => {
      tomSelectInstance.current?.destroy();
      tomSelectInstance.current = null;
    };
  }, [profesiones, step]);

  // Sincroniza el valor cuando cambia externamente (modo edición)
  useEffect(() => {
    const ts = tomSelectInstance.current;
    if (!ts) return;
    const current = ts.getValue() as string;
    if (current !== (emocional.profesion || '')) {
      ts.setValue(emocional.profesion || '', true);
    }
  }, [emocional.profesion]);

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
        setContacto((prev) => ({ ...prev, departamento: value, ciudad: '' }));
        if (!value) {
          setTimeout(() => {
            const ts = depTomSelect.current;
            if (!ts) return;
            ts.setTextboxValue('');
            ts.refreshOptions(false);
            ts.open();
          }, 0);
        }
      },
    });
    return () => { depTomSelect.current?.destroy(); depTomSelect.current = null; };
  }, [departamentos, step, tab, contacto.departamento]);

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
        setContacto((prev) => ({ ...prev, ciudad: value }));
        if (!value) {
          setTimeout(() => {
            const ts = ciuTomSelect.current;
            if (!ts) return;
            ts.setTextboxValue('');
            ts.refreshOptions(false);
            ts.open();
          }, 0);
        }
      },
    });
    if (!contacto.departamento) ciuTomSelect.current.lock();
    return () => { ciuTomSelect.current?.destroy(); ciuTomSelect.current = null; };
  }, [ciudades, step, tab]);

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
        setContacto((prev) => ({ ...prev, cod_canales: value !== '' ? Number(value) : '', cod_oficinas: '' }));
        if (!value) {
          setTimeout(() => {
            const ts = canalTomSelect.current;
            if (!ts) return;
            ts.setTextboxValue('');
            ts.refreshOptions(false);
            ts.open();
          }, 0);
        }
      },
    });
    if (canalOptions.length === 0) canalTomSelect.current.lock();
    return () => { canalTomSelect.current?.destroy(); canalTomSelect.current = null; };
  }, [canales, step, tab, formReady]);

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
        setContacto((prev) => ({ ...prev, cod_oficinas: value !== '' ? Number(value) : '' }));
        if (!value) {
          setTimeout(() => {
            const ts = oficinaTomSelect.current;
            if (!ts) return;
            ts.setTextboxValue('');
            ts.refreshOptions(false);
            ts.open();
          }, 0);
        }
      },
    });
    if (contacto.cod_canales !== '' && oficinaOptions.length > 0) {
      oficinaTomSelect.current.enable();
    } else {
      oficinaTomSelect.current.disable();
    }
    return () => { oficinaTomSelect.current?.destroy(); oficinaTomSelect.current = null; };
  }, [oficinas, step, tab, formReady]);

  useEffect(() => {
    const ts = oficinaTomSelect.current; if (!ts) return;
    const val = contacto.cod_oficinas !== '' ? String(contacto.cod_oficinas) : '';
    if ((ts.getValue() as string) !== val) ts.setValue(val, true);
    const oficinaOptions = (oficinas ?? []).filter(oficina => oficina.nom_oficinas?.trim());
    if (contacto.cod_canales !== '' && oficinaOptions.length > 0) ts.enable();
    else ts.disable();
  }, [contacto.cod_oficinas, contacto.cod_canales, oficinas]);

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
        setTributario((prev) => ({ ...prev, eps: value !== '' ? Number(value) : null }));
        if (!value) {
          setTimeout(() => { const ts = epsTs.current; if (!ts) return; ts.setTextboxValue(''); ts.refreshOptions(false); ts.open(); }, 0);
        }
      },
      render: { no_results: () => '<div class="no-results px-3 py-2 text-muted small">Sin resultados</div>' },
    });
    if (contacto.requiere_comision === false) epsTs.current.disable();
    return () => { epsTs.current?.destroy(); epsTs.current = null; };
  }, [epsOpciones, step]);

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
      placeholder: 'Seleccione AFP / Fondo de pensiones...', maxOptions: null,
      onChange(value: string) {
        setTributario((prev) => ({ ...prev, afp: value !== '' ? Number(value) : null }));
        if (!value) {
          setTimeout(() => { const ts = afpTs.current; if (!ts) return; ts.setTextboxValue(''); ts.refreshOptions(false); ts.open(); }, 0);
        }
      },
      render: { no_results: () => '<div class="no-results px-3 py-2 text-muted small">Sin resultados</div>' },
    });
    if (contacto.requiere_comision === false) afpTs.current.disable();
    return () => { afpTs.current?.destroy(); afpTs.current = null; };
  }, [afpOpciones, step]);

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
        setTributario((prev) => ({ ...prev, arl: value !== '' ? Number(value) : null }));
        if (!value) {
          setTimeout(() => { const ts = arlTs.current; if (!ts) return; ts.setTextboxValue(''); ts.refreshOptions(false); ts.open(); }, 0);
        }
      },
      render: { no_results: () => '<div class="no-results px-3 py-2 text-muted small">Sin resultados</div>' },
    });
    if (contacto.requiere_comision === false) arlTs.current.disable();
    return () => { arlTs.current?.destroy(); arlTs.current = null; };
  }, [arlOpciones, step]);

  useEffect(() => {
    const ts = arlTs.current; if (!ts) return;
    const wanted = tributario.arl !== null ? String(tributario.arl) : '';
    if ((ts.getValue() as string) !== wanted) ts.setValue(wanted, true);
    if (contacto.requiere_comision === false) ts.disable(); else ts.enable();
  }, [tributario.arl, contacto.requiere_comision]);

  // ── Mantener savedEps/AFP/ARL con el último valor "real" (no NO_COMISION) ──
  // Se actualiza cada vez que el usuario elige una opción válida en el dropdown.
  // Si el valor es null o NO_COMISION, NO se modifica el ref → preserva el último valor real.
  useEffect(() => {
    if (tributario.eps !== null && tributario.eps !== NO_COMISION_EPS) {
      savedEps.current = tributario.eps;
    }
  }, [tributario.eps]);

  useEffect(() => {
    if (tributario.afp !== null && tributario.afp !== NO_COMISION_AFP) {
      savedAfp.current = tributario.afp;
    }
  }, [tributario.afp]);

  useEffect(() => {
    if (tributario.arl !== null && tributario.arl !== NO_COMISION_ARL) {
      savedArl.current = tributario.arl;
    }
  }, [tributario.arl]);

  // ── Sin/Con Comisión — sincroniza eps/afp/arl con NO COMISION ────────────
  useEffect(() => {
    if (contacto.requiere_comision === false) {
      setTributario((prev) => ({ ...prev, eps: NO_COMISION_EPS, afp: NO_COMISION_AFP, arl: NO_COMISION_ARL }));
    } else if (contacto.requiere_comision === true) {
      setTributario((prev) => ({
        ...prev,
        eps: savedEps.current,
        afp: savedAfp.current,
        arl: savedArl.current,
      }));
    }
  }, [contacto.requiere_comision]);

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
        setContacto((prev) => ({ ...prev, banco: value !== '' ? Number(value) : null }));
        if (!value) {
          setTimeout(() => { const ts = bancoTs.current; if (!ts) return; ts.setTextboxValue(''); ts.refreshOptions(false); ts.open(); }, 0);
        }
      },
      render: { no_results: () => '<div class="no-results px-3 py-2 text-muted small">Sin resultados</div>' },
    });
    return () => { bancoTs.current?.destroy(); bancoTs.current = null; };
  }, [bancosOpciones, step]);

  useEffect(() => {
    const ts = bancoTs.current; if (!ts) return;
    const wanted = contacto.banco !== null ? String(contacto.banco) : '';
    if ((ts.getValue() as string) !== wanted) ts.setValue(wanted, true);
  }, [contacto.banco]);

  function handleBuscar() {
    const filtros: { tipo_doc?: string; documento?: string } = {};
    if (searchTipoDoc) filtros.tipo_doc = searchTipoDoc;
    if (searchDocumento) filtros.documento = searchDocumento;
    setFiltrosQuery(filtros);
    setFiltrosActivos(true);
    setPage(1);
  }

  function handleLimpiar() {
    setSearchTipoDoc('');
    setSearchDocumento('');
    setFiltrosQuery(undefined);
    setFiltrosActivos(false);
    setPage(1);
  }

  function abrirEdicion(documento: string) {
    editLoadedTrigger.current = -1;
    setFormReady(false);
    setEditTrigger((prev) => prev + 1);
    setContacto({ ...initContacto, numero_documento: documento });
    setTributario(initTributario);
    setEmocional(initEmocional);
    setStep(1);
    setError('');
    setExitoso(false);
    setTab('registro');
    if (documento === documentoEditar) {
      detalle.refetch();
    } else {
      setDocumentoEditar(documento);
    }
  }

  function nuevoRegistro() {
    setDocumentoEditar(null);
    setContacto(initContacto);
    setTributario(initTributario);
    setEmocional(initEmocional);
    setStep(1);
    setError('');
    setExitoso(false);
    setTab('registro');
  }

  async function handlePaso1(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!contacto.acepto_habeas_data) {
      setError('Debe aceptar el habeas data');
      toast.warning('Debe aceptar el habeas data', { title: 'Datos incompletos' });
      return;
    }
    if (!documentoEditar) {
      try {
        const check = await verificarAsesorMovilidadApi(contacto.numero_documento);
        if (check.registrado) {
          const yaReg = `El asesor con ${contacto.tipo_documento} ${contacto.numero_documento} ya está registrado`;
          setError(yaReg);
          toast.warning(yaReg, { title: 'Documento ya registrado' });
          return;
        }
      } catch {
        setError('No se pudo verificar el documento. Intente de nuevo.');
        toast.error('No se pudo verificar el documento. Intente de nuevo.', { title: 'Error de verificacion' });
        return;
      }
    }
    try {
      const result = await paso1Mut.mutateAsync(
        payloadContactoAsesorMov(contacto, contacto.numero_documento),
      );
      setDocumentoRegistrado(result.numero_documento);
      setStep(2);
      toast.success('Datos de contacto guardados.', { title: 'Paso contacto' });
    } catch (err: unknown) {
      const detalle = detalleError(err, 'Error en paso 1');
      setError(detalle);
      toast.error('No se pudo guardar el contacto.', { title: 'Error de contacto', detail: detalle });
    }
  }

  async function handlePaso2(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    const mensaje = validarTributarioMov(contacto, tributario);
    if (mensaje) {
      setError(mensaje);
      toast.warning(mensaje, { title: 'Datos incompletos' });
      return;
    }
    const docNum = documentoRegistrado || contacto.numero_documento;
    try {
      await paso1Mut.mutateAsync(payloadContactoAsesorMov(contacto, docNum));
      await paso2Mut.mutateAsync(payloadTributarioAsesorMov(tributario, docNum));
      // Eliminar documentos cuya entidad quedó en NO COMISION
      const idsAEliminar = documentosTributariosAEliminar(tributario, docEps, docAfp, docArl);
      if (idsAEliminar.length > 0) {
        await Promise.all(idsAEliminar.map((id) => apiClient.delete(`/documentos/${id}`)));
      }
      setStep(3);
      toast.success('Informacion tributaria guardada.', { title: 'Paso tributario' });
    } catch (err: unknown) {
      const detalle = detalleError(err, 'Error en paso 2');
      setError(detalle);
      toast.error('No se pudo guardar la informacion tributaria.', { title: 'Error tributario', detail: detalle });
    }
  }

  async function handlePaso3(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!emocional.acepto_terminos_y_condiciones) {
      setError('Debe aceptar los términos y condiciones');
      toast.warning('Debe aceptar los términos y condiciones', { title: 'Datos incompletos' });
      return;
    }
    try {
      await paso3Mut.mutateAsync(
        payloadEmocionalAsesorMov(emocional, documentoRegistrado || contacto.numero_documento),
      );
      setStep(4);
      toast.success('Informacion emocional guardada.', { title: 'Paso emocional' });
    } catch (err: unknown) {
      const detalle = detalleError(err, 'Error en paso 3');
      setError(detalle);
      toast.error('No se pudo guardar la informacion emocional.', { title: 'Error emocional', detail: detalle });
    }
  }

  async function handleFinalizar() {
    setError('');
    try {
      await finalizarMut.mutateAsync(documentoRegistrado || contacto.numero_documento);
      setExitoso(true);
      lista.refetch();
      toast.success('Registro finalizado correctamente.', { title: 'Registro completo' });
    } catch (err: unknown) {
      const detalle = detalleError(err, 'Error al finalizar');
      setError(detalle);
      toast.error('No se pudo finalizar el registro.', { title: 'Error al finalizar', detail: detalle });
    }
  }

  const [docUploading, setDocUploading] = useState(false);
  const isBusy = algunoPendiente(paso1Mut.isPending, paso2Mut.isPending, paso3Mut.isPending, finalizarMut.isPending);

  async function confirmarDeshabilitarCuenta() {
    if (!cuentaObjetivo) return;
    try {
      await cambiarCuentaMut.mutateAsync({
        programa: 'movilidad',
        numeroDocumento: cuentaObjetivo.doc,
        payload: { activo: false },
      });
      setCuentaMsg(`Cuenta de acceso de ${cuentaObjetivo.nombre} deshabilitada`);
      setCuentaObjetivo(null);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(Array.isArray(msg) ? msg.join(' | ') : (msg ?? 'No se pudo deshabilitar la cuenta'));
      setCuentaObjetivo(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Asesor Movilidad"
        subtitle="Gestión de asesores del programa Movilidad (Vehículos)"
        icon="bi-car-front-fill"
        actions={
          tab === 'lista' ? (
            <Button variant="danger" size="sm" onClick={nuevoRegistro}>
              <i className="bi bi-plus-circle me-1" />Nuevo Asesor
            </Button>
          ) : undefined
        }
      />

      {cuentaMsg && (
        <Alert variant="success" dismissible onClose={() => setCuentaMsg('')}>
          <i className="bi bi-check-circle me-2" />
          {cuentaMsg}
        </Alert>
      )}

      <Card className="shadow-sm" style={{ border: 'none' }}>
        <Card.Header className="bg-white border-0 pt-3">
          <Nav variant="tabs" activeKey={tab} onSelect={(k) => setTab(k as Tab)}>
            <Nav.Item>
              <Nav.Link eventKey="lista">
                <i className="bi bi-people me-2" />Lista de Asesores
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="registro">
                <i className="bi bi-person-plus me-2" />
                {documentoEditar ? 'Editar Asesor' : 'Registro'}
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="documentos">
                <i className="bi bi-folder me-2" />Documentación
              </Nav.Link>
            </Nav.Item>
          </Nav>
        </Card.Header>

        <Card.Body className={tab === 'lista' || tab === 'documentos' ? 'p-0' : 'p-4'}>
          {tab === 'documentos' && <DocumentosTab />}

          {/* ── TAB LISTA ── */}
          {tab === 'lista' && (() => (
            <>
              <div className="d-flex align-items-center justify-content-between px-3 pt-3 pb-2 gap-2 flex-wrap">
                <small className="text-muted">
                  {lista.data ? `${lista.data.total} ${filtrosActivos ? 'asesores encontrados' : 'asesores registrados'}` : ''}
                </small>
                <Form.Select
                  size="sm"
                  style={{ width: 'auto' }}
                  value={size}
                  onChange={(e) => { setSize(Number(e.target.value)); setPage(1); }}
                >
                  {[10, 20, 30].map((n) => (
                    <option key={n} value={n}>Ver {n} por página</option>
                  ))}
                </Form.Select>
              </div>

              {/* ── Panel de búsqueda ── */}
              <div className="px-3 pb-3">
                <div className="d-flex align-items-end gap-2 flex-wrap p-3 rounded" style={{ background: '#f8f9fa', border: '1px solid #dee2e6' }}>
                  <Form.Group style={{ minWidth: 160 }}>
                    <Form.Label className="small mb-1 fw-semibold">Tipo de Documento</Form.Label>
                    <Form.Select
                      size="sm"
                      value={searchTipoDoc}
                      onChange={(e) => setSearchTipoDoc(e.target.value)}
                    >
                      <option value="">Todos</option>
                      <option value="CC">C.C.</option>
                      <option value="CE">C.E.</option>
                      <option value="F&I">F&amp;I</option>
                      <option value="GC">GC</option>
                      <option value="PEP">PEP</option>
                      <option value="PPT">PPT</option>
                      <option value="VDA">VDA</option>
                    </Form.Select>
                  </Form.Group>
                  <Form.Group style={{ minWidth: 180 }}>
                    <Form.Label className="small mb-1 fw-semibold">Documento</Form.Label>
                    <Form.Control
                      size="sm"
                      placeholder="Ej: 12345678"
                      value={searchDocumento}
                      onChange={(e) => setSearchDocumento(e.target.value.replace(/\D/g, ''))}
                      maxLength={20}
                    />
                  </Form.Group>
                  <Button
                    variant="danger"
                    size="sm"
                    disabled={!searchTipoDoc && !searchDocumento}
                    onClick={handleBuscar}
                  >
                    <i className="bi bi-search me-1" />Buscar
                  </Button>
                  <Button
                    variant="outline-secondary"
                    size="sm"
                    onClick={handleLimpiar}
                  >
                    <i className="bi bi-x-circle me-1" />Limpiar
                  </Button>
                </div>
              </div>

              {lista.isLoading ? (
                <div className="text-center py-5"><Spinner animation="border" variant="danger" /></div>
              ) : lista.data?.items.length === 0 ? (
                <div className="text-center py-5 text-muted">
                  <i className="bi bi-inbox fs-1 d-block mb-2" />
                  Sin asesores de Movilidad registrados
                </div>
              ) : (
                <Table hover responsive className="mb-0">
                  <thead className="table-light">
                    <tr>
                      <th>Documento</th>
                      <th>Tipo Doc.</th>
                      <th>Género</th>
                      <th>Nombre</th>
                      <th>Celular</th>
                      <th>Departamento</th>
                      <th>Ciudad</th>
                      <th>Estado</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {lista.data?.items.map((asesor) => (
                      <tr
                        key={asesor.numero_documento}
                        style={{ cursor: 'pointer' }}
                        onClick={() => abrirEdicion(asesor.numero_documento)}
                      >
                        <td className="font-monospace">{asesor.numero_documento}</td>
                        <td>{asesor.tipo_documento?.nombre ?? '—'}</td>
                        <td>{asesor.genero?.nombre ?? '—'}</td>
                        <td>{asesor.nombre_completo ?? '—'}</td>
                        <td>{asesor.celular ?? '—'}</td>
                        <td>{asesor.departamento?.departamento ?? '—'}</td>
                        <td>{asesor.ciudad?.ciudad ?? '—'}</td>
                        <td>
                          <Badge bg={asesor.estado === 1 ? 'success' : 'secondary'}>
                            {asesor.estado === 1 ? 'Activo' : 'Inactivo'}
                          </Badge>
                        </td>
                        <td onClick={(e) => e.stopPropagation()}>
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            className="me-1"
                            title="Editar"
                            onClick={() => abrirEdicion(asesor.numero_documento)}
                          >
                            <i className="bi bi-pencil" />
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            title="Deshabilitar cuenta de acceso"
                            onClick={() =>
                              setCuentaObjetivo({
                                doc: asesor.numero_documento,
                                nombre: asesor.nombre_completo ?? asesor.numero_documento,
                              })
                            }
                          >
                            <i className="bi bi-person-fill-slash" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}

              {lista.data && lista.data.pages > 1 && (
                <div className="d-flex justify-content-center align-items-center gap-2 py-3">
                  <Button variant="outline-secondary" size="sm" disabled={page === 1} onClick={() => setPage(1)} title="Primera página">
                    <i className="bi bi-chevron-double-left" />
                  </Button>
                  <Button variant="outline-secondary" size="sm" disabled={page === 1} onClick={() => setPage((prev) => prev - 1)} title="Página anterior">
                    <i className="bi bi-chevron-left" />
                  </Button>
                  <span className="small">Página {page} de {lista.data.pages}</span>
                  <Button variant="outline-secondary" size="sm" disabled={page === lista.data.pages} onClick={() => setPage((prev) => prev + 1)} title="Página siguiente">
                    <i className="bi bi-chevron-right" />
                  </Button>
                  <Button variant="outline-secondary" size="sm" disabled={page === lista.data.pages} onClick={() => setPage(lista.data.pages)} title="Última página">
                    <i className="bi bi-chevron-double-right" />
                  </Button>
                </div>
              )}
            </>
          ))()}

          {/* ── TAB REGISTRO / EDICIÓN ── */}
          {tab === 'registro' && (() => (
            <>
              {documentoEditar && (!formReady || detalle.isLoading) && (
                <div className="text-center py-4"><Spinner animation="border" variant="danger" /></div>
              )}

              {(!documentoEditar || formReady) && !detalle.isLoading && (
                <>
                  <WizardStepper step={step} />
                  {error && <Alert variant="danger" onClose={() => setError('')} dismissible>{error}</Alert>}

                  {/* ── Paso 1: Contacto ── */}
                  {step === 1 && (() => (
                    <Form onSubmit={handlePaso1}>
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
                            <Form.Label><i className="bi bi-hash me-1 text-danger" />Número Documento *</Form.Label>
                            <Form.Control required value={contacto.numero_documento} onChange={e => setContacto((prev) => ({ ...prev,numero_documento: e.target.value }))} placeholder="Solo dígitos" disabled={!!documentoEditar} />
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
                            <Form.Control
                              type="email"
                              value={contacto.email}
                              onChange={e => setContacto((prev) => ({ ...prev,email: e.target.value }))}
                              placeholder="ejemplo@correo.com"
                              maxLength={254}
                            />
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
                            <select ref={oficinaSelectRef} className="form-select" disabled />
                          </Form.Group>
                        </Col>
                        <Col xs={12} md={6}>
                          <Form.Group>
                            <div>
                              <EstadoSwitch
                                id="asesor-movilidad-estado"
                                checked={contacto.estado === 1}
                                onChange={(checked) => setContacto((prev) => ({ ...prev, estado: checked ? 1 : 0 }))}
                              />
                            </div>
                          </Form.Group>
                        </Col>
                        <Col xs={12}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-file-earmark-check me-1 text-danger" />Firma de Contrato</Form.Label>
                            <div className="d-flex gap-4 flex-wrap">
                              <Form.Check
                                type="radio"
                                id="firma-contrato-si-mov"
                                name="firma_contrato-mov"
                                label="El contrato fue firmado"
                                checked={contacto.firma_contrato === true}
                                onChange={() => setContacto((prev) => ({ ...prev,firma_contrato: true }))}
                              />
                              <Form.Check
                                type="radio"
                                id="firma-contrato-no-mov"
                                name="firma_contrato-mov"
                                label="No requiere firma de Contrato"
                                checked={contacto.firma_contrato === false}
                                onChange={() => setContacto((prev) => ({ ...prev,firma_contrato: false }))}
                              />
                            </div>
                          </Form.Group>
                        </Col>
                        <Col xs={12}>
                          <Form.Check
                            type="checkbox"
                            id="habeas-data-movilidad"
                            label="Acepto el tratamiento de datos personales (Habeas Data) *"
                            checked={contacto.acepto_habeas_data}
                            onChange={e => setContacto((prev) => ({ ...prev,acepto_habeas_data: e.target.checked }))}
                          />
                        </Col>
                        <Col xs={12}>
                          <Form.Check
                            type="checkbox"
                            id="incentivos-movilidad"
                            label="Tiene Incentivos"
                            checked={contacto.incentivos}
                            onChange={e => setContacto((prev) => ({ ...prev,incentivos: e.target.checked }))}
                          />
                        </Col>
                      </Row>
                      <div className="wizard-nav mt-4">
                        <Button variant="outline-secondary" onClick={() => setTab('lista')}>
                          <i className="bi bi-arrow-left me-1" />Cancelar
                        </Button>
                        <Button type="submit" variant="danger" disabled={isBusy}>
                          {paso1Mut.isPending ? <Spinner size="sm" className="me-1" /> : <i className="bi bi-arrow-right me-1" />}
                          Siguiente
                        </Button>
                      </div>
                    </Form>
                  ))()}

                  {/* ── Paso 2: Tributario ── */}
                  {step === 2 && (() => (
                    <Form onSubmit={handlePaso2}>
                      <Row className="g-3">

                        <Col xs={12}>
                          <div className="border rounded p-3">
                            <p className="mb-3" style={{ fontWeight: 500 }}>
                              1. Para realizar su actividad de comisionista usted tuvo que contratar a más de una persona durante el último año por 6 meses o más?
                            </p>
                            <div className="d-flex gap-4">
                              <Form.Check type="radio" id="contratacion-no" name="contratacion_personal" label="No" checked={tributario.contratacion_personal === false} onChange={() => setTributario((prev) => ({ ...prev,contratacion_personal: false }))} />
                              <Form.Check type="radio" id="contratacion-si" name="contratacion_personal" label="Sí" checked={tributario.contratacion_personal === true} onChange={() => setTributario((prev) => ({ ...prev,contratacion_personal: true }))} />
                            </div>
                          </div>
                        </Col>
                        <Col xs={12}>
                          <div className="border rounded p-3">
                            <p className="mb-3" style={{ fontWeight: 500 }}>
                              2. ¿A qué régimen de IVA pertenece?
                            </p>
                            <div className="d-flex gap-4">
                              <Form.Check type="radio" id="regimen-simplificado" name="regimen_iva" label="No responsable de IVA (Simplificado)" checked={tributario.regimen_iva === false} onChange={() => setTributario((prev) => ({ ...prev,regimen_iva: false }))} />
                              <Form.Check type="radio" id="regimen-comun" name="regimen_iva" label="Responsable de IVA (Común)" checked={tributario.regimen_iva === true} onChange={() => setTributario((prev) => ({ ...prev,regimen_iva: true }))} />
                            </div>
                          </div>
                        </Col>

                        {/* ── Bloque EPS / AFP / ARL ── */}
                        <Col xs={12}>
                          <div className="border rounded p-3">
                            <p className="mb-3" style={{ fontWeight: 500 }}>
                              3. Autorizo a la compañía CADENA SA, identificada con Nit 890.930.534-0 para que efectúe los descuentos correspondientes a los aportes en seguridad social, en salud, pensión y riesgos laborales y realice los pagos respectivos por cuenta mía a las siguientes entidades:
                            </p>

                            {/* ── Con / Sin Comisión ── */}
                            <div className={`rounded p-2 mb-3 ${contacto.requiere_comision === null ? 'bg-warning-subtle border border-warning' : 'bg-light border'}`}>
                              <p className="mb-2 fw-semibold small">
                                <i className="bi bi-toggles me-2" />¿El asesor trabaja con o sin comisión?
                              </p>
                              <div className="d-flex gap-4">
                                <Form.Check
                                  type="radio"
                                  id="comision-con"
                                  name="requiere_comision"
                                  label="Con Comisión"
                                  checked={contacto.requiere_comision === true}
                                  onChange={() => setContacto((prev) => ({ ...prev,requiere_comision: true }))}
                                />
                                <Form.Check
                                  type="radio"
                                  id="comision-sin"
                                  name="requiere_comision"
                                  label="Sin Comisión"
                                  checked={contacto.requiere_comision === false}
                                  onChange={() => setContacto((prev) => ({ ...prev,requiere_comision: false }))}
                                />
                              </div>
                            </div>

                            {/* EPS */}
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">EPS</Form.Label>
                              <DocZone
                                tipoLabel="EPS" tipoPrefix="EPS" tipo={7}
                                numeroDocumento={contacto.numero_documento}
                                existingDoc={docEps}
                                onUploaded={() => { void refetchDocs(); }}
                                onDeleted={() => { void refetchDocs(); }}
                                onUploadingChange={setDocUploading}
                                disabled={tributario.eps === null || tributario.eps === NO_COMISION_EPS}
                              >
                                <select ref={epsSelectRef} className="form-select" />
                              </DocZone>
                            </Form.Group>

                            {/* AFP / Fondo de pensiones */}
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">Fondo de pensiones</Form.Label>
                              <DocZone
                                tipoLabel="AFP" tipoPrefix="AFP" tipo={8}
                                numeroDocumento={contacto.numero_documento}
                                existingDoc={docAfp}
                                onUploaded={() => { void refetchDocs(); }}
                                onDeleted={() => { void refetchDocs(); }}
                                onUploadingChange={setDocUploading}
                                disabled={tributario.afp === null || tributario.afp === NO_COMISION_AFP}
                              >
                                <select ref={afpSelectRef} className="form-select" />
                              </DocZone>
                            </Form.Group>

                            {/* ARL */}
                            <Form.Group className="mb-0">
                              <Form.Label className="fw-semibold">ARL</Form.Label>
                              <DocZone
                                tipoLabel="ARL" tipoPrefix="ARL" tipo={9}
                                numeroDocumento={contacto.numero_documento}
                                existingDoc={docArl}
                                onUploaded={() => { void refetchDocs(); }}
                                onDeleted={() => { void refetchDocs(); }}
                                onUploadingChange={setDocUploading}
                                disabled={tributario.arl === null || tributario.arl === NO_COMISION_ARL}
                              >
                                <select ref={arlSelectRef} className="form-select" />
                              </DocZone>
                            </Form.Group>
                          </div>
                        </Col>

                        {/* ── Bloque Banco / Cuenta ── */}
                        <Col xs={12}>
                          <div className="border rounded p-3">
                            <p className="mb-3" style={{ fontWeight: 500 }}>
                              4. Información bancaria para pago de comisiones:
                            </p>

                            {/* Banco */}
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">Banco</Form.Label>
                              <select ref={bancoSelectRef} className="form-select" />
                            </Form.Group>

                            {/* Tipo de cuenta */}
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">Tipo de cuenta</Form.Label>
                              <Form.Select
                                value={contacto.tipo_de_cuenta}
                                onChange={e => setContacto((prev) => ({ ...prev,tipo_de_cuenta: e.target.value }))}
                              >
                                <option value="">Seleccione...</option>
                                <option value="Cuenta de ahorros">Cuenta de ahorros</option>
                                <option value="Cuenta corriente">Cuenta corriente</option>
                              </Form.Select>
                            </Form.Group>

                            {/* Número de cuenta */}
                            <Form.Group className="mb-3">
                              <Form.Label className="fw-semibold">Número de cuenta</Form.Label>
                              <Form.Control
                                value={contacto.numero_de_cuenta}
                                onChange={e => setContacto((prev) => ({ ...prev,numero_de_cuenta: e.target.value.replace(/\D/g, '') }))}
                                placeholder="Número de cuenta"
                                inputMode="numeric"
                                maxLength={30}
                              />
                            </Form.Group>

                            {/* Verifica número de cuenta */}
                            <Form.Group className="mb-0">
                              <Form.Label className="fw-semibold">Verifica número de cuenta</Form.Label>
                              <Form.Control
                                value={contacto.numero_de_cuenta_verifica}
                                onChange={e => setContacto((prev) => ({ ...prev,numero_de_cuenta_verifica: e.target.value.replace(/\D/g, '') }))}
                                placeholder="Repite el número de cuenta"
                                inputMode="numeric"
                                maxLength={30}
                              />
                              {contacto.numero_de_cuenta_verifica !== '' && contacto.numero_de_cuenta !== contacto.numero_de_cuenta_verifica && (
                                <Form.Text className="text-danger">
                                  <i className="bi bi-exclamation-circle me-1" />Los números de cuenta no coinciden
                                </Form.Text>
                              )}
                            </Form.Group>
                          </div>
                        </Col>

                        {/* ── Bloque Certificados (beneficios tributarios) ── */}
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
                                  onUploaded={() => { void refetchDocs(); }}
                                  onDeleted={() => { void refetchDocs(); }}
                                  onUploadingChange={setDocUploading}
                                />
                              </Col>
                              <Col xs={12} md={6}>
                                <CertificadoRow
                                  label="Certificado intereses de vivienda" tipo={11} tipoPrefix="VIVIENDA"
                                  numeroDocumento={contacto.numero_documento}
                                  existingDoc={docVivienda}
                                  onUploaded={() => { void refetchDocs(); }}
                                  onDeleted={() => { void refetchDocs(); }}
                                  onUploadingChange={setDocUploading}
                                />
                              </Col>
                              <Col xs={12} md={6}>
                                <CertificadoRow
                                  label="Dependientes" tipo={14} tipoPrefix="DEPENDIENTES"
                                  numeroDocumento={contacto.numero_documento}
                                  existingDoc={docDependientes}
                                  onUploaded={() => { void refetchDocs(); }}
                                  onDeleted={() => { void refetchDocs(); }}
                                  onUploadingChange={setDocUploading}
                                />
                              </Col>
                              <Col xs={12} md={6}>
                                <CertificadoRow
                                  label="Pensión voluntaria" tipo={12} tipoPrefix="PENSIONVOL"
                                  numeroDocumento={contacto.numero_documento}
                                  existingDoc={docPensionVol}
                                  onUploaded={() => { void refetchDocs(); }}
                                  onDeleted={() => { void refetchDocs(); }}
                                  onUploadingChange={setDocUploading}
                                />
                              </Col>
                              <Col xs={12} md={6}>
                                <CertificadoRow
                                  label="AFC" tipo={13} tipoPrefix="AFC"
                                  numeroDocumento={contacto.numero_documento}
                                  existingDoc={docAfc}
                                  onUploaded={() => { void refetchDocs(); }}
                                  onDeleted={() => { void refetchDocs(); }}
                                  onUploadingChange={setDocUploading}
                                />
                              </Col>
                            </Row>
                          </div>
                        </Col>

                        {/* ── Bloque Documentos de usuario ── */}
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
                                  onUploaded={() => { void refetchDocs(); }}
                                  onDeleted={() => { void refetchDocs(); }}
                                  onUploadingChange={setDocUploading}
                                />
                              </Col>
                              <Col xs={12} md={6}>
                                <CertificadoRow
                                  label="RUT" tipo={5} tipoPrefix="RUT"
                                  numeroDocumento={contacto.numero_documento}
                                  existingDoc={docRut}
                                  onUploaded={() => { void refetchDocs(); }}
                                  onDeleted={() => { void refetchDocs(); }}
                                  onUploadingChange={setDocUploading}
                                />
                              </Col>
                            </Row>
                          </div>
                        </Col>
                      </Row>
                      <div className="wizard-nav mt-4">
                        <Button variant="outline-secondary" onClick={() => setStep(1)} disabled={isBusy || docUploading}>
                          <i className="bi bi-arrow-left me-1" />Anterior
                        </Button>
                        <Button type="submit" variant="danger" disabled={isBusy || docUploading}>
                          {paso2Mut.isPending ? <Spinner size="sm" className="me-1" /> : <i className="bi bi-arrow-right me-1" />}
                          Siguiente
                        </Button>
                      </div>
                    </Form>
                  ))()}

                  {/* ── Paso 3: Perfil Emocional ── */}
                  {step === 3 && (() => (
                    <Form onSubmit={handlePaso3}>
                      <Row className="g-3">
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-heart me-1 text-danger" />Estado Civil</Form.Label>
                            <Form.Select value={emocional.estado_civil} onChange={e => setEmocional((prev) => ({ ...prev,estado_civil: e.target.value }))}>
                              <option value="">Seleccione...</option>
                              <option>Soltero/a</option><option>Casado/a</option><option>Unión libre</option>
                              <option>Divorciado/a</option><option>Viudo/a</option>
                            </Form.Select>
                          </Form.Group>
                        </Col>
                        <Col xs={12}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-person-hearts me-1 text-danger" />¿Tiene hijos?</Form.Label>
                            <TieneHijosSelector
                              numeroHijos={emocional.numero_hijos}
                              infoHijos={emocional.info_hijos}
                              onChange={(numero, info) => setEmocional((prev) => ({ ...prev,numero_hijos: numero, info_hijos: info }))}
                            />
                          </Form.Group>
                        </Col>
                        <Col xs={12}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-patch-heart me-1 text-danger" />¿Tiene mascota?</Form.Label>
                            <TieneMascotaSelector
                              numeroMascotas={emocional.numero_mascotas}
                              infoMascotas={emocional.info_mascotas}
                              onChange={(num, info) => setEmocional((prev) => ({ ...prev,numero_mascotas: num, info_mascotas: info }))}
                            />
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-mortarboard me-1 text-danger" />Nivel Educativo</Form.Label>
                            <Form.Select value={emocional.nivel_educativo} onChange={e => setEmocional((prev) => ({ ...prev,nivel_educativo: e.target.value }))}>
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
                          <MetroTileToggle
                            title="¿Con quién vive?"
                            icon="bi-people-fill"
                            color="red"
                            size="medium"
                            subtitle="Selecciona una o varias opciones"
                            badge={badgeCount(emocional.con_quien_vives)}
                          >
                            <ConQuienVivesSelector
                              value={emocional.con_quien_vives}
                              onChange={next => setEmocional((prev) => ({ ...prev,con_quien_vives: next }))}
                            />
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="Premios que le gustaría recibir"
                            icon="bi-trophy-fill"
                            color="gold"
                            size="medium"
                            subtitle="Marca todos los premios de su interés"
                            badge={badgeCount(emocional.premios_gustaria_recibir)}
                          >
                            <PremiosSelector
                              value={emocional.premios_gustaria_recibir}
                              onChange={next => setEmocional((prev) => ({ ...prev,premios_gustaria_recibir: next }))}
                            />
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="¿Cuáles son tus Hobbies?"
                            icon="bi-controller"
                            color="teal"
                            size="wide"
                            subtitle="Despliega para elegir hasta 10 hobbies"
                            badge={badgeCount(emocional.hobbies)}
                          >
                            <div className="metro-hobbies-grid">
                              <HobbiesSelector
                                value={emocional.hobbies}
                                onChange={next => setEmocional((prev) => ({ ...prev,hobbies: next }))}
                              />
                            </div>
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="¿En qué temas te gustaría profundizar o aprender?"
                            icon="bi-book-half"
                            color="blue"
                            size="medium"
                            subtitle="Selecciona los temas de interés"
                            badge={badgeCount(emocional.temas_a_profundizar)}
                          >
                            <TemasProfundizarSelector
                              value={emocional.temas_a_profundizar}
                              onChange={next => setEmocional((prev) => ({ ...prev,temas_a_profundizar: next }))}
                            />
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="Propósitos con tu Familia"
                            icon="bi-house-heart-fill"
                            color="red"
                            size="medium"
                            subtitle="Marca los propósitos familiares"
                            badge={badgeCount(emocional.propositos_familiares)}
                          >
                            <PropositosFamiliaresSelector
                              value={emocional.propositos_familiares}
                              onChange={next => setEmocional((prev) => ({ ...prev,propositos_familiares: next }))}
                            />
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="Propósitos Financieros"
                            icon="bi-currency-dollar"
                            color="green"
                            size="medium"
                            subtitle="Selecciona los propósitos financieros"
                            badge={badgeCount(emocional.propositos_financieros)}
                          >
                            <PropositosFinancierosSelector
                              value={emocional.propositos_financieros}
                              onChange={next => setEmocional((prev) => ({ ...prev,propositos_financieros: next }))}
                            />
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="Propósitos Diversión"
                            icon="bi-joystick"
                            color="yellow"
                            size="wide"
                            subtitle="Despliega para elegir actividades de diversión"
                            badge={badgeCount(emocional.propositos_diversion)}
                          >
                            <div className="metro-twocol-grid">
                              <PropositosDiversionSelector
                                value={emocional.propositos_diversion}
                                onChange={next => setEmocional((prev) => ({ ...prev,propositos_diversion: next }))}
                              />
                            </div>
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="Propósitos Salud"
                            icon="bi-heart-pulse-fill"
                            color="teal"
                            size="medium"
                            subtitle="Selecciona los propósitos de salud y bienestar"
                            badge={badgeCount(emocional.propositos_salud)}
                          >
                            <PropositosSaludSelector
                              value={emocional.propositos_salud}
                              onChange={next => setEmocional((prev) => ({ ...prev,propositos_salud: next }))}
                            />
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <MetroTileToggle
                            title="Propósitos Competencias"
                            icon="bi-award-fill"
                            color="navy"
                            size="wide"
                            subtitle="Despliega para elegir competencias a desarrollar"
                            badge={badgeCount(emocional.propositos_competencias)}
                          >
                            <div className="metro-twocol-grid">
                              <PropositosCompetenciasSelector
                                value={emocional.propositos_competencias}
                                onChange={next => setEmocional((prev) => ({ ...prev,propositos_competencias: next }))}
                              />
                            </div>
                          </MetroTileToggle>
                        </Col>
                        <Col xs={12}>
                          <Form.Check
                            type="checkbox"
                            id="terminos-movilidad"
                            label="Acepto los términos y condiciones *"
                            checked={emocional.acepto_terminos_y_condiciones}
                            onChange={e => setEmocional((prev) => ({ ...prev,acepto_terminos_y_condiciones: e.target.checked }))}
                          />
                        </Col>
                      </Row>
                      <div className="wizard-nav mt-4">
                        <Button variant="outline-secondary" onClick={() => setStep(2)}>
                          <i className="bi bi-arrow-left me-1" />Anterior
                        </Button>
                        <Button type="submit" variant="danger" disabled={isBusy}>
                          {paso3Mut.isPending ? <Spinner size="sm" className="me-1" /> : <i className="bi bi-arrow-right me-1" />}
                          Siguiente
                        </Button>
                      </div>
                    </Form>
                  ))()}

                  {/* ── Paso 4: Confirmación ── */}
                  {step === 4 && (() => (
                    exitoso ? (
                      <Alert variant="success" className="text-center">
                        <i className="bi bi-check-circle-fill fs-2 d-block mb-2" />
                        <strong>¡Registro completado!</strong>
                        <p className="mb-2">El asesor <strong>{documentoRegistrado || contacto.numero_documento}</strong> fue registrado exitosamente.</p>
                        <Button variant="success" onClick={() => {
                          setDocumentoEditar(null);
                          setContacto(initContacto);
                          setTributario(initTributario);
                          setEmocional(initEmocional);
                          setStep(1);
                          setExitoso(false);
                          setTab('lista');
                        }}>
                          <i className="bi bi-list-ul me-1" />Ver lista de asesores
                        </Button>
                      </Alert>
                    ) : (
                      <>
                        <h6 className="mb-3 text-muted">Datos de perfil de contacto</h6>
                        <div className="registro-resumen">
                          {construirResumenMov(
                            contacto, documentoRegistrado, departamentos, ciudades, canales, oficinas,
                          ).map(([label, value]) => (
                            <div key={label} className="registro-resumen__row">
                              <span className="registro-resumen__label">{label}</span>
                              <span className="registro-resumen__value">{value || '—'}</span>
                            </div>
                          ))}
                        </div>
                        <div className="wizard-nav mt-4">
                          <Button variant="outline-secondary" onClick={() => setStep(3)}>
                            <i className="bi bi-arrow-left me-1" />Anterior
                          </Button>
                          <Button variant="danger" onClick={handleFinalizar} disabled={isBusy}>
                            {finalizarMut.isPending ? <Spinner size="sm" className="me-1" /> : <i className="bi bi-check-circle me-1" />}
                            Finalizar Registro
                          </Button>
                        </div>
                      </>
                    )
                  ))()}
                </>
              )}
            </>
          ))()}
        </Card.Body>
      </Card>

      <ConfirmModal
        show={cuentaObjetivo !== null}
        title="Deshabilitar cuenta de acceso"
        message={
          cuentaObjetivo ? (
            <>
              ¿Confirma deshabilitar la cuenta de acceso de{' '}
              <strong>{cuentaObjetivo.nombre}</strong>?
              <br />
              <small className="text-muted">
                El comisionista no podrá iniciar sesión hasta que sea habilitado de nuevo
                por un administrador.
              </small>
            </>
          ) : (
            ''
          )
        }
        confirmLabel="Deshabilitar"
        confirmIcon="bi-person-fill-slash"
        confirmVariant="danger"
        loading={cambiarCuentaMut.isPending}
        loadingLabel="Deshabilitando…"
        onConfirm={confirmarDeshabilitarCuenta}
        onHide={() => setCuentaObjetivo(null)}
      />
    </div>
  );
}
