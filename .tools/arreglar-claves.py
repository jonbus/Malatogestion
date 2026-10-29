"""Arregla las claves del traslado en la prueba."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r".tools/prueba-usuario-completa.mjs"
t = open(p, encoding="utf-8").read()
t = t.replace("clave: T + ':x'", "clave: hoy + '|x|' + T")
open(p, "w", encoding="utf-8").write(t)
print("  arreglado")
