import { LoginForm } from '../../features/auth/ui/LoginForm';
import { BrandLogo } from '../../shared/ui/components/BrandLogo';
import { BrandShowcase } from './BrandShowcase';

export function LoginPage() {

  return (
    <div className="login-page">
      {/* Brand panel — landing animado */}
      <div className="login-page__brand">
        <BrandShowcase />
      </div>

      {/* Form panel */}
      <div className="login-page__form">
        <div style={{ width: '100%', maxWidth: 380 }}>
          <div className="mb-0">
            <BrandLogo height={32} />
          </div>
          <LoginForm />
        </div>
      </div>
    </div>
  );
}
