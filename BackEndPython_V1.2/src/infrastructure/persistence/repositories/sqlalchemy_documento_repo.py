from datetime import datetime
from typing import Any

from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.documento_entity import DocumentoEntity
from src.domain.ports.outbound.cifrador_campos import CifradorCampos
from src.infrastructure.persistence.models.documento_model import DocumentoModel
from src.shared.constants.cifrado import TABLA_PERFIL_CONTACTO
from src.shared.utils.cifrado_aad import construir_aad


class SQLAlchemyDocumentoRepo:
    def __init__(self, session: AsyncSession, cipher: CifradorCampos) -> None:
        self._session = session
        self._cipher = cipher

    async def obtener_por_documento_tipo_async(self, numero_documento: str, tipo: int) -> DocumentoEntity | None:
        result = await self._session.execute(
            select(DocumentoModel).where(
                DocumentoModel.numero_documento == numero_documento,
                DocumentoModel.tipo == tipo,
            )
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def obtener_por_did_async(self, did: int) -> DocumentoEntity | None:
        result = await self._session.execute(
            select(DocumentoModel).where(DocumentoModel.did == did)
        )
        row = result.scalar_one_or_none()
        return self._to_entity(row) if row else None

    async def guardar_async(self, entity: DocumentoEntity) -> DocumentoEntity:
        existing = await self.obtener_por_documento_tipo_async(entity.numero_documento, entity.tipo)
        if existing and existing.did is not None:
            nueva_version: int = (existing.version or 1) + 1
            await self._session.execute(
                update(DocumentoModel)
                .where(DocumentoModel.did == existing.did)
                .values(nombre=entity.nombre, estado=entity.estado, version=nueva_version, fecha=datetime.utcnow())
            )
            entity.did = existing.did
            entity.version = nueva_version
        else:
            model = DocumentoModel(
                numero_documento=entity.numero_documento,
                nombre=entity.nombre,
                estado=entity.estado,
                version=1,
                fecha=datetime.utcnow(),
                tipo=entity.tipo,
            )
            self._session.add(model)
            await self._session.flush()
            entity.did = model.did
            entity.version = 1
        return entity

    async def listar_por_asesor_async(self, numero_documento: str) -> list[DocumentoEntity]:
        result = await self._session.execute(
            select(DocumentoModel).where(DocumentoModel.numero_documento == numero_documento)
        )
        return [self._to_entity(row) for row in result.scalars().all()]

    async def eliminar_async(self, did: int) -> None:
        await self._session.execute(delete(DocumentoModel).where(DocumentoModel.did == did))

    async def actualizar_estado_async(self, did: int, estado: str) -> None:
        await self._session.execute(
            update(DocumentoModel).where(DocumentoModel.did == did).values(estado=estado)
        )

    async def actualizar_documento_async(
        self,
        did: int,
        nombre: str | None,
        estado: str | None,
        fecha: datetime | None,
    ) -> DocumentoEntity | None:
        values: dict[str, Any] = {}
        if nombre is not None:
            values["nombre"] = nombre
        if estado is not None:
            values["estado"] = estado
        if fecha is not None:
            values["fecha"] = fecha
        if values:
            await self._session.execute(
                update(DocumentoModel).where(DocumentoModel.did == did).values(**values)
            )
        return await self.obtener_por_did_async(did)

    async def listar_asesores_con_documentos_async(
        self,
        programa: int,
        page: int,
        page_size: int,
        cedula: str | None = None,
        tipo_doc: str | None = None,
    ) -> tuple[list[tuple[str, str, str | None]], int]:
        params: dict[str, Any] = {"programa": programa}
        filtros: str = ""
        if cedula:
            filtros += " AND pc.numero_documento LIKE :cedula "
            params["cedula"] = f"%{cedula}%"
        if tipo_doc:
            filtros += " AND LTRIM(RTRIM(pc.tipo_documento)) = :tipo_doc "
            params["tipo_doc"] = tipo_doc.strip()

        sql_count: str = (
            "SELECT COUNT(DISTINCT pc.numero_documento) AS total "
            "FROM dbo.users_perfil_contacto pc "
            "INNER JOIN dbo.user_documento ud "
            "  ON CAST(ud.numero_documento AS nvarchar(40)) = pc.numero_documento "
            f"WHERE pc.comisionista_programa_id = :programa{filtros}"
        )
        total_res = await self._session.execute(text(sql_count), params)
        total: int = int(total_res.scalar_one() or 0)

        offset: int = (page - 1) * page_size
        params_page: dict[str, Any] = {**params, "_off": offset, "_ps": page_size}
        # email es un campo restringido cifrado en reposo (AP-0147): se lee como
        # email_enc (varbinary) y se descifra con AAD = tabla|columna|numero_documento.
        sql_page: str = (
            "SELECT pc.tipo_documento, pc.numero_documento, pc.email_enc "
            "FROM dbo.users_perfil_contacto pc "
            "WHERE pc.comisionista_programa_id = :programa "
            "  AND EXISTS (SELECT 1 FROM dbo.user_documento ud2 "
            "      WHERE CAST(ud2.numero_documento AS nvarchar(40)) = pc.numero_documento) "
            f"{filtros}"
            "ORDER BY pc.numero_documento "
            "OFFSET :_off ROWS FETCH NEXT :_ps ROWS ONLY"
        )
        res = await self._session.execute(text(sql_page), params_page)
        rows: list[tuple[str, str, str | None]] = []
        for row in res.fetchall():
            numero_documento: str = (row[1] or "").strip()
            email_claro: str | None = self._cipher.descifrar(
                row[2],
                aad=construir_aad(TABLA_PERFIL_CONTACTO, "email", numero_documento),
            )
            rows.append(
                (
                    (row[0] or "").strip() if row[0] else "CC",
                    numero_documento,
                    email_claro,
                )
            )
        return rows, total

    async def listar_pendientes_async(self) -> list[DocumentoEntity]:
        result = await self._session.execute(
            select(DocumentoModel).where(DocumentoModel.estado == "pendiente")
        )
        return [self._to_entity(row) for row in result.scalars().all()]

    @staticmethod
    def _to_entity(row: DocumentoModel) -> DocumentoEntity:
        return DocumentoEntity(
            numero_documento=str(row.numero_documento) if row.numero_documento else "",
            nombre=row.nombre or "",
            estado=row.estado or "pendiente",
            version=row.version or 1,
            fecha=row.fecha,
            tipo=row.tipo or 0,
            did=row.did,
        )
