import { useEffect, useRef, useState } from 'react';
import TomSelect from 'tom-select';
import 'tom-select/dist/css/tom-select.bootstrap5.css';
import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  Nav,
  Row,
  Spinner,
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
import {
  useDetalleAsesorConsumo,
  useSubprogramasConsumo,
  useWizardPaso1Consumo,
  useWizardPaso3Consumo,
} from '../../features/asesor-consumo/model/useAsesorConsumo';
import { useAuthStore } from '../../entities/user/model/authStore';

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

function toJsonStr(v: unknown): string {
  if (Array.isArray(v)) return v.length === 0 ? '' : JSON.stringify(v);
  if (typeof v === 'string') return v;
  return '';
}

function fromJsonStr(s: string): string[] {
  if (!s) return [];
  try {
    const parsed: unknown = JSON.parse(s);
    if (Array.isArray(parsed)) return parsed.map(String);
  } catch {
    /* ignore */
  }
  return [];
}

type PerfilTab = 'contacto' | 'emocional';

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
  departamento: '', ciudad: '', comisionista_subprograma_id: '',
  cod_canales: '', cod_oficinas: '',
  acepto_habeas_data: true,
  incentivos: false,
  estado: 1,
  firma_contrato: null,
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

// ── Helpers puros de parseo del contacto recibido del backend (AP-0036) ──────
function _str(v: unknown): string {
  return v === null || v === undefined ? '' : String(v);
}

function _refObj(raw: unknown): Record<string, unknown> | null {
  return typeof raw === 'object' && raw !== null ? (raw as Record<string, unknown>) : null;
}

function _refId(raw: unknown, key: string): number | '' {
  if (typeof raw === 'object' && raw !== null) {
    const v = (raw as Record<string, unknown>)[key];
    return typeof v === 'number' ? v : '';
  }
  return typeof raw === 'number' ? raw : '';
}

function _parseTipoDoc(raw: unknown): string {
  if (typeof raw === 'object' && raw !== null) {
    return (raw as Record<string, string>).codigo ?? 'CC';
  }
  return typeof raw === 'string' ? raw : 'CC';
}

function _parseGenero(raw: unknown): string {
  if (typeof raw === 'object' && raw !== null) {
    return (raw as Record<string, string>).nombre ?? '';
  }
  if (typeof raw === 'string') {
    return _GENERO_NOMBRE[raw] ?? raw;
  }
  return '';
}

function _parseEstado(v: unknown): 0 | 1 | null {
  if (v === 1) return 1;
  if (v === 0) return 0;
  return null;
}

function _parseFirma(v: unknown): boolean | null {
  return v !== undefined && v !== null ? Boolean(v) : null;
}

function mapearContactoConsumo(
  c: Record<string, unknown>,
): { form: FormContacto; selectedDid: number | null } {
  const depObj = _refObj(c.departamento);
  const ciuObj = _refObj(c.ciudad);
  const fechaNac = typeof c.fecha_nacimiento === 'string' ? c.fecha_nacimiento.slice(0, 10) : '';
  const form: FormContacto = {
    numero_documento: _str(c.numero_documento),
    tipo_documento: _parseTipoDoc(c.tipo_documento).replace(/\./g, ''),
    nombre_completo: _str(c.nombre_completo),
    genero: _parseGenero(c.genero),
    fecha_nacimiento: fechaNac,
    celular: _str(c.celular),
    telefono: c.telefono ? String(c.telefono) : '',
    email: c.email ? String(c.email) : '',
    direccion: _str(c.direccion),
    departamento: depObj ? _str(depObj.did) : _str(c.departamento),
    ciudad: ciuObj ? _str(ciuObj.cid) : _str(c.ciudad),
    comisionista_subprograma_id: _refId(c.comisionista_subprograma_id, 'cspid'),
    cod_canales: _refId(c.cod_canales, 'cod_canales'),
    cod_oficinas: _refId(c.cod_oficinas, 'cod_oficinas'),
    acepto_habeas_data: Boolean(c.acepto_habeas_data),
    incentivos: Boolean(c.incentivos),
    estado: _parseEstado(c.estado),
    firma_contrato: _parseFirma(c.firma_contrato),
  };
  const did = _refId(c.departamento, 'did');
  return { form, selectedDid: typeof did === 'number' ? did : null };
}

function BotonGuardar({ pending, disabled }: { pending: boolean; disabled: boolean }) {
  return (
    <Button type="submit" variant="danger" disabled={disabled}>
      {pending ? <Spinner size="sm" className="me-2" /> : <i className="bi bi-check-circle me-2" />}
      Guardar
    </Button>
  );
}

