"""Algoritmos de simplificación de CFGs. Cada función recibe la gramática y una
bitácora (lista) donde va registrando los pasos para mostrarlos en pantalla."""
from itertools import product
from gramatica import es_no_terminal, texto_cuerpo, texto_gramatica


def _conjunto(c):
    return "{" + ", ".join(sorted(c)) + "}" if c else "∅"


def _registrar_gramatica(log, g, titulo):
    log.append(("sub", titulo))
    for l in texto_gramatica(g):
        log.append(("gram", l))


# ---------------------------------------------------------------- a) producciones-ε
def encontrar_anulables(g, log):
    anulables = {A for A, cuerpos in g.items() if () in cuerpos}
    log.append(("txt", f"Ronda 0 (A → ε directo): {_conjunto(anulables)}"))
    ronda = 1
    while True:
        nuevos = {A for A, cuerpos in g.items() if A not in anulables
                  and any(c and all(s in anulables for s in c) for c in cuerpos)}
        if not nuevos:
            log.append(("txt", f"Ronda {ronda}: no se agregan símbolos. Punto fijo."))
            break
        anulables |= nuevos
        log.append(("txt", f"Ronda {ronda}: se agregan {_conjunto(nuevos)} "
                           f"-> anulables = {_conjunto(anulables)}"))
        ronda += 1
    return anulables


def eliminar_epsilon(g, log):
    log.append(("tit", "a) Eliminación de producciones-ε"))
    log.append(("sub", "Paso 1: símbolos anulables"))
    anulables = encontrar_anulables(g, log)

    prods_anulables = [f"{A} → {texto_cuerpo(c)}" for A, cs in g.items()
                       for c in cs if all(s in anulables for s in c)]
    log.append(("txt", "Producciones anulables (todo su cuerpo es anulable): "
                       + ", ".join(prods_anulables)))

    log.append(("sub", "Paso 2: nuevas producciones (2^m casos por producción)"))
    nueva = {}
    for A, cuerpos in g.items():
        nueva[A] = []
        for c in cuerpos:
            if not c:
                log.append(("txt", f"{A} → ε : se elimina."))
                continue
            pos = [i for i, s in enumerate(c) if s in anulables]
            m = len(pos)
            if m == 0:
                log.append(("txt", f"{A} → {texto_cuerpo(c)} : m = 0, se conserva igual."))
                resultados = [c]
            else:
                resultados = []
                casos = []
                for mascara in product([True, False], repeat=m):
                    quitar = {p for p, conservar in zip(pos, mascara) if not conservar}
                    r = tuple(s for i, s in enumerate(c) if i not in quitar)
                    casos.append(texto_cuerpo(r) + (" (se descarta)" if not r else ""))
                    if r:
                        resultados.append(r)
                anul = ", ".join(f"{c[p]} en posición {p + 1}" for p in pos)
                log.append(("txt", f"{A} → {texto_cuerpo(c)} : m = {m} ({anul}), "
                                   f"2^{m} = {2 ** m} casos: " + ", ".join(casos)))
            for r in resultados:
                if r not in nueva[A]:
                    nueva[A].append(r)
    _registrar_gramatica(log, nueva, "Gramática sin producciones-ε:")
    return nueva


# ---------------------------------------------------------------- b) unitarias
def _es_unitaria(c):
    return len(c) == 1 and es_no_terminal(c[0])


def eliminar_unitarias(g, log):
    log.append(("tit", "b) Eliminación de producciones unitarias"))
    unitarias = [f"{A} → {c[0]}" for A, cs in g.items() for c in cs if _es_unitaria(c)]
    log.append(("txt", "Producciones unitarias: " + (", ".join(unitarias) or "ninguna")))

    log.append(("sub", "Pares unitarios (A, B) tales que A ⇒* B usando solo unitarias"))
    pares = {}
    for A in g:
        alcanzados, pila = [A], [A]
        while pila:
            X = pila.pop()
            for c in g.get(X, []):
                if _es_unitaria(c) and c[0] not in alcanzados:
                    alcanzados.append(c[0])
                    pila.append(c[0])
        pares[A] = alcanzados
        log.append(("txt", f"{A}: " + ", ".join(f"({A}, {B})" for B in alcanzados)))

    log.append(("sub", "Para cada par (A, B) se copian a A las producciones no unitarias de B"))
    nueva = {}
    for A in g:
        nueva[A] = []
        for B in pares[A]:
            aporta = [c for c in g.get(B, []) if not _es_unitaria(c)]
            if B != A:
                log.append(("txt", f"({A}, {B}): {A} recibe "
                                   + (" | ".join(texto_cuerpo(c) for c in aporta) or "nada")))
            for c in aporta:
                if c not in nueva[A]:
                    nueva[A].append(c)
    _registrar_gramatica(log, nueva, "Gramática sin producciones unitarias:")
    return nueva


