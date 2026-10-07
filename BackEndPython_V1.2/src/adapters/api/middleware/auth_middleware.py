from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer

from src.domain.exceptions.token_invalido import TokenInvalido
from src.infrastructure.config.settings import Settings
from src.infrastructure.security.jwt_handler import JWTHandler

_bearer = HTTPBearer(auto_error=False)


async def get_current_user(request: Request) -> dict:
    settings = Settings()
    handler = JWTHandler(settings.jwt_secret_key, settings.jwt_algorithm)
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
    token = auth.split(" ", 1)[1]
    try:
        return handler.decode(token)
    except TokenInvalido as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
