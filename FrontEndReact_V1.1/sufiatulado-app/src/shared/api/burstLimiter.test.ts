import { describe, it, expect } from 'vitest';
import { BurstLimiter, RateLimitError } from './burstLimiter';

describe('BurstLimiter - burst limiting del cliente (AP-0206)', () => {
  it('permite una rafaga de hasta capacity y luego rechaza', () => {
    const limiter = new BurstLimiter({ capacity: 3, refillPerSec: 0, now: () => 1000 });
    expect(limiter.intentar()).toBe(true);
    expect(limiter.intentar()).toBe(true);
    expect(limiter.intentar()).toBe(true);
    expect(limiter.intentar()).toBe(false);
  });

  it('repone tokens con el tiempo segun refillPerSec', () => {
    let ahora = 0;
    const limiter = new BurstLimiter({ capacity: 2, refillPerSec: 1, now: () => ahora });
    expect(limiter.intentar()).toBe(true);
    expect(limiter.intentar()).toBe(true);
    expect(limiter.intentar()).toBe(false);
    ahora = 1000;
    expect(limiter.intentar()).toBe(true);
    expect(limiter.intentar()).toBe(false);
  });

  it('no acumula tokens por encima de capacity', () => {
    let ahora = 0;
    const limiter = new BurstLimiter({ capacity: 2, refillPerSec: 100, now: () => ahora });
    ahora = 10000;
    expect(limiter.disponibles()).toBe(2);
  });

  it('RateLimitError tiene nombre estable', () => {
    expect(new RateLimitError().name).toBe('RateLimitError');
  });
});
