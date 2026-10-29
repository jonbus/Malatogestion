"""Dónde se pinta el panel de modificar: tiene que estar en todas las pantallas."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
js = open("docs/nube/public/index.html", encoding="utf-8").read().split("<script>")[-1].split("</script>")[0]

funciones = [(m.start(), m.group(1)) for m in re.finditer(r"function ([\w]+)\(", js)]
sitios = []
for m in re.finditer(r"panelEdicion\(\)", js):
    k = m.start()
    antes = [n for p, n in funciones if p < k]
    sitios.append(antes[-1] if antes else "?")

print("  el panel de modificar se pinta en:")
for s in sorted(set(sitios)):
    print("   ", s)

falta = [x for x in ("pintaMenu", "pintaExtra", "pinta", "pintaGerencia") if x not in sitios]
print("\n  falta en:", falta if falta else "ninguna")
