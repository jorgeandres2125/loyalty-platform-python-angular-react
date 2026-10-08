import { type ReactNode, type CSSProperties, type KeyboardEvent } from 'react';
import '../../../styles/components/IconPillButton.scss';

export type IconPillColor =
  | 'red'
  | 'navy'
  | 'blue'
  | 'gold'
  | 'yellow'
  | 'dark-navy'
  | 'teal'
  | 'green'
  | 'gray'
  | 'orange'
  | 'purple';

interface CustomColor {
  base: string;
  dark: string;
}

interface IconPillButtonProps {
  label: string;
  icon: ReactNode | string;
  color?: IconPillColor;
  customColor?: CustomColor;
  selected?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  ariaLabel?: string;
  className?: string;
}

export function IconPillButton({
  label,
  icon,
  color = 'blue',
  customColor,
  selected = false,
  disabled = false,
  onClick,
  ariaLabel,
  className = '',
}: IconPillButtonProps) {
  const colorClass: string = customColor ? 'has-custom-color' : `icon-pill--${color}`;
  const style: CSSProperties | undefined = customColor
    ? ({
        '--icon-pill-color': customColor.base,
        '--icon-pill-color-dark': customColor.dark,
      } as CSSProperties)
    : undefined;

  function handleKey(e: KeyboardEvent<HTMLButtonElement>): void {
    if (disabled) return;
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault();
      onClick?.();
    }
  }

  return (
    <button
      type="button"
      className={`icon-pill ${colorClass} ${selected ? 'is-selected' : ''} ${disabled ? 'is-disabled' : ''} ${className}`}
      aria-pressed={selected}
      aria-label={ariaLabel ?? label}
      disabled={disabled}
      onClick={onClick}
      onKeyDown={handleKey}
      style={style}
    >
      <span className="icon-pill__icon" aria-hidden="true">
        {typeof icon === 'string' ? <i className={`bi ${icon}`} /> : icon}
      </span>
      <span className="icon-pill__label">{label}</span>
    </button>
  );
}
