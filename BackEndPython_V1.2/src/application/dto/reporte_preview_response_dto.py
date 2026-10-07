from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ReportePreviewResponseDTO:
    columns: list[str]
    rows: list[list[Any]]
    total: int
    page: int
    page_size: int
