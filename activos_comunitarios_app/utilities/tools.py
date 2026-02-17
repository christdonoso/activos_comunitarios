"""
Funciones de utilidad para diferentes tareas
"""


remove_csrftoken = lambda x:{k:v for k,v in x.items() if k != 'csrfmiddlewaretoken'}