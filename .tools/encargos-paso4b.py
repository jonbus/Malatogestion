"""El resumen tiene que saber de quién es cada pedido.

Al guardar, el campo «qué es» se llena con el proveedor («Zuaza» o «Tahona»),
y el producto va aparte. Así el resumen agrupa sin adivinar nada.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()
fallos = 0


def rep(v, n, e):
    global t, fallos
    if t.count(v) == 1:
        t = t.replace(v, n, 1)
        fallos += 1
        print("  ok  " + e)
    elif t.count(v) == 0:
        print("  NO ENCONTRADO: " + e)
    else:
        print(f"  OJO, aparece {t.count(v)} veces: " + e)


# 1 · al guardar, «qué es» es el proveedor
rep("""  const cuerpo = {
    quien: quien.id, que: que,""",
    """  /* si es de un proveedor, «qué es» guarda el nombre del proveedor y el
     producto va en su campo. Así el resumen agrupa sin adivinar. */
  const nombreProveedor = encProveedor === "zuaza" ? "Zuaza"
    : encProveedor === "tahona" ? "Tahona" : "";
  const cuerpo = {
    quien: quien.id, que: (nombreProveedor || que),""",
    "el nombre del proveedor al guardar")

# 2 · el resumen agrupa por ese nombre
rep("""      const g = e.producto ? (e.que && e.que.toLowerCase().includes("zuaza") ? "Zuaza" : "Proveedor") : "Varios";""",
    """      const g = e.producto ? (e.que || "Proveedor") : "Varios";""",
    "el resumen agrupa por el nombre")

rep("v-2026-10-26-91", "v-2026-10-26-92", "sube la versión")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambios: {fallos}")
