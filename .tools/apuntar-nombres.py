"""Cada tarea nueva apunta su nombre en la memoria."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"docs/nube/netlify/functions/nucleo.js"
t = open(p, encoding="utf-8").read()

viejo = """      estado.encargos.push({
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        t: texto, p: puesto, q: marca,"""
nuevo = """      /* la memoria de los nombres: solo el texto, sin fechas ni cantidades, y no caduca */
      estado.nombres = estado.nombres || [];
      if (!estado.nombres.includes(texto)) {
        estado.nombres.push(texto);
        if (estado.nombres.length > 500) estado.nombres.shift();
      }
      estado.encargos.push({
        id: Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
        t: texto, p: puesto, q: marca,"""

if viejo not in t:
    print("  NO ENCONTRADO")
    sys.exit(1)
t = t.replace(viejo, nuevo, 1)
open(p, "w", encoding="utf-8").write(t)
print("  ok  cada tarea nueva apunta su nombre")
