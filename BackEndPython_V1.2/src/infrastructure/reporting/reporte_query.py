from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReporteQuery:
    sheet_name: str
    headers: tuple[str, ...]
    sql_body: str
    order_by: str
    params: dict[str, Any]
    transformer: Callable[[Mapping[str, Any]], list[Any]]
    numeric_cols: frozenset[int] | None = field(default=None)
