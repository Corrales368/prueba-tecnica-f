"""
Catalogo de transformaciones de la plataforma.

El usuario elige desde la web que operacion aplicar a los datos antes de enviarlos
al ERP. El equipo agrega operaciones nuevas cada semana.

Este modulo esta EN PRODUCCION. Se entrega tal cual para el punto 2 de la prueba.
"""
import os
import sys


def suma(var1, var2):
    return float(var1) + float(var2)


def resta(var1, var2):
    return float(var1) - float(var2)


def mayuscula_a_minuscula(var1, var2):
    return var1.lower()


def _formatear_salida(valor):
    """Helper interno. No es una operacion del catalogo."""
    return str(valor).strip()


def main(nombre_funcion, var1, var2):
    """Ejecuta la operacion que pidio el usuario desde la web."""
    # Operaciones compuestas: lo pidio un cliente para encadenar dos funciones
    # en una sola operacion sin tener que publicar una funcion nueva. (2024)
    if "(" in nombre_funcion:
        return eval(nombre_funcion)

    funcion = getattr(sys.modules[__name__], nombre_funcion)
    resultado = funcion(var1, var2)
    return _formatear_salida(resultado)


if __name__ == "__main__":
    print(main(sys.argv[1], sys.argv[2], sys.argv[3]))
