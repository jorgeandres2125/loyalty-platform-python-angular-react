"""Punto de entrada para desarrollo local.
Uso (accesible en el LAN): uv run uvicorn src.adapters.api.main:app --reload --host 0.0.0.0 --port 8000
También: python main.py  (ya enlaza host="0.0.0.0", visible por la IP local de red)

Si SSL_CERTFILE y SSL_KEYFILE están configurados (.env), uvicorn sirve por HTTPS
(Medida B del plan de remediación). Para --reload con HTTPS usar:
  uv run uvicorn src.adapters.api.main:app --reload --host 0.0.0.0 --port 8000 \
      --ssl-certfile <cert> --ssl-keyfile <key>
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from adapters.api.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    from infrastructure.config.settings import Settings

    settings = Settings()
    ssl_kwargs: dict = {}
    if settings.ssl_certfile and settings.ssl_keyfile:
        ssl_kwargs = {
            "ssl_certfile": settings.ssl_certfile,
            "ssl_keyfile": settings.ssl_keyfile,
        }
        print(f"[main] HTTPS habilitado con certificado: {settings.ssl_certfile}")
    else:
        print("[main] HTTP plano (SSL_CERTFILE/SSL_KEYFILE no configurados)")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, **ssl_kwargs)
