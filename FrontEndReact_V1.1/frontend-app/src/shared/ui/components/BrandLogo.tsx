import logoSrc from '../../../assets/LOGO_CLEAR.png';

interface BrandLogoProps {
  height?: number;
  className?: string;
  style?: React.CSSProperties;
}

export function BrandLogo({ height = 40, className, style }: BrandLogoProps) {
  return (
    <img
      src={logoSrc}
      alt="SUFI Contigo"
      height={height}
      draggable={false}
      className={className}
      style={{ display: 'block', objectFit: 'contain', ...style }}
    />
  );
}