function payloadEmocionalConsumo(e: FormEmocional, numero_documento: string | null) {
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

export function PerfilConsumoPage() {
  const [tab, setTab] = useState<PerfilTab>('contacto');
  const [contacto, setContacto] = useState<FormContacto>(initContacto);
  const [emocional, setEmocional] = useState<FormEmocional>(initEmocional);
  const [selectedDid, setSelectedDid] = useState<number | null>(null);
  const [error, setError] = useState('');
  const [okMsg, setOkMsg] = useState('');
  const [datosListos, setDatosListos] = useState(false);

  const miDocumento = useAuthStore((state) => state.user?.username) ?? null;
  const detalle = useDetalleAsesorConsumo(miDocumento);
  const guardarContacto = useWizardPaso1Consumo();
  const guardarEmocional = useWizardPaso3Consumo();
  const subprogramas = useSubprogramasConsumo(PROGRAMA_CONSUMO_ID);

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
      `/referencias/canales?cpid=${PROGRAMA_CONSUMO_ID}&cspid=${contacto.comisionista_subprograma_id}`,
    ).then(r => r.data),
    enabled: contacto.comisionista_subprograma_id !== '',
  });

  const { data: oficinas } = useQuery({
    queryKey: ['oficinas-canal', contacto.cod_canales, contacto.comisionista_subprograma_id],
    queryFn: () => apiClient.get<{ cod_oficinas: number; nom_oficinas: string | null }[]>(
      `/referencias/oficinas?cod_canales=${contacto.cod_canales}&cspid=${contacto.comisionista_subprograma_id}`,
    ).then(r => r.data),
    enabled: contacto.cod_canales !== '',
  });

  const { data: profesiones } = useQuery({
    queryKey: ['profesiones'],
    queryFn: () => apiClient.get<{ tid: number; nombre: string }[]>('/referencias/profesiones').then(r => r.data),
  });

  // ── TomSelect refs ────────────────────────────────────────────────────────
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

  // ── Cargar datos del usuario logueado ────────────────────────────────────
  useEffect(() => {
    if (!detalle.data) return;
    const contactoData = detalle.data.contacto as Record<string, unknown> | null | undefined;
    if (!contactoData) {
      setDatosListos(true);
      return;
    }
    const { form, selectedDid: did } = mapearContactoConsumo(contactoData);
    if (did) setSelectedDid(did);
    setContacto(form);
    setDatosListos(true);
  }, [detalle.data]);

  useEffect(() => {
    const emocionalData = detalle.data?.emocional as Record<string, unknown> | null | undefined;
    if (!emocionalData) return;
    setEmocional({
      con_quien_vives: toJsonStr(emocionalData.con_quien_vives),
      estado_civil: String(emocionalData.estado_civil ?? ''),
      numero_hijos: emocionalData.numero_hijos != null ? String(emocionalData.numero_hijos) : '',
      info_hijos: String(emocionalData.info_hijos ?? ''),
      hobbies: toJsonStr(emocionalData.hobbies),
      nivel_educativo: String(emocionalData.nivel_educativo ?? ''),
      profesion: String(emocionalData.profesion ?? ''),
      temas_a_profundizar: toJsonStr(emocionalData.temas_a_profundizar),
      premios_gustaria_recibir: toJsonStr(emocionalData.premios_gustaria_recibir),
      propositos_familiares: toJsonStr(emocionalData.propositos_familiares),
      propositos_financieros: toJsonStr(emocionalData.propositos_financieros),
      propositos_diversion: toJsonStr(emocionalData.propositos_diversion),
      propositos_salud: toJsonStr(emocionalData.propositos_salud),
      propositos_competencias: toJsonStr(emocionalData.propositos_competencias),
      numero_mascotas: emocionalData.numero_mascotas != null ? String(emocionalData.numero_mascotas) : '',
      info_mascotas: String(emocionalData.info_mascotas ?? ''),
      acepto_terminos_y_condiciones: Boolean(emocionalData.acepto_terminos_y_condiciones ?? true),
    });
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
        // Solo limpiar ciudad si el departamento REALMENTE cambió,
        // así TomSelect re-creándose por cambio de opciones no pisa la ciudad.
        setContacto((prev) => {
          if (prev.departamento === value) return prev;
          setSelectedDid(Number(value) || null);
          return { ...prev, departamento: value, ciudad: '' };
        });
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
        setContacto((prev) => (prev.ciudad === value ? prev : { ...prev, ciudad: value }));
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
        setContacto((prev) => ({ ...prev, cod_canales: value !== '' ? Number(value) : '', cod_oficinas: '' }));
      },
    });
    if (canalOptions.length === 0) canalTomSelect.current.lock();
    return () => { canalTomSelect.current?.destroy(); canalTomSelect.current = null; };
  }, [canales, tab]);

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
      },
    });
    if (contacto.cod_canales !== '' && oficinaOptions.length > 0) oficinaTomSelect.current.enable();
    else oficinaTomSelect.current.disable();
    return () => { oficinaTomSelect.current?.destroy(); oficinaTomSelect.current = null; };
  }, [oficinas, tab]);

  useEffect(() => {
    const ts = oficinaTomSelect.current; if (!ts) return;
    const val = contacto.cod_oficinas !== '' ? String(contacto.cod_oficinas) : '';
    if ((ts.getValue() as string) !== val) ts.setValue(val, true);
    const oficinaOptions = (oficinas ?? []).filter(oficina => oficina.nom_oficinas?.trim());
    if (contacto.cod_canales !== '' && oficinaOptions.length > 0) ts.enable();
    else ts.disable();
  }, [contacto.cod_oficinas, contacto.cod_canales, oficinas]);

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
        setEmocional(prev => ({ ...prev, profesion: value }));
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

  const setEmo = <K extends keyof FormEmocional>(key: K, value: FormEmocional[K]) =>
    setEmocional(prev => ({ ...prev, [key]: value }));

  const setEmoList = (key: keyof FormEmocional, jsonStr: string) => {
    const arr = fromJsonStr(jsonStr);
    setEmocional(prev => ({ ...prev, [key]: arr.length ? JSON.stringify(arr) : '' }));
  };

  async function handleGuardarContacto(e: React.FormEvent) {
    e.preventDefault();
    setError(''); setOkMsg('');
    if (!contacto.departamento) { setError('Debe seleccionar un Departamento'); return; }
    if (!contacto.ciudad) { setError('Debe seleccionar una ciudad'); return; }
    if (!contacto.acepto_habeas_data) { setError('Debe aceptar el habeas data'); return; }
    if (contacto.estado === null) { setError('Debe seleccionar el estado del asesor'); return; }
    try {
      const result = await guardarContacto.mutateAsync({
        numero_documento: contacto.numero_documento || miDocumento,
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
      setOkMsg('Datos de contacto guardados.');
      if (result?.numero_documento) detalle.refetch();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(Array.isArray(msg) ? msg.join(' | ') : (msg ?? 'Error en paso 1'));
    }
  }

  async function handleGuardarEmocional(e: React.FormEvent) {
    e.preventDefault();
    setError(''); setOkMsg('');
    if (!emocional.acepto_terminos_y_condiciones) {
      setError('Debe aceptar los términos y condiciones'); return;
    }
    try {
      await guardarEmocional.mutateAsync(
        payloadEmocionalConsumo(emocional, contacto.numero_documento || miDocumento),
      );
      setOkMsg('Perfil emocional guardado.');
      detalle.refetch();
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(Array.isArray(msg) ? msg.join(' | ') : (msg ?? 'Error en paso 3'));
    }
  }

  const isBusy = guardarContacto.isPending || guardarEmocional.isPending;
  // No incluyo detalle.isFetching: en un refetch (tras guardar o tocar "Recargar")
  // queremos que el form siga montado para que los TomSelect conserven su selección.
  const cargando = !datosListos || detalle.isLoading;

  useEffect(() => {
    if (!okMsg) return;
    const timeoutId = setTimeout(() => setOkMsg(''), 10_000);
    return () => clearTimeout(timeoutId);
  }, [okMsg]);

  useEffect(() => {
    if (!error) return;
    const timeoutId = setTimeout(() => setError(''), 10_000);
    return () => clearTimeout(timeoutId);
  }, [error]);

  return (
    <div>
      <PageHeader
        title="Mi Perfil — Comisionista Consumo"
        subtitle="Edita tus datos de contacto y tu perfil emocional"
        icon="bi-person-circle"
      />

      <Card className="shadow-sm" style={{ border: 'none' }}>
        <Card.Header className="bg-white border-0 pt-3">
          <Nav variant="tabs" activeKey={tab} onSelect={(tabKey) => tabKey && setTab(tabKey as PerfilTab)}>
            <Nav.Item>
              <Nav.Link eventKey="contacto">
                <i className="bi bi-person me-2" />Contacto
              </Nav.Link>
            </Nav.Item>
            <Nav.Item>
              <Nav.Link eventKey="emocional">
                <i className="bi bi-heart me-2" />Perfil Emocional
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
              {tab === 'contacto' && (
                <Form onSubmit={handleGuardarContacto}>
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
                          onChange={e => setContacto((prev) => ({ ...prev,comisionista_subprograma_id: e.target.value === '' ? '' : Number(e.target.value), cod_canales: '', cod_oficinas: '' }))}
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
                            id="perfil-consumo-estado"
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
                          <Form.Check
                            type="radio"
                            id="perfil-firma-contrato-si"
                            name="firma_contrato"
                            label="El contrato fue firmado"
                            checked={contacto.firma_contrato === true}
                            onChange={() => setContacto((prev) => ({ ...prev,firma_contrato: true }))}
                          />
                          <Form.Check
                            type="radio"
                            id="perfil-firma-contrato-no"
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
                        id="perfil-habeas-data-consumo"
                        label="Acepto el tratamiento de datos personales (Habeas Data) *"
                        checked={contacto.acepto_habeas_data}
                        onChange={e => setContacto((prev) => ({ ...prev,acepto_habeas_data: e.target.checked }))}
                      />
                    </Col>
                    <Col xs={12}>
                      <Form.Check
                        type="checkbox"
                        id="perfil-incentivos-consumo"
                        label="Tiene Incentivos"
                        checked={contacto.incentivos}
                        onChange={e => setContacto((prev) => ({ ...prev,incentivos: e.target.checked }))}
                        disabled
                      />
                    </Col>
                  </Row>
                  <div className="d-flex justify-content-end mt-4">
                    <BotonGuardar pending={guardarContacto.isPending} disabled={isBusy} />
                  </div>
                </Form>
              )}

              {/* ── Tab: Perfil Emocional ── */}
              {tab === 'emocional' && (
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
                      <MetroTileToggle
                        title="¿Con quién vives?"
                        icon="bi-people-fill"
                        color="red"
                        size="medium"
                        subtitle="Selecciona una o varias opciones"
                        badge={countSelections(emocional.con_quien_vives) || null}
                      >
                        <ConQuienVivesSelector
                          value={emocional.con_quien_vives}
                          onChange={next => setEmoList('con_quien_vives', next)}
                        />
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <MetroTileToggle
                        title="Premios que te gustaría recibir"
                        icon="bi-trophy-fill"
                        color="gold"
                        size="medium"
                        subtitle="Marca todos los premios de tu interés"
                        badge={countSelections(emocional.premios_gustaria_recibir) || null}
                      >
                        <PremiosSelector
                          value={emocional.premios_gustaria_recibir}
                          onChange={next => setEmoList('premios_gustaria_recibir', next)}
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
                        badge={countSelections(emocional.hobbies) || null}
                      >
                        <div className="metro-hobbies-grid">
                          <HobbiesSelector
                            value={emocional.hobbies}
                            onChange={next => setEmoList('hobbies', next)}
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
                        badge={countSelections(emocional.temas_a_profundizar) || null}
                      >
                        <TemasProfundizarSelector
                          value={emocional.temas_a_profundizar}
                          onChange={next => setEmoList('temas_a_profundizar', next)}
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
                        badge={countSelections(emocional.propositos_familiares) || null}
                      >
                        <PropositosFamiliaresSelector
                          value={emocional.propositos_familiares}
                          onChange={next => setEmoList('propositos_familiares', next)}
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
                        badge={countSelections(emocional.propositos_financieros) || null}
                      >
                        <PropositosFinancierosSelector
                          value={emocional.propositos_financieros}
                          onChange={next => setEmoList('propositos_financieros', next)}
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
                        badge={countSelections(emocional.propositos_diversion) || null}
                      >
                        <div className="metro-twocol-grid">
                          <PropositosDiversionSelector
                            value={emocional.propositos_diversion}
                            onChange={next => setEmoList('propositos_diversion', next)}
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
                        badge={countSelections(emocional.propositos_salud) || null}
                      >
                        <PropositosSaludSelector
                          value={emocional.propositos_salud}
                          onChange={next => setEmoList('propositos_salud', next)}
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
                        badge={countSelections(emocional.propositos_competencias) || null}
                      >
                        <div className="metro-twocol-grid">
                          <PropositosCompetenciasSelector
                            value={emocional.propositos_competencias}
                            onChange={next => setEmoList('propositos_competencias', next)}
                          />
                        </div>
                      </MetroTileToggle>
                    </Col>
                    <Col xs={12}>
                      <Form.Check
                        type="checkbox"
                        id="perfil-terminos-consumo"
                        label="Acepto los términos y condiciones *"
                        checked={emocional.acepto_terminos_y_condiciones}
                        onChange={e => setEmo('acepto_terminos_y_condiciones', e.target.checked)}
                      />
                    </Col>
                  </Row>
                  <div className="d-flex justify-content-end mt-4">
                    <BotonGuardar pending={guardarEmocional.isPending} disabled={isBusy} />
                  </div>
                </Form>
              )}
            </>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}
