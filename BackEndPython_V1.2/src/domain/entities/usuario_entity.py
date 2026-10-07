from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.value_objects.rol_usuario import RolUsuario


@dataclass
class UsuarioEntity:
    uid: int | None
    nombre: str
    email: str
    roles: list[RolUsuario] = field(default_factory=list)
    activo: bool = True
    password_hash: str | None = None   # dbo.users.pass  — owned by Drupal, never overwritten
    new_pass_hash: str | None = None   # dbo.users.new_pass — bcrypt, written only by new system
    creado_en: datetime = None             # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.creado_en is None:
            # UTC naive, equivalente a datetime.utcnow() pero sin DeprecationWarning
            self.creado_en = datetime.now(UTC).replace(tzinfo=None)

    def tiene_rol(self, rol: RolUsuario) -> bool:
        return rol in self.roles
