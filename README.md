Laboratorio 7 - Simplificación de gramáticas

Video de demostración (Problema 1): 

Estructura
- main.py: programa principal.
- gramatica.py: lectura y validación de los archivos de gramáticas.
- validador.py: regex de producciones evaluada con el AFN de Thompson del Proyecto 1.
- simplificacion.py: eliminación de producciones-ε, unitarias, símbolos inútiles y paso a CNF.
- shunting_yard.py, arbol_sintactico.py, afn_thompson.py: módulos del Proyecto 1.
- gramaticas/: gramatica1.txt, gramatica2.txt, gramatica3.txt y gramatica_error.txt.
- problema2/Problema2.pdf: solución del Problema 2 con todo el procedimiento.

Formato de los archivos
Una producción por línea, con cuerpos separados por |. La flecha puede escribirse -> o →.
Mayúsculas son no terminales; minúsculas y dígitos son terminales; ε es la cadena vacía.
Ejemplo: S -> 0A0 | 1B1 | BB

Validación
Cada línea se normaliza (sin espacios, flecha como > y ε como &) y se simula en el AFN construido con:
N>((N|T)+|&)(\|((N|T)+|&))*
donde N = (A|B|...|Z) y T = (a|...|z|0|...|9). Si una línea no es aceptada se indica el carácter
donde el AFN se queda sin estados y la ejecución se detiene.

Uso
python main.py gramaticas/gramatica1.txt          (solo eliminación de producciones-ε)
python main.py gramaticas/gramatica1.txt --todo   (ε, unitarias, inútiles y CNF)
python main.py gramaticas/gramatica_error.txt     (demostración de la validación)
