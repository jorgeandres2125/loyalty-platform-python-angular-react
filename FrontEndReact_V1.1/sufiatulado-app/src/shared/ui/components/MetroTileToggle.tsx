import { useState, useId, type ReactNode, type CSSProperties } from 'react';
import { motion, AnimatePresence, type Variants } from 'framer-motion';
import '../../../styles/components/MetroTileToggle.scss';

export type MetroTileSize = 'small' | 'medium' | 'wide';

export type MetroTileColor =
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
  | 'orange-deep'
  | 'amber'
  | 'cyan'
  | 'cyan-deep'
  | 'purple'
  | 'violet'
  | 'magenta';

interface CustomColor {
  base: string;
  dark: string;
}

interface MetroTileToggleProps {
  title: string;
  icon: string;
  children: ReactNode;
  subtitle?: string;
  color?: MetroTileColor;
  customColor?: CustomColor;
  size?: MetroTileSize;
  badge?: number | string | null;
  defaultOpen?: boolean;
  closeLabel?: string;
  className?: string;
  onSave?: () => void;
  saveLabel?: string;
  saving?: boolean;
  saveDisabled?: boolean;
}

const HEADER_VARIANTS: Variants = {
  rest:    { scale: 1,    y: 0 },
  hover:   { scale: 1.02, y: -2 },
  pressed: { scale: 0.98 },
};

const BODY_VARIANTS: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
    transition: { duration: 0.32, ease: [0.22, 1, 0.36, 1] },
  },
  expanded: {
    height: 'auto',
    opacity: 1,
    transition: { duration: 0.42, ease: [0.22, 1, 0.36, 1] },
  },
};

const CONTENT_VARIANTS: Variants = {
  hidden:  { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.32, ease: [0.22, 1, 0.36, 1], delay: 0.08 },
  },
  exit:    { opacity: 0, y: 6, transition: { duration: 0.18 } },
};

interface MetroTileSaveButtonProps {
  onSave: () => void;
  label: string;
  saving: boolean;
  disabled: boolean;
}

function MetroTileSaveButton({ onSave, label, saving, disabled }: MetroTileSaveButtonProps) {
  return (
    <button
      type="button"
      className="metro-tile__save"
      onClick={onSave}
      disabled={saving || disabled}
    >
      {saving ? (
        <>
          <span
            className="spinner-border spinner-border-sm"
            role="status"
            aria-hidden="true"
          />
          Guardando…
        </>
      ) : (
        <>
          <i className="bi bi-check-lg" />
          {label}
        </>
      )}
    </button>
  );
}

interface MetroTileFooterProps {
  onClose: () => void;
  closeLabel: string;
  onSave?: () => void;
  saveLabel: string;
  saving: boolean;
  saveDisabled: boolean;
}

function MetroTileFooter({
  onClose,
  closeLabel,
  onSave,
  saveLabel,
  saving,
  saveDisabled,
}: MetroTileFooterProps) {
  return (
    <div className="metro-tile__footer">
      {onSave && (
        <MetroTileSaveButton
          onSave={onSave}
          label={saveLabel}
          saving={saving}
          disabled={saveDisabled}
        />
      )}
      <button type="button" className="metro-tile__close" onClick={onClose}>
        <i className="bi bi-x-lg" />
        {closeLabel}
      </button>
    </div>
  );
}

export function MetroTileToggle({
  title,
  icon,
  children,
  subtitle,
  color = 'red',
  customColor,
  size = 'medium',
  badge = null,
  defaultOpen = false,
  closeLabel = 'Cerrar',
  className = '',
  onSave,
  saveLabel = 'Guardar',
  saving = false,
  saveDisabled = false,
}: MetroTileToggleProps) {
  const [open, setOpen] = useState<boolean>(defaultOpen);
  const reactId: string = useId();
  const bodyId: string = `metro-tile-body-${reactId}`;

  const colorClass: string = customColor ? 'has-custom-color' : `metro-tile--${color}`;
  const sizeClass: string = `metro-tile--${size}`;

  const customStyle: CSSProperties | undefined = customColor
    ? ({
        '--metro-tile-color': customColor.base,
        '--metro-tile-color-dark': customColor.dark,
      } as CSSProperties)
    : undefined;

  const showBadge: boolean = badge !== null && badge !== undefined && badge !== '' && badge !== 0;

  return (
    <motion.div
      layout
      transition={{ layout: { duration: 0.42, ease: [0.22, 1, 0.36, 1] } }}
      className={`metro-tile ${colorClass} ${sizeClass} ${open ? 'is-open' : ''} ${className}`}
      style={customStyle}
    >
      <motion.button
        type="button"
        layout
        variants={HEADER_VARIANTS}
        initial="rest"
        animate="rest"
        whileHover="hover"
        whileTap="pressed"
        transition={{ type: 'spring', stiffness: 320, damping: 24 }}
        className="metro-tile__header"
        aria-expanded={open}
        aria-controls={bodyId}
        role="button"
        onClick={() => setOpen(prev => !prev)}
      >
        <span className="metro-tile__icon" aria-hidden="true">
          <i className={`bi ${icon}`} />
        </span>
        <span className="metro-tile__titles">
          <span className="metro-tile__title">{title}</span>
          {subtitle && <span className="metro-tile__subtitle">{subtitle}</span>}
        </span>
        {showBadge && <span className="metro-tile__badge">{badge}</span>}
        <span className="metro-tile__chevron" aria-hidden="true">
          <i className="bi bi-chevron-down" />
        </span>
      </motion.button>

      <AnimatePresence initial={false}>
        {open && (
          <motion.section
            key="body"
            id={bodyId}
            variants={BODY_VARIANTS}
            initial="collapsed"
            animate="expanded"
            exit="collapsed"
            className="metro-tile__body"
            aria-hidden={!open}
          >
            <motion.div
              variants={CONTENT_VARIANTS}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="metro-tile__content"
            >
              {children}
            </motion.div>
            <MetroTileFooter
              onClose={() => setOpen(false)}
              closeLabel={closeLabel}
              onSave={onSave}
              saveLabel={saveLabel}
              saving={saving}
              saveDisabled={saveDisabled}
            />
          </motion.section>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
