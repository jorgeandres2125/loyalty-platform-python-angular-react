
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.persistence.base import Base


class CiudadModel(Base):
    __tablename__ = "ciudades"

    # `cid` no es IDENTITY — el repositorio asigna MAX(cid)+1.
    cid: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    # Composición geográfica: al borrar un departamento, sus ciudades se
    # eliminan en cascada (CASCADE). did es nullable; las ciudades sin
    # departamento no se ven afectadas.
    did: Mapped[int | None] = mapped_column(
        ForeignKey("departamentos.did", ondelete="CASCADE")
    )
    ciudad: Mapped[str | None] = mapped_column(String(50))
