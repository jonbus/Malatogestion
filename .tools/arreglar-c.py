"""Arregla el `c` que no existe en el calendario."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/generar-nube.py"
t = open(p, encoding="utf-8").read()

n = 0
for viejo, nuevo in (
    ('c.querySelectorAll(".inp-enc")', 'document.querySelectorAll(".inp-enc")'),
    ('c.querySelectorAll("[data-borrar-enc]")', 'document.querySelectorAll("[data-borrar-enc]")'),
    ('c.querySelectorAll("[data-borrar]")', 'document.querySelectorAll("[data-borrar]")'),
):
    if viejo in t:
        cuantos = t.count(viejo)
        t = t.replace(viejo, nuevo)
        print(f"   ok  {viejo} -> document  ({cuantos} sitios)")
        n += cuantos
    else:
        print(f"   (no estaba: {viejo})")

open(p, "w", encoding="utf-8").write(t)
print(f"\n  cambiados {n} sitios")
