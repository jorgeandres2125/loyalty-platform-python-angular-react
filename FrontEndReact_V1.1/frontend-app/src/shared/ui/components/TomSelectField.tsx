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
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
}

export function TomSelectField({
  id, options, value, onChange,
  placeholder = '— Seleccionar —',
  disabled = false,
  required = false,
}: Props) {
  const elRef = useRef<HTMLSelectElement>(null);
  const tsRef = useRef<InstanceType<typeof TomSelectLib> | null>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  // Inicializa una sola vez
  useEffect(() => {
    if (!elRef.current) return;
    const ts = new TomSelectLib(elRef.current, {
      valueField: 'value',
      labelField: 'label',
      searchField: ['label'],
      placeholder,
      options: options.map((option) => ({ value: option.value, label: option.label })),
      items: value ? [value] : [],
      onChange(v: unknown) {
        onChangeRef.current(typeof v === 'string' ? v : '');
      },
    });
    tsRef.current = ts;
    return () => {
      ts.destroy();
      tsRef.current = null;
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sincroniza opciones cuando cambian (ej. cambio de departamento)
  useEffect(() => {
    const ts = tsRef.current;
    if (!ts) return;
    ts.clearOptions();
    options.forEach((option) => ts.addOption({ value: option.value, label: option.label }));
    ts.refreshOptions(false);
    // Restaura el valor si todavía es válido; de lo contrario limpia
    if (value && options.some((option) => option.value === value)) {
      ts.setValue(value, true);
    } else {
      ts.clear(true);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [options]);

  // Sincroniza valor desde fuera (carga de edición, reset)
  useEffect(() => {
    const ts = tsRef.current;
    if (!ts) return;
    const cur = String(ts.getValue() ?? '');
    if (cur !== (value ?? '')) {
      ts.setValue(value || '', true);
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
      className="form-select"
      defaultValue={value}
    />
  );
}
