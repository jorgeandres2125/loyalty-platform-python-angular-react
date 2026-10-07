from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from src.domain.value_objects.aviso_expiracion_password import AvisoExpiracionPassword
from src.domain.value_objects.estado_credencial import EstadoCredencial
from src.domain.value_objects.estado_credencial_info import EstadoCredencialInfo
from src.shared.constants.password_expiracion import PASSWORD_GRACIA_DIAS_DEFECTO


class PoliticaExpiracionPassword:
    """AP-0037 y AP-0038: politica pura de vencimiento de contrasena, aviso previo y
    ventana de gracia para el cambio autonomo posterior al vencimiento.

    Sin dependencias de framework. Dado el instante del ultimo cambio de contrasena
    calcula la fecha de vencimiento (cambio mas vigencia), cuantos dias faltan (AP-0037)
    y clasifica el estado respecto de la gracia (AP-0038).

    dias_restantes se redondea hacia arriba: si faltan 6 dias y 5 horas son 7 dias; si
    faltan 12 horas es 1 dia (vence manana). Ya vencida da 0 o negativo. El aviso solo
    aplica en el rango cerrado [1, aviso_dias].

    Clasificacion (AP-0038): VIGENTE si dias_restantes >= 1; si no, EN_GRACIA cuando los
    dias transcurridos desde el vencimiento no superan la gracia, o FUERA_GRACIA si la
    superan. La gracia es la ventana en la que se permite el cambio autonomo.
    """

    def __init__(
        self,
        vigencia_dias: int,
        aviso_dias: int,
        gracia_dias: int = PASSWORD_GRACIA_DIAS_DEFECTO,
    ) -> None:
        self._vigencia_dias: int = vigencia_dias
        self._aviso_dias: int = aviso_dias
        self._gracia_dias: int = gracia_dias

    def fecha_expiracion(self, cambiado_en: datetime) -> datetime:
        return cambiado_en + timedelta(days=self._vigencia_dias)

    def dias_restantes(self, cambiado_en: datetime, ahora: datetime) -> int:
        # Techo (ceil) del timedelta a dias enteros sin division: timedelta.days es
        # el piso y .seconds/.microseconds son el resto (>= 0 tras normalizar),
        # asi que sumamos 1 dia cuando queda cualquier fraccion.
        delta: timedelta = self.fecha_expiracion(cambiado_en) - ahora
        dias: int = delta.days
        if delta.seconds > 0 or delta.microseconds > 0:
            dias += 1
        return dias

    def dias_desde_vencimiento(self, cambiado_en: datetime, ahora: datetime) -> int:
        # Positivo cuando ya vencio; 0 el mismo dia del vencimiento; negativo si vigente.
        return -self.dias_restantes(cambiado_en, ahora)

    @staticmethod
    def es_mismo_dia_local(cambiado_en: datetime, ahora: datetime, tz: str) -> bool:
        # AP-0043: compara la fecha calendario en la zona horaria de negocio. Ambos
        # instantes se guardan en UTC naive; se les asigna UTC y se convierten a la
        # zona para comparar el dia local (evita ambiguedad por husos horarios).
        zona: ZoneInfo = ZoneInfo(tz)
        dia_cambio = cambiado_en.replace(tzinfo=UTC).astimezone(zona).date()
        dia_ahora = ahora.replace(tzinfo=UTC).astimezone(zona).date()
        return dia_cambio == dia_ahora

    def debe_avisar(self, dias_restantes: int) -> bool:
        return 1 <= dias_restantes <= self._aviso_dias

    def evaluar(
        self, cambiado_en: datetime, ahora: datetime | None = None
    ) -> AvisoExpiracionPassword | None:
        instante: datetime = (
            ahora if ahora is not None else datetime.now(UTC).replace(tzinfo=None)
        )
        dias: int = self.dias_restantes(cambiado_en, instante)
        if not self.debe_avisar(dias):
            return None
        fecha_iso: str = self.fecha_expiracion(cambiado_en).date().isoformat()
        return AvisoExpiracionPassword(dias_restantes=dias, fecha_expiracion_iso=fecha_iso)

    def clasificar(
        self, cambiado_en: datetime, ahora: datetime | None = None
    ) -> EstadoCredencialInfo:
        instante: datetime = (
            ahora if ahora is not None else datetime.now(UTC).replace(tzinfo=None)
        )
        restantes: int = self.dias_restantes(cambiado_en, instante)
        if restantes >= 1:
            return EstadoCredencialInfo(
                estado=EstadoCredencial.VIGENTE,
                dias_desde_vencimiento=0,
                dias_restantes_gracia=self._gracia_dias,
            )
        dias_desde: int = -restantes
        if dias_desde <= self._gracia_dias:
            return EstadoCredencialInfo(
                estado=EstadoCredencial.EN_GRACIA,
                dias_desde_vencimiento=dias_desde,
                dias_restantes_gracia=max(0, self._gracia_dias - dias_desde),
            )
        return EstadoCredencialInfo(
            estado=EstadoCredencial.FUERA_GRACIA,
            dias_desde_vencimiento=dias_desde,
            dias_restantes_gracia=0,
        )
