"""Evaluación automática del SLO al finalizar la corrida (AP-0031 / AP-0032).

Engancha el evento `quitting` de Locust: calcula p95 y fail_ratio del agregado,
los compara contra el SLO y fija el código de salida del proceso (0 = verde,
1 = incumple). Además escribe `evidence/slo_summary.json` como evidencia de auditoría.

Esto convierte la prueba en un gate objetivo y reproducible: si la corrida no
cumple <5 s y 0 % de errores, el proceso falla y el control NO puede pasar a Verde.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import loadtest_config as cfg
from locust import events
from locust.env import Environment

_EVIDENCE_DIR: Path = Path(__file__).resolve().parent / "evidence"


@events.quitting.add_listener
def _evaluar_slo(environment: Environment, **_kwargs: Any) -> None:
    stats = environment.stats.total
    p95_ms: float = float(stats.get_response_time_percentile(0.95) or 0)
    p99_ms: float = float(stats.get_response_time_percentile(0.99) or 0)
    mediana_ms: float = float(stats.median_response_time or 0)
    max_ms: float = float(stats.max_response_time or 0)
    fail_ratio: float = float(stats.fail_ratio or 0)
    num_requests: int = int(stats.num_requests)
    num_failures: int = int(stats.num_failures)

    cumple_latencia: bool = p95_ms < cfg.SLO_P95_MS
    cumple_errores: bool = fail_ratio <= cfg.SLO_FAIL_RATIO
    verde: bool = cumple_latencia and cumple_errores and num_requests > 0

    resumen: dict[str, Any] = {
        "concurrencia_objetivo": cfg.CONCURRENCIA_OBJETIVO,
        "num_requests": num_requests,
        "num_failures": num_failures,
        "fail_ratio": round(fail_ratio, 6),
        "latencia_ms": {
            "mediana": round(mediana_ms, 1),
            "p95": round(p95_ms, 1),
            "p99": round(p99_ms, 1),
            "max": round(max_ms, 1),
        },
        "slo": {
            "p95_max_ms": cfg.SLO_P95_MS,
            "fail_ratio_max": cfg.SLO_FAIL_RATIO,
        },
        "veredicto": {
            "AP-0031_latencia": "VERDE" if cumple_latencia else "ROJO",
            "AP-0032_errores": "VERDE" if cumple_errores else "ROJO",
            "global": "VERDE" if verde else "ROJO",
        },
    }

    _EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    (_EVIDENCE_DIR / "slo_summary.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Fijar el gate ANTES de imprimir: ningún fallo de E/S de consola debe
    # impedir que el exit code refleje el veredicto.
    environment.process_exit_code = 0 if verde else 1

    # Salida 100 % ASCII para no fallar en consolas Windows (cp1252).
    lineas: list[str] = [
        "",
        "=" * 64,
        "  EVALUACION SLO - AP-0031 / AP-0032",
        "=" * 64,
        f"  Peticiones: {num_requests}  |  Fallos: {num_failures}  |  fail_ratio: {fail_ratio:.4%}",
        f"  Latencia (ms): mediana={mediana_ms:.0f}  p95={p95_ms:.0f}  p99={p99_ms:.0f}  max={max_ms:.0f}",
        f"  AP-0031 (p95 < {cfg.SLO_P95_MS:.0f} ms): {'VERDE' if cumple_latencia else 'ROJO'}",
        f"  AP-0032 (errores <= {cfg.SLO_FAIL_RATIO:.0%}):  {'VERDE' if cumple_errores else 'ROJO'}",
        f"  GLOBAL: {'VERDE' if verde else 'ROJO'}",
        "=" * 64,
        "",
    ]
    print("\n".join(lineas))
