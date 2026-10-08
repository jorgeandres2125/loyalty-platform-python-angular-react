import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';

// Desmonta el árbol React y limpia el localStorage entre tests para que
// el estado persistido del authStore (zustand `persist`) no contamine
// pruebas posteriores.
afterEach(() => {
  cleanup();
  localStorage.clear();
});
