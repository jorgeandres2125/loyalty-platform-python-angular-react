import { BrowserRouter } from 'react-router-dom';
import { QueryProvider } from './providers/QueryProvider';
import { AppRouter } from './router/AppRouter';
import { ErrorBoundary } from '../shared/ui/components/ErrorBoundary';
import { ToastProvider } from '../shared/ui/components/ToastProvider';
import '../styles/main.scss';
import 'bootstrap-icons/font/bootstrap-icons.css';

export function App() {
  return (
    <BrowserRouter>
      <QueryProvider>
        <ErrorBoundary>
          <ToastProvider>
            <AppRouter />
          </ToastProvider>
        </ErrorBoundary>
      </QueryProvider>
    </BrowserRouter>
  );
}
