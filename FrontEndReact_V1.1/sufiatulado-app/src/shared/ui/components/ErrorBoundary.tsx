import { Component, type ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../../entities/user/model/authStore';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
}

class ErrorBoundaryClass extends Component<Props & { onError: () => void }, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(): void {
    this.props.onError();
  }

  render(): ReactNode {
    if (this.state.hasError) return null;
    return this.props.children;
  }
}

export function ErrorBoundary({ children }: Props) {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated());

  const handleError = () => {
    navigate(isAuthenticated ? '/' : '/login', { replace: true });
  };

  return (
    <ErrorBoundaryClass onError={handleError}>
      {children}
    </ErrorBoundaryClass>
  );
}
