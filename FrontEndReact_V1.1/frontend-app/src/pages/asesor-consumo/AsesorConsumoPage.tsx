import { useEffect, useRef, useState } from 'react';
import TomSelect from 'tom-select';
import 'tom-select/dist/css/tom-select.bootstrap5.css';
import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Form,
  Nav,
  Row,
  Spinner,
  Table,
} from 'react-bootstrap';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../shared/api/client';
import { PageHeader } from '../../shared/ui/components/PageHeader';
import { ConfirmModal } from '../../shared/ui/components/ConfirmModal';
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
import {
  useAsesorConsumoList,
  useDetalleAsesorConsumo,
  useFinalizarConsumo,
  useSubprogramasConsumo,
  useWizardPaso1Consumo,
  useWizardPaso3Consumo,
} from '../../features/asesor-consumo/model/useAsesorConsumo';
import { verificarAsesorConsumoApi } from '../../features/asesor-consumo/model/apiAsesorConsumo';
import { useCambiarEstadoComisionista } from '../../features/admin-usuarios/model/useAdminUsuarios';
import { parseGenero, parseTipoDoc, refObj, strDe } from '../../shared/lib/parseContacto';

const PROGRAMA_CONSUMO_ID = 2 as const;

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

type Tab = 'lista' | 'registro';
type WizardStep = 1 | 2 | 3;

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
  comisionista_subprograma_id: number | '';
  cod_canales: number | '';
  cod_oficinas: number | '';
  acepto_habeas_data: boolean;
  incentivos: boolean;
  estado: 0 | 1 | null;
  firma_contrato: boolean | null;
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
  departamento: '', ciudad: '', comisionista_subprograma_id: 2,
  cod_canales: '', cod_oficinas: '',
  acepto_habeas_data: false,
  incentivos: false,
  estado: 1,
  firma_contrato: null,
};

const initEmocional: FormEmocional = {
  con_quien_vives: '', estado_civil: '', numero_hijos: '', info_hijos: '', hobbies: '',
  nivel_educativo: '', profesion: '', temas_a_profundizar: '', premios_gustaria_recibir: '',
  propositos_familiares: '', propositos_financieros: '', propositos_diversion: '',
  propositos_salud: '', propositos_competencias: '',
  numero_mascotas: '', info_mascotas: '', acepto_terminos_y_condiciones: false,
};

const GENERO_CONSUMO: Record<string, string> = {
  '0': 'Femenino', '1': 'Masculino',
  'F': 'Femenino', 'M': 'Masculino',
  'Femenino': 'Femenino', 'Masculino': 'Masculino', 'Otro': 'Otro', 'O': 'Otro',
};

function estadoConsumo(v: unknown): 0 | 1 | null {
  if (v === undefined || v === null) return null;
  return Number(v) === 1 ? 1 : 0;
}

function mapearContactoConsumoReg(
  c: Record<string, unknown>,
  documentoEditar: string | null,
): { form: FormContacto; selectedDid: number | null } {
  const depObj = refObj(c.departamento);
  const ciuObj = refObj(c.ciudad);
  const form: FormContacto = {
    numero_documento: String(c.numero_documento ?? documentoEditar),
    tipo_documento: parseTipoDoc(c.tipo_documento),
    nombre_completo: strDe(c.nombre_completo),
    genero: parseGenero(c.genero, GENERO_CONSUMO),
    fecha_nacimiento: c.fecha_nacimiento ? String(c.fecha_nacimiento) : '',
    celular: strDe(c.celular),
    telefono: strDe(c.telefono),
    email: c.email ? String(c.email) : '',
    direccion: strDe(c.direccion),
    departamento: depObj ? strDe(depObj.did) : strDe(c.departamento),
    ciudad: ciuObj ? strDe(ciuObj.cid) : strDe(c.ciudad),
    comisionista_subprograma_id: c.comisionista_subprograma_id ? Number(c.comisionista_subprograma_id) : 2,
    cod_canales: (c.cod_canales as number) ?? '',
    cod_oficinas: (c.cod_oficinas as number) ?? '',
    acepto_habeas_data: Boolean(c.acepto_habeas_data),
    incentivos: Boolean(c.incentivos),
    estado: estadoConsumo(c.estado),
    firma_contrato: c.firma_contrato !== undefined && c.firma_contrato !== null ? Boolean(c.firma_contrato) : null,
  };
  const did = depObj?.did;
  return { form, selectedDid: typeof did === 'number' ? did : null };
}

