from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AdminProgramaFormDTO:
    """Único campo editable según decisión 3."""
    cp_nombre: str
