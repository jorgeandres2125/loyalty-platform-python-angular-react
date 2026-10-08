import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { existsSync, readFileSync } from 'fs';

// Certificados mkcert compartidos (D:\SUFI\certificates). Si existen, el dev server
// sirve por HTTPS — requisito para que la cookie de sesión `Secure` funcione en dev
// (Medida B del plan de remediación). Si no, cae a HTTP plano.
const CERT = 'D:/SUFI/certificates/localhost+3.pem';
const KEY = 'D:/SUFI/certificates/localhost+3-key.pem';
const httpsConfig =
  existsSync(CERT) && existsSync(KEY)
    ? { cert: readFileSync(CERT), key: readFileSync(KEY) }
    : undefined;

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
  css: {
    preprocessorOptions: {
      scss: {
        quietDeps: true,
      },
    },
  },
  server: {
    // host: true → escucha en 0.0.0.0 (todas las interfaces), de modo que el
    // dev server es accesible desde otros equipos vía la IP local de red.
    host: true,
    port: 3000,
    https: httpsConfig,
    proxy: {
      '/api': {
        // El backend ahora sirve por HTTPS (mismos certificados mkcert). secure:false
        // acepta el certificado de desarrollo. El navegador sólo habla con Vite
        // (mismo origen /api/v1), por lo que no se dispara CORS en lo proxeado.
        target: 'https://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
