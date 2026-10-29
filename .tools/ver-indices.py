"""Todos los accesos [2] y [2] encadenados de la app."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

print("  === accesos [2] ===")
for m in re.finditer(r"\[2\]", js):
    i = m.start()
    linea = js[:i].count("\n") + 1
    print(f"   L{linea}: …{js[max(0,i-75):i+25]}…".replace("\n", " "))

print("\n  === accesos [1] (por si el error cambia) ===")
for m in list(re.finditer(r"\[1\]", js))[:6]:
    i = m.start()
    linea = js[:i].count("\n") + 1
    print(f"   L{linea}: …{js[max(0,i-75):i+25]}…".replace("\n", " "))
