import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useIdleTimeout } from './useIdleTimeout';

afterEach(() => {
  vi.useRealTimers();
});

describe('useIdleTimeout (AP-0129)', () => {
  it('avisa antes del cierre y luego cierra por inactividad', () => {
    vi.useFakeTimers();
    const onWarning = vi.fn();
    const onTimeout = vi.fn();
    renderHook(() =>
      useIdleTimeout({ idleMs: 1000, warningMs: 200, active: true, onWarning, onTimeout }),
    );
    act(() => vi.advanceTimersByTime(800));
    expect(onWarning).toHaveBeenCalledTimes(1);
    expect(onTimeout).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(200));
    expect(onTimeout).toHaveBeenCalledTimes(1);
  });

  it('la actividad del usuario reinicia el contador de inactividad', () => {
    vi.useFakeTimers();
    const onTimeout = vi.fn();
    renderHook(() =>
      useIdleTimeout({
        idleMs: 1000,
        warningMs: 200,
        active: true,
        onWarning: vi.fn(),
        onTimeout,
      }),
    );
    act(() => vi.advanceTimersByTime(900));
    act(() => {
      window.dispatchEvent(new Event('keydown'));
    });
    act(() => vi.advanceTimersByTime(900));
    expect(onTimeout).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(100));
    expect(onTimeout).toHaveBeenCalledTimes(1);
  });

  it('no arranca cuando active es false', () => {
    vi.useFakeTimers();
    const onTimeout = vi.fn();
    renderHook(() =>
      useIdleTimeout({
        idleMs: 1000,
        warningMs: 200,
        active: false,
        onWarning: vi.fn(),
        onTimeout,
      }),
    );
    act(() => vi.advanceTimersByTime(3000));
    expect(onTimeout).not.toHaveBeenCalled();
  });
});