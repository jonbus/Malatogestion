"""Dónde están los dos cortes y si el segundo está en su sitio."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

funciones = [(m.start(), m.group(1)) for m in re.finditer(r"function ([\w]+)\(", js)]
for m in re.finditer(r"indexOf\(MARCA\)", js):
    k = m.start()
    antes = [n for p, n in funciones if p < k]
    cual = antes[-1] if antes else "?"
    print(f"  linea {js[:k].count(chr(10)) + 1}: dentro de {cual}")
