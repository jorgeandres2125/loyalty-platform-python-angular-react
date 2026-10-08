export const environment = {
  production: false,
  apiBaseUrl: '/api/v1',
  // AP-0206 burst limiting del cliente (configurable). Complementa el rate limiting del backend (AP-0166).
  rateLimitEnabled: true,
  rateLimitBurst: 60,
  rateLimitRefillPerSec: 10,
};
