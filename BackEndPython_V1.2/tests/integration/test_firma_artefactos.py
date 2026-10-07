"""AP-0149: firma criptografica de los artefactos de produccion en CI."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

_WF = Path(__file__).resolve().parents[3].joinpath(
    ".github", "workflows", "build-sign-release.yml"
)

if not _WF.is_file():
    pytest.skip("workflow de firma no disponible", allow_module_level=True)

_TXT = _WF.read_text(encoding="utf-8")
_DOC = yaml.safe_load(_TXT)
_COSIGN_INSTALLER = "sigstore" + chr(47) + "cosign-installer"


def test_yaml_valido() -> None:
    assert isinstance(_DOC, dict)


def test_usa_cosign_para_firmar() -> None:
    assert _COSIGN_INSTALLER in _TXT
    assert "cosign sign --yes" in _TXT
    assert "cosign sign-blob" in _TXT


def test_firma_keyless_con_id_token() -> None:
    assert "id-token: write" in _TXT


def test_se_dispara_en_release_o_tag() -> None:
    assert "release:" in _TXT
    assert "tags:" in _TXT


def test_firma_checksums_de_artefactos() -> None:
    assert "SHA256SUMS" in _TXT
