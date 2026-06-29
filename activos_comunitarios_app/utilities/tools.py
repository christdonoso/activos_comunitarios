"""
Funciones de utilidad para diferentes tareas
"""
import re
from itertools import cycle
from datetime import date


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



def calcular_edad(fecha_nacimiento):
    today = date.today()
    edad = today.year - fecha_nacimiento.year
    
    cumplio_años = (today.month, today.day) >= (fecha_nacimiento.month, fecha_nacimiento.day)
    
    if not cumplio_años:
        edad -= 1
        
    return edad



def is_point_in_polygon(lat, lng, polygon):
    """
    Valida si un punto está dentro de un polígono con formato GeoJSON.
    Nota: GeoJSON usa [longitud, latitud].
    """
    try:
        # Extraer la lista de puntos: coordinates[0] es el anillo exterior
        # El formato es [[long, lat], [long, lat], ...]
        polygon = polygon['geometry']['coordinates'][0]
        
        n = len(polygon)
        inside = False
        
        # Punto A (el que queremos verificar)
        x, y = lng, lat  # x=long, y=lat para que coincida con GeoJSON
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    except (KeyError, IndexError, TypeError):
        return False