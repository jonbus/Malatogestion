"""Mira cómo se crea un encargo, para apuntar su nombre."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = open(r"docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()
i = t.find("endsWith('/encargo')")
print(t[max(0, i - 120):i + 1100])
