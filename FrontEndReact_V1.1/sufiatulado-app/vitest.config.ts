import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

// Config de Vitest separada del vite.config.ts de producción. Reutiliza los
// plugins/alias de Vite vía mergeConfig y añade el bloque `test`. Este archivo
// NO está incluido en ningún tsconfig, así que `tsc -b` (build) no lo
// type-chequea — evitando el choque de tipos rollup/rolldown de Vite 8.
export default mergeConfig(
  viteConfig,
  defineConfig({
    // Runtime JSX automático para los *.test.tsx (excluidos de tsconfig.app),
    // evita "React is not defined".
    esbuild: { jsx: 'automatic' },
    test: {
      globals: true,
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
      css: false,
      include: ['src/**/*.{test,spec}.{ts,tsx}'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html'],
        reportsDirectory: './coverage',
        include: ['src/**/*.{ts,tsx}'],
        exclude: [
          'src/**/*.test.{ts,tsx}',
          'src/**/*.spec.{ts,tsx}',
          'src/test/**',
          'src/**/types/**',
          'src/**/*.d.ts',
          'src/main.tsx',
          'src/vite-env.d.ts',
        ],
      },
    },
  }),
);
