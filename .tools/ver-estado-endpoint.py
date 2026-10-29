"""Muestra el endpoint /api/estado."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
i = t.find("/estado'")
print(t[max(0, i - 40):i + 560])
