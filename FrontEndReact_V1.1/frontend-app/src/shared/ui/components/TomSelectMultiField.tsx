import { useEffect, useRef } from 'react';
import TomSelectLib from 'tom-select';
import 'tom-select/dist/css/tom-select.bootstrap5.css';

export interface TomSelectOption {
  value: string;
  label: string;
}

interface Props {
  id: string;
  options: TomSelectOption[];
  value: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  maxItems?: number | null;
  maxOptions?: number;
}

export function TomSelectMultiField({
  id,
  options,
  value,
  onChange,
  placeholder = '— Seleccionar —',
  disabled = false,
  required = false,
  maxItems = null,
  maxOptions,
}: Props) {
  const elRef = useRef<HTMLSelectElement>(null);
  const tsRef = useRef<InstanceType<typeof TomSelectLib> | null>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  // Inicializa una sola vez
  useEffect(() => {
    if (!elRef.current) return;
    const ts = new TomSelectLib(elRef.current, {
      plugins: ['remove_button'],
      valueField: 'value',
      labelField: 'label',
      searchField: ['label'],
      placeholder,
      maxItems: maxItems ?? undefined,
      maxOptions: maxOptions ?? options.length,
      options: options.map((option) => ({ value: option.value, label: option.label })),
      items: value,
      onChange(v: unknown) {
        if (Array.isArray(v)) {
          onChangeRef.current(v.map((item) => String(item)));
        } else if (typeof v === 'string' && v !== '') {
          onChangeRef.current([v]);
        } else {
          onChangeRef.current([]);
        }
      },
    });
    tsRef.current = ts;
    return () => {
      ts.destroy();
      tsRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sincroniza opciones cuando cambian (sin destruir la instancia)
  useEffect(() => {
    const ts = tsRef.current;
    if (!ts) return;
    ts.clearOptions();
    options.forEach((option) => ts.addOption({ value: option.value, label: option.label }));
    // Re-aplica maxOptions: la lista activa real es la fuente de verdad
    ts.settings.maxOptions = maxOptions ?? options.length;
    ts.refreshOptions(false);
    // Mantener solo los valores que siguen siendo válidos
    const valid: string[] = value.filter((val) => options.some((option) => option.value === val));
    ts.setValue(valid, true);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options, maxOptions]);

  // Sincroniza valores desde fuera (carga de edición, reset)
  useEffect(() => {
    const ts = tsRef.current;
    if (!ts) return;
    const raw: unknown = ts.getValue();
    const curArr: string[] = Array.isArray(raw)
      ? raw.map((item) => String(item))
      : raw
        ? [String(raw)]
        : [];
    const sameLength: boolean = curArr.length === value.length;
    const sameItems: boolean = sameLength && curArr.every((item) => value.includes(item));
    if (!sameItems) {
      ts.setValue(value, true);
    }
  }, [value]);

  // Sincroniza estado habilitado/deshabilitado
  useEffect(() => {
    const ts = tsRef.current;
    if (!ts) return;
    if (disabled) ts.disable();
    else ts.enable();
  }, [disabled]);

  return (
    <select
      ref={elRef}
      id={id}
      required={required}
      multiple
      className="form-select"
    />
  );
}