function mapearEmocionalConsumoReg(e: Record<string, unknown>): FormEmocional {
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

function badgeCount(s: string): number | null {
  return countSelections(s) || null;
}

function detalleError(err: unknown, fallback: string): string {
  const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
  return Array.isArray(msg) ? msg.join(' | ') : (msg ?? fallback);
}

function dash(v: string): string {
  return v || '—';
}

function algunoPendiente(...flags: boolean[]): boolean {
  return flags.some(Boolean);
}

function nombreEn<T>(items: T[] | undefined, match: (x: T) => boolean, get: (x: T) => string | null): string {
  const found = items?.find(match);
  return (found ? get(found) : null) ?? '—';
}

function etiquetaTipoDoc(t: string): string {
  if (t === 'CC') return 'C.C.';
  if (t === 'CE') return 'C.E.';
  if (t === 'NIT') return 'NIT';
  return t || '—';
}

function etiquetaEstado(e: 0 | 1 | null): string {
  if (e === 1) return 'Activo';
  if (e === 0) return 'Inactivo';
  return '—';
}

function etiquetaFirma(f: boolean | null): string {
  if (f === true) return 'Sí';
  if (f === false) return 'No';
  return '—';
}

function construirResumenConsumo(
  contacto: FormContacto,
  documentoRegistrado: string,
  departamentos: { did: number; departamento: string }[] | undefined,
  ciudades: { cid: number; ciudad: string }[] | undefined,
  subprogramas: { cspid: number; cspid_nombre: string }[] | undefined,
  canales: { cod_canales: number; nom_canales: string }[] | undefined,
  oficinas: { cod_oficinas: number; nom_oficinas: string | null }[] | undefined,
): [string, string][] {
  return [
    ['Tipo Documento', etiquetaTipoDoc(contacto.tipo_documento)],
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
    ['Programa', 'Consumo y Servicios'],
    ['Subprograma', nombreEn(subprogramas, (s) => s.cspid === contacto.comisionista_subprograma_id, (s) => s.cspid_nombre)],
    ['Canal', nombreEn(canales, (c) => String(c.cod_canales) === String(contacto.cod_canales), (c) => c.nom_canales)],
    ['Oficina', nombreEn(oficinas, (o) => String(o.cod_oficinas) === String(contacto.cod_oficinas), (o) => o.nom_oficinas)],
    ['Estado', etiquetaEstado(contacto.estado)],
    ['Firma Contrato', etiquetaFirma(contacto.firma_contrato)],
    ['Incentivos', contacto.incentivos ? 'Sí' : 'No'],
    ['Habeas Data', contacto.acepto_habeas_data ? 'Aceptado' : 'No aceptado'],
  ];
}

function payloadEmocionalConsumoReg(e: FormEmocional, numero_documento: string) {
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
    comisionista_programa_id: PROGRAMA_CONSUMO_ID,
    acepto_terminos_y_condiciones: 1 as const,
  };
}

