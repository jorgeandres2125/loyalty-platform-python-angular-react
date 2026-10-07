from __future__ import annotations

import ctypes
import sys
from types import TracebackType


class SecureBuffer:
    """AP-0080: contenedor de un secreto en memoria mutable con borrado fiable por
    sobrescritura con ceros al terminar su uso.

    Mantiene el secreto en un bytearray, lo bloquea en RAM best-effort (evita swap), lo expone
    sin copiar mediante memoryview y lo sobrescribe con ceros al salir del contexto o en clear:
    con ctypes.memset sobre la direccion del buffer (borrado a nivel de memoria) y, si hay una
    vista exportada, por asignacion de slice del mismo tamano (CPython la respeta). No expone el
    contenido en repr (anti-fuga en logs y trazas).

        with SecureBuffer.desde_bytes(secreto) as sb:
            usar(sb.vista())   # memoryview, sin convertir a str
        # aqui el buffer subyacente ya quedo en ceros

    Limitacion documentada (AP-0080): no elimina copias inmutables previas (str o bytes) ni la
    memoria interna de librerias de terceros; es el maximo alcanzable en el runtime de Python.
    """

    def __init__(self, datos: bytearray) -> None:
        self._buffer: bytearray = datos
        self._limpio: bool = False
        self._bloqueado: bool = self._intentar_mlock()

    @classmethod
    def desde_bytes(cls, secreto: bytes | bytearray) -> SecureBuffer:
        return cls(bytearray(secreto))

    def vista(self) -> memoryview:
        if self._limpio:
            raise ValueError("SecureBuffer ya fue limpiado: el secreto ya no esta disponible")
        return memoryview(self._buffer)

    def clear(self) -> None:
        if self._limpio:
            return
        longitud: int = len(self._buffer)
        if longitud:
            if self._bloqueado:
                self._munlock_best_effort()
            direccion: int | None = self._direccion_o_none()
            if direccion is not None:
                ctypes.memset(ctypes.c_void_p(direccion), 0, longitud)
            else:
                self._buffer[:] = bytes(longitud)
        self._bloqueado = False
        self._limpio = True

    def _direccion_o_none(self) -> int | None:
        try:
            referencia = ctypes.c_char.from_buffer(self._buffer)
            direccion: int = ctypes.addressof(referencia)
            del referencia
            return direccion
        except (BufferError, ValueError):
            return None

    def _intentar_mlock(self) -> bool:
        if not len(self._buffer):
            return False
        direccion: int | None = self._direccion_o_none()
        if direccion is None:
            return False
        try:
            return self._mlock_os(direccion, len(self._buffer))
        except Exception:  # noqa: BLE001 -- best-effort: mlock nunca debe romper el flujo
            return False

    def _munlock_best_effort(self) -> None:
        direccion: int | None = self._direccion_o_none()
        if direccion is None:
            return None
        try:
            self._munlock_os(direccion, len(self._buffer))
        except Exception:  # noqa: BLE001 -- best-effort
            return None

    @staticmethod
    def _mlock_os(direccion: int, longitud: int) -> bool:
        if sys.platform == "win32":
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            return bool(
                kernel32.VirtualLock(ctypes.c_void_p(direccion), ctypes.c_size_t(longitud))
            )
        biblioteca = ctypes.CDLL(None, use_errno=True)
        return biblioteca.mlock(ctypes.c_void_p(direccion), ctypes.c_size_t(longitud)) == 0

    @staticmethod
    def _munlock_os(direccion: int, longitud: int) -> None:
        if sys.platform == "win32":
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.VirtualUnlock(ctypes.c_void_p(direccion), ctypes.c_size_t(longitud))
        else:
            biblioteca = ctypes.CDLL(None, use_errno=True)
            biblioteca.munlock(ctypes.c_void_p(direccion), ctypes.c_size_t(longitud))

    def __enter__(self) -> SecureBuffer:
        return self

    def __exit__(
        self,
        _tipo: type[BaseException] | None,
        _valor: BaseException | None,
        _traza: TracebackType | None,
    ) -> None:
        self.clear()

    def __del__(self) -> None:
        try:
            self.clear()
        except Exception:  # noqa: BLE001 -- respaldo: nunca propagar desde el finalizador
            return None

    def __repr__(self) -> str:
        estado: str = "limpio" if self._limpio else f"activo, {len(self._buffer)} bytes"
        return f"<SecureBuffer {estado}>"
