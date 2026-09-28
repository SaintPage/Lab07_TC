"""Carga de gramáticas desde archivo de texto."""
import sys
from validador import construir_validador, validar, normalizar, REGEX_PRODUCCION


def leer_gramatica(ruta):
    afn = construir_validador()
    gramatica = {}
    with open(ruta, encoding="utf-8") as f:
        lineas = [l.rstrip("\n") for l in f if l.strip()]

    print(f"Validando {ruta} con la regex:\n  {REGEX_PRODUCCION}\n")
    for num, linea in enumerate(lineas, 1):
        pasos = []
        if not validar(afn, linea, pasos):
            print(f"  Línea {num}: {linea}   ->  INVÁLIDA")
            forma = normalizar(linea)
            print(f"  Forma normalizada: {forma}")
            leidos = sum("Leyendo" in p for p in pasos)
            if any("No hay estados" in p for p in pasos):
                print("                     " + " " * (leidos - 1) + "^")
                print(f"  El AFN se quedó sin estados al leer '{forma[leidos - 1]}' (posición {leidos - 1}).")
            else:
                print("  El AFN leyó toda la línea pero no terminó en estado de aceptación (línea incompleta).")
            print("\nLa gramática tiene errores. Se detiene la ejecución.")
            sys.exit(1)
        print(f"  Línea {num}: {linea}   ->  válida")

        cabeza, cuerpos = normalizar(linea).split(">")
        for cuerpo in cuerpos.split("|"):
            simbolos = () if cuerpo == "&" else tuple(cuerpo)
            gramatica.setdefault(cabeza, [])
            if simbolos not in gramatica[cabeza]:
                gramatica[cabeza].append(simbolos)
    # No-terminales que aparecen en cuerpos pero no tienen producciones propias
    for cuerpos in list(gramatica.values()):
        for c in cuerpos:
            for s in c:
                if es_no_terminal(s) and s not in gramatica:
                    gramatica[s] = []
                    print(f"  Aviso: {s} aparece en un cuerpo pero no tiene producciones.")
    print()
    return gramatica


def es_no_terminal(simbolo):
    return simbolo[0].isupper()


def texto_cuerpo(cuerpo):
    if not cuerpo:
        return "ε"
    separador = " " if any(len(s) > 1 for s in cuerpo) else ""
    return separador.join(cuerpo)


def texto_gramatica(g):
    return [f"{A} → " + " | ".join(texto_cuerpo(c) for c in cuerpos) if cuerpos
            else f"{A} → (sin producciones)" for A, cuerpos in g.items()]


def imprimir_gramatica(g, titulo):
    print(titulo)
    for l in texto_gramatica(g):
        print("  " + l)
    print()
