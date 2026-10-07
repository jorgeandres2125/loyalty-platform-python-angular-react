from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ReportePreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    columns: list[str]
    rows: list[list[object]]
    total: int
    page: int
    page_size: int
