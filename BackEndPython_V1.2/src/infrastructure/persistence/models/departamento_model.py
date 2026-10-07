
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class DepartamentoModel(Base):
    __tablename__ = "departamentos"

    # `did` no es IDENTITY — el repositorio asigna MAX(did)+1.
    did: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    pid: Mapped[int | None] = mapped_column(Integer)
    departamento: Mapped[str | None] = mapped_column(String(50))
