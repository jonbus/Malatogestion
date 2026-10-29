"""Cómo recibe el cuerpo el manejador del núcleo."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
i = t.find("return async function")
if i < 0:
    i = t.find("const manejar")
if i < 0:
    i = t.find("async (peticion)")
if i < 0:
    # se busca donde se desestructura metodo/ruta/cuerpo
    i = t.find("cuerpo }")
print(t[max(0, i - 400):i + 900])
