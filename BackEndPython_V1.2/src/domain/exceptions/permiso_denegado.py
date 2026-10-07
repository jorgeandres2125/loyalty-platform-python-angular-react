class PermisoDenegado(Exception):
    def __init__(self, permiso: str) -> None:
        super().__init__(f"Permiso denegado: {permiso}")
        self.permiso = permiso
