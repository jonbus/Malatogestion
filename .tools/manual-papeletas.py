"""Las papeletas estarán listas el lunes: el manual deja de avisar de eso."""
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


# --- el aviso grande de recortar, ya resuelto
rep("""### ⚠ Lo primero que hay que resolver: las papeletas están SIN RECORTAR

**Las 500 papeletas están todavía en las 34 hojas, sin recortar y sin doblar.**

**Eso es trabajo de manos, y no se puede hacer el mismo día a las 10 de la mañana con la tienda llena.**

- [ ] **Recortar las 34 hojas** — por la línea de puntos
- [ ] **Doblar las 500**
- [ ] **Y dejarlas en la urna antes de abrir**

> **Cómo se reparte el trabajo**: **cortar es lo que más tarda**. **Con dos personas y una guillotina, una hora.** **A mano con tijera, dos o tres.**""",
    """### ✓ Las papeletas: resueltas antes

**La propiedad las tendrá recortadas y dobladas para el LUNES 2 de noviembre.**

**Eso era lo único que iba justo de tiempo** — **y ya no lo va**. **El domingo no se recorta nada.**

- [ ] **Recoger las papeletas el lunes 2**
- [ ] **Contarlas**: **tienen que ser 500**
- [ ] **Guardarlas en el almacén, con la urna**, hasta el día

> **Y el domingo solo hay que abrir la urna y meterlas.** **Dos minutos.**""",
    "las papeletas, resueltas")

# --- la lista de lo que tiene que estar listo
rep("| **La urna** y las papeletas | 500 · 34 hojas | — | — |",
    "| **La urna** y las papeletas | 500, **recortadas y dobladas** | **listas el lunes 2** | **—** |",
    "la urna y las papeletas, en la lista")

# --- el calendario
rep("| **Esta semana** *(29 – 1 nov)* | **Recortar y doblar las 500 papeletas** — **lo que más tiempo cuesta y no depende de nadie** · **decidir qué piezas de globos** y **hacer sus bases** · comprar lo que falte |",
    "| **Esta semana** *(29 – 1 nov)* | **Decidir qué piezas de globos** y **hacer sus bases** · comprar lo que falte |",
    "el calendario, sin las papeletas")

rep("| **Semana del 2** | **Comprar el picoteo** *(jamón, cabecero, chorizo, queso, pastas Dulcesol)* · **confirmar la batukada** · **mirar el tiempo** y decidir la carpa · **imprimir los carteles** |",
    "| **Semana del 2** | **Recoger las 500 papeletas** *(el lunes 2)* · **comprar el picoteo** *(jamón, cabecero, chorizo, queso, pastas Dulcesol)* · **confirmar la batukada** · **mirar el tiempo** y decidir la carpa · **imprimir los carteles** |",
    "el lunes 2, recoger las papeletas")

# --- el día, hora a hora
rep("| **9:00 – 10:00** | **Recortar y doblar las 500 papeletas** · la urna · **la mesa de la tarta**: caballetes, tablón, mantel, tarta, lazos, letras, palmeritas |",
    "| **9:00 – 10:00** | **La urna con las papeletas** · **la mesa de la tarta**: caballetes, tablón, mantel, tarta, lazos, letras, palmeritas |",
    "el dia, sin recortar")

rep("""> **Lo que no esté a las 10:00, ya no se monta.** **A partir de ahí la tienda está llena y no hay hueco.** **Por eso las papeletas se recortan antes** — **las 500.**""",
    """> **Lo que no esté a las 10:00, ya no se monta.** **A partir de ahí la tienda está llena y no hay hueco.** **Y por eso las papeletas llegan ya hechas: el domingo no se recorta nada.**""",
    "el aviso de las 10:00")

# --- lo que no puede pasar
rep("| **Que no haya papeletas recortadas** | **500 sin recortar no se arreglan a las 10 de la mañana** |",
    "| **Que las papeletas no estén el lunes 2** | **500 sin recortar no se arreglan a las 10 de la mañana** |",
    "el riesgo, actualizado")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
