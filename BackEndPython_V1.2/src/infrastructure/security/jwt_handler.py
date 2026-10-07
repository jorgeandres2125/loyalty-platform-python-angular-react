from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from src.domain.exceptions.token_invalido import TokenInvalido


class JWTHandler:
    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self._secret = secret_key
        self._algorithm = algorithm

    def encode(self, payload: dict[str, Any], expires_minutes: int = 60) -> str:
        data = payload.copy()
        data["exp"] = datetime.now(UTC) + timedelta(minutes=expires_minutes)
        return jwt.encode(data, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except JWTError as exc:
            raise TokenInvalido(str(exc)) from exc
