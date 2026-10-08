import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
      reactRefresh.configs.vite,
    ],
    // Proyecto en React 18 (sin React Compiler): registramos el plugin
    // manualmente y activamos solo las dos reglas clásicas. El preset
    // `reactHooks.configs.flat.recommended` de v7 habilita además ~14 reglas
    // del React Compiler (React 19) que marcan patrones válidos en React 18.
    plugins: {
      'react-hooks': reactHooks,
    },
    languageOptions: {
      globals: globals.browser,
    },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      // AP-0036: complejidad ciclomática (McCabe) < 20. ESLint marca cuando supera
      // el umbral, por lo que 19 fuerza que toda función quede en <= 19 (< 20).
      complexity: ['error', 19],
    },
  },
])