function WizardStepper({ step }: { step: WizardStep }) {
  const steps: { label: string; icon: string }[] = [
    { label: 'Contacto',        icon: 'bi-person'       },
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

export function AsesorConsumoPage() {
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
  const [emocional, setEmocional] = useState<FormEmocional>(initEmocional);
  const [selectedDid, setSelectedDid] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [exitoso, setExitoso] = useState(false);
  const [documentoRegistrado, setDocumentoRegistrado] = useState('');
  // AP-0001: deshabilitar la cuenta de acceso del comisionista (distinto del estado de registro).
  const [cuentaObjetivo, setCuentaObjetivo] = useState<{ doc: string; nombre: string } | null>(null);
  const [cuentaMsg, setCuentaMsg] = useState('');
  const cambiarCuentaMut = useCambiarEstadoComisionista();
  const profesionSelectRef = useRef<HTMLSelectElement>(null);
  const tomSelectInstance = useRef<TomSelect | null>(null);
  const depSelectRef = useRef<HTMLSelectElement>(null);
  const depTomSelect = useRef<TomSelect | null>(null);
  const ciuSelectRef = useRef<HTMLSelectElement>(null);
  const ciuTomSelect = useRef<TomSelect | null>(null);
  const canalSelectRef = useRef<HTMLSelectElement>(null);
  const canalTomSelect = useRef<TomSelect | null>(null);
  const oficinaSelectRef = useRef<HTMLSelectElement>(null);
  const oficinaTomSelect = useRef<TomSelect | null>(null);

  const lista = useAsesorConsumoList(page, size, filtrosQuery);
  const detalle = useDetalleAsesorConsumo(documentoEditar);
  const subprogramas = useSubprogramasConsumo(PROGRAMA_CONSUMO_ID);
  const paso1Mut = useWizardPaso1Consumo();
  const paso3Mut = useWizardPaso3Consumo();
  const finalizarMut = useFinalizarConsumo();

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
    queryKey: ['canales-consumo', contacto.comisionista_subprograma_id],
    queryFn: () => apiClient.get<{ cod_canales: number; nom_canales: string; cpid: number; cspid: number }[]>(
      `/referencias/canales?cpid=${PROGRAMA_CONSUMO_ID}&cspid=${contacto.comisionista_subprograma_id}`
    ).then(r => r.data),
    enabled: contacto.comisionista_subprograma_id !== '',
  });

  const { data: oficinas } = useQuery({
    queryKey: ['oficinas-canal', contacto.cod_canales, contacto.comisionista_subprograma_id],
    queryFn: () => apiClient.get<{ cod_oficinas: number; nom_oficinas: string | null }[]>(
      `/referencias/oficinas?cod_canales=${contacto.cod_canales}&cspid=${contacto.comisionista_subprograma_id}`
    ).then(r => r.data),
    enabled: contacto.cod_canales !== '',
  });

  const { data: profesiones } = useQuery({
    queryKey: ['profesiones'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/profesiones').then(r => r.data),
  });


  useEffect(() => {
    if (!detalle.data || !documentoEditar) return;
    const contactoRaw = detalle.data.contacto as Record<string, unknown> | null;
    const emocionalRaw = detalle.data.emocional as Record<string, unknown> | null;
    if (contactoRaw) {
      const { form, selectedDid: did } = mapearContactoConsumoReg(contactoRaw, documentoEditar);
      if (did) setSelectedDid(did);
      setContacto(form);
      setFormReady(true);
    }
    if (emocionalRaw) setEmocional(mapearEmocionalConsumoReg(emocionalRaw));
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
        setSelectedDid(Number(value) || null);
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
  }, [ciudades, step, tab, formReady]);

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
  }, [oficinas, step, tab]);

  useEffect(() => {
    const ts = oficinaTomSelect.current; if (!ts) return;
    const val = contacto.cod_oficinas !== '' ? String(contacto.cod_oficinas) : '';
    if ((ts.getValue() as string) !== val) ts.setValue(val, true);
    const oficinaOptions = (oficinas ?? []).filter(oficina => oficina.nom_oficinas?.trim());
    if (contacto.cod_canales !== '' && oficinaOptions.length > 0) ts.enable();
    else ts.disable();
  }, [contacto.cod_oficinas, contacto.cod_canales, oficinas]);

  function handleBuscar() {
    const f: { tipo_doc?: string; documento?: string } = {};
    if (searchTipoDoc) f.tipo_doc = searchTipoDoc;
    if (searchDocumento) f.documento = searchDocumento;
    setFiltrosQuery(f);
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
    setFormReady(false);
    setEditTrigger((prev) => prev + 1);
    setContacto({ ...initContacto, numero_documento: documento });
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
    setFormReady(true);
    setDocumentoEditar(null);
    setContacto(initContacto);
    setEmocional(initEmocional);
    setStep(1);
    setError('');
    setExitoso(false);
    setTab('registro');
  }

  async function handlePaso1(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!contacto.acepto_habeas_data) { setError('Debe aceptar el habeas data'); return; }
    if (contacto.estado === null) { setError('Debe seleccionar el estado del asesor'); return; }
    if (!documentoEditar) {
      try {
        const check = await verificarAsesorConsumoApi(contacto.numero_documento);
        if (check.registrado) {
          setError(`El asesor con ${contacto.tipo_documento} ${contacto.numero_documento} ya está registrado`);
          return;
        }
      } catch {
        setError('No se pudo verificar el documento. Intente de nuevo.');
        return;
      }
    }
    try {
      const result = await paso1Mut.mutateAsync({
        numero_documento: contacto.numero_documento,
        tipo_documento: contacto.tipo_documento,
        nombre_completo: contacto.nombre_completo,
        genero: contacto.genero,
        fecha_nacimiento: contacto.fecha_nacimiento,
        celular: contacto.celular,
        telefono: contacto.telefono || null,
        email: contacto.email || null,
        direccion: contacto.direccion,
        departamento: contacto.departamento,
        ciudad: contacto.ciudad,
        comisionista_programa_id: PROGRAMA_CONSUMO_ID,
        comisionista_subprograma_id: Number(contacto.comisionista_subprograma_id),
        cod_canales: contacto.cod_canales !== '' ? Number(contacto.cod_canales) : null,
        cod_oficinas: contacto.cod_oficinas !== '' ? Number(contacto.cod_oficinas) : null,
        acepto_habeas_data: 1,
        incentivos: contacto.incentivos,
        estado: contacto.estado as 0 | 1,
        firma_contrato: contacto.firma_contrato,
      });
      setDocumentoRegistrado(result.numero_documento);
      setStep(2);
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(Array.isArray(msg) ? msg.join(' | ') : (msg ?? 'Error en paso 1'));
    }
  }

  async function handlePaso3(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (!emocional.acepto_terminos_y_condiciones) { setError('Debe aceptar los términos y condiciones'); return; }
    try {
      await paso3Mut.mutateAsync(
        payloadEmocionalConsumoReg(emocional, documentoRegistrado || contacto.numero_documento),
      );
      setStep(3);
    } catch (err: unknown) {
      setError(detalleError(err, 'Error en paso 3'));
    }
  }

  async function handleFinalizar() {
    setError('');
    try {
      await finalizarMut.mutateAsync(documentoRegistrado || contacto.numero_documento);
      setExitoso(true);
      lista.refetch();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(Array.isArray(msg) ? msg.join(' | ') : (msg ?? 'Error al finalizar'));
    }
  }

  const isBusy = algunoPendiente(paso1Mut.isPending, paso3Mut.isPending, finalizarMut.isPending);

  async function confirmarDeshabilitarCuenta() {
    if (!cuentaObjetivo) return;
    try {
      await cambiarCuentaMut.mutateAsync({
        programa: 'consumo',
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
        title="Asesor Consumo"
        subtitle="Gestión de asesores del programa Consumo y Servicios"
        icon="bi-person-plus-fill"
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
          <Nav variant="tabs" activeKey={tab} onSelect={(tabKey) => setTab(tabKey as Tab)}>
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
          </Nav>
        </Card.Header>

        <Card.Body className={tab === 'lista' ? 'p-0' : 'p-4'}>

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
                  Sin asesores de Consumo registrados
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
                      <th>Subprograma</th>
                      <th>Departamento</th>
                      <th>Ciudad</th>
                      <th>Estado</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {lista.data?.items.map((a) => (
                      <tr
                        key={a.numero_documento}
                        style={{ cursor: 'pointer' }}
                        onClick={() => abrirEdicion(a.numero_documento)}
                      >
                        <td className="font-monospace">{a.numero_documento}</td>
                        <td>{a.tipo_documento?.nombre ?? '—'}</td>
                        <td>{a.genero?.nombre ?? '—'}</td>
                        <td>{a.nombre_completo ?? '—'}</td>
                        <td>{a.celular ?? '—'}</td>
                        <td>{a.subprograma?.cspid_nombre ?? '—'}</td>
                        <td>{a.departamento?.departamento ?? '—'}</td>
                        <td>{a.ciudad?.ciudad ?? '—'}</td>
                        <td>
                          <Badge bg={a.estado === 1 ? 'success' : 'secondary'}>
                            {a.estado === 1 ? 'Activo' : 'Inactivo'}
                          </Badge>
                        </td>
                        <td onClick={(e) => e.stopPropagation()}>
                          <Button
                            variant="outline-secondary"
                            size="sm"
                            className="me-1"
                            title="Editar"
                            onClick={() => abrirEdicion(a.numero_documento)}
                          >
                            <i className="bi bi-pencil" />
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            title="Deshabilitar cuenta de acceso"
                            onClick={() =>
                              setCuentaObjetivo({
                                doc: a.numero_documento,
                                nombre: a.nombre_completo ?? a.numero_documento,
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
          {tab === 'registro' && (
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
                              <option value="CC">C.C.</option>
                              <option value="CE">C.E.</option>
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
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-map me-1 text-danger" />Departamento *</Form.Label>
                            <select ref={depSelectRef} className="form-select" />
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-pin-map me-1 text-danger" />Ciudad *</Form.Label>
                            <select ref={ciuSelectRef} className="form-select" />
                          </Form.Group>
                        </Col>
                        <Col md={4}>
                          <Form.Group>
                            <Form.Label><i className="bi bi-diagram-2 me-1 text-danger" />Subprograma</Form.Label>
                            <Form.Select
                              value={contacto.comisionista_subprograma_id}
                              onChange={e => setContacto((prev) => ({ ...prev,comisionista_subprograma_id: Number(e.target.value), cod_canales: '', cod_oficinas: '' }))}
                            >
                              <option value="">Seleccione...</option>
                              {subprogramas.data?.map(subprograma => (
                                <option key={subprograma.cspid} value={subprograma.cspid}>{subprograma.cspid_nombre}</option>
                              ))}
                            </Form.Select>
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
                                id="asesor-consumo-estado"
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
                                id="firma-contrato-si"
                                name="firma_contrato"
                                label="El contrato fue firmado"
                                checked={contacto.firma_contrato === true}
                                onChange={() => setContacto((prev) => ({ ...prev,firma_contrato: true }))}
                              />
                              <Form.Check
                                type="radio"
                                id="firma-contrato-no"
                                name="firma_contrato"
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
                            id="habeas-data-consumo"
                            label="Acepto el tratamiento de datos personales (Habeas Data) *"
                            checked={contacto.acepto_habeas_data}
                            onChange={e => setContacto((prev) => ({ ...prev,acepto_habeas_data: e.target.checked }))}
                          />
                        </Col>
                        <Col xs={12}>
                          <Form.Check
                            type="checkbox"
                            id="incentivos-consumo"
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

                  {/* ── Paso 2: Perfil Emocional ── */}
                  {step === 2 && (() => (
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
                            id="terminos-consumo"
                            label="Acepto los términos y condiciones *"
                            checked={emocional.acepto_terminos_y_condiciones}
                            onChange={e => setEmocional((prev) => ({ ...prev,acepto_terminos_y_condiciones: e.target.checked }))}
                          />
                        </Col>
                      </Row>
                      <div className="wizard-nav mt-4">
                        <Button variant="outline-secondary" onClick={() => setStep(1)}>
                          <i className="bi bi-arrow-left me-1" />Anterior
                        </Button>
                        <Button type="submit" variant="danger" disabled={isBusy}>
                          {paso3Mut.isPending ? <Spinner size="sm" className="me-1" /> : <i className="bi bi-arrow-right me-1" />}
                          Siguiente
                        </Button>
                      </div>
                    </Form>
                  ))()}

                  {/* ── Paso 3: Confirmación ── */}
                  {step === 3 && (() => (
                    exitoso ? (
                      <Alert variant="success" className="text-center">
                        <i className="bi bi-check-circle-fill fs-2 d-block mb-2" />
                        <strong>¡Registro completado!</strong>
                        <p className="mb-2">El asesor <strong>{documentoRegistrado || contacto.numero_documento}</strong> fue registrado exitosamente.</p>
                        <Button variant="success" onClick={() => {
                          setDocumentoEditar(null);
                          setContacto(initContacto);
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
                          {construirResumenConsumo(
                            contacto, documentoRegistrado, departamentos, ciudades,
                            subprogramas.data, canales, oficinas,
                          ).map(([label, value]) => (
                            <div key={label} className="registro-resumen__row">
                              <span className="registro-resumen__label">{label}</span>
                              <span className="registro-resumen__value">{value || '—'}</span>
                            </div>
                          ))}
                        </div>
                        <div className="wizard-nav mt-4">
                          <Button variant="outline-secondary" onClick={() => setStep(2)}>
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
          )}
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
