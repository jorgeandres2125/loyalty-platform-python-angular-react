from src.domain.value_objects.permiso import Permiso
from src.domain.value_objects.rol_usuario import RolUsuario
from src.shared.constants.rbac import ROL_PERMISOS, permisos_de_roles


class TestRolPermisos:
    def test_administrator_tiene_todos(self) -> None:
        assert ROL_PERMISOS[RolUsuario.ADMINISTRATOR] == frozenset(Permiso)

    def test_reproduce_guardia_catalogos(self) -> None:
        con = {
            r for r, p in ROL_PERMISOS.items()
            if Permiso.ADMIN_CATALOGOS_GESTIONAR in p
        }
        assert con == {RolUsuario.ADMINISTRATOR}

    def test_reproduce_guardia_usuarios(self) -> None:
        con = {
            r for r, p in ROL_PERMISOS.items()
            if Permiso.USUARIOS_GESTIONAR_ESTADO in p
        }
        assert con == {RolUsuario.ADMINISTRATOR, RolUsuario.WEBMASTER}

    def test_comisionista_es_usuario_final_no_staff(self) -> None:
        perms = ROL_PERMISOS[RolUsuario.COMISIONISTA]
        assert Permiso.MOVILIDAD_PERFIL_VER_PROPIO in perms
        assert Permiso.MOVILIDAD_ASESORES_GESTIONAR not in perms
        assert Permiso.REPORTES_EXPORTAR not in perms
        assert Permiso.DOCUMENTOS_MODERAR not in perms

    def test_resolver_une_permisos_de_varios_roles(self) -> None:
        roles = frozenset({RolUsuario.COMISIONISTA, RolUsuario.DOCUMENTADOR})
        efectivos = permisos_de_roles(roles)
        assert Permiso.MOVILIDAD_PERFIL_VER_PROPIO in efectivos
        assert Permiso.DOCUMENTOS_MODERAR in efectivos

    def test_rol_sin_permisos_no_aporta(self) -> None:
        assert permisos_de_roles(frozenset({RolUsuario.ANONIMO})) == frozenset()

    def test_ningun_permiso_queda_huerfano(self) -> None:
        asignados: set[Permiso] = set()
        for permisos in ROL_PERMISOS.values():
            asignados |= permisos
        assert asignados == frozenset(Permiso)
