# Pruebas de carga — AP-0031 / AP-0032

Arnés de carga reproducible que produce la **evidencia auditada** de dos controles
de seguridad/rendimiento del proyecto SUFI:

| Control | Requisito | SLO verificable |
|---|---|---|
| **AP-0031** | Tiempo de respuesta a concurrencia máxima ≤ 5 s | **p95 < 5000 ms** |
| **AP-0032** | Porcentaje de errores a concurrencia máxima = 0 % | **fail_ratio == 0** |

**Concurrencia máxima esperada:** 100 usuarios simultáneos (alineado con el pool
de conexiones `db_pool_min + max_overflow = 100`). Configurable por entorno.

Estos controles son de **verificación**, no de reforma de código: el remedio ante
un incumplimiento es de *configuración* (tamaño de pool, workers de uvicorn,
índices SQL), nunca reescritura de lógica de negocio.

## Componentes

| Archivo | Responsabilidad |
|---|---|
| `loadtest_config.py` | SLO, concurrencia, rango de usuarios y catálogos válidos (override por env). |
| `seed_loadtest_users.py` | Siembra/limpia 100 comisionistas dedicados (`99000000xx`) con bcrypt + rol. |
| `locustfile.py` | Escenarios Locust: login una vez + lecturas + escritura idempotente del perfil propio. |
| `slo_listener.py` | Gate del SLO en `quitting`: calcula p95/fail_ratio, fija exit code y escribe `evidence/slo_summary.json`. |
| `evidence/` | Salida: `report.html`, `sufi_*.csv`, `slo_summary.json` (evidencia para auditoría). |

## Requisitos

- Stack Docker arriba (`Docker/`): SQL Server `sufiatulado` en `127.0.0.1:1433`.
- Backend respondiendo en `http://127.0.0.1:8000`.
- `locust` instalado en el venv: `uv pip install locust` (o `pip install locust`).

## Procedimiento

Desde la raíz del backend (`BackEndPython_V1.2/`) con el venv activo:

```bash
# 1) Levantar el backend contra la DB Docker (un worker = una instancia de contenedor)
python -m uvicorn src.adapters.api.main:app --host 0.0.0.0 --port 8000

# 2) Sembrar los 100 usuarios de carga (otra terminal)
python tests/load/seed_loadtest_users.py

# 3) Ejecutar la prueba: rampa a 100 usuarios (10/s) y 3 min de meseta
locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 3m \
       --host http://127.0.0.1:8000 \
       --html tests/load/evidence/report.html \
       --csv tests/load/evidence/sufi

# 4) Limpiar los datos sembrados
python tests/load/seed_loadtest_users.py --reset
```

El comando de Locust devuelve **exit code 0** si se cumple el SLO (verde) y **1** si
no (rojo) — directamente usable como gate en CI.

## Evidencia generada

- `evidence/report.html` — reporte visual de Locust (percentiles, RPS, fallos).
- `evidence/sufi_stats.csv`, `sufi_failures.csv`, `sufi_stats_history.csv` — datos crudos.
- `evidence/slo_summary.json` — veredicto máquina-legible AP-0031/AP-0032.

## Notas de diseño

- **Login una sola vez por usuario** (`on_start`): bcrypt (rounds=12) es CPU-bound;
  en producción un usuario se autentica una vez y luego navega. Repetir login en
  cada iteración no es realista y saturaría la CPU del worker.
- **Autenticación por Bearer**: el JWT se envía en `Authorization: Bearer`, con lo
  que el middleware CSRF se omite (doble-submit sólo aplica a sesiones por cookie).
- **Escritura sin colisión**: cada usuario virtual sólo edita *su propio* perfil
  (`PUT /me/perfil-contacto`, UPDATE idempotente) → no hay choques de constraint
  entre usuarios concurrentes, condición necesaria para 0 % de errores.
- **Override por entorno**: `SUFI_LOAD_USERS`, `SUFI_LOAD_HOST`, `SUFI_SLO_P95_MS`,
  `SUFI_SLO_FAIL_RATIO`, `SUFI_LOAD_PASSWORD`, `SUFI_LOAD_SEED_COUNT`.
