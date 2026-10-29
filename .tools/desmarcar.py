"""El encargo se puede desmarcar (y ojo: aquí está la cascada)."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()

viejo = "      e.hecho = true; e.qHecho = marca; e.hHecho = hora; e.diaHecho = hoyISO(zona);"
nuevo = """      /* se puede marcar y DESMARCAR: si alguien le dio sin querer, se deshace */
      if (cuerpo.deshacer) {
        e.hecho = false;
        delete e.qHecho; delete e.hHecho; delete e.diaHecho;
      } else {
        e.hecho = true; e.qHecho = marca; e.hHecho = hora; e.diaHecho = hoyISO(zona);
      }"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  el encargo se puede desmarcar")
