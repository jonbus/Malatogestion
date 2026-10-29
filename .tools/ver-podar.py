"""Muestra podar() y el endpoint de encargo tal como están ahora."""
import sys

sys.stdout.reconfigure(encoding="utf-8")
t = open("docs/nube/netlify/functions/nucleo.js", encoding="utf-8").read()

i = t.find("function podar")
j = t.find("\nfunction ", i + 10)
print("=== podar ===")
print(t[i:j])

i = t.find("/encargo'")
print("\n\n=== endpoint de encargo ===")
print(t[max(0, i - 80):i + 1400])
