# Importa TODOS los modelos para que queden registrados en Base.metadata.
# Imprescindible para create_all y para que SQLAlchemy resuelva los ForeignKey
# por nombre de tabla (catálogos y tablas Drupal incluidas).
from .aes_password_model import AesPasswordModel
from .afp_model import AfpModel
from .arl_model import ArlModel
from .banco_model import BancoModel
from .canal_model import CanalModel
from .canal_oficina_model import CanalOficinaModel
from .ciudad_model import CiudadModel
from .comisionista_programa_model import ComisionistaProgramaModel
from .comisionista_subprograma_model import ComisionistaSubprogramaModel
from .departamento_model import DepartamentoModel
from .documento_model import DocumentoModel
from .drupal_rol_model import DrupalRolModel
from .drupal_user_model import DrupalUserModel
from .drupal_user_rol_model import DrupalUserRolModel
from .ejecutivo_asignacion_model import EjecutivoAsignacionModel
from .ejecutivo_model import EjecutivoCatalogoModel
from .eps_model import EpsModel
from .frontend_module_model import FrontendModuleModel
from .frontend_module_permission_model import FrontendModulePermissionModel
from .historico_correo_model import HistoricoCorreoModel
from .oficina_model import OficinaModel
from .perfil_contacto_model import PerfilContactoModel
from .perfil_emocional_model import PerfilEmocionalModel
from .perfil_tributario_model import PerfilTributarioModel
from .profesion_model import ProfesionModel

__all__ = [
    "DepartamentoModel", "CiudadModel",
    "ArlModel", "AfpModel", "EpsModel", "BancoModel", "ProfesionModel",
    "DrupalRolModel", "DrupalUserModel", "DrupalUserRolModel",
    "CanalModel", "OficinaModel", "CanalOficinaModel",
    "ComisionistaProgramaModel", "ComisionistaSubprogramaModel",
    "PerfilContactoModel", "PerfilTributarioModel", "PerfilEmocionalModel",
    "DocumentoModel",
    "EjecutivoCatalogoModel", "EjecutivoAsignacionModel",
    "AesPasswordModel",
    "FrontendModuleModel", "FrontendModulePermissionModel",
    "HistoricoCorreoModel",
]
