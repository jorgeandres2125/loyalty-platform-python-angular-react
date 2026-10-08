import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useFormTimeout } from './useFormTimeout';

afterEach(() => {
  vi.useRealTimers();
});

describe('useFormTimeout', () => {
  it('ejecuta onTimeout tras delayMs cuando está activo', () => {
    vi.useFakeTimers();
    const onTimeout = vi.fn();
    renderHook(() => useFormTimeout({ delayMs: 60_000, active: true, onTimeout }));

    expect(onTimeout).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(60_000));
    expect(onTimeout).toHaveBeenCalledTimes(1);
  });

  it('no arranca cuando active es false', () => {
    vi.useFakeTimers();
    const onTimeout = vi.fn();
    renderHook(() => useFormTimeout({ delayMs: 60_000, active: false, onTimeout }));

    act(() => vi.advanceTimersByTime(120_000));
    expect(onTimeout).not.toHaveBeenCalled();
  });

  it('límite ABSOLUTO: un re-render con las mismas deps no reinicia el plazo', () => {
    vi.useFakeTimers();
    const onTimeout = vi.fn();
    const { rerender } = renderHook(
      ({ active }) => useFormTimeout({ delayMs: 60_000, active, onTimeout }),
      { initialProps: { active: true } },
    );

    act(() => vi.advanceTimersByTime(40_000));
    rerender({ active: true }); // re-render sin cambio de deps → no reinicia
    act(() => vi.advanceTimersByTime(20_000));
    expect(onTimeout).toHaveBeenCalledTimes(1); // 40 + 20 = 60 → vence
  });

  it('modo inactividad: cambiar resetKey reinicia el temporizador', () => {
    vi.useFakeTimers();
    const onTimeout = vi.fn();
    const { rerender } = renderHook(
      ({ resetKey }) => useFormTimeout({ delayMs: 60_000, active: true, onTimeout, resetKey }),
      { initialProps: { resetKey: 'a' } },
    );

    act(() => vi.advanceTimersByTime(50_000));
    rerender({ resetKey: 'b' }); // cambia la clave → reinicia
    act(() => vi.advanceTimersByTime(50_000));
    expect(onTimeout).not.toHaveBeenCalled(); // solo 50 s desde el reinicio
    act(() => vi.advanceTimersByTime(10_000));
    expect(onTimeout).toHaveBeenCalledTimes(1);
  });

  it('cancela el temporizador al desmontar', () => {
    vi.useFakeTimers();
    const onTimeout = vi.fn();
    const { unmount } = renderHook(() =>
      useFormTimeout({ delayMs: 60_000, active: true, onTimeout }),
    );

    unmount();
    act(() => vi.advanceTimersByTime(60_000));
    expect(onTimeout).not.toHaveBeenCalled();
  });
});
