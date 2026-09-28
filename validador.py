"""Validación de producciones usando el pipeline del Proyecto 1 (regex -> AFN de Thompson)."""
import string
from shunting_yard import a_postfix
from arbol_sintactico import construir_arbol
from afn_thompson import construir_afn

NO_TERMINAL = "(" + "|".join(string.ascii_uppercase) + ")"
TERMINAL = "(" + "|".join(string.ascii_lowercase + string.digits) + ")"
CUERPO = f"(({NO_TERMINAL}|{TERMINAL})+|\\&)"

# Forma de una línea ya normalizada:  X>cuerpo|cuerpo|...   (& representa a ε)
REGEX_PRODUCCION = f"{NO_TERMINAL}\\>{CUERPO}(\\|{CUERPO})*"


def normalizar(linea):
    """Quita espacios, unifica la flecha en '>' y cambia ε por '&'.
    ε se sustituye porque dentro de la regex del Proyecto 1 ε significa 'cadena vacía',
    así que no puede usarse para reconocer el carácter ε del archivo."""
    linea = "".join(linea.split())
    return linea.replace("→", ">").replace("->", ">").replace("ε", "&")


def construir_validador():
    postfix, _ = a_postfix(REGEX_PRODUCCION)
    raiz = construir_arbol(postfix, [])
    return construir_afn(raiz, [])


def validar(afn, linea, pasos=None):
    return afn.acepta(normalizar(linea), pasos)
