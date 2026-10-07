from __future__ import annotations


class PasoOmitido(Exception):
    """AP-0187: se intento ejecutar un paso del wizard sin completar los previos.

    El orden de pasos se garantiza en el servidor; ningun paso puede saltarse a
    nivel tecnico aunque el cliente invoque directamente un endpoint posterior.
    """
