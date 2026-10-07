from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, description="Nombre de usuario")
    password: str = Field(min_length=1, description="Contrasena")
    fingerprint: str | None = Field(
        default=None, max_length=256, description="Huella del dispositivo (AP-0014)"
    )
    device_name: str | None = Field(
        default=None, max_length=200, description="Nombre del dispositivo (AP-0014)"
    )
