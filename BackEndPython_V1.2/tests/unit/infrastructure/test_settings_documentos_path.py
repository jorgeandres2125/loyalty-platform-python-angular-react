"""AP-0084: el directorio de documentos siempre se resuelve a una ruta absoluta."""
from __future__ import annotations

from pathlib import Path

from src.infrastructure.config.settings import Settings

_SECRETO: str = "xxxxxxxxxxxxxxxxxxxxxxxx"


def test_documentos_path_es_absoluta_por_defecto() -> None:
    cfg: Settings = Settings(documentos_dir="")
    assert cfg.documentos_path.is_absolute()


def test_documentos_path_default_apunta_a_uploads_documentos() -> None:
    cfg: Settings = Settings(documentos_dir="")
    assert cfg.documentos_path.name == "documentos"
    assert cfg.documentos_path.parent.name == "uploads"


def test_documentos_path_relativa_se_ancla_y_es_absoluta() -> None:
    cfg: Settings = Settings(documentos_dir="archivos/docs")
    assert cfg.documentos_path.is_absolute()
    assert cfg.documentos_path.name == "docs"


def test_documentos_path_absoluta_se_respeta() -> None:
    absoluta: Path = (Path.cwd().resolve() / "var" / "sufi" / "docs")
    cfg: Settings = Settings(documentos_dir=str(absoluta))
    assert cfg.documentos_path == absoluta


def test_documentos_path_absoluta_en_todos_los_ambientes() -> None:
    for env in ("development", "test", "staging", "production"):
        cfg: Settings = Settings(
            app_env=env,
            db_user="app_sufi",
            jwt_secret_key=_SECRETO,
            db_password=_SECRETO,
            email_api_password="",
            kms_provider="aws",
            kms_key_id="kms-test-key-id",
            documentos_dir="",
        )
        assert cfg.documentos_path.is_absolute()
