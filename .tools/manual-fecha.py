"""Pone la fecha del aniversario y el calendario de estos días."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs\ANIVERSARIO-PROCEDIMIENTO.md"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if v in t:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    else:
        print("  NO ENCONTRADO: " + e)


# --- la fecha, arriba del todo
rep("""> **Para que ese día no dependa de que nadie se acuerde de nada.**""",
    """> **DOMINGO 8 DE NOVIEMBRE DE 2026** · **de 10:00 a 14:30**
>
> **Para que ese día no dependa de que nadie se acuerde de nada.**""",
    "la fecha, arriba del todo")

rep("**De 10:00 a 14:30.** **La gente entra con una palmera y una bolsa, y sale con una papeleta.**",
    "**Domingo 8 de noviembre. De 10:00 a 14:30.** **La gente entra con una palmera y una bolsa, y sale con una papeleta.**",
    "la fecha, en la primera frase")

# --- el calendario
CALENDARIO = """## 2 · El calendario de estos días

**Hoy es jueves 29 de octubre. Quedan diez días.**

| Cuándo | Qué |
|---|---|
| **Esta semana** *(29 – 1 nov)* | **Recortar y doblar las 500 papeletas** — **lo que más tiempo cuesta y no depende de nadie** · **decidir qué piezas de globos** y **hacer sus bases** · comprar lo que falte |
| **Semana del 2** | **Comprar el picoteo** *(jamón, cabecero, chorizo, queso, pastas Dulcesol)* · **confirmar la batukada** · **mirar el tiempo** y decidir la carpa · **imprimir los carteles** |
| **Jueves 5** | **Montar los globos de estructura** *(arcos, columnas)* · dejarlos en el almacén |
| **Viernes 6** | **Los globos que se ven de cerca** · **el picoteo que se pueda dejar hecho** · la carpa, si se ha decidido |
| **Sábado 7** | **Dejarlo todo listo**: mesa, mantel, tarta, lazos, letras · **las bolsas y los premios en el almacén, juntos y a mano** · **si se puede, el picoteo montado** |
| **Domingo 8** | **9:00** subir los globos y montar la mesa · **10:00** abrir · **14:30** cerrar y recoger |

> **Los globos del jueves 5 al domingo 8 son TRES DÍAS.** **Un globo de látex, inflado con aire, a los tres días está mustio.** **Lo que se monte el jueves: la estructura, que no se ve de cerca.** **Lo de la entrada y la mesa, el viernes por la noche o el sábado.**

> **Y el sábado 7 no es un día perdido**: **es el día que hace que el domingo salga bien.** **Ese día no se monta nada nuevo: se deja todo listo.**

"""

rep("## 2 · Lo que tiene que estar listo ANTES", CALENDARIO + "## 3 · Lo que tiene que estar listo ANTES", "el calendario")

# se renumera del 3 en adelante (el 2 antiguo pasa a 3, y todo lo demas sube)
import re


def sube(m):
    n = int(m.group(1))
    return f"## {n + 1} ·" if n >= 3 and "calendario" not in m.group(0) else m.group(0)


partes = t.split("\n")
salida = []
visto_calendario = False
for linea in partes:
    m = re.match(r"^## (\d+) · (.*)$", linea)
    if m:
        n = int(m.group(1))
        titulo = m.group(2)
        if "El calendario de estos días" in titulo:
            salida.append(linea)
        elif n >= 3:
            salida.append(f"## {n + 1} · {titulo}")
        else:
            salida.append(linea)
    else:
        salida.append(linea)
t = "\n".join(salida)

# --- el jueves y el viernes, con fecha
rep("| **Jueves y viernes** | **Montar los globos** con el compresor · dejarlos en el almacén |",
    "| **Jueves 5 y viernes 6** | **Montar los globos** con el compresor · dejarlos en el almacén |",
    "el jueves y el viernes, con fecha")

rep("| **La fecha del aniversario** | pendiente |",
    "| ~~La fecha~~ | **domingo 8 de noviembre de 2026** — cerrado |",
    "la fecha, cerrada")

open(p, "w", encoding="utf-8").write(t)

numeros = [int(x) for x in re.findall(r"^## (\d+) ·", t, re.M)]
print(f"\n  apartados: {numeros}")
print(f"  seguidos: {numeros == list(range(1, len(numeros) + 1))}")
print(f"  cambios: {fallos}")
