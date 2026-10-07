"""Arnés de carga SUFI — valida AP-0031 (<5 s) y AP-0032 (0 % errores).

Perfil de carga (mix realista con escrituras), por usuario virtual:
  - on_start: login una sola vez (bcrypt) → guarda el JWT y autentica por Bearer
    (con Bearer el middleware CSRF se omite, igual que una integración M2M).
  - tareas ponderadas: lecturas de catálogo + perfil propio + dashboard, y una
    ESCRITURA idempotente sobre el PROPIO perfil de contacto (UPDATE, sin colisión
    entre usuarios → 0 % de errores alcanzable a 100 concurrentes).

El gate del SLO lo aplica `slo_listener` (importado abajo) en el evento `quitting`.

Ejecución típica (headless, 100 usuarios, 3 min de meseta):
    locust -f tests/load/locustfile.py --headless -u 100 -r 10 -t 3m \
           --host http://127.0.0.1:8000 \
           --html tests/load/evidence/report.html --csv tests/load/evidence/sufi
"""
from __future__ import annotations

from typing import Any

import loadtest_config as cfg
import slo_listener  # noqa: F401  (registra el listener del evento quitting)
from locust import HttpUser, between, task

# Documento de contacto base: válido contra el esquema (extra="forbid", validadores).
_FECHA_NACIMIENTO: str = "1990-05-15"


def _cuerpo_contacto(numero_documento: str) -> dict[str, Any]:
    """Cuerpo válido para PUT /me/perfil-contacto (idempotente para el mismo doc)."""
    return {
        "numero_documento": numero_documento,
        "tipo_documento": "C.C.",
        "nombre_completo": f"Carga Prueba {numero_documento}",
        "genero": "M",
        "fecha_nacimiento": _FECHA_NACIMIENTO,
        "celular": "3001234567",
        "direccion": "Calle 123 # 45-67 Carga",
        "departamento": cfg.DEPARTAMENTO_VALIDO,
        "ciudad": cfg.CIUDAD_VALIDA,
        "comisionista_programa_id": cfg.PROGRAMA_MOVILIDAD,
        "acepto_habeas_data": 1,
        "incentivos": False,
        "estado": 1,
    }


class ComisionistaSUFI(HttpUser):
    """Simula un comisionista autenticado navegando su área privada."""

    host = cfg.HOST
    # Pausa realista entre acciones de un mismo usuario.
    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        # Cada usuario virtual toma un documento determinista del rango sembrado.
        # El id 1-based se deriva del contador global de Locust de forma estable.
        indice: int = (ComisionistaSUFI._siguiente_indice() % cfg.LOADTEST_COUNT) + 1
        self._numero_documento: str = cfg.documento_de_indice(indice)
        self._login()

    _contador: int = 0

    @classmethod
    def _siguiente_indice(cls) -> int:
        valor: int = cls._contador
        cls._contador += 1
        return valor

    def _login(self) -> None:
        with self.client.post(
            "/api/v1/auth/login",
            json={"username": self._numero_documento, "password": cfg.LOADTEST_PASSWORD},
            name="POST /auth/login",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"login {resp.status_code}: {resp.text[:120]}")
                return
            token: str | None = resp.json().get("access_token")
            if not token:
                resp.failure("login sin access_token")
                return
            # Bearer → require_token lo acepta y el middleware CSRF se omite.
            self.client.headers["Authorization"] = f"Bearer {token}"
            resp.success()

    # ── Lecturas (mayoría del tráfico) ──────────────────────────────────────

    @task(5)
    def leer_catalogo_ubicaciones(self) -> None:
        self.client.get("/api/v1/ubicaciones/departamentos", name="GET /ubicaciones/departamentos")

    @task(5)
    def leer_mi_perfil_contacto(self) -> None:
        self.client.get("/api/v1/me/perfil-contacto", name="GET /me/perfil-contacto")

    @task(3)
    def leer_mi_dashboard(self) -> None:
        self.client.get("/api/v1/me/dashboard", name="GET /me/dashboard")

    @task(2)
    def leer_usuario_actual(self) -> None:
        self.client.get("/api/v1/auth/me", name="GET /auth/me")

    @task(1)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")

    # ── Escritura idempotente sobre el PROPIO perfil ────────────────────────

    @task(1)
    def actualizar_mi_perfil_contacto(self) -> None:
        self.client.put(
            "/api/v1/me/perfil-contacto",
            json=_cuerpo_contacto(self._numero_documento),
            name="PUT /me/perfil-contacto",
        )
