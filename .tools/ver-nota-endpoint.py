"""Muestra el endpoint de la nota, para copiar su estructura."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
i = t.find("/nota'")
print(t[max(0, i - 250):i + 950])
