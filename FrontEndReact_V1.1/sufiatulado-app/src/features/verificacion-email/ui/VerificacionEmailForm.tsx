import { useState } from 'react';
import { Alert, Button, Form, InputGroup } from 'react-bootstrap';
import { useSearchParams } from 'react-router-dom';
import { getProblemMessage } from '../../../shared/api/problemDetails';
import { useConfirmarCodigo, useSolicitarCodigo } from '../model/useVerificacionEmail';
import { useFormTimeout } from '../../../shared/lib/useFormTimeout';
import { AUTH_FORM_TIMEOUT_MS } from '../../../shared/config/constants';

type Paso = 'solicitar' | 'confirmar' | 'verificado';

const TIPOS_DOCUMENTO: ReadonlyArray<{ value: string; label: string }> = [
  { value: 'C.C.', label: 'Cédula de ciudadanía' },
  { value: 'C.E.', label: 'Cédula de extranjería' },
  { value: 'TI', label: 'Tarjeta de identidad' },
  { value: 'PA', label: 'Pasaporte' },
  { value: 'NIT', label: 'NIT' },
];

const MENSAJE_NEUTRO =
  'Si los datos corresponden a un registro con correo, te enviamos un código de 8 dígitos. Revisa tu bandeja de entrada (y la carpeta de spam).';