# ---------------------------------------------------------------- c) inútiles
def eliminar_inutiles(g, inicial, log):
    log.append(("tit", "c) Eliminación de símbolos inútiles"))

    log.append(("sub", "c.a) Símbolos que producen (generadores)"))
    gen = {A for A, cs in g.items() if any(all(not es_no_terminal(s) for s in c) for c in cs)}
    log.append(("txt", f"Ronda 0 (producen solo terminales): {_conjunto(gen)}"))
    ronda = 1
    while True:
        nuevos = {A for A, cs in g.items() if A not in gen and
                  any(all(not es_no_terminal(s) or s in gen for s in c) for c in cs)}
        if not nuevos:
            log.append(("txt", f"Ronda {ronda}: no se agregan símbolos. Punto fijo."))
            break
        gen |= nuevos
        log.append(("txt", f"Ronda {ronda}: se agregan {_conjunto(nuevos)} -> {_conjunto(gen)}"))
        ronda += 1
    no_gen = set(g) - gen
    log.append(("txt", f"No producen: {_conjunto(no_gen)}. Se eliminan junto con "
                       "toda producción que los contenga."))
    g1 = {A: [c for c in cs if all(not es_no_terminal(s) or s in gen for s in c)]
          for A, cs in g.items() if A in gen}
    _registrar_gramatica(log, g1, "Gramática tras quitar los que no producen:")

    log.append(("sub", f"c.b) Símbolos alcanzables desde {inicial}"))
    alc = {inicial}
    frontera = [inicial]
    ronda = 0
    log.append(("txt", f"Ronda 0: {_conjunto(alc)}"))
    while frontera:
        ronda += 1
        nuevos = set()
        for A in frontera:
            for c in g1.get(A, []):
                nuevos |= {s for s in c if es_no_terminal(s) and s not in alc}
        if not nuevos:
            log.append(("txt", f"Ronda {ronda}: no se agregan símbolos. Punto fijo."))
            break
        alc |= nuevos
        log.append(("txt", f"Ronda {ronda}: se agregan {_conjunto(nuevos)} -> {_conjunto(alc)}"))
        frontera = list(nuevos)
    log.append(("txt", f"No alcanzables: {_conjunto(set(g1) - alc)}. Se eliminan."))
    g2 = {A: cs for A, cs in g1.items() if A in alc}
    _registrar_gramatica(log, g2, "Gramática sin símbolos inútiles:")
    return g2


# ---------------------------------------------------------------- d) CNF
def a_chomsky(g, log):
    log.append(("tit", "d) Forma Normal de Chomsky"))

    log.append(("sub", "Paso 1: en cuerpos de longitud ≥ 2, cada terminal t se cambia por X_t (X_t → t)"))
    terminales = {}
    g1 = {}
    for A, cs in g.items():
        g1[A] = []
        for c in cs:
            if len(c) >= 2:
                nuevo = []
                for s in c:
                    if not es_no_terminal(s):
                        terminales.setdefault(s, "X" + s)
                        s = terminales[s]
                    nuevo.append(s)
                c = tuple(nuevo)
            g1[A].append(c)
    for t, X in sorted(terminales.items()):
        log.append(("txt", f"Nueva variable {X} → {t}"))
        g1[X] = [(t,)]
    _registrar_gramatica(log, g1, "Resultado del paso 1:")

    log.append(("sub", "Paso 2: cuerpos de longitud ≥ 3 se parten en cadenas de 2 símbolos"))
    sufijos = {}
    g2 = {A: [] for A in g1}

    def partir(c):
        if len(c) <= 2:
            return c
        resto = tuple(c[1:])
        if resto not in sufijos:
            Y = f"Y{len(sufijos) + 1}"
            sufijos[resto] = Y
            g2[Y] = [partir(resto)]
            log.append(("txt", f"Nueva variable {Y} → {texto_cuerpo(g2[Y][0])}  "
                               f"(representa {texto_cuerpo(resto)})"))
        return (c[0], sufijos[resto])

    for A in list(g1):
        for c in g1[A]:
            nuevo = partir(c)
            if nuevo != c:
                log.append(("txt", f"{A} → {texto_cuerpo(c)}  se convierte en  {A} → {texto_cuerpo(nuevo)}"))
            g2[A].append(nuevo)
    if not sufijos:
        log.append(("txt", "No hay cuerpos de longitud ≥ 3."))
    _registrar_gramatica(log, g2, "Gramática en CNF:")
    return g2


def es_cnf(g):
    return all((len(c) == 1 and not es_no_terminal(c[0])) or
               (len(c) == 2 and all(es_no_terminal(s) for s in c))
               for cs in g.values() for c in cs)
