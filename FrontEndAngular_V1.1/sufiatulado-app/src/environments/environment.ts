// Equivalente Angular de las variables VITE_* del .env del proyecto React.
// En build de desarrollo se reemplaza por environment.development.ts (ver angular.json).
export const environment = {
  production: true,
  apiBaseUrl: '/api/v1',
  // AP-0206 burst limiting del cliente (configurable). Complementa el rate limiting del backend (AP-0166).
  rateLimitEnabled: true,
  rateLimitBurst: 60,
  rateLimitRefillPerSec: 10,
};
