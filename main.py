"""Laboratorio 7 - Simplificación de gramáticas.
Uso: python main.py gramaticas/gramatica1.txt [--todo]
Sin --todo solo se eliminan producciones-ε (lo pedido en el Problema 1).
Con --todo también se quitan unitarias, inútiles y se pasa a CNF."""
import sys
from gramatica import leer_gramatica, imprimir_gramatica
from simplificacion import (eliminar_epsilon, eliminar_unitarias,
                            eliminar_inutiles, a_chomsky, es_cnf)


def mostrar(log):
    for tipo, texto in log:
        if tipo == "tit":
            print("\n" + texto.upper())
            print("-" * len(texto))
        elif tipo == "sub":
            print("\n" + texto)
        elif tipo == "gram":
            print("    " + texto)
        else:
            print("  " + texto)
    log.clear()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    ruta = sys.argv[1]
    g = leer_gramatica(ruta)
    inicial = next(iter(g))
    imprimir_gramatica(g, "Gramática original:")

    log = []
    g = eliminar_epsilon(g, log)
    mostrar(log)

    if "--todo" in sys.argv:
        g = eliminar_unitarias(g, log)
        mostrar(log)
        g = eliminar_inutiles(g, inicial, log)
        mostrar(log)
        g = a_chomsky(g, log)
        mostrar(log)
        print(f"\n¿Está en CNF? {'sí' if es_cnf(g) else 'no'}")


if __name__ == "__main__":
    main()
