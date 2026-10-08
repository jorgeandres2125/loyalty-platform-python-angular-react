// AP-0206: limitador de rafaga (token bucket) del lado del cliente. Complementa el
// rate limiting del backend (slowapi, AP-0166) para evitar consumo masivo desde la
// SPA. Cada peticion consume un token; el cubo se repone a refillPerSec hasta
// capacity. Sin tokens, la peticion se rechaza en el navegador (no llega a viajar).

export interface BurstLimiterConfig {
  capacity: number;
  refillPerSec: number;
  now?: () => number;
}

export class RateLimitError extends Error {
  constructor(message = 'Limite de rafaga de peticiones excedido en el cliente') {
    super(message);
    this.name = 'RateLimitError';
  }
}

export class BurstLimiter {
  private readonly capacity: number;
  private readonly refillPerSec: number;
  private readonly now: () => number;
  private tokens: number;
  private ultimoMs: number;

  constructor(config: BurstLimiterConfig) {
    this.capacity = Math.max(1, config.capacity);
    this.refillPerSec = Math.max(0, config.refillPerSec);
    this.now = config.now ?? ((): number => Date.now());
    this.tokens = this.capacity;
    this.ultimoMs = this.now();
  }

  private reponer(): void {
    const ahora = this.now();
    const transcurridoSeg = Math.max(0, (ahora - this.ultimoMs) * 0.001);
    if (transcurridoSeg > 0) {
      const repuestos = this.tokens + transcurridoSeg * this.refillPerSec;
      this.tokens = Math.min(this.capacity, repuestos);
      this.ultimoMs = ahora;
    }
  }

  intentar(): boolean {
    this.reponer();
    if (this.tokens >= 1) {
      this.tokens -= 1;
      return true;
    }
    return false;
  }

  disponibles(): number {
    this.reponer();
    return this.tokens;
  }
}
