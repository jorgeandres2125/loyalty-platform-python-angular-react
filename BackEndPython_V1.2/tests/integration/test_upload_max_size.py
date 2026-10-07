"""AP-0137: los archivos subidos tienen un tamano maximo definido y validado."""
from __future__ import annotations

import io

import pytest
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.testclient import TestClient

from src.adapters.api.validacion_archivos import (
    verificar_tamano_contenido,
    verificar_tamano_upload,
)
from src.infrastructure.config.settings import Settings

SL = chr(47)
_MAX = 1024
_GRANDE = 2000
_CHICO = 100


def _make_client() -> TestClient:
    app = FastAPI()

    @app.post(SL + "up")
    async def up(file: UploadFile = File(...)) -> dict:
        verificar_tamano_upload(file, _MAX)
        contenido = await file.read()
        verificar_tamano_contenido(contenido, _MAX)
        return {"size": len(contenido)}

    return TestClient(app)


_CLIENT = _make_client()


def test_archivo_dentro_del_limite_aceptado() -> None:
    r = _CLIENT.post(
        SL + "up",
        files={"file": ("a.pdf", bytes(_CHICO), "application/pdf")},
    )
    assert r.status_code == 200
    assert r.json() == {"size": _CHICO}


def test_archivo_excede_limite_rechazado_413() -> None:
    r = _CLIENT.post(
        SL + "up",
        files={"file": ("a.pdf", bytes(_GRANDE), "application/pdf")},
    )
    assert r.status_code == 413


def test_helper_contenido_excedido_lanza() -> None:
    with pytest.raises(HTTPException) as exc:
        verificar_tamano_contenido(bytes(_GRANDE), _MAX)
    assert exc.value.status_code == 413


def test_helper_contenido_dentro_no_lanza() -> None:
    verificar_tamano_contenido(bytes(_CHICO), _MAX)


def test_helper_upload_por_size_declarado() -> None:
    grande = UploadFile(file=io.BytesIO(bytes(_GRANDE)), size=_GRANDE)
    with pytest.raises(HTTPException) as exc:
        verificar_tamano_upload(grande, _MAX)
    assert exc.value.status_code == 413
    chico = UploadFile(file=io.BytesIO(bytes(_CHICO)), size=_CHICO)
    verificar_tamano_upload(chico, _MAX)
    sin_size = UploadFile(file=io.BytesIO(bytes(_GRANDE)), size=None)
    verificar_tamano_upload(sin_size, _MAX)


def test_settings_default_10mb() -> None:
    assert Settings.model_fields["max_upload_bytes"].default == 10_485_760
