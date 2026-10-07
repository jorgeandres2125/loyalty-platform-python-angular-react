import base64
from dataclasses import dataclass
from datetime import datetime

from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Util.Padding import pad

from src.domain.value_objects.token_sapin import TokenSAPIN
from src.shared.constants.cifrado import TAMANO_BLOQUE_AES_BYTES
from src.shared.utils.vector_inicializacion import generar_iv

_LONGITUD_CLAVE_CTR: int = 16
_LONGITUD_CLAVE_CBC: int = 32


@dataclass
class CryptoSAPIN:
    """AES-128-CTR para tokens SAPIN + AES-256-CBC para passwords legacy.

    AP-0179 (Vector de Inicializacion):
    - cifrar_password_cbc usa un IV ALEATORIO recien generado en cada cifrado
      (generar_iv), de 16 bytes (bloque AES), antepuesto al criptograma.
    - generar_token_ctr usa un IV FIJO compartido con la plataforma SAPIN externa:
      es la UNICA excepcion documentada, exigida por la paridad byte-for-byte con
      el PHP legado (CLAUDE.md, restriccion de migracion 2). En CTR la clave es de
      16 bytes y el IV tambien de 16 bytes, de modo que IV == longitud de clave
      (clausula de longitud de AP-0179 satisfecha); solo la aleatoriedad se cede
      por el contrato del SSO externo.

    Las longitudes de clave e IV se validan en construccion (AP-0179).
    """
    aes_key_ctr: bytes
    aes_iv_ctr: bytes
    aes_key_cbc: bytes

    def __post_init__(self) -> None:
        if len(self.aes_key_ctr) != _LONGITUD_CLAVE_CTR:
            raise ValueError("aes_key_ctr debe ser de 16 bytes (AES-128)")
        if len(self.aes_iv_ctr) != _LONGITUD_CLAVE_CTR:
            raise ValueError(
                "aes_iv_ctr debe ser de 16 bytes (AP-0179, IV igual a longitud de clave CTR)"
            )
        if len(self.aes_key_cbc) != _LONGITUD_CLAVE_CBC:
            raise ValueError("aes_key_cbc debe ser de 32 bytes (AES-256)")

    def generar_token_ctr(self, cedula: str, nombre: str, alianza: str) -> TokenSAPIN:
        payload = f"{cedula}|{nombre}|{alianza}".encode()
        ctr = Counter.new(128, initial_value=int.from_bytes(self.aes_iv_ctr, "big"))
        cipher = AES.new(self.aes_key_ctr, AES.MODE_CTR, counter=ctr)
        cifrado = cipher.encrypt(payload)
        token_b64 = base64.urlsafe_b64encode(cifrado).decode("ascii")
        return TokenSAPIN(token_cifrado=token_b64, cedula=cedula, generado_en=datetime.utcnow())

    def descifrar_password_cbc(self, password_cifrado_b64: str) -> str:
        """Descifra un password AES-256-CBC del snapshot aes_passwords."""
        raw = base64.b64decode(password_cifrado_b64)
        iv = raw[:16]
        cipher = AES.new(self.aes_key_cbc, AES.MODE_CBC, iv=iv)
        decrypted = cipher.decrypt(raw[16:])
        pad_len = decrypted[-1]
        return decrypted[:-pad_len].decode("utf-8")

    def cifrar_password_cbc(self, password: str) -> str:
        # AP-0179, IV aleatorio recien generado por cifrado (16 bytes, bloque AES).
        iv = generar_iv(TAMANO_BLOQUE_AES_BYTES)
        cipher = AES.new(self.aes_key_cbc, AES.MODE_CBC, iv=iv)
        cifrado = cipher.encrypt(pad(password.encode("utf-8"), TAMANO_BLOQUE_AES_BYTES))
        return base64.b64encode(iv + cifrado).decode("ascii")
