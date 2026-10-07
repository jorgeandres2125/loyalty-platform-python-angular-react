class ProgramaNoAutorizado(Exception):
    def __init__(self, programa: str) -> None:
        super().__init__(f"Sin autorización para el programa: {programa}")
        self.programa = programa
