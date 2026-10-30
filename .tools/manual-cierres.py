"""Cierra tres huecos del manual: la tarta es adorno, la mesa es de los niños
y los turnos de la tienda ya están arreglados."""
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


# --- 1 · la tarta es de adorno
rep("""### Paso 4 · La tarta
- [ ] **Subir la estructura** de la tarta""",
    """### Paso 4 · La tarta

> **La tarta es de ADORNO.** **Es una estructura de porexpan: no se corta, no se reparte y no se come.** **Nadie tiene que llevar cuchillo ni platos** — **lo que se come son las palmeritas.**

- [ ] **Subir la estructura** de la tarta""",
    "la tarta es de adorno")

# --- 2 · los niños llevan la mesa de las palmeras y la urna
rep("""**Uno da la palmera y el otro la bolsa** — **a todos los clientes, antes de entrar**.""",
    """**Uno da la palmera y el otro la bolsa** — **a todos los clientes, antes de entrar**.

**Y además se encargan de la mesa de las palmeras y de la urna.** **Es su sitio**: **ahí está todo lo que se da, y ellos son los que lo dan.**""",
    "los niños llevan la mesa")

rep("""- [ ] **Que un adulto esté pendiente de ellos** — **son dos críos en la puerta todo el día**""",
    """- [ ] **Que un adulto esté cerca** — **no para quitarles el sitio, sino para que puedan ir al baño, comer o descansar un rato**
- [ ] **Que la mesa de las palmeras y la urna estén donde ellos alcancen** — **sin tener que salir de su sitio**""",
    "el adulto cerca, no encima")

# --- 3 · los turnos de la tienda
rep("""| **Tienda** | **La jornada normal** — **la tienda funciona como cualquier día** |""",
    """| **Tienda** | **La jornada normal.** **Los turnos ya están arreglados** — **no hay que tocar nada** |""",
    "los turnos, arreglados")

# --- 4 · se cierran las preguntas que ya tienen respuesta
rep("""| **Quién vigila la urna** | pendiente |""",
    """| ~~Quién vigila la urna~~ | **los niños** — cerrado |""",
    "la urna, cerrada")

rep("""| **Si la tarta se corta o es solo adorno** | **por confirmar** |""",
    """| ~~Si la tarta se corta~~ | **es de adorno: no se corta** — cerrado |""",
    "la tarta, cerrada")

rep("""| **Quién cubre a los niños** en el relevo | pendiente |""",
    """| **Quién está cerca de los niños** en el relevo | pendiente |""",
    "el relevo, sigue abierto")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
