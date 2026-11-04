"""El alta de encargos (la que usa la pantalla) guarda producto, cantidad y nota.

La pantalla NO usa /api/encargo: usa /api/encargo-fecha. Ahí es donde tienen
que ir los tres datos, o el formulario nuevo guardaría el encargo sin ellos.
"""
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = r"docs\nube\netlify\functions\nucleo.js"
t = open(p, encoding="utf-8").read()

ANCLA = "        que: que,"
NUEVO = ("        que: que,\n"
         "        /* el pedido por proveedor: el producto del desplegable, la cantidad\n"
         "           y la observación libre. Si no vienen, no se guardan. */\n"
         "        producto: c.producto ? String(c.producto).slice(0, 40) : undefined,\n"
         "        cantidad: Number.isFinite(Number(c.cantidad)) ? Number(c.cantidad) : undefined,\n"
         "        nota: c.nota ? String(c.nota).slice(0, 300) : undefined,")

if "producto: c.producto ? String(c.producto)" in t and ANCLA in t:
    print("  OJO: ya hay un producto en el fichero. No se toca.")
    sys.exit(1)

if ANCLA not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)

t = t.replace(ANCLA, NUEVO, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  el alta de encargos guarda producto, cantidad y observación")
