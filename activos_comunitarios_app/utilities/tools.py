"""
Funciones de utilidad para diferentes tareas
"""
import re
from itertools import cycle


def validar_rut_chileno(rut):
    """Valida el RUT chileno (algoritmo módulo 11)."""
    rut = rut.upper().replace(".", "").replace("-", "")
    if not re.match(r"^\d{1,8}[0-9K]$", rut):
        return False
    aux = rut[:-1]
    dv = rut[-1:]
    reversa = map(int, reversed(aux))
    factores = cycle(range(2, 8))
    suma = sum(d * f for d, f in zip(reversa, factores))
    res = 11 - (suma % 11)
    esperado = '0' if res == 11 else 'K' if res == 10 else str(res)
    return dv == esperado