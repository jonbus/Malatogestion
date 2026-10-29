"""Arregla: leer() se olvidaba de los recuentos."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()

viejo = """      encargos: Array.isArray(guardado.encargos) ? guardado.encargos : [],
      fichajes: Array.isArray(guardado.fichajes) ? guardado.fichajes : []
    };"""
nuevo = """      encargos: Array.isArray(guardado.encargos) ? guardado.encargos : [],
      fichajes: Array.isArray(guardado.fichajes) ? guardado.fichajes : [],
      /* se guardaba, pero aquí se olvidaba: se escribía y no se leía nunca */
      recuentos: guardado.recuentos && typeof guardado.recuentos === 'object'
        ? guardado.recuentos : {}
    };"""

if viejo in t:
    open(p, "w", encoding="utf-8").write(t.replace(viejo, nuevo, 1))
    print("  ok  leer() ya devuelve los recuentos")
else:
    print("  NO ENCONTRADO")
