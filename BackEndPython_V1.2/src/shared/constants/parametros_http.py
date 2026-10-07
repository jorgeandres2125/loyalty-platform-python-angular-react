from __future__ import annotations

from typing import Final

# AP-0199: nombres de parametros de query que la aplicacion define como
# multi-valor (pueden repetirse legitimamente). El API SUFI no expone hoy ningun
# filtro multi-seleccion, de modo que el conjunto esta vacio: todo nombre de
# parametro de query repetido se colapsa a su primera aparicion (se descartan las
# demas). Ampliar aqui solo si un endpoint define un parametro que admite N valores.
PARAMETROS_QUERY_MULTIVALOR: Final[frozenset[str]] = frozenset()