export function VerificacionEmailForm() {
  // El enlace del correo trae ?doc=&tipo= → aterrizamos directo en el paso de
  // ingresar el código, con el documento ya resuelto (solo falta teclear el código).
  const [searchParams] = useSearchParams();
  const docParam = (searchParams.get('doc') ?? '').replace(/\D/g, '').slice(0, 20);
  const tipoParam = searchParams.get('tipo');
  const tipoInicial = TIPOS_DOCUMENTO.some((t) => t.value === tipoParam) ? tipoParam! : 'C.C.';

  const [paso, setPaso] = useState<Paso>(docParam ? 'confirmar' : 'solicitar');
  const [tipoDocumento, setTipoDocumento] = useState(tipoInicial);
  const [numeroDocumento, setNumeroDocumento] = useState(docParam);
  const [codigo, setCodigo] = useState('');
  const [emailEnmascarado, setEmailEnmascarado] = useState<string | null>(null);
  const [expirado, setExpirado] = useState(false);

  const solicitar = useSolicitarCodigo();
  const confirmar = useConfirmarCodigo();

  // AP-0018: límite absoluto de 1 min desde la primera interacción. Vencido el
  // plazo sin enviar, se borran el documento/código tecleados y se vuelve al inicio.
  const hayInteraccion: boolean =
    paso !== 'verificado' && (numeroDocumento.length > 0 || codigo.length > 0);
  useFormTimeout({
    delayMs: AUTH_FORM_TIMEOUT_MS,
    active: hayInteraccion && !solicitar.isPending && !confirmar.isPending,
    onTimeout: () => {
      setNumeroDocumento('');
      setCodigo('');
      setEmailEnmascarado(null);
      confirmar.reset();
      setPaso('solicitar');
      setExpirado(true);
    },
  });

  function handleSolicitar(e: React.FormEvent) {
    e.preventDefault();
    confirmar.reset();
    solicitar.mutate(
      { tipo_documento: tipoDocumento, numero_documento: numeroDocumento },
      {
        onSuccess: (data) => {
          setEmailEnmascarado(data.email_enmascarado);
          setCodigo('');
          setPaso('confirmar');
        },
      },
    );
  }

  function handleConfirmar(e: React.FormEvent) {
    e.preventDefault();
    confirmar.mutate(
      { tipo_documento: tipoDocumento, numero_documento: numeroDocumento, codigo },
      { onSuccess: () => setPaso('verificado') },
    );
  }

  function handleReenviar() {
    confirmar.reset();
    solicitar.mutate({ tipo_documento: tipoDocumento, numero_documento: numeroDocumento });
  }

  // ── Paso 3: verificado ─────────────────────────────────────────────────────
  if (paso === 'verificado') {
    return (
      <div className="text-center py-3">
        <div
          className="d-inline-flex align-items-center justify-content-center rounded-circle mb-3"
          style={{ width: 72, height: 72, background: '#D1F4E0' }}
        >
          <i className="bi bi-check-lg" style={{ fontSize: '2.5rem', color: '#0F7B4E' }} />
        </div>
        <h4 className="fw-bold mb-2" style={{ color: '#100941' }}>
          Correo verificado
        </h4>
        <p className="text-muted mb-0" style={{ fontSize: '0.9rem' }}>
          Confirmamos que el correo te pertenece. Ya puedes cerrar esta ventana.
        </p>
      </div>
    );
  }

  // ── Paso 2: confirmar código ───────────────────────────────────────────────
  if (paso === 'confirmar') {
    return (
      <Form onSubmit={handleConfirmar} noValidate style={{ width: '100%' }}>
        <h4 className="fw-bold mb-1" style={{ color: '#100941' }}>
          Ingresa el código
        </h4>
        <Alert variant="info" className="py-2 px-3 mb-3" style={{ fontSize: '0.85rem' }}>
          <i className="bi bi-envelope-check me-2" />
          {emailEnmascarado
            ? `Enviamos un código de 8 dígitos a ${emailEnmascarado}.`
            : MENSAJE_NEUTRO}
        </Alert>

        {confirmar.isError && (
          <Alert variant="danger" className="py-2 px-3" style={{ fontSize: '0.85rem' }}>
            <i className="bi bi-exclamation-circle me-2" />
            {getProblemMessage(confirmar.error, 'No se pudo validar el código.')}
          </Alert>
        )}

        <Form.Group className="mb-3">
          <Form.Label>Código de verificación</Form.Label>
          <InputGroup>
            <InputGroup.Text className="bg-light border-end-0">
              <i className="bi bi-shield-lock text-muted" />
            </InputGroup.Text>
            <Form.Control
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              placeholder="8 dígitos"
              value={codigo}
              maxLength={8}
              onChange={(e) => setCodigo(e.target.value.replace(/\D/g, '').slice(0, 8))}
              required
              autoFocus
              className="border-start-0"
              style={{ letterSpacing: '0.3rem', fontWeight: 600 }}
            />
          </InputGroup>
        </Form.Group>

        <Button
          type="submit"
          variant="primary"
          className="w-100 py-2 mb-2"
          disabled={confirmar.isPending || codigo.length !== 8}
        >
          {confirmar.isPending ? (
            <>
              <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
              Verificando...
            </>
          ) : (
            <>
              <i className="bi bi-check2-circle me-2" />
              Verificar correo
            </>
          )}
        </Button>

        <div className="d-flex justify-content-between">
          <Button
            variant="link"
            type="button"
            className="px-0 text-decoration-none"
            style={{ fontSize: '0.85rem' }}
            onClick={() => setPaso('solicitar')}
          >
            <i className="bi bi-arrow-left me-1" />
            Cambiar documento
          </Button>
          <Button
            variant="link"
            type="button"
            className="px-0 text-decoration-none"
            style={{ fontSize: '0.85rem' }}
            onClick={handleReenviar}
            disabled={solicitar.isPending}
          >
            {solicitar.isPending ? 'Reenviando...' : 'Reenviar código'}
          </Button>
        </div>
      </Form>
    );
  }

  // ── Paso 1: solicitar código ───────────────────────────────────────────────
  return (
    <Form onSubmit={handleSolicitar} noValidate style={{ width: '100%' }}>
      <h4 className="fw-bold mb-1" style={{ color: '#100941' }}>
        Verifica tu correo
      </h4>
      <p className="text-muted mb-4" style={{ fontSize: '0.875rem' }}>
        Te enviaremos un código al correo registrado para confirmar que te pertenece.
      </p>

      {expirado && (
        <Alert variant="warning" className="py-2 px-3 mb-3" style={{ fontSize: '0.85rem' }}>
          <i className="bi bi-clock-history me-2" />
          Por seguridad se limpiaron tus datos tras 1 minuto sin enviarlos. Ingrésalos de nuevo.
        </Alert>
      )}

      <Form.Group className="mb-3">
        <Form.Label>Tipo de documento</Form.Label>
        <Form.Select value={tipoDocumento} onChange={(e) => setTipoDocumento(e.target.value)}>
          {TIPOS_DOCUMENTO.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </Form.Select>
      </Form.Group>

      <Form.Group className="mb-4">
        <Form.Label>Número de documento</Form.Label>
        <InputGroup>
          <InputGroup.Text className="bg-light border-end-0">
            <i className="bi bi-person-vcard text-muted" />
          </InputGroup.Text>
          <Form.Control
            type="text"
            inputMode="numeric"
            placeholder="Solo números"
            value={numeroDocumento}
            onChange={(e) => {
              setNumeroDocumento(e.target.value.replace(/\D/g, '').slice(0, 20));
              setExpirado(false);
            }}
            required
            autoFocus
            className="border-start-0"
          />
        </InputGroup>
      </Form.Group>

      <Button
        type="submit"
        variant="primary"
        className="w-100 py-2"
        disabled={solicitar.isPending || numeroDocumento.length < 3}
      >
        {solicitar.isPending ? (
          <>
            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
            Enviando código...
          </>
        ) : (
          <>
            <i className="bi bi-envelope-arrow-up me-2" />
            Enviar código
          </>
        )}
      </Button>
    </Form>
  );
}
