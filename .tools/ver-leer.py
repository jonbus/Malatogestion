"""Muestra leer() y escribir() del núcleo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
for nombre in ("async function leer", "async function escribir"):
    i = t.find(nombre)
    j = t.find("\n  }", i)
    print(f"=== {nombre} ===")
    print(t[i:j + 4])
    print()
